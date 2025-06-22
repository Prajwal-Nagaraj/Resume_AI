import React, { useState, useCallback } from 'react';
import { Upload, FileText, Check, AlertCircle, X } from 'lucide-react';

interface FileUploadProps {
  onFileUpload: (file: File) => void;
}

export const FileUpload: React.FC<FileUploadProps> = ({ onFileUpload }) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle');
  const [uploadProgress, setUploadProgress] = useState(0);
  const [errorMessage, setErrorMessage] = useState('');
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);

  const validateFile = (file: File): boolean => {
    const allowedTypes = [
      'application/pdf',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'application/msword'
    ];
    
    const maxSize = 10 * 1024 * 1024; // 10MB

    if (!allowedTypes.includes(file.type)) {
      setErrorMessage('Please upload a PDF or Word document (.pdf, .docx, .doc)');
      return false;
    }

    if (file.size > maxSize) {
      setErrorMessage('File size must be less than 10MB');
      return false;
    }

    return true;
  };

  const simulateUpload = (file: File) => {
    setUploadStatus('uploading');
    setUploadProgress(0);
    
    const interval = setInterval(() => {
      setUploadProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          setUploadStatus('success');
          setUploadedFile(file);
          onFileUpload(file);
          return 100;
        }
        return prev + 10;
      });
    }, 200);
  };

  const handleFileSelect = useCallback((file: File) => {
    setErrorMessage('');
    setUploadStatus('idle');
    setUploadProgress(0);

    if (validateFile(file)) {
      simulateUpload(file);
    } else {
      setUploadStatus('error');
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  }, [handleFileSelect]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  const resetUpload = () => {
    setUploadStatus('idle');
    setUploadProgress(0);
    setUploadedFile(null);
    setErrorMessage('');
  };

  const getUploadIcon = () => {
    switch (uploadStatus) {
      case 'uploading':
        return <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>;
      case 'success':
        return <Check className="h-8 w-8 text-green-600" />;
      case 'error':
        return <AlertCircle className="h-8 w-8 text-red-600" />;
      default:
        return <Upload className="h-8 w-8 text-gray-400" />;
    }
  };

  const getStatusMessage = () => {
    switch (uploadStatus) {
      case 'uploading':
        return 'Uploading your resume...';
      case 'success':
        return `Successfully uploaded: ${uploadedFile?.name}`;
      case 'error':
        return errorMessage || 'Upload failed. Please try again.';
      default:
        return 'Drop your resume here or click to browse';
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div
        className={`relative border-2 border-dashed rounded-xl p-8 text-center transition-all duration-300 cursor-pointer
          ${isDragOver 
            ? 'border-blue-500 bg-blue-50 scale-102' 
            : uploadStatus === 'success'
            ? 'border-green-500 bg-green-50'
            : uploadStatus === 'error'
            ? 'border-red-500 bg-red-50'
            : 'border-gray-300 hover:border-gray-400 hover:bg-gray-50'
          }`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => uploadStatus !== 'uploading' && document.getElementById('fileInput')?.click()}
      >
        <input
          id="fileInput"
          type="file"
          accept=".pdf,.doc,.docx"
          onChange={handleFileInput}
          className="hidden"
          disabled={uploadStatus === 'uploading'}
        />
        
        <div className="flex flex-col items-center space-y-4">
          {getUploadIcon()}
          
          <div className="space-y-2">
            <p className={`text-lg font-medium ${
              uploadStatus === 'success' 
                ? 'text-green-700' 
                : uploadStatus === 'error'
                ? 'text-red-700'
                : 'text-gray-700'
            }`}>
              {getStatusMessage()}
            </p>
            
            {uploadStatus === 'idle' && (
              <p className="text-sm text-gray-500">
                Supports PDF, DOC, and DOCX files up to 10MB
              </p>
            )}
          </div>

          {uploadStatus === 'uploading' && (
            <div className="w-full max-w-xs">
              <div className="bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                ></div>
              </div>
              <p className="text-sm text-gray-600 mt-2">{uploadProgress}% complete</p>
            </div>
          )}

          {uploadStatus === 'success' && (
            <div className="flex items-center space-x-2">
              <div className="flex items-center space-x-2 bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm">
                <FileText className="h-4 w-4" />
                <span className="font-medium">{uploadedFile?.name}</span>
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  resetUpload();
                }}
                className="p-1 hover:bg-gray-200 rounded-full transition-colors"
              >
                <X className="h-4 w-4 text-gray-500" />
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};