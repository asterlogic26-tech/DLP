import React, { useEffect, useState } from 'react';
import { api } from '../api';
import { Shield, AlertTriangle, Download, CreditCard, RefreshCw } from 'lucide-react';

export default function Dashboard() {
  const [events, setEvents] = useState([]);
  const [isPaid, setIsPaid] = useState(localStorage.getItem('is_paid') === 'true');
  const [loading, setLoading] = useState(true);

  const fetchEvents = async () => {
    try {
      const res = await api.get('/events');
      setEvents(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEvents();
  }, []);

  const handleUpgrade = async () => {
    try {
      // Simulate payment
      await api.post('/payment/upgrade');
      localStorage.setItem('is_paid', 'true');
      setIsPaid(true);
      alert("Payment Successful! You can now download the extension.");
    } catch (err) {
      alert("Upgrade failed");
    }
  };

  return (
    <div className="min-h-screen bg-cyber-dark text-slate-200 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <header className="flex justify-between items-center mb-10">
          <h1 className="text-3xl font-bold text-white flex items-center gap-3">
            <Shield className="text-cyber-accent" /> Security Dashboard
          </h1>
          <button onClick={() => {
            localStorage.clear();
            window.location.reload();
          }} className="text-sm text-slate-400 hover:text-white">Logout</button>
        </header>

        {/* Status Cards */}
        <div className="grid md:grid-cols-3 gap-6 mb-10">
          <div className="bg-cyber-card p-6 rounded-xl border border-slate-700">
            <h3 className="text-slate-400 mb-2">Account Status</h3>
            <div className="text-2xl font-bold text-white flex items-center gap-2">
              {isPaid ? <span className="text-cyber-accent">Premium Active</span> : <span className="text-yellow-500">Free Trial</span>}
            </div>
          </div>
          
          <div className="bg-cyber-card p-6 rounded-xl border border-slate-700">
             <h3 className="text-slate-400 mb-2">Threats Blocked</h3>
             <div className="text-2xl font-bold text-white">{events.length}</div>
          </div>

          <div className="bg-cyber-card p-6 rounded-xl border border-slate-700 flex items-center justify-center">
            {!isPaid ? (
              <button onClick={handleUpgrade} className="w-full h-full flex flex-col items-center justify-center text-cyber-accent hover:bg-slate-800 rounded-lg transition p-4">
                <CreditCard size={32} className="mb-2" />
                <span className="font-bold">Upgrade to Pro ($9.99)</span>
              </button>
            ) : (
              <a href="https://github.com/asterlogic26-tech/DLP/archive/refs/heads/main.zip" target="_blank" className="w-full h-full flex flex-col items-center justify-center text-blue-400 hover:bg-slate-800 rounded-lg transition p-4">
                <Download size={32} className="mb-2" />
                <span className="font-bold">Download Extension (ZIP)</span>
              </a>
            )}
          </div>
        </div>

        {/* Events Table */}
        <div className="bg-cyber-card rounded-xl border border-slate-700 overflow-hidden">
          <div className="p-6 border-b border-slate-700 flex justify-between items-center">
            <h2 className="text-xl font-bold text-white">Security Logs</h2>
            <button onClick={fetchEvents} className="p-2 hover:bg-slate-700 rounded-full"><RefreshCw size={20} /></button>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead className="bg-slate-800 text-slate-400">
                <tr>
                  <th className="p-4">Time</th>
                  <th className="p-4">Event Type</th>
                  <th className="p-4">Details</th>
                  <th className="p-4">Action</th>
                </tr>
              </thead>
              <tbody>
                {events.map((event) => (
                  <tr key={event.id} className="border-b border-slate-700 hover:bg-slate-800/50">
                    <td className="p-4 text-sm text-slate-400">{new Date(event.timestamp).toLocaleString()}</td>
                    <td className="p-4">
                      <span className={`px-2 py-1 rounded text-xs font-bold ${
                        event.event_type === 'LEAK_ATTEMPT' ? 'bg-red-500/20 text-red-400' : 'bg-blue-500/20 text-blue-400'
                      }`}>
                        {event.event_type}
                      </span>
                    </td>
                    <td className="p-4 text-white">{event.description}</td>
                    <td className="p-4 text-cyber-accent">{event.action_taken}</td>
                  </tr>
                ))}
                {events.length === 0 && (
                  <tr>
                    <td colSpan="4" className="p-8 text-center text-slate-500">No security events detected yet.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
