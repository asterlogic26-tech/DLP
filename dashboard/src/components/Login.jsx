import React, { useState } from 'react';
import { GoogleLogin } from '@react-oauth/google';
import { useNavigate } from 'react-router-dom';
import { api } from '../api';
import { Shield } from 'lucide-react';

export default function Login({ setAuth }) {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSignup, setIsSignup] = useState(false);

  const handleSuccess = async (res) => {
    localStorage.setItem('token', res.data.access_token);
    localStorage.setItem('is_paid', res.data.is_paid);
    setAuth(true);
    navigate('/dashboard');
  };

  const handleGoogleSuccess = async (credentialResponse) => {
    try {
      const res = await api.post('/auth/google', {
        token: credentialResponse.credential
      });
      handleSuccess(res);
    } catch (err) {
      console.error("Login failed", err);
      alert("Login failed. Please try again.");
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const endpoint = isSignup ? '/auth/signup' : '/auth/login';
      const res = await api.post(endpoint, { email, password });
      handleSuccess(res);
    } catch (err) {
      console.error("Auth failed", err);
      alert(err.response?.data?.detail || "Authentication failed");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-cyber-dark text-white">
      <div className="bg-cyber-card p-10 rounded-2xl border border-slate-700 w-full max-w-md text-center shadow-2xl">
        <div className="flex justify-center mb-6 text-cyber-accent">
          <Shield size={64} />
        </div>
        <h2 className="text-3xl font-bold mb-2">{isSignup ? 'Create Account' : 'Welcome Back'}</h2>
        <p className="text-slate-400 mb-8">{isSignup ? 'Sign up to protect your digital life' : 'Sign in to access your security dashboard'}</p>
        
        <form onSubmit={handleSubmit} className="mb-6 space-y-4">
          <input
            type="email"
            placeholder="Email address"
            className="w-full p-3 bg-slate-800 rounded border border-slate-600 focus:border-cyber-accent outline-none"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder="Password"
            className="w-full p-3 bg-slate-800 rounded border border-slate-600 focus:border-cyber-accent outline-none"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <button type="submit" className="w-full bg-cyber-accent text-black font-bold p-3 rounded hover:bg-cyan-400 transition">
            {isSignup ? 'Sign Up' : 'Login'}
          </button>
        </form>

        <div className="relative mb-6">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-slate-600"></div>
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-2 bg-cyber-card text-slate-400">Or continue with</span>
          </div>
        </div>
        
        <div className="flex justify-center mb-4">
          <GoogleLogin
            onSuccess={handleGoogleSuccess}
            onError={() => console.log('Login Failed')}
            theme="filled_black"
            shape="pill"
          />
        </div>

        <button 
          onClick={() => setIsSignup(!isSignup)} 
          className="text-cyber-accent text-sm hover:underline"
        >
          {isSignup ? 'Already have an account? Login' : "Don't have an account? Sign Up"}
        </button>
      </div>
    </div>
  );
}
