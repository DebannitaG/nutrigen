import { useNavigate } from 'react-router-dom';
import { Activity, Target, Zap, Users, ArrowRight, Heart } from 'lucide-react';

const stats = [
  { label: 'Foods in Database', value: '65+', icon: Heart, color: 'text-green-600', bg: 'bg-green-50' },
  { label: 'Indian/Bengali Items', value: '25+', icon: Users, color: 'text-orange-600', bg: 'bg-orange-50' },
  { label: 'ML Model Accuracy', value: '~92%', icon: Zap, color: 'text-blue-600', bg: 'bg-blue-50' },
  { label: 'Goals Supported', value: '3', icon: Target, color: 'text-purple-600', bg: 'bg-purple-50' },
];

const features = [
  { title: 'Hybrid Recommendations', desc: 'Rule-based + ML + Content filtering for personalized meals', color: 'border-green-200 bg-green-50' },
  { title: 'RAG-Powered Chat', desc: 'Ask nutrition questions answered from a curated knowledge base', color: 'border-blue-200 bg-blue-50' },
  { title: 'Regional Intelligence', desc: 'Bengali, Indian, South Indian, and global food support', color: 'border-orange-200 bg-orange-50' },
  { title: 'Explainable AI', desc: 'Understand why each meal was recommended for you', color: 'border-purple-200 bg-purple-50' },
];

export default function Dashboard() {
  const navigate = useNavigate();
  const profile = JSON.parse(localStorage.getItem('hg_profile') || 'null');

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="bg-gradient-to-br from-green-500 to-emerald-600 rounded-2xl p-8 text-white mb-8 relative overflow-hidden">
        <div className="absolute right-0 top-0 w-64 h-64 bg-white opacity-5 rounded-full -translate-y-1/2 translate-x-1/4"></div>
        <div className="relative z-10">
          <p className="text-green-100 text-sm font-medium mb-2">Welcome to</p>
          <h1 className="text-3xl font-bold mb-2">NutriGen</h1>
          <p className="text-green-100 max-w-lg">
            Your personalized nutrition intelligence platform with Bengali & Indian cuisine support,
            powered by RAG and Machine Learning.
          </p>
          <div className="flex gap-3 mt-6">
            <button
              onClick={() => navigate('/profile')}
              className="bg-white text-green-700 px-5 py-2.5 rounded-xl font-semibold text-sm flex items-center gap-2 hover:bg-green-50 transition-colors"
            >
              Get Started <ArrowRight size={16} />
            </button>
            <button
              onClick={() => navigate('/chat')}
              className="bg-green-400 bg-opacity-30 border border-green-300 text-white px-5 py-2.5 rounded-xl font-semibold text-sm hover:bg-opacity-40 transition-colors"
            >
              Ask AI
            </button>
          </div>
        </div>
      </div>

      {profile && (
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 mb-8">
          <h2 className="font-semibold text-gray-700 mb-4">Your Health Summary</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { label: 'BMI', value: profile.bmi, unit: '', color: 'text-green-600' },
              { label: 'Category', value: profile.bmi_category, unit: '', color: 'text-blue-600' },
              { label: 'Daily Target', value: Math.round(profile.target_calories), unit: 'kcal', color: 'text-orange-600' },
              { label: 'Goal', value: profile.goal?.replace(/_/g, ' '), unit: '', color: 'text-purple-600' },
            ].map(item => (
              <div key={item.label} className="text-center p-4 bg-gray-50 rounded-xl">
                <p className={`text-2xl font-bold ${item.color}`}>{item.value} <span className="text-sm">{item.unit}</span></p>
                <p className="text-xs text-gray-500 mt-1">{item.label}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {stats.map(({ label, value, icon: Icon, color, bg }) => (
          <div key={label} className="bg-white rounded-xl border border-gray-100 shadow-sm p-4 flex items-center gap-4">
            <div className={`${bg} p-3 rounded-xl`}>
              <Icon size={20} className={color} />
            </div>
            <div>
              <p className="text-xl font-bold text-gray-900">{value}</p>
              <p className="text-xs text-gray-500">{label}</p>
            </div>
          </div>
        ))}
      </div>

      <h2 className="font-semibold text-gray-900 mb-4">Platform Features</h2>
      <div className="grid md:grid-cols-2 gap-4">
        {features.map(({ title, desc, color }) => (
          <div key={title} className={`rounded-xl border p-5 ${color}`}>
            <h3 className="font-semibold text-gray-900 mb-1">{title}</h3>
            <p className="text-sm text-gray-600">{desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
}