import React, { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import api from "../services/api";

const DetailSkeleton = () => (
    <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8 animate-pulse">
        <div className="h-5 bg-gray-200 rounded w-48 mb-6"></div>
        <div className="bg-white shadow rounded-lg mb-6">
            <div className="px-4 py-5 sm:px-6">
                <div className="h-8 bg-gray-300 rounded w-1/2"></div>
                <div className="h-4 bg-gray-200 rounded w-1/4 mt-2"></div>
            </div>
        </div>
        <div className="space-y-6">
            <div className="h-6 bg-gray-300 rounded w-1/3"></div>
            {[...Array(3)].map((_, i) => (
                <div
                    key={i}
                    className="bg-white p-6 rounded-lg shadow-md border border-gray-200"
                >
                    <div className="h-5 bg-gray-300 rounded w-1/4 mb-4"></div>
                    <div className="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
                    <div className="space-y-2">
                        <div className="h-3 bg-gray-200 rounded"></div>
                        <div className="h-3 bg-gray-200 rounded w-5/6"></div>
                    </div>
                </div>
            ))}
        </div>
    </div>
);

const DetailPage = () => {
    const { uploadId } = useParams();
    const [upload, setUpload] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        const fetchDetails = async () => {
            try {
                const response = await api.get(`/api/v1/uploads/${uploadId}`);
                setUpload(response.data);
            } catch (err) {
                setError("Failed to fetch upload details.");
                console.error(err);
            } finally {
                setIsLoading(false);
            }
        };
        fetchDetails();
    }, [uploadId]);

    if (isLoading) return <DetailSkeleton />;
    if (error)
        return <div className="text-center p-10 text-red-500">{error}</div>;
    if (!upload)
        return <div className="text-center p-10">Upload not found.</div>;

    return (
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
            <div className="mb-4">
                <Link to="/" className="text-indigo-600 hover:text-indigo-900">
                    &larr; Back to all uploads
                </Link>
            </div>
            <div className="bg-white shadow overflow-hidden sm:rounded-lg mb-6">
                <div className="px-4 py-5 sm:px-6">
                    <h2 className="text-2xl leading-6 font-bold text-gray-900">
                        {upload.filename}
                    </h2>
                    <p className="mt-1 max-w-2xl text-sm text-gray-500">
                        Status:{" "}
                        <span className="font-medium">{upload.status}</span>
                    </p>
                </div>
            </div>

            <div className="space-y-6">
                <h3 className="text-xl font-semibold text-gray-800">
                    Analysis Results by Topic
                </h3>
                {upload.results.length > 0 ? (
                    upload.results.map((result) => (
                        <div
                            key={result.topic}
                            className="bg-white p-6 rounded-lg shadow-md border border-gray-200"
                        >
                            <h4 className="text-lg font-bold text-gray-800 capitalize">
                                {result.topic}
                            </h4>
                            <div className="text-sm text-gray-500 my-2">
                                <span>{result.review_count} reviews</span>{" "}
                                &middot;
                                <span>
                                    {" "}
                                    Avg. Sentiment:{" "}
                                    <span
                                        className={
                                            result.sentiment_score > 0.05
                                                ? "text-green-600"
                                                : result.sentiment_score < -0.05
                                                ? "text-red-600"
                                                : "text-gray-600"
                                        }
                                    >
                                        {result.sentiment_score.toFixed(2)}
                                    </span>
                                </span>
                            </div>
                            <p className="text-gray-700 leading-relaxed">
                                {result.summary}
                            </p>
                        </div>
                    ))
                ) : (
                    <div className="text-center bg-white p-6 rounded-lg shadow-md border">
                        {upload.status === "processing" ? (
                            <p>
                                Analysis is still in progress. Please check back
                                in a moment.
                            </p>
                        ) : (
                            <p>
                                No analysis results are available for this
                                upload.
                            </p>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

export default DetailPage;
