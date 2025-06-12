import React, { useState, useEffect, useCallback } from "react";
import api from "../services/api";
import axios from "axios";
import { useDropzone } from "react-dropzone";
import { Link } from "react-router-dom";
import toast from "react-hot-toast";
import Papa from "papaparse";
import {
    FaCheckCircle,
    FaExclamationTriangle,
    FaFileCsv,
} from "react-icons/fa";

const FileUpload = ({ onUploadSuccess }) => {
    const [isUploading, setIsUploading] = useState(false);

    const validateCsvHeader = (file) => {
        return new Promise((resolve, reject) => {
            Papa.parse(file, {
                header: true,
                preview: 1,
                complete: (results) => {
                    if (results.meta.fields.includes("Review Text")) {
                        resolve();
                    } else {
                        reject(
                            new Error(
                                "Validation Failed: CSV must contain a 'Review Text' column."
                            )
                        );
                    }
                },
                error: (error) => {
                    reject(new Error("Failed to parse CSV file."));
                },
            });
        });
    };

    const onDrop = useCallback(
        async (acceptedFiles) => {
            const file = acceptedFiles[0];
            if (!file) return;

            setIsUploading(true);

            try {
                await validateCsvHeader(file);
            } catch (validationError) {
                toast.error(validationError.message);
                setIsUploading(false);
                return;
            }

            const uploadPromise = async () => {
                const presignedUrlResponse = await api.post(
                    `/api/v1/uploads/presigned-url?filename=${file.name}`
                );
                const { url, fields } = presignedUrlResponse.data;

                const formData = new FormData();
                Object.entries(fields).forEach(([key, value]) =>
                    formData.append(key, value)
                );
                formData.append("file", file);

                await axios.post(url, formData);
            };

            try {
                await toast.promise(uploadPromise(), {
                    loading: "Uploading file...",
                    success: "Upload successful! Processing has started.",
                    error: (err) =>
                        err.response?.data?.detail ??
                        "Upload failed. Please try again.",
                });
                setTimeout(() => onUploadSuccess(), 1000);
            } catch (err) {
                console.error(err);
            } finally {
                setIsUploading(false);
            }
        },
        [onUploadSuccess]
    );

    const { getRootProps, getInputProps } = useDropzone({
        onDrop,
        accept: { "text/csv": [".csv"] },
        maxFiles: 1,
        disabled: isUploading,
    });

    return (
        <div className="mb-8 p-6 bg-white rounded-lg shadow">
            <h2 className="text-lg font-medium text-gray-900 mb-4">
                Upload New Feedback File
            </h2>
            <div
                {...getRootProps()}
                className="p-8 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer text-center hover:border-blue-500 transition-colors"
            >
                <input {...getInputProps()} />
                {isUploading ? (
                    <p>Uploading...</p>
                ) : (
                    <p>Drag 'n' drop a CSV file here, or click to select</p>
                )}
            </div>

            <div className="mt-4 text-sm text-gray-600 space-y-2">
                <h3 className="font-semibold text-gray-700">Requirements:</h3>
                <ul className="list-inside list-disc pl-2 space-y-1">
                    <li className="flex items-center">
                        <FaFileCsv className="text-green-500 mr-2" />
                        File must be in `.csv` format.
                    </li>
                    <li className="flex items-center">
                        <FaCheckCircle className="text-green-500 mr-2" />
                        Filename can only contain letters, numbers, dots,
                        underscores, and hyphens. (e.g.,
                        `sample_feedback-v1.csv`)
                    </li>
                    <li className="flex items-center">
                        <FaExclamationTriangle className="text-amber-500 mr-2" />
                        Filename must be unique. You cannot re-upload a file
                        with the same name.
                    </li>
                    <li className="flex items-center">
                        <FaCheckCircle className="text-green-500 mr-2" />
                        CSV file must contain a header row with a column named
                        exactly "Review Text" on which Analysis happen.
                    </li>
                </ul>
            </div>
        </div>
    );
};

const UploadsListPage = () => {
    const [uploads, setUploads] = useState([]);
    const [isLoading, setIsLoading] = useState(true);

    const fetchUploads = useCallback(async () => {
        if (uploads.length === 0) setIsLoading(true);
        try {
            const response = await api.get("/api/v1/uploads/");
            setUploads(response.data);
        } catch (error) {
            console.error("Failed to fetch uploads", error);
        } finally {
            setIsLoading(false);
        }
    }, [uploads.length]);

    useEffect(() => {
        fetchUploads();
    }, []);

    const SkeletonRow = () => (
        <li className="px-4 py-4 sm:px-6">
            <div className="animate-pulse flex space-x-4">
                <div className="flex-1 space-y-3 py-1">
                    <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                    <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                </div>
                <div className="h-5 bg-gray-200 rounded w-20"></div>
            </div>
        </li>
    );

    return (
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
            <FileUpload onUploadSuccess={fetchUploads} />
            <div className="bg-white shadow overflow-hidden sm:rounded-md">
                <div className="px-4 py-3 sm:px-6 border-b border-gray-200">
                    <h2 className="text-lg leading-6 font-medium text-gray-900">
                        Upload History
                    </h2>
                </div>
                <ul role="list" className="divide-y divide-gray-200">
                    {isLoading && uploads.length === 0 ? (
                        <>
                            <SkeletonRow />
                            <SkeletonRow />
                            <SkeletonRow />
                        </>
                    ) : (
                        uploads.map((upload) => (
                            <li key={upload.id}>
                                <Link
                                    to={`/upload/${upload.id}`}
                                    className="block hover:bg-gray-50"
                                >
                                    <div className="px-4 py-4 sm:px-6">
                                        <div className="flex items-center justify-between">
                                            <p className="text-md font-medium text-indigo-600 truncate">
                                                {upload.filename}
                                            </p>
                                            <div className="ml-2 flex-shrink-0 flex">
                                                <p
                                                    className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                                                        upload.status ===
                                                        "completed"
                                                            ? "bg-green-100 text-green-800"
                                                            : upload.status ===
                                                              "failed"
                                                            ? "bg-red-100 text-red-800"
                                                            : "bg-yellow-100 text-yellow-800"
                                                    }`}
                                                >
                                                    {upload.status}
                                                </p>
                                            </div>
                                        </div>
                                        <div className="mt-2 text-sm text-gray-500">
                                            <p>
                                                Uploaded on:{" "}
                                                {new Date(
                                                    upload.created_at
                                                ).toLocaleString()}
                                            </p>
                                        </div>
                                    </div>
                                </Link>
                            </li>
                        ))
                    )}
                </ul>
                {isLoading && uploads.length === 0 && (
                    <p className="text-center p-4 text-gray-500">
                        Loading uploads...
                    </p>
                )}
                {!isLoading && uploads.length === 0 && (
                    <p className="text-center p-4 text-gray-500">
                        No uploads found. Upload a file to get started.
                    </p>
                )}
            </div>
        </div>
    );
};

export default UploadsListPage;
