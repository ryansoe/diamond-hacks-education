import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { apiService } from '../services/api';
import { ArrowLeftIcon, ClockIcon, ChatBubbleLeftIcon, ExclamationCircleIcon } from '@heroicons/react/24/outline';

const DeadlineDetail = () => {
  const { id } = useParams();
  const [deadline, setDeadline] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    const fetchDeadlineDetail = async () => {
      try {
        setLoading(true);
        const response = await apiService.getDeadline(id);
        setDeadline(response.data);
        setError(null);
      } catch (err) {
        console.error('Error fetching deadline details:', err);
        setError('Failed to load deadline details. Please try again later.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchDeadlineDetail();
  }, [id]);
  
  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-center">
          <div className="loader ease-linear rounded-full border-4 border-t-4 border-gray-200 h-12 w-12 mb-4 mx-auto"></div>
          <h2 className="text-center text-gray-700 text-xl font-semibold">Loading deadline details...</h2>
        </div>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-center">
          <ExclamationCircleIcon className="mx-auto h-12 w-12 text-red-500" />
          <h2 className="mt-2 text-center text-red-700 text-xl font-semibold">Error</h2>
          <p className="mt-1 text-center text-gray-500">{error}</p>
          <Link to="/" className="mt-4 inline-flex items-center text-primary-600 hover:text-primary-800">
            <ArrowLeftIcon className="h-4 w-4 mr-1" />
            Back to dashboard
          </Link>
        </div>
      </div>
    );
  }
  
  return (
    <div className="container mx-auto px-4">
      <div className="mb-4">
        <Link to="/" className="inline-flex items-center text-primary-600 hover:text-primary-800">
          <ArrowLeftIcon className="h-4 w-4 mr-1" />
          Back to dashboard
        </Link>
      </div>
      
      <div className="bg-white shadow overflow-hidden rounded-lg">
        <div className="px-4 py-5 sm:px-6 border-b border-gray-200">
          <h2 className="text-xl font-bold text-gray-900">{deadline.title}</h2>
          <p className="mt-1 max-w-2xl text-sm text-gray-500">
            Deadline details and source information
          </p>
        </div>
        
        <div className="border-t border-gray-200">
          <dl>
            <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Due Date</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2 flex items-center">
                <ClockIcon className="h-5 w-5 text-gray-400 mr-2" />
                {deadline.date_str}
              </dd>
            </div>
            
            <div className="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Source</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                {deadline.guild_name} / #{deadline.channel_name}
              </dd>
            </div>
            
            <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Posted By</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2 flex items-center">
                <ChatBubbleLeftIcon className="h-5 w-5 text-gray-400 mr-2" />
                {deadline.author_name}
              </dd>
            </div>
            
            <div className="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Original Message</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                {deadline.raw_content}
              </dd>
            </div>
            
            <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Discord Link</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                <a 
                  href={deadline.source_link} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-primary-600 hover:text-primary-800"
                >
                  View original message on Discord
                </a>
              </dd>
            </div>
          </dl>
        </div>
      </div>
      
      <div className="mt-8 text-center text-gray-500 text-sm">
        <p>Detail view is a placeholder. Your team will implement the full functionality.</p>
      </div>
    </div>
  );
};

export default DeadlineDetail; 