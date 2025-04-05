import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { apiService } from '../services/api';
import { ClockIcon, ExclamationCircleIcon } from '@heroicons/react/24/outline';

const Dashboard = () => {
  const [deadlines, setDeadlines] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    search: '',
    sort: 'date',
  });
  
  useEffect(() => {
    const fetchDeadlines = async () => {
      try {
        setLoading(true);
        const response = await apiService.getDeadlines();
        setDeadlines(response.data.deadlines);
        setError(null);
      } catch (err) {
        console.error('Error fetching deadlines:', err);
        setError('Failed to load deadlines. Please try again later.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchDeadlines();
  }, []);
  
  // Filter and sort deadlines based on user selections
  const filteredDeadlines = deadlines
    .filter(deadline => 
      deadline.title.toLowerCase().includes(filters.search.toLowerCase()) ||
      deadline.date_str.toLowerCase().includes(filters.search.toLowerCase()) ||
      deadline.channel_name.toLowerCase().includes(filters.search.toLowerCase())
    )
    .sort((a, b) => {
      if (filters.sort === 'date') {
        // Sort by date (this is a simplified example)
        return a.date_str.localeCompare(b.date_str);
      }
      return 0;
    });
  

    const clubEvents = filteredDeadlines.filter(d =>
      /meeting|club|food/i.test(d.title)
    );
    
    const academicEvents = filteredDeadlines.filter(d =>
      /internship|hiring|scholarship/i.test(d.title)
    );    

  return (
    <div className="container mx-auto px-4">
      <div className="pb-5 border-b border-gray-200 sm:flex sm:items-center sm:justify-between">
        <h2 className="text-2xl font-bold leading-tight text-gray-900">
          Upcoming Tasks
        </h2>
        <div className="mt-3 sm:mt-0 sm:ml-4">
          <div className="flex rounded-md shadow-sm">
            <input
              type="text"
              name="search"
              id="search"
              className="focus:ring-primary-500 focus:border-primary-500 flex-1 block w-full rounded-md sm:text-sm border-gray-300"
              placeholder="Search deadlines"
              value={filters.search}
              onChange={(e) => setFilters({ ...filters, search: e.target.value })}
            />
          </div>
        </div>
      </div>
      
      <div className = "border-b pt-5 text-xl font-bold leading-tight text-gray-900">
        <h1>Club Events/Free Food</h1>
      </div>




      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="text-center">
            <div className="loader ease-linear rounded-full border-4 border-t-4 border-gray-200 h-12 w-12 mb-4 mx-auto"></div>
            <h2 className="text-center text-gray-700 text-xl font-semibold">Loading...</h2>
            <p className="text-center text-gray-500">This may take a few seconds</p>
          </div>
        </div>
      ) : error ? (
        <div className="flex justify-center items-center h-64">
          <div className="text-center">
            <ExclamationCircleIcon className="mx-auto h-12 w-12 text-red-500" />
            <h2 className="mt-2 text-center text-red-700 text-xl font-semibold">Error</h2>
            <p className="mt-1 text-center text-gray-500">{error}</p>
          </div>
        </div>
      ) : (
        <div className="mt-6 bg-white shadow overflow-hidden rounded-md">
        <ul className="divide-y divide-gray-200">
          {clubEvents.length > 0 ? (
            clubEvents.map((deadline) => (
              <li key={deadline.id}>
                <Link to={`/deadlines/${deadline.id}`} className="block hover:bg-gray-50">
                    <div className="px-4 py-4 sm:px-6">
                      <div className="flex items-center justify-between">
                        <p className="text-lg font-medium text-primary-600 truncate">
                          {deadline.title}
                        </p>
                        <div className="ml-2 flex-shrink-0 flex">
                          <p className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                            {deadline.channel_name}
                          </p>
                        </div>
                      </div>
                      <div className="mt-2 sm:flex sm:justify-between">
                        <div className="sm:flex">
                          <p className="flex items-center text-sm text-gray-500">
                            <ClockIcon className="flex-shrink-0 mr-1.5 h-5 w-5 text-gray-400" />
                            {deadline.date_str}
                          </p>
                        </div>
                        <div className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
                          <p>
                            From {deadline.guild_name}
                          </p>
                        </div>
                      </div>
                    </div>
                  </Link>
              </li>
            ))
          ) : (
            <li className="px-4 py-4 sm:px-6 text-center text-gray-500">
              No club events found.
            </li>
          )}
        </ul>
      </div>
    )}

      <div className = "border-b pt-5 text-xl font-bold leading-tight text-gray-900">
        <h2>Academic/Internship/Hiring Opportunities</h2>
      </div>


      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="text-center">
            <div className="loader ease-linear rounded-full border-4 border-t-4 border-gray-200 h-12 w-12 mb-4 mx-auto"></div>
            <h2 className="text-center text-gray-700 text-xl font-semibold">Loading...</h2>
            <p className="text-center text-gray-500">This may take a few seconds</p>
          </div>
        </div>
      ) : error ? (
        <div className="flex justify-center items-center h-64">
          <div className="text-center">
            <ExclamationCircleIcon className="mx-auto h-12 w-12 text-red-500" />
            <h2 className="mt-2 text-center text-red-700 text-xl font-semibold">Error</h2>
            <p className="mt-1 text-center text-gray-500">{error}</p>
          </div>
        </div>
      ) : (
        <div className="mt-6 bg-white shadow overflow-hidden rounded-md">
        <ul className="divide-y divide-gray-200">
          {academicEvents.length > 0 ? (
            academicEvents.map((deadline) => (
              <li key={deadline.id}>
                <Link to={`/deadlines/${deadline.id}`} className="block hover:bg-gray-50">
                    <div className="px-4 py-4 sm:px-6">
                      <div className="flex items-center justify-between">
                        <p className="text-lg font-medium text-primary-600 truncate">
                          {deadline.title}
                        </p>
                        <div className="ml-2 flex-shrink-0 flex">
                          <p className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                            {deadline.channel_name}
                          </p>
                        </div>
                      </div>
                      <div className="mt-2 sm:flex sm:justify-between">
                        <div className="sm:flex">
                          <p className="flex items-center text-sm text-gray-500">
                            <ClockIcon className="flex-shrink-0 mr-1.5 h-5 w-5 text-gray-400" />
                            {deadline.date_str}
                          </p>
                        </div>
                        <div className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
                          <p>
                            From {deadline.guild_name}
                          </p>
                        </div>
                      </div>
                    </div>
                  </Link>
              </li>
            ))
          ) : (
            <li className="px-4 py-4 sm:px-6 text-center text-gray-500">
              No academic events found.
            </li>
          )}
        </ul>
      </div>
    )}
    
    </div>
  );
};

export default Dashboard; 