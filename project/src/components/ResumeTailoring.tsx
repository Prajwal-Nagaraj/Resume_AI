import React, { useState, useEffect } from 'react';
import { 
  Download, 
  CheckCircle, 
  Clock, 
  AlertCircle, 
  FileText, 
  Building, 
  MapPin, 
  RefreshCw,
  ArrowLeft,
  Target,
  Zap
} from 'lucide-react';

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

interface TailoringJob extends Job {
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  tailoredResumeUrl?: string;
  processingStartTime?: Date;
  completedTime?: Date;
  errorMessage?: string;
}

interface ResumeTailoringProps {
  selectedJobs: Job[];
  onBack: () => void;
}

export const ResumeTailoring: React.FC<ResumeTailoringProps> = ({ selectedJobs, onBack }) => {
  const [tailoringJobs, setTailoringJobs] = useState<TailoringJob[]>([]);
  const [overallProgress, setOverallProgress] = useState(0);
  const [isProcessing, setIsProcessing] = useState(true);
  const [completedCount, setCompletedCount] = useState(0);

  useEffect(() => {
    // Initialize tailoring jobs with pending status
    const initialJobs: TailoringJob[] = selectedJobs.map(job => ({
      ...job,
      status: 'pending',
      progress: 0
    }));
    
    setTailoringJobs(initialJobs);
    
    // Start the tailoring process
    startTailoringProcess(initialJobs);
  }, [selectedJobs]);

  const startTailoringProcess = async (jobs: TailoringJob[]) => {
    setIsProcessing(true);
    
    // Process each job sequentially with realistic timing
    for (let i = 0; i < jobs.length; i++) {
      const job = jobs[i];
      
      // Update job to processing status
      setTailoringJobs(prev => prev.map(j => 
        j.id === job.id 
          ? { ...j, status: 'processing', processingStartTime: new Date() }
          : j
      ));

      // Simulate tailoring process with progress updates
      await simulateTailoringProgress(job.id);
      
      // Mark as completed
      const tailoredResumeUrl = await generateTailoredResume(job);
      
      setTailoringJobs(prev => prev.map(j => 
        j.id === job.id 
          ? { 
              ...j, 
              status: 'completed', 
              progress: 100,
              completedTime: new Date(),
              tailoredResumeUrl 
            }
          : j
      ));

      setCompletedCount(prev => prev + 1);
    }
    
    setIsProcessing(false);
  };

  const simulateTailoringProgress = async (jobId: string) => {
    const steps = [10, 25, 40, 60, 75, 90, 100];
    
    for (const progress of steps) {
      await new Promise(resolve => setTimeout(resolve, 800 + Math.random() * 400));
      
      setTailoringJobs(prev => prev.map(job => 
        job.id === jobId 
          ? { ...job, progress }
          : job
      ));
    }
  };

  const generateTailoredResume = async (job: TailoringJob): Promise<string> => {
    // Simulate backend API call to generate tailored resume
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // In a real application, this would return the actual download URL from the backend
    return `/api/download-resume/${job.id}`;
  };

  const handleDownload = async (job: TailoringJob) => {
    if (!job.tailoredResumeUrl) return;
    
    try {
      // In a real application, this would trigger the actual download
      console.log(`Downloading tailored resume for ${job.title} at ${job.company}`);
      
      // Simulate download
      const link = document.createElement('a');
      link.href = job.tailoredResumeUrl;
      link.download = `Resume_${job.company.replace(/\s+/g, '_')}_${job.title.replace(/\s+/g, '_')}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      // Show success message
      alert(`✅ Resume for ${job.title} at ${job.company} downloaded successfully!`);
    } catch (error) {
      console.error('Download failed:', error);
      alert('❌ Download failed. Please try again.');
    }
  };

  const handleDownloadAll = async () => {
    const completedJobs = tailoringJobs.filter(job => job.status === 'completed');
    
    if (completedJobs.length === 0) {
      alert('No completed resumes to download.');
      return;
    }

    try {
      // Download all completed resumes
      for (const job of completedJobs) {
        await handleDownload(job);
        // Small delay between downloads
        await new Promise(resolve => setTimeout(resolve, 500));
      }
      
      alert(`✅ All ${completedJobs.length} tailored resumes downloaded successfully!`);
    } catch (error) {
      console.error('Bulk download failed:', error);
      alert('❌ Some downloads may have failed. Please try downloading individually.');
    }
  };

  const getStatusIcon = (status: TailoringJob['status']) => {
    switch (status) {
      case 'pending':
        return <Clock className="h-5 w-5 text-gray-400" />;
      case 'processing':
        return <RefreshCw className="h-5 w-5 text-blue-500 animate-spin" />;
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'failed':
        return <AlertCircle className="h-5 w-5 text-red-500" />;
      default:
        return <Clock className="h-5 w-5 text-gray-400" />;
    }
  };

  const getStatusText = (job: TailoringJob) => {
    switch (job.status) {
      case 'pending':
        return 'Waiting in queue...';
      case 'processing':
        return 'Tailoring resume...';
      case 'completed':
        return 'Ready for download';
      case 'failed':
        return job.errorMessage || 'Tailoring failed';
      default:
        return 'Unknown status';
    }
  };

  const getStatusColor = (status: TailoringJob['status']) => {
    switch (status) {
      case 'pending':
        return 'text-gray-600';
      case 'processing':
        return 'text-blue-600';
      case 'completed':
        return 'text-green-600';
      case 'failed':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  // Calculate overall progress
  useEffect(() => {
    const totalProgress = tailoringJobs.reduce((sum, job) => sum + job.progress, 0);
    const avgProgress = tailoringJobs.length > 0 ? totalProgress / tailoringJobs.length : 0;
    setOverallProgress(avgProgress);
  }, [tailoringJobs]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <button
              onClick={onBack}
              className="inline-flex items-center space-x-2 px-4 py-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-all duration-200"
            >
              <ArrowLeft className="h-4 w-4" />
              <span>Back to Job Search</span>
            </button>
            
            <div className="flex items-center space-x-4">
              {completedCount > 0 && (
                <button
                  onClick={handleDownloadAll}
                  className="inline-flex items-center space-x-2 px-6 py-3 bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700 text-white font-semibold rounded-lg transition-all duration-200 transform hover:scale-105 focus:outline-none focus:ring-4 focus:ring-green-200"
                >
                  <Download className="h-5 w-5" />
                  <span>Download All ({completedCount})</span>
                </button>
              )}
            </div>
          </div>

          <div className="text-center">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              Resume Tailoring Status
            </h1>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto mb-6">
              Your resumes are being tailored for each selected job. Track the progress below and download when ready.
            </p>
          </div>

          {/* Overall Progress */}
          <div className="bg-white rounded-2xl shadow-lg p-6 mb-8">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <Target className="h-6 w-6 text-blue-600" />
                <h2 className="text-xl font-semibold text-gray-900">Overall Progress</h2>
              </div>
              <div className="text-sm text-gray-600">
                {completedCount} of {tailoringJobs.length} completed
              </div>
            </div>
            
            <div className="space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Progress</span>
                <span className="font-medium text-gray-900">{Math.round(overallProgress)}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div 
                  className="bg-gradient-to-r from-blue-600 to-purple-600 h-3 rounded-full transition-all duration-500"
                  style={{ width: `${overallProgress}%` }}
                ></div>
              </div>
              <div className="flex justify-between text-xs text-gray-500">
                <span>Started</span>
                <span>{isProcessing ? 'Processing...' : 'Completed'}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Job Tailoring Cards */}
        <div className="space-y-6">
          {tailoringJobs.map((job, index) => (
            <div
              key={job.id}
              className={`bg-white rounded-xl shadow-lg p-6 border transition-all duration-300 ${
                job.status === 'completed' 
                  ? 'border-green-200 bg-green-50' 
                  : job.status === 'processing'
                  ? 'border-blue-200 bg-blue-50'
                  : job.status === 'failed'
                  ? 'border-red-200 bg-red-50'
                  : 'border-gray-200'
              }`}
            >
              <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
                {/* Job Info */}
                <div className="flex-1 space-y-4">
                  <div className="flex items-start justify-between">
                    <div className="space-y-2">
                      <div className="flex items-center space-x-3">
                        <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded-full">
                          #{index + 1}
                        </span>
                        <h3 className="text-xl font-bold text-gray-900">
                          {job.title}
                        </h3>
                      </div>
                      <div className="flex items-center space-x-4 text-gray-600">
                        <div className="flex items-center space-x-1">
                          <Building className="h-4 w-4" />
                          <span className="font-medium">{job.company}</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <MapPin className="h-4 w-4" />
                          <span>{job.location}</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Status and Progress */}
                  <div className="space-y-3">
                    <div className="flex items-center space-x-3">
                      {getStatusIcon(job.status)}
                      <span className={`font-medium ${getStatusColor(job.status)}`}>
                        {getStatusText(job)}
                      </span>
                      {job.status === 'processing' && (
                        <div className="flex items-center space-x-2 text-sm text-gray-500">
                          <Zap className="h-4 w-4" />
                          <span>AI is analyzing and optimizing...</span>
                        </div>
                      )}
                    </div>
                    
                    {(job.status === 'processing' || job.status === 'completed') && (
                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-600">Tailoring Progress</span>
                          <span className="font-medium text-gray-900">{job.progress}%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className={`h-2 rounded-full transition-all duration-500 ${
                              job.status === 'completed' 
                                ? 'bg-gradient-to-r from-green-500 to-green-600' 
                                : 'bg-gradient-to-r from-blue-500 to-purple-500'
                            }`}
                            style={{ width: `${job.progress}%` }}
                          ></div>
                        </div>
                      </div>
                    )}

                    {/* Timing Info */}
                    {job.processingStartTime && (
                      <div className="text-xs text-gray-500">
                        {job.status === 'completed' && job.completedTime ? (
                          <span>
                            Completed in {Math.round((job.completedTime.getTime() - job.processingStartTime.getTime()) / 1000)}s
                          </span>
                        ) : job.status === 'processing' ? (
                          <span>
                            Processing for {Math.round((new Date().getTime() - job.processingStartTime.getTime()) / 1000)}s
                          </span>
                        ) : null}
                      </div>
                    )}
                  </div>
                </div>

                {/* Actions */}
                <div className="flex flex-col space-y-3 lg:min-w-[200px]">
                  {job.status === 'completed' && (
                    <button
                      onClick={() => handleDownload(job)}
                      className="inline-flex items-center justify-center space-x-2 px-6 py-3 bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700 text-white font-semibold rounded-lg transition-all duration-200 transform hover:scale-105 focus:outline-none focus:ring-4 focus:ring-green-200"
                    >
                      <Download className="h-4 w-4" />
                      <span>Download Resume</span>
                    </button>
                  )}
                  
                  <div className="inline-flex items-center justify-center space-x-2 px-6 py-3 border border-gray-300 text-gray-700 font-medium rounded-lg bg-gray-50">
                    <FileText className="h-4 w-4" />
                    <span>Tailored Resume</span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Summary */}
        {!isProcessing && (
          <div className="mt-8 bg-white rounded-2xl shadow-lg p-6">
            <div className="text-center">
              <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-4" />
              <h3 className="text-2xl font-bold text-gray-900 mb-2">
                All Resumes Tailored Successfully!
              </h3>
              <p className="text-gray-600 mb-6">
                Your {tailoringJobs.length} tailored resumes are ready for download. 
                Each resume has been optimized specifically for the job requirements.
              </p>
              <button
                onClick={handleDownloadAll}
                className="inline-flex items-center space-x-2 px-8 py-4 bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700 text-white font-semibold rounded-xl transition-all duration-200 transform hover:scale-105 focus:outline-none focus:ring-4 focus:ring-green-200"
              >
                <Download className="h-5 w-5" />
                <span>Download All Tailored Resumes</span>
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};