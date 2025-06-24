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
  const [resumeId, setResumeId] = useState<string | null>(null);
  const [isExtracting, setIsExtracting] = useState(false);
  const [selectedJobsForTailoring, setSelectedJobsForTailoring] = useState<Job[]>([]);
  const [extractedData, setExtractedData] = useState<any | null>(null);

  const handleFileUpload = (file: File, resumeId: string) => {
    setUploadedFile(file);
    setResumeId(resumeId);
    console.log('File uploaded:', file.name, 'Resume ID:', resumeId);
  };

  const handleExtractDetails = async () => {
    if (!resumeId) return;

    setIsExtracting(true);
    setExtractedData(null);

    try {
      // 1. Start extraction
      const startResponse = await fetch(`http://localhost:8000/api/extract/${resumeId}`, {
        method: 'POST',
      });

      if (!startResponse.ok) {
        throw new Error('Failed to start extraction process.');
      }

      // 2. Poll for status
      const poll = async (): Promise<any> => {
        const statusResponse = await fetch(`http://localhost:8000/api/extract/${resumeId}/status`);
        if (!statusResponse.ok) {
          throw new Error('Failed to get extraction status.');
        }
        const statusData = await statusResponse.json();

        if (statusData.status === 'completed') {
          return statusData.extracted_data;
        } else if (statusData.status === 'failed') {
          throw new Error(statusData.error_message || 'Extraction failed.');
        } else {
          // It's still processing, wait and poll again
          await new Promise(resolve => setTimeout(resolve, 2000)); // wait 2 seconds
          return await poll();
        }
      };

      const data = await poll();
      setExtractedData(data);

      // Navigate to Resume Details tab
      setActiveTab('details');
    } catch (error: any) {
      console.error('Error extracting resume details:', error);
      alert(`Extraction failed: ${error.message}`);
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
            <div className="text-center max-w-4xl mx-auto p-8">
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
              {extractedData ? (
                <div className="bg-white p-6 rounded-lg shadow-md text-left">
                  <h3 className="text-xl font-bold mb-4">Extracted Data</h3>
                  <pre className="bg-gray-100 p-4 rounded-md overflow-x-auto">
                    {JSON.stringify(extractedData, null, 2)}
                  </pre>
                </div>
              ) : (
                <p className="text-gray-600">No extracted data to show.</p>
              )}
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