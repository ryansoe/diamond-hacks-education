import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { apiService } from '../services/api';
import { ClockIcon, ExclamationCircleIcon } from '@heroicons/react/24/outline';

import {
  UserGroupIcon,
  AcademicCapIcon,
} from "@heroicons/react/24/outline";


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
      /meeting|club|event|food/i.test(d.title)
    );
    
    const academicEvents = filteredDeadlines.filter(d =>
      /internship|hiring|job|scholarship/i.test(d.title)
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
              className="rounded-full px-4 py-2 border border-gray-300 shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition w-60"
              placeholder="Search deadlines"
              value={filters.search}
              onChange={(e) => setFilters({ ...filters, search: e.target.value })}
            />
          </div>
        </div>
      </div>
      
      <div className="space-y-10 px-4 py-6 sm:px-8 ">
        {/* Club Events Section */}
  <section>
    <div className="flex items-center gap-2 border-b pb-2">
      <UserGroupIcon className="h-6 w-6 text-indigo-500" />
      <h2 className="text-xl font-bold text-gray-800">
        Club Events / Free Food
      </h2>
    </div>

    {clubEvents.length === 0 ? (
      <div className="mt-4 text-gray-500 italic text-sm">No events currently</div>
    ) : (
      <ul className="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-4">
        {clubEvents.map((deadline) => (
          <li
            key={deadline.id}
            className="relative rounded-lg border bg-white p-5 shadow-sm transition hover:shadow-md"
          >
            <div className="flex justify-between items-start">
              <h3 className="text-base font-semibold text-gray-800">
                {deadline.title}
              </h3>
              <span className="text-xs bg-indigo-100 text-indigo-700 px-2 py-0.5 rounded-full">
                {deadline.channel_name}
              </span>
            </div>
            <p className="mt-2 text-sm text-gray-600 line-clamp-2">
              {deadline.description}
            </p>
            <div className="mt-3 flex items-center justify-between text-sm text-gray-500">
              <p className="flex items-center">
                <ClockIcon className="h-4 w-4 mr-1 text-indigo-400" />
                {deadline.date_str}
              </p>
              <p className="italic">From {deadline.guild_name}</p>
            </div>
          </li>
        ))}
      </ul>
    )}
  </section>

  {/* Academic Deadlines Section */}
  <section>
    <div className="flex items-center gap-2 border-b pb-2">
      <AcademicCapIcon className="h-6 w-6 text-indigo-500" />
      <h2 className="text-xl font-bold text-gray-800">
        Academic / Internship / Hiring Opportunities
      </h2>
    </div>

    {academicEvents.length === 0 ? (
      <div className="mt-4 text-gray-500 italic text-sm">No opportunities currently</div>
    ) : (
      <ul className="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-4">
        {academicEvents.map((deadline) => (
          <li
            key={deadline.id}
            className="relative rounded-lg border bg-white p-5 shadow-sm transition hover:shadow-md"
          >
            <div className="flex justify-between items-start">
              <h3 className="text-base font-semibold text-gray-800">
                {deadline.title}
              </h3>
              <span className="text-xs bg-green-100 text-green-800 px-2 py-0.5 rounded-full">
                {deadline.channel_name}
              </span>
            </div>
            <p className="mt-2 text-sm text-gray-600 line-clamp-2">
              {deadline.description}
            </p>
            <div className="mt-3 flex items-center justify-between text-sm text-gray-500">
              <p className="flex items-center">
                <ClockIcon className="h-4 w-4 mr-1 text-indigo-400" />
                {deadline.date_str}
              </p>
              <p className="italic">From {deadline.guild_name}</p>
            </div>
          </li>
        ))}
      </ul>
    )}
  </section>
</div>
</div>
  );
};

export default Dashboard; 