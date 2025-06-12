import pandas as pd
import re
import os
import nltk
from typing import Optional, List

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import openai
from dotenv import load_dotenv

load_dotenv()

# Configure client for openrouter.ai
client = openai.OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

# Make sure that nltk finds its data files
nltk.data.path.append(os.path.join(os.path.dirname(__file__), "nltk_data"))

sia = SentimentIntensityAnalyzer()


def clean_text(text: str) -> str:
    # Clean the text
    
    if not isinstance(text, str): return ""
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def get_ai_summary(feedback_list: List[str], topic_keywords: str) -> str:
    # Used free model from openrouter for summarization
    if not client.api_key: return "OpenRouter API key not found."

    feedback_str = "\n- ".join(feedback_list)
    prompt = (
        f"You are a product analyst summarizing customer feedback about '{topic_keywords}'.\n"
        f"Here is the raw feedback:\n- {feedback_str}\n\n"
        f"Please write a single, coherent paragraph that summarizes the key points and sentiments expressed."
    )
    
    try:
        response = client.chat.completions.create(
            # we can change the url here 
            extra_headers={"HTTP-Referer": "http://localhost:3000", "X-Title": "ProductPulse"},
            model="google/gemma-3-27b-it:free",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=250, temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"AI summary could not be generated due to an API error: {e}"

def process_feedback_file(filepath: str) -> Optional[List[dict]]:
    # This funciton gets file and does the AI analysis

    print(f"--- Starting AI Analysis on {filepath} ---")

    try:
        df = pd.read_csv(filepath, engine='python', on_bad_lines='skip')

        if "Review Text" not in df.columns:
            print("Error: 'Review Text' column not found in the CSV file.")
            raise ValueError("Required column 'Review Text' is missing from the input file.")

        df['cleaned_feedback'] = df['Review Text'].apply(clean_text)
        df.reset_index(inplace=True); df.rename(columns={'index': 'doc_id'}, inplace=True)
        
        modeling_df = df[df['cleaned_feedback'] != ''].copy()
        if modeling_df.empty: return []

        print("Vectorizing text...")
        vectorizer = CountVectorizer(max_df=0.9, min_df=5, stop_words='english')
        text_counts = vectorizer.fit_transform(modeling_df['cleaned_feedback'])
        
        # For now we fixed the topic count to 7
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

            # Calculate the average compound sentiment score
            sentiment_scores = topic_docs_df['cleaned_feedback'].apply(lambda t: sia.polarity_scores(t)['compound'])
            avg_sentiment_score = sentiment_scores.mean()

            # Get a sentiment dictionary for the entire topic
            sentiment_text_sample = " ".join(topic_docs_df.head(50)['cleaned_feedback'])
            topic_sentiment_dict = sia.polarity_scores(sentiment_text_sample)
            
            # Get raw feedback for the AI summary
            summary_docs = topic_docs_df.head(10)
            raw_feedback_list = df.loc[summary_docs['doc_id']]['Review Text'].dropna().tolist()
            ai_summary = get_ai_summary(raw_feedback_list, top_words)

            topic_result = {
                "topic_id": topic_id,
                "top_words": top_words,
                "review_count": len(topic_docs_df),
                "avg_sentiment": avg_sentiment_score,
                "sentiment_dict": topic_sentiment_dict,
                "ai_summary": ai_summary
            }
            final_results.append(topic_result)
        
        print("\n--- AI Analysis Complete ---")

        return final_results
    except Exception as e:
        print(f"An unexpected error occurred in worker: {e}")
        return None