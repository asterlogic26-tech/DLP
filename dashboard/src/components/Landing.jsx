import React from 'react';
import { Link } from 'react-router-dom';
import { Shield, Lock, Eye, CheckCircle } from 'lucide-react';

export default function Landing() {
  return (
    <div className="min-h-screen bg-cyber-dark text-white font-sans">
      {/* Navbar */}
      <nav className="p-6 flex justify-between items-center max-w-7xl mx-auto">
        <div className="flex items-center gap-2 text-cyber-accent">
          <Shield size={32} />
          <span className="text-xl font-bold tracking-wider">CYBERGUARD</span>
        </div>
        <div className="space-x-4">
          <Link to="/login" className="px-6 py-2 border border-cyber-accent text-cyber-accent rounded hover:bg-cyber-accent hover:text-white transition">
            Login
          </Link>
          <Link to="/login" className="px-6 py-2 bg-cyber-accent text-cyber-dark font-bold rounded hover:opacity-90 transition">
            Get Protected
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <header className="text-center py-20 px-4">
        <h1 className="text-5xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-green-400 to-blue-500 bg-clip-text text-transparent">
          Enterprise-Grade Data Protection
        </h1>
        <p className="text-xl text-slate-400 max-w-2xl mx-auto mb-10">
          Prevent sensitive data leaks, block malicious content, and monitor security threats in real-time. 
          The ultimate browser extension for privacy.
        </p>
        <Link to="/login" className="inline-block px-8 py-4 bg-cyber-accent text-cyber-dark font-bold text-lg rounded-lg shadow-[0_0_20px_rgba(16,185,129,0.4)] hover:shadow-[0_0_30px_rgba(16,185,129,0.6)] transition">
          Start Free Trial
        </Link>
      </header>

      {/* Features */}
      <section className="py-20 bg-cyber-card">
        <div className="max-w-7xl mx-auto grid md:grid-cols-3 gap-8 px-6">
          <FeatureCard 
            icon={<Lock />} 
            title="DLP Prevention" 
            desc="Automatically blocks PAN, Aadhar, and credit card leaks in real-time." 
          />
          <FeatureCard 
            icon={<Eye />} 
            title="Content Filtering" 
            desc="AI-powered detection of adult content and malicious websites." 
          />
          <FeatureCard 
            icon={<CheckCircle />} 
            title="Gmail Security" 
            desc="Scans outgoing emails for sensitive info and incoming spam." 
          />
        </div>
      </section>
    </div>
  );
}

function FeatureCard({ icon, title, desc }) {
  return (
    <div className="p-8 bg-cyber-dark rounded-xl border border-slate-700 hover:border-cyber-accent transition group">
      <div className="text-cyber-accent mb-4 group-hover:scale-110 transition duration-300">{icon}</div>
      <h3 className="text-xl font-bold mb-2">{title}</h3>
      <p className="text-slate-400">{desc}</p>
    </div>
  );
}
