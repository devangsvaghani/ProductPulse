import pandas as pd
import re
import os
from typing import Optional, List

# --- Imports ---
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import openai # We still use the openai library to call OpenRouter
from dotenv import load_dotenv

# --- Setup ---
load_dotenv()

# We configure the openai client to point to OpenRouter's API
client = openai.OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

try:
    sia = SentimentIntensityAnalyzer()
except LookupError:
    import nltk
    print("Downloading VADER lexicon...")
    nltk.download('vader_lexicon')
    sia = SentimentIntensityAnalyzer()


def clean_text(text: str) -> str:
    """Cleans the raw text for analysis."""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text

def get_ai_summary(feedback_list: List[str], topic_keywords: str) -> str:
    """
    Uses a powerful, free model from OpenRouter to generate a high-quality summary.
    """
    if not client.api_key:
        return "OpenRouter API key not found. Cannot generate summary."

    feedback_str = "\n- ".join(feedback_list)
    
    # This is the powerful pre-prompting you wanted
    prompt = (
        f"You are an expert product analyst. Your task is to summarize customer feedback for a specific topic.\n"
        f"The topic is generally about: '{topic_keywords}'.\n\n"
        f"Here is the raw feedback from several customers:\n- {feedback_str}\n\n"
        f"Please analyze all the feedback provided and write a single, coherent, and well-written paragraph that summarizes the key points, sentiments, and any actionable insights. Ensure the summary is a complete thought and does not end abruptly."
    )
    
    try:
        response = client.chat.completions.create(
            # This extra_headers part is recommended by OpenRouter
            extra_headers={
              # You can replace this with your actual GitHub repo URL if you like
              "HTTP-Referer": "https://github.com/your-username/productpulse", 
              "X-Title": "ProductPulse",
            },
            # --- Here is the new, corrected model ID ---
            model="google/gemma-3-27b-it:free",
            messages=[
                {"role": "system", "content": "You are a world-class product analyst summarizing customer reviews."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=250,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"An error occurred with the OpenRouter API: {e}")
        return "AI summary could not be generated due to an API error."


def process_feedback_file(filepath: str) -> Optional[List[dict]]:
    """
    Loads, cleans, and performs a full AI analysis using OpenRouter for summarization.
    """
    print(f"--- Starting Full AI Analysis Pipeline on {filepath} ---")
    
    try:
        df = pd.read_csv(filepath)
        df['cleaned_feedback'] = df['Review Text'].apply(clean_text)
        df.reset_index(inplace=True)
        df.rename(columns={'index': 'doc_id'}, inplace=True)
        
        modeling_df = df[df['cleaned_feedback'] != ''].copy()
        
        if modeling_df.empty: return []

        print("Vectorizing text...")
        vectorizer = CountVectorizer(max_df=0.9, min_df=5, stop_words='english')
        text_counts = vectorizer.fit_transform(modeling_df['cleaned_feedback'])
        
        n_topics = 7
        print(f"Identifying {n_topics} topics with LDA...")
        lda = LatentDirichletAllocation(n_components=n_topics, random_state=42)
        modeling_df['topic_id'] = lda.fit_transform(text_counts).argmax(axis=1)

        print("Analyzing topics, sentiment, and generating summaries with OpenRouter...")
        final_results = []
        feature_names = vectorizer.get_feature_names_out()

        for topic_id in range(n_topics):
            top_words_indices = lda.components_[topic_id].argsort()[:-6:-1]
            top_words = " ".join([feature_names[i] for i in top_words_indices])
            topic_docs_df = modeling_df[modeling_df['topic_id'] == topic_id]
            
            if topic_docs_df.empty: continue

            sentiment_scores = topic_docs_df['cleaned_feedback'].apply(lambda text: sia.polarity_scores(text)['compound'])
            avg_sentiment_score = sentiment_scores.mean()
            
            summary_docs = topic_docs_df.head(10)
            raw_feedback_list = df.loc[summary_docs['doc_id']]['Review Text'].dropna().tolist()
            
            ai_summary = get_ai_summary(raw_feedback_list, top_words)

            topic_result = {
                "topic_id": topic_id, "top_words": top_words, "review_count": len(topic_docs_df),
                "avg_sentiment": avg_sentiment_score, "ai_summary": ai_summary
            }
            final_results.append(topic_result)
        
        print("\n--- AI Analysis Complete ---")
        return final_results

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

if __name__ == "__main__":
    large_file_path = "large_feedback.csv"
    analysis_results = process_feedback_file(large_file_path)

    if analysis_results:
        print("\n\n--- Final Structured Results ---")
        for result in analysis_results:
            print(f"\nTopic {result['topic_id']}: {result['top_words']} ({result['review_count']} reviews)")
            print(f"  Avg. Sentiment Score: {result['avg_sentiment']:.4f}")
            print(f"  AI Summary: {result['ai_summary']}")