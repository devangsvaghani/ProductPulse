import React, { useState, useEffect, useCallback } from 'react';
import api from '../services/api';
import axios from 'axios';
import { useDropzone } from 'react-dropzone';
import { Link } from 'react-router-dom';

const API_URL = 'http://localhost:8000';

const FileUpload = ({ onUploadSuccess }) => {
  const [status, setStatus] = useState('idle');

  const onDrop = useCallback(async (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (!file) return;

    setStatus('uploading');
    try {
      const presignedUrlResponse = await api.post(`${API_URL}/api/v1/uploads/presigned-url?filename=${file.name}`);
      const { url, fields } = presignedUrlResponse.data;

      const formData = new FormData();
      Object.entries(fields).forEach(([key, value]) => formData.append(key, value));
      formData.append('file', file);

      await axios.post(url, formData);
      setStatus('success');
      setTimeout(() => onUploadSuccess(), 1000); // Trigger refresh after 1 sec
    } catch (err) {
      console.error(err);
      setStatus('error');
    }
  }, [onUploadSuccess]);

  const { getRootProps, getInputProps } = useDropzone({ onDrop, accept: { 'text/csv': ['.csv'] }, maxFiles: 1 });

  return (
    <div className="mb-8 p-6 bg-white rounded-lg shadow">
      <h2 className="text-lg font-medium text-gray-900 mb-4">Upload New Feedback File</h2>
      <div {...getRootProps()} className="p-8 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer text-center hover:border-blue-500 transition-colors">
        <input {...getInputProps()} />
        {status === 'uploading' ? <p>Uploading...</p> : <p>Drag 'n' drop a CSV file here, or click to select</p>}
      </div>
      {status === 'success' && <p className="text-green-600 text-center mt-2">Upload successful! Processing has started.</p>}
      {status === 'error' && <p className="text-red-600 text-center mt-2">Upload failed. Please try again.</p>}
    </div>
  );
};

const UploadsListPage = () => {
  const [uploads, setUploads] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchUploads = useCallback(async () => {
    // Only set loading true on the first fetch
    if (uploads.length === 0) setIsLoading(true);
    try {
      const response = await api.get(`${API_URL}/api/v1/uploads/`);
      setUploads(response.data);
    } catch (error) {
      console.error("Failed to fetch uploads", error);
    } finally {
      setIsLoading(false);
    }
  }, [uploads.length]);

//   useEffect(() => {
//     fetchUploads();
//     const intervalId = setInterval(fetchUploads, 5000); // Refresh list every 5 seconds
//     return () => clearInterval(intervalId);
//   }, [fetchUploads]);

    useEffect(() => {
        fetchUploads();
    }, []);

  return (
    <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <FileUpload onUploadSuccess={fetchUploads} />
      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <div className="px-4 py-3 sm:px-6 border-b border-gray-200">
          <h2 className="text-lg leading-6 font-medium text-gray-900">Upload History</h2>
        </div>
        <ul role="list" className="divide-y divide-gray-200">
          {uploads.map((upload) => (
            <li key={upload.id}>
              <Link to={`/upload/${upload.id}`} className="block hover:bg-gray-50">
                <div className="px-4 py-4 sm:px-6">
                  <div className="flex items-center justify-between">
                    <p className="text-md font-medium text-indigo-600 truncate">{upload.filename}</p>
                    <div className="ml-2 flex-shrink-0 flex">
                      <p className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        upload.status === 'completed' ? 'bg-green-100 text-green-800' :
                        upload.status === 'failed' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {upload.status}
                      </p>
                    </div>
                  </div>
                  <div className="mt-2 text-sm text-gray-500">
                    <p>Uploaded on: {new Date(upload.created_at).toLocaleString()}</p>
                  </div>
                </div>
              </Link>
            </li>
          ))}
        </ul>
        {isLoading && uploads.length === 0 && <p className="text-center p-4 text-gray-500">Loading uploads...</p>}
        {!isLoading && uploads.length === 0 && <p className="text-center p-4 text-gray-500">No uploads found. Upload a file to get started.</p>}
      </div>
    </div>
  );
};

export default UploadsListPage;