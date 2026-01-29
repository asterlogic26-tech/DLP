import { useEffect, useState } from "react";
import { api } from "./api";
import { Shield, Activity, LogOut, Menu } from "lucide-react";

export default function Dashboard({ onLogout }) {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [view, setView] = useState("loading"); // loading | dashboard
  const [isSubscribed, setIsSubscribed] = useState(true);

  useEffect(() => {
    if (!localStorage.token) return;

    // Check Subscription Status (temporarily always active server-side)
    api("/auth/status")
      .then(statusData => {
        if (statusData.active) {
          setIsSubscribed(true);
          setView("dashboard");
          // Only fetch events if subscribed
          return api("/events");
        } else {
          setIsSubscribed(false);
          setLoading(false);
          return null;
        }
      })
      .then(eventsData => {
        if (eventsData) {
          setEvents(eventsData);
        }
        setLoading(false);
      })
      .catch(() => {
        setLoading(false);
        setView("dashboard"); 
      });
  }, []);

  const logout = () => {
    if (onLogout) onLogout();
  };

  if (loading) {
      return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-100 flex">
      {/* Sidebar - Only show navigation if subscribed */}
      <div className="hidden md:flex flex-col w-64 bg-indigo-800 text-white">
        <div className="flex items-center justify-center h-16 border-b border-indigo-700">
          <Shield className="h-8 w-8 text-indigo-300 mr-2" />
          <span className="text-xl font-bold">DLP Admin</span>
        </div>
        
        <div className="flex-1 overflow-y-auto">
          <nav className="px-2 py-4 space-y-1">
            <button 
              onClick={() => setView("dashboard")}
              className={`w-full flex items-center px-4 py-3 rounded-md transition-colors ${view === 'dashboard' ? 'bg-indigo-900 text-white' : 'text-indigo-100 hover:bg-indigo-700'}`}
            >
              {/* Icon removed to avoid unused import */}
              <span className="h-5 w-5 mr-3">🏠</span>
              Dashboard
            </button>
          </nav>
        </div>
        
        <div className="p-4 border-t border-indigo-700">
          <button onClick={logout} className="flex items-center w-full px-4 py-2 text-indigo-100 hover:bg-indigo-700 rounded-md">
            <LogOut className="h-5 w-5 mr-3" />
            Sign Out
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Header */}
        <header className="flex justify-between items-center py-4 px-6 bg-white shadow-sm border-b">
          <div className="flex items-center md:hidden">
            <button className="text-gray-500 focus:outline-none">
              <Menu className="h-6 w-6" />
            </button>
          </div>
          <h1 className="text-2xl font-semibold text-gray-800">Security Overview</h1>
        </header>

        {/* Content Body */}
        <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-100 p-6">
            {
            <>
              {/* Install Extension Banner */}
              <div className="bg-indigo-600 rounded-lg shadow-lg p-6 mb-8 text-white">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-xl font-bold mb-2">Step 3: Install Protection</h2>
                    <p className="text-indigo-100">
                      Protection is active. Install the extension to start blocking distraction.
                    </p>
                  </div>
                  <button 
                    onClick={() => alert("To install the extension:\n1. Open chrome://extensions\n2. Enable 'Developer mode' (top right)\n3. Click 'Load unpacked'\n4. Select the 'extension' folder in this project")}
                    className="bg-white text-indigo-600 px-6 py-2 rounded-full font-bold hover:bg-indigo-50 transition-colors"
                  >
                    Download Extension
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="bg-white rounded-lg shadow p-6 border-l-4 border-indigo-500">
                  <div className="flex items-center">
                    <div className="p-3 rounded-full bg-indigo-100 text-indigo-500">
                      <span className="h-8 w-8">📊</span>
                    </div>
                    <div className="ml-4">
                      <p className="mb-2 text-sm font-medium text-gray-600">Total Events</p>
                      <p className="text-lg font-semibold text-gray-700">{events.length}</p>
                    </div>
                  </div>
                </div>
                 {/* More widgets can go here */}
              </div>

              <div className="bg-white shadow rounded-lg overflow-hidden">
                <div className="px-6 py-4 border-b border-gray-200">
                  <h3 className="text-lg font-medium text-gray-900">Recent Security Events</h3>
                </div>
                {/* Event list implementation */}
              </div>
            </>
          )}
        </main>
      </div>
    </div>
  );
}
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Domain</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Action</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Time</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {loading ? (
                        <tr><td colSpan="4" className="px-6 py-4 text-center">Loading...</td></tr>
                      ) : events.length === 0 ? (
                        <tr><td colSpan="4" className="px-6 py-4 text-center text-gray-500">No events found</td></tr>
                      ) : (
                        events.map((e) => (
                          <tr key={e.id}>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                                {e.data_type}
                              </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{e.domain}</td>
                            <td className="px-6 py-4 whitespace-nowrap">
                               <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${e.action === 'block' ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'}`}>
                                {e.action}
                              </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {new Date(e.created_at).toLocaleString()}
                            </td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          )}
        </main>
      </div>
    </div>
  );
}
