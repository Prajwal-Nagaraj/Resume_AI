import React from 'react';
import { 
  X, 
  Building, 
  MapPin, 
  Clock, 
  Users, 
  ExternalLink, 
  Briefcase, 
  DollarSign,
  Calendar,
  Star,
  Share2,
  Bookmark,
  Target
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
  requirements?: string[];
  responsibilities?: string[];
  benefits?: string[];
  companySize?: string;
  industry?: string;
  skills?: string[];
}

interface JobDetailsModalProps {
  job: Job;
  isOpen: boolean;
  onClose: () => void;
}

export const JobDetailsModal: React.FC<JobDetailsModalProps> = ({ job, isOpen, onClose }) => {
  if (!isOpen) return null;

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  const handleApplyClick = () => {
    window.open(job.linkedinUrl, '_blank');
  };

  // Enhanced job data for demonstration
  const enhancedJob = {
    ...job,
    requirements: job.requirements || [
      'Bachelor\'s degree in Computer Science or related field',
      '3+ years of experience in software development',
      'Proficiency in React, TypeScript, and modern web technologies',
      'Experience with RESTful APIs and database design',
      'Strong problem-solving and communication skills',
      'Experience with version control systems (Git)'
    ],
    responsibilities: job.responsibilities || [
      'Develop and maintain high-quality web applications using React and TypeScript',
      'Collaborate with cross-functional teams to define and implement new features',
      'Write clean, maintainable, and well-documented code',
      'Participate in code reviews and contribute to technical discussions',
      'Optimize applications for maximum speed and scalability',
      'Stay up-to-date with emerging technologies and industry best practices'
    ],
    benefits: job.benefits || [
      'Competitive salary and equity package',
      'Comprehensive health, dental, and vision insurance',
      'Flexible work arrangements and remote work options',
      'Professional development budget and learning opportunities',
      'Generous PTO and parental leave policies',
      '401(k) with company matching'
    ],
    companySize: job.companySize || '500-1000 employees',
    industry: job.industry || 'Technology',
    skills: job.skills || ['React', 'TypeScript', 'Node.js', 'Python', 'AWS', 'Docker']
  };

  return (
    <div 
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      onClick={handleBackdropClick}
    >
      <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center space-x-4 mb-4">
                {enhancedJob.companyLogo && (
                  <img 
                    src={enhancedJob.companyLogo} 
                    alt={`${enhancedJob.company} logo`}
                    className="w-16 h-16 rounded-lg bg-white p-2"
                  />
                )}
                <div>
                  <h2 className="text-2xl font-bold mb-2">{enhancedJob.title}</h2>
                  <div className="flex items-center space-x-2 text-blue-100">
                    <Building className="h-5 w-5" />
                    <span className="text-lg font-medium">{enhancedJob.company}</span>
                  </div>
                </div>
              </div>
              
              <div className="flex flex-wrap items-center gap-4 text-sm text-blue-100">
                <div className="flex items-center space-x-1">
                  <MapPin className="h-4 w-4" />
                  <span>{enhancedJob.location}</span>
                </div>
                <div className="flex items-center space-x-1">
                  <Clock className="h-4 w-4" />
                  <span>{enhancedJob.postedDate}</span>
                </div>
                <div className="flex items-center space-x-1">
                  <Briefcase className="h-4 w-4" />
                  <span>{enhancedJob.employmentType}</span>
                </div>
                {enhancedJob.applicants && (
                  <div className="flex items-center space-x-1">
                    <Users className="h-4 w-4" />
                    <span>{enhancedJob.applicants} applicants</span>
                  </div>
                )}
              </div>
            </div>
            
            <button
              onClick={onClose}
              className="p-2 hover:bg-white hover:bg-opacity-20 rounded-full transition-colors"
            >
              <X className="h-6 w-6" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="overflow-y-auto max-h-[calc(90vh-200px)]">
          <div className="p-6 space-y-8">
            {/* Quick Info */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-blue-50 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-blue-600 mb-1">{enhancedJob.experienceLevel}</div>
                <div className="text-sm text-gray-600">Experience Level</div>
              </div>
              {enhancedJob.salary && (
                <div className="bg-green-50 rounded-lg p-4 text-center">
                  <div className="text-2xl font-bold text-green-600 mb-1">{enhancedJob.salary}</div>
                  <div className="text-sm text-gray-600">Salary Range</div>
                </div>
              )}
              <div className="bg-purple-50 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-purple-600 mb-1">{enhancedJob.companySize}</div>
                <div className="text-sm text-gray-600">Company Size</div>
              </div>
            </div>

            {/* Job Description */}
            <div>
              <h3 className="text-xl font-bold text-gray-900 mb-4">Job Description</h3>
              <div className="prose prose-gray max-w-none">
                <p className="text-gray-700 leading-relaxed">{enhancedJob.description}</p>
              </div>
            </div>

            {/* Key Responsibilities */}
            <div>
              <h3 className="text-xl font-bold text-gray-900 mb-4">Key Responsibilities</h3>
              <ul className="space-y-3">
                {enhancedJob.responsibilities.map((responsibility, index) => (
                  <li key={index} className="flex items-start space-x-3">
                    <div className="bg-blue-100 rounded-full p-1 mt-1">
                      <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
                    </div>
                    <span className="text-gray-700 leading-relaxed">{responsibility}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Requirements */}
            <div>
              <h3 className="text-xl font-bold text-gray-900 mb-4">Requirements</h3>
              <ul className="space-y-3">
                {enhancedJob.requirements.map((requirement, index) => (
                  <li key={index} className="flex items-start space-x-3">
                    <div className="bg-purple-100 rounded-full p-1 mt-1">
                      <div className="w-2 h-2 bg-purple-600 rounded-full"></div>
                    </div>
                    <span className="text-gray-700 leading-relaxed">{requirement}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Skills */}
            <div>
              <h3 className="text-xl font-bold text-gray-900 mb-4">Required Skills</h3>
              <div className="flex flex-wrap gap-2">
                {enhancedJob.skills.map((skill, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-800 hover:bg-gray-200 transition-colors"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>

            {/* Benefits */}
            <div>
              <h3 className="text-xl font-bold text-gray-900 mb-4">Benefits & Perks</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {enhancedJob.benefits.map((benefit, index) => (
                  <div key={index} className="flex items-start space-x-3 p-3 bg-green-50 rounded-lg">
                    <Star className="h-5 w-5 text-green-600 mt-0.5 flex-shrink-0" />
                    <span className="text-gray-700">{benefit}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Company Info */}
            <div className="bg-gray-50 rounded-lg p-6">
              <h3 className="text-xl font-bold text-gray-900 mb-4">About {enhancedJob.company}</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                  <span className="text-sm font-medium text-gray-500">Industry</span>
                  <p className="text-gray-900">{enhancedJob.industry}</p>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-500">Company Size</span>
                  <p className="text-gray-900">{enhancedJob.companySize}</p>
                </div>
              </div>
              <p className="text-gray-700 leading-relaxed">
                Join our innovative team and help shape the future of technology. We're committed to creating 
                an inclusive environment where everyone can thrive and make a meaningful impact.
              </p>
            </div>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="border-t border-gray-200 p-6 bg-gray-50">
          <div className="flex flex-col sm:flex-row gap-3 justify-between items-center">
            <div className="flex space-x-3">
              <button className="inline-flex items-center space-x-2 px-4 py-2 border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50 hover:border-gray-400 transition-all duration-200">
                <Bookmark className="h-4 w-4" />
                <span>Save Job</span>
              </button>
              <button className="inline-flex items-center space-x-2 px-4 py-2 border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50 hover:border-gray-400 transition-all duration-200">
                <Share2 className="h-4 w-4" />
                <span>Share</span>
              </button>
            </div>
            
            <div className="flex space-x-3">
              <button className="inline-flex items-center space-x-2 px-6 py-3 border border-blue-300 text-blue-600 font-semibold rounded-lg hover:bg-blue-50 hover:border-blue-400 transition-all duration-200">
                <Target className="h-4 w-4" />
                <span>Tailor Resume</span>
              </button>
              <button
                onClick={handleApplyClick}
                className="inline-flex items-center space-x-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold rounded-lg transition-all duration-200 transform hover:scale-105 focus:outline-none focus:ring-4 focus:ring-blue-200"
              >
                <span>Apply on LinkedIn</span>
                <ExternalLink className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};