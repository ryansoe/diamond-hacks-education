import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import { format, startOfMonth, endOfMonth, eachDayOfInterval, isSameMonth, isToday, parseISO } from 'date-fns';

const Calendar = () => {
  const [deadlines, setDeadlines] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentMonth, setCurrentMonth] = useState(new Date());
  
  // Get calendar days for the current month
  const monthStart = startOfMonth(currentMonth);
  const monthEnd = endOfMonth(currentMonth);
  const calendarDays = eachDayOfInterval({ start: monthStart, end: monthEnd });
  
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
  
  const prevMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1, 1));
  };
  
  const nextMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 1));
  };
  
  // Check if a day has deadlines
  const getDayDeadlines = (day) => {
    return deadlines.filter(deadline => {
      const deadlineDate = new Date(deadline.timestamp);
      // console.log("timestamp: ", deadline.timestamp);
      return deadlineDate.getDate() === day.getDate() &&
             deadlineDate.getMonth() === day.getMonth() &&
             deadlineDate.getFullYear() === day.getFullYear();
    });
  };


  const [filters, setFilters] = useState({
      search: '',
      sort: 'date',
  });

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
          Task Calendar
        </h2>
        <div className="mt-3 sm:mt-0 sm:ml-4">
          <div className="flex items-center space-x-4">
            <button
              onClick={prevMonth}
              className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-primary-700 bg-primary-100 hover:bg-primary-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              Previous
            </button>
            <h3 className="text-lg font-medium text-gray-900">
              {format(currentMonth, 'MMMM yyyy')}
            </h3>
            <button
              onClick={nextMonth}
              className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-primary-700 bg-primary-100 hover:bg-primary-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              Next
            </button>
          </div>
        </div>
      </div>
      
      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="text-center">
            <div className="loader ease-linear rounded-full border-4 border-t-4 border-gray-200 h-12 w-12 mb-4 mx-auto"></div>
            <h2 className="text-center text-gray-700 text-xl font-semibold">Loading calendar...</h2>
          </div>
        </div>
      ) : error ? (
        <div className="flex justify-center items-center h-64">
          <div className="text-center">
            <h2 className="text-center text-red-700 text-xl font-semibold">Error</h2>
            <p className="text-center text-gray-500">{error}</p>
          </div>
        </div>
      ) : (
        <div className="mt-6 bg-white shadow overflow-hidden rounded-md">
          <div className="grid grid-cols-7 gap-px bg-gray-200">
            {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((day) => (
              <div key={day} className="bg-white p-2 text-center text-sm font-medium text-gray-500">
                {day}
              </div>
            ))}
          </div>
          
          <div className="grid grid-cols-7 gap-px bg-gray-200">
            {calendarDays.map((day, i) => {
              const dayDeadlines = getDayDeadlines(day);
              
              return (
                <div
                  key={i}
                  className={`
                    bg-white min-h-[100px] p-2
                    ${!isSameMonth(day, currentMonth) ? 'text-gray-400' : ''}
                    ${isToday(day) ? 'bg-blue-50' : ''}
                  `}
                >
                  <div className="text-right">{format(day, 'd')}</div>
                  
                  {dayDeadlines.length > 0 && (
                    <div className="mt-1">
{dayDeadlines.map((deadline) => {
  // Determine type of event
  const isClub = /meeting|club|event|food/i.test(deadline.title);
  const isAcademic = /internship|hiring|job|scholarship/i.test(deadline.title);

  // Choose a color based on type
  const bgColor = isClub
    ? 'bg-red-100 text-red-800'
    : isAcademic
    ? 'bg-blue-100 text-blue-800'
    : 'bg-gray-100 text-gray-800'; 

  return (
    <div
      key={deadline.id}
      className={`text-xs p-1 mb-1 rounded truncate ${bgColor}`}
      title={deadline.title}
    >
      {deadline.title}
    </div>
  );
})}

                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export default Calendar; 