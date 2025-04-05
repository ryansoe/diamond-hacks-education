import React from 'react';

const AdminPanel = () => {
  return (
    <div className="container mx-auto px-4">
      <div className="pb-5 border-b border-gray-200">
        <h2 className="text-2xl font-bold leading-tight text-gray-900">
          Admin Panel
        </h2>
        <p className="mt-2 text-sm text-gray-500">
          Manage deadlines and system settings
        </p>
      </div>
      
      <div className="mt-8 bg-white shadow overflow-hidden sm:rounded-lg">
        <div className="px-4 py-5 sm:px-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900">
            Admin Controls
          </h3>
          <p className="mt-1 max-w-2xl text-sm text-gray-500">
            This is a placeholder for the admin panel. Your team will implement the full functionality.
          </p>
        </div>
        
        <div className="border-t border-gray-200 px-4 py-5 sm:p-6">
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
            <div className="col-span-1 bg-gray-50 p-6 rounded-lg">
              <h4 className="text-md font-medium text-gray-900">Discord Bot Settings</h4>
              <p className="text-sm text-gray-500 mt-2">
                Configure bot behavior and scanning patterns
              </p>
              <div className="mt-4">
                <button
                  type="button"
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                  disabled
                >
                  Manage Bot
                </button>
              </div>
            </div>
            
            <div className="col-span-1 bg-gray-50 p-6 rounded-lg">
              <h4 className="text-md font-medium text-gray-900">Deadline Management</h4>
              <p className="text-sm text-gray-500 mt-2">
                Manually add, edit, or remove deadlines
              </p>
              <div className="mt-4">
                <button
                  type="button"
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                  disabled
                >
                  Manage Deadlines
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div className="mt-8 text-center text-gray-500 text-sm">
        <p>Admin panel is a placeholder. Your team will implement the full functionality.</p>
      </div>
    </div>
  );
};

export default AdminPanel; 