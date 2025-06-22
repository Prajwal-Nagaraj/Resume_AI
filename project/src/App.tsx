import React, { useState } from 'react';
import { Navigation } from './components/Navigation';
import { LandingPage } from './components/LandingPage';
import { JobSearch } from './components/JobSearch';
import { ResumeTailoring } from './components/ResumeTailoring';

interface Job {
  id: string;
  title: string;
  company: string;
  location: string;
  postedDate: string;
  description: string;
  employmentType: string;
  experienceLevel: string;
  salary?: string;
  linkedinUrl: string;
  companyLogo?: string;
  applicants?: number;
}

function App() {
  const [activeTab, setActiveTab] = useState('landing');
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [isExtracting, setIsExtracting] = useState(false);
  const [selectedJobsForTailoring, setSelectedJobsForTailoring] = useState<Job[]>([]);

  const handleFileUpload = (file: File) => {
    setUploadedFile(file);
    console.log('File uploaded:', file.name);
  };

  const saveFileToResumesFolder = async (file: File): Promise<void> => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      // Create a timestamp for unique filename
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      const fileExtension = file.name.split('.').pop();
      const fileName = `resume_${timestamp}.${fileExtension}`;
      
      // Convert file to base64 for storage
      const reader = new FileReader();
      return new Promise((resolve, reject) => {
        reader.onload = async () => {
          try {
            const base64Data = reader.result as string;
            const response = await fetch('/api/save-resume', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                fileName,
                fileData: base64Data,
                originalName: file.name
              })
            });
            
            if (!response.ok) {
              throw new Error('Failed to save file');
            }
            
            resolve();
          } catch (error) {
            reject(error);
          }
        };
        reader.onerror = reject;
        reader.readAsDataURL(file);
      });
    } catch (error) {
      console.error('Error saving file:', error);
      throw error;
    }
  };

  const handleExtractDetails = async () => {
    if (!uploadedFile) return;
    
    setIsExtracting(true);
    
    try {
      // Simulate file processing and saving
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // In a real application, you would save the file to the server here
      // For now, we'll simulate the process
      console.log('Saving file to resumes folder:', uploadedFile.name);
      
      // Navigate to Resume Details tab
      setActiveTab('details');
    } catch (error) {
      console.error('Error extracting resume details:', error);
    } finally {
      setIsExtracting(false);
    }
  };

  const handleJobsTailored = (jobs: Job[]) => {
    setSelectedJobsForTailoring(jobs);
    setActiveTab('tailoring');
  };

  const handleBackToJobSearch = () => {
    setActiveTab('search');
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'landing':
        return (
          <LandingPage 
            onFileUpload={handleFileUpload} 
            uploadedFile={uploadedFile}
            onExtractDetails={handleExtractDetails}
            isExtracting={isExtracting}
          />
        );
      case 'details':
        return (
          <div className="min-h-screen bg-gray-50 flex items-center justify-center">
            <div className="text-center max-w-2xl mx-auto p-8">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">Resume Details</h2>
              {uploadedFile && (
                <div className="bg-white rounded-lg shadow-md p-6 mb-6">
                  <p className="text-lg text-gray-700 mb-2">
                    Successfully processed: <span className="font-semibold text-blue-600">{uploadedFile.name}</span>
                  </p>
                  <p className="text-sm text-gray-500">
                    File size: {(uploadedFile.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
              )}
              <p className="text-gray-600">Resume details extraction and analysis coming soon...</p>
            </div>
          </div>
        );
      case 'search':
        return <JobSearch onJobsTailored={handleJobsTailored} />;
      case 'tailoring':
        return (
          <ResumeTailoring 
            selectedJobs={selectedJobsForTailoring}
            onBack={handleBackToJobSearch}
          />
        );
      default:
        return (
          <LandingPage 
            onFileUpload={handleFileUpload} 
            uploadedFile={uploadedFile}
            onExtractDetails={handleExtractDetails}
            isExtracting={isExtracting}
          />
        );
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation activeTab={activeTab} onTabChange={setActiveTab} />
      {renderContent()}
    </div>
  );
}

export default App;