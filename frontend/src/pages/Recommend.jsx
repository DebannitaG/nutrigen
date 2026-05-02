import { useState, useEffect } from 'react';
import { getRecommendations } from '../services/api';
import MealCard from '../components/MealCard';
import { Loader2, Info, Utensils, Sun, Moon, Cookie } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const slots = [
  { key: 'breakfast', label: 'Breakfast', icon: Sun, color: 'text-yellow-500' },
  { key: 'lunch', label: 'Lunch', icon: Utensils, color: 'text-green-500' },
  { key: 'dinner', label: 'Dinner', icon: Moon, color: 'text-blue-500' },
  { key: 'snacks', label: 'Snacks', icon: Cookie, color: 'text-orange-500' },
];

export default function Recommend() {
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const form = JSON.parse(localStorage.getItem('hg_form') || 'null');
    if (!form) return;
    fetchRecommendations(form);
  }, []);

  const fetchRecommendations = async (form) => {
    setLoading(true);
    setError('');
    try {
      const res = await getRecommendations(form);
      setData(res.data);
    } catch (e) {
      setError('Could not load recommendations. Make sure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const profileData = JSON.parse(localStorage.getItem('hg_profile') || 'null');

  if (!profileData) return (
    <div className="max-w-2xl mx-auto px-4 py-20 text-center">
      <Utensils size={48} className="text-gray-300 mx-auto mb-4" />
      <h2 className="text-xl font-bold text-gray-900 mb-2">No Profile Found</h2>
      <p className="text-gray-500 mb-6">Please complete your profile first to get personalized recommendations.</p>
      <button onClick={() => navigate('/profile')} className="bg-green-500 text-white px-6 py-2.5 rounded-xl font-semibold hover:bg-green-600 transition-colors">
        Create Profile
      </button>
    </div>
  );

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Your Personalized Diet Plan</h1>
        <p className="text-gray-500 text-sm mt-1">Generated using Hybrid ML + Rule-based Engine</p>
      </div>

      {loading && (
        <div className="flex items-center justify-center py-20">
          <Loader2 size={32} className="animate-spin text-green-500" />
          <span className="ml-3 text-gray-500">Generating your plan...</span>
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl text-sm">
          {error}
        </div>
      )}

      {data && (
        <>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            {[
              { label: 'Target Calories', value: `${Math.round(data.target_calories)} kcal`, color: 'text-green-600' },
              { label: 'Total Protein', value: `${data.total_protein}g`, color: 'text-blue-600' },
              { label: 'Total Carbs', value: `${data.total_carbs}g`, color: 'text-yellow-600' },
              { label: 'ML Suggested Goal', value: data.ml_predicted_goal?.replace(/_/g, ' '), color: 'text-purple-600' },
            ].map(({ label, value, color }) => (
              <div key={label} className="bg-white rounded-xl border border-gray-100 shadow-sm p-4 text-center">
                <p className={`text-xl font-bold ${color}`}>{value}</p>
                <p className="text-xs text-gray-500 mt-1">{label}</p>
              </div>
            ))}
          </div>

          {data.explanation && (
            <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-6 flex gap-3">
              <Info size={18} className="text-blue-500 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-blue-800">{data.explanation}</p>
            </div>
          )}

          {slots.map(({ key, label, icon: Icon, color }) => (
            data[key]?.length > 0 && (
              <div key={key} className="mb-7">
                <div className="flex items-center gap-2 mb-3">
                  <Icon size={18} className={color} />
                  <h3 className="font-semibold text-gray-900">{label}</h3>
                  <span className="text-xs text-gray-400 ml-1">
                    {Math.round(data[key].reduce((s, m) => s + m.calories, 0))} kcal
                  </span>
                </div>
                <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-4">
                  {data[key].map((meal, i) => (
                    <MealCard key={i} meal={meal} userId={profileData?.user_id} />
                  ))}
                </div>
              </div>
            )
          ))}
        </>
      )}
    </div>
  );
}