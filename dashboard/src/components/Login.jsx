import React from 'react';
import { GoogleLogin } from '@react-oauth/google';
import { useNavigate } from 'react-router-dom';
import { api } from '../api';
import { Shield } from 'lucide-react';

export default function Login({ setAuth }) {
  const navigate = useNavigate();

  const handleSuccess = async (credentialResponse) => {
    try {
      const res = await api.post('/auth/google', {
        token: credentialResponse.credential
      });
      
      localStorage.setItem('token', res.data.access_token);
      localStorage.setItem('is_paid', res.data.is_paid);
      setAuth(true);
      navigate('/dashboard');
    } catch (err) {
      console.error("Login failed", err);
      alert("Login failed. Please try again.");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-cyber-dark text-white">
      <div className="bg-cyber-card p-10 rounded-2xl border border-slate-700 w-full max-w-md text-center shadow-2xl">
        <div className="flex justify-center mb-6 text-cyber-accent">
          <Shield size={64} />
        </div>
        <h2 className="text-3xl font-bold mb-2">Welcome Back</h2>
        <p className="text-slate-400 mb-8">Sign in to access your security dashboard</p>
        
        <div className="flex justify-center">
          <GoogleLogin
            onSuccess={handleSuccess}
            onError={() => {
              console.log('Login Failed');
            }}
            theme="filled_black"
            shape="pill"
          />
        </div>
      </div>
    </div>
  );
}
