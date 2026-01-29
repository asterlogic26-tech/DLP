import { CreditCard } from 'lucide-react';
import { api } from './api';

export default function Subscribe({ onSubscribe }) {
  async function subscribe(plan) {
    try {
        const sub = await api("/subscription/create", "POST", { plan });
        
        const options = {
            key: "YOUR_KEY_ID", // Replace with actual key in production
            subscription_id: sub.id,
            name: "DLP Protection",
            description: `${plan} Subscription`,
            handler: function (response) {
                // alert("Payment successful! Subscription ID: " + response.razorpay_subscription_id);
                // window.location.reload();
                if (onSubscribe) onSubscribe();
            },
            prefill: {
                name: "User Name",
                email: "user@example.com"
            },
            theme: {
                color: "#4F46E5"
            }
        };

        const rzp1 = new window.Razorpay(options);
        rzp1.open();
    } catch (e) {
        console.error(e);
        alert("Failed to initiate subscription");
    }
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
      <div className="flex items-center mb-4">
        <CreditCard className="h-6 w-6 text-indigo-600 mr-2" />
        <h2 className="text-lg font-semibold text-gray-900">Subscription Plans</h2>
      </div>
      <div className="space-y-4">
        <div className="border rounded-md p-4 hover:border-indigo-500 cursor-pointer transition-colors">
            <h3 className="font-medium text-gray-900">B2C Plan</h3>
            <p className="text-gray-500 text-sm mb-3">For individuals</p>
            <button 
                onClick={() => subscribe("B2C")}
                className="w-full bg-indigo-600 text-white py-2 px-4 rounded hover:bg-indigo-700 transition-colors"
            >
                Subscribe ₹125 / month
            </button>
        </div>
        <div className="border rounded-md p-4 hover:border-indigo-500 cursor-pointer transition-colors">
            <h3 className="font-medium text-gray-900">B2B Plan</h3>
            <p className="text-gray-500 text-sm mb-3">For organizations</p>
            <button 
                onClick={() => subscribe("B2B")}
                className="w-full bg-white text-indigo-600 border border-indigo-600 py-2 px-4 rounded hover:bg-indigo-50 transition-colors"
            >
                Subscribe ₹225 / user
            </button>
        </div>
      </div>
    </div>
  );
}
