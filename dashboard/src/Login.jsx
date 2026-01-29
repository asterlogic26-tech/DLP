import { Shield } from 'lucide-react';
import { GoogleLogin } from '@react-oauth/google';
import { API_URL } from './api';

export default function Login({ onLogin }) {
  
  const handleSuccess = async (credentialResponse) => {
    try {
      const r = await fetch(`${API_URL}/auth/google`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          token: credentialResponse.credential
        })
      });
      
      if (r.ok) {
          const j = await r.json();
          // localStorage.token = j.token; // Handled by parent
          // window.location.reload(); // Removed for speed
          onLogin(j.token);
      } else {
          const errText = await r.text();
          alert(`Login failed by server: ${r.status} ${r.statusText}\n${errText}`);
      }
    } catch (e) {
      alert(`Network Error: Could not connect to backend server at ${API_URL}.\nEnsure the backend is running.\nDetails: ${e.message}`);
    }
  };

  const handleError = () => {
    console.log('Login Failed');
    alert("Google Sign-In Client Error.\n\nPossible causes:\n1. 'http://localhost:5173' is not added to 'Authorized JavaScript origins' in Google Cloud Console.\n2. The Client ID in main.jsx is incorrect.\n3. The popup was closed manually.");
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8 bg-white p-8 rounded-lg shadow-lg">
        <div className="text-center">
          <Shield className="mx-auto h-12 w-12 text-indigo-600" />
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
            DLP Console
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Sign in to manage your organization's policies
          </p>
        </div>
        
        <div className="mt-8 flex justify-center">
            <GoogleLogin
                onSuccess={handleSuccess}
                onError={handleError}
                // useOneTap removed to prevent Windows Security prompt issues
            />
        </div>
        
        <div className="mt-6">
            <div className="relative">
                <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-gray-300" />
                </div>
                <div className="relative flex justify-center text-sm">
                    <span className="px-2 bg-white text-gray-500">
                        Or continue with email (legacy)
                    </span>
                </div>
            </div>
        </div>

        {/* Keeping old form hidden or minimized if needed, but for now just showing Google as primary */}
      </div>
    </div>
  );
}
