import React, { useState } from 'react';
import { FileUpload } from './FileUpload';
import { Zap, Brain, Target, CheckCircle, ArrowRight } from 'lucide-react';

interface LandingPageProps {
  onFileUpload: (file: File, resumeId: string) => void;
  uploadedFile: File | null;
  onExtractDetails: () => void;
  isExtracting: boolean;
}

const features = [
  {
    icon: Brain,
    title: 'AI-Powered Analysis',
    description: 'Our advanced AI analyzes your resume and identifies key strengths and areas for improvement.'
  },
  {
    icon: Target,
    title: 'Job-Specific Tailoring',
    description: 'Automatically customize your resume for each job application to maximize your chances.'
  },
  {
    icon: Zap,
    title: 'Instant Optimization',
    description: 'Get real-time suggestions and improvements to make your resume stand out.'
  },
  {
    icon: CheckCircle,
    title: 'ATS Optimization',
    description: 'Ensure your resume passes through Applicant Tracking Systems with confidence.'
  }
];

export const LandingPage: React.FC<LandingPageProps> = ({ 
  onFileUpload, 
  uploadedFile, 
  onExtractDetails, 
  isExtracting 
}) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-24">
          <div className="text-center">
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 mb-6">
              Transform Your Resume with
              <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent"> AI Power</span>
            </h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-12 leading-relaxed">
              Get your dream job faster with our intelligent resume tailoring platform. 
              Upload your resume and let AI optimize it for any job opportunity.
            </p>
            
            {/* Upload Section */}
            <div className="mb-8">
              <FileUpload onFileUpload={onFileUpload} />
            </div>

            {/* Extract Details Button */}
            {uploadedFile && (
              <div className="mb-16">
                <button
                  onClick={onExtractDetails}
                  disabled={isExtracting}
                  className={`inline-flex items-center space-x-3 px-8 py-4 rounded-xl text-lg font-semibold transition-all duration-300 transform hover:scale-105 focus:outline-none focus:ring-4 focus:ring-blue-200 ${
                    isExtracting
                      ? 'bg-gray-400 cursor-not-allowed'
                      : 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-lg hover:shadow-xl'
                  }`}
                >
                  {isExtracting ? (
                    <>
                      <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>
                      <span>Extracting Resume Details...</span>
                    </>
                  ) : (
                    <>
                      <span>Extract Resume Details</span>
                      <ArrowRight className="h-5 w-5" />
                    </>
                  )}
                </button>
              </div>
            )}
            
            {/* Stats */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-8 max-w-2xl mx-auto mb-16">
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-600 mb-2">95%</div>
                <div className="text-gray-600">Success Rate</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-purple-600 mb-2">50K+</div>
                <div className="text-gray-600">Resumes Optimized</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-green-600 mb-2">2x</div>
                <div className="text-gray-600">More Interviews</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Why Choose ResumeAI?
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Our platform combines cutting-edge AI technology with recruitment expertise 
              to give you the competitive edge you need.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <div
                  key={index}
                  className="text-center p-6 rounded-xl hover:shadow-lg transition-all duration-300 group hover:scale-105"
                >
                  <div className="bg-gradient-to-r from-blue-500 to-purple-500 p-3 rounded-full w-16 h-16 mx-auto mb-4 group-hover:scale-110 transition-transform duration-300">
                    <Icon className="h-10 w-10 text-white" />
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-3">
                    {feature.title}
                  </h3>
                  <p className="text-gray-600 leading-relaxed">
                    {feature.description}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* How it Works */}
      <div className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              How It Works
            </h2>
            <p className="text-lg text-gray-600">
              Three simple steps to transform your resume
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-blue-600">1</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Upload Resume</h3>
              <p className="text-gray-600">
                Upload your current resume in PDF or Word format
              </p>
            </div>
            
            <div className="text-center">
              <div className="bg-purple-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-purple-600">2</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">AI Analysis</h3>
              <p className="text-gray-600">
                Our AI analyzes your resume and job requirements
              </p>
            </div>
            
            <div className="text-center">
              <div className="bg-green-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-green-600">3</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Get Results</h3>
              <p className="text-gray-600">
                Receive your optimized, tailored resume instantly
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};