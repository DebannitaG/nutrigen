import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createProfile } from '../services/api';
import { User, Loader2, CheckCircle } from 'lucide-react';

const HEALTH_OPTIONS = [
  'diabetes',
  'hypertension',
  'heart disease',
  'thyroid',
  'pcos',
  'obesity',
  'cholesterol',
  'kidney disease',
  'liver disease',
  'anemia',
  'asthma',
  'arthritis',
  'osteoporosis',
  'ibs',
  'celiac disease',
  'lactose intolerance',
  'fatty liver',
  'uric acid / gout',
  'cancer',
  'none'
];

const Field = ({ label, children, required }) => (
  <div>
    <label className="block text-sm font-medium text-gray-700 mb-1.5">
      {label}{required && <span className="text-red-500 ml-1">*</span>}
    </label>
    {children}
  </div>
);


export default function ProfileForm() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');
  const [form, setForm] = useState({
    name: '', age: '', gender: 'male',
    height_cm: '', weight_kg: '',
    activity_level: 'moderately_active',
    goal: 'maintenance',
    diet_preference: 'veg',
    region: 'bengali',
    health_conditions: []
  });

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }));

  const toggleHealth = (cond) => {
    setForm(f => ({
      ...f,
      health_conditions: f.health_conditions.includes(cond)
        ? f.health_conditions.filter(c => c !== cond)
        : [...f.health_conditions, cond]
    }));
  };

  const handleSubmit = async () => {
    if (!form.name || !form.age || !form.height_cm || !form.weight_kg) {
      setError('Please fill all required fields.');
      return;
    }
    setLoading(true);
    setError('');
    try {
      const payload = { ...form, age: +form.age, height_cm: +form.height_cm, weight_kg: +form.weight_kg };
      const res = await createProfile(payload);
      const profileData = res.data;
      localStorage.setItem('hg_profile', JSON.stringify(profileData));
      localStorage.setItem('hg_form', JSON.stringify(payload));
      setSuccess(true);
      setTimeout(() => navigate('/recommend'), 1500);
    } catch (e) {
      setError(e.response?.data?.detail || 'Failed to save profile. Is the backend running?');
    } finally {
      setLoading(false);
    }
  };



  const inputClass = "w-full border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-400 focus:border-transparent bg-gray-50 transition";
  const selectClass = inputClass;

  if (success) return (
    <div className="max-w-lg mx-auto px-4 py-20 text-center">
      <CheckCircle size={56} className="text-green-500 mx-auto mb-4" />
      <h2 className="text-xl font-bold text-gray-900">Profile Saved!</h2>
      <p className="text-gray-500 text-sm mt-2">Redirecting to your diet plan...</p>
    </div>
  );

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-8">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 bg-green-100 rounded-xl flex items-center justify-center">
            <User size={20} className="text-green-600" />
          </div>
          <div>
            <h2 className="font-bold text-lg text-gray-900">Your Health Profile</h2>
            <p className="text-sm text-gray-500">We'll personalize your diet plan based on this</p>
          </div>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl text-sm mb-5">
            {error}
          </div>
        )}

        <div className="space-y-5">
          <Field label="Full Name" required>
            <input className={inputClass} placeholder="Your name" value={form.name} onChange={e => set('name', e.target.value)} />
          </Field>

          <div className="grid grid-cols-2 gap-4">
            <Field label="Age" required>
              <input type="number" className={inputClass} placeholder="25" value={form.age} onChange={e => set('age', e.target.value)} />
            </Field>
            <Field label="Gender">
              <select className={selectClass} value={form.gender} onChange={e => set('gender', e.target.value)}>
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="other">Other</option>
              </select>
            </Field>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <Field label="Height (cm)" required>
              <input type="number" className={inputClass} placeholder="170" value={form.height_cm} onChange={e => set('height_cm', e.target.value)} />
            </Field>
            <Field label="Weight (kg)" required>
              <input type="number" className={inputClass} placeholder="70" value={form.weight_kg} onChange={e => set('weight_kg', e.target.value)} />
            </Field>
          </div>

          <Field label="Activity Level">
            <select className={selectClass} value={form.activity_level} onChange={e => set('activity_level', e.target.value)}>
              <option value="sedentary">Sedentary (desk job)</option>
              <option value="lightly_active">Lightly Active (1-3 days/week)</option>
              <option value="moderately_active">Moderately Active (3-5 days/week)</option>
              <option value="very_active">Very Active (6-7 days/week)</option>
              <option value="extra_active">Extra Active (athlete)</option>
            </select>
          </Field>

          <div className="grid grid-cols-2 gap-4">
            <Field label="Goal">
              <select className={selectClass} value={form.goal} onChange={e => set('goal', e.target.value)}>
                <option value="weight_loss">Weight Loss</option>
                <option value="weight_gain">Weight Gain</option>
                <option value="maintenance">Maintenance</option>
              </select>
            </Field>
            <Field label="Diet Preference">
              <select className={selectClass} value={form.diet_preference} onChange={e => set('diet_preference', e.target.value)}>
  <option value="veg">Vegetarian (no meat/fish/eggs)</option>
  <option value="eggetarian">Eggetarian (veg + eggs)</option>
  <option value="non-veg">Non-Vegetarian (all foods)</option>
  <option value="veg-nonveg">Veg + Non-Veg (flexible)</option>
  <option value="jain">Jain (no onion/garlic/root veg)</option>
  <option value="sattvic">Sattvic (pure veg, no spices)</option>
  <option value="pescatarian">Pescatarian (veg + fish only)</option>
  <option value="vegan">Vegan (no animal products)</option>
</select>
            </Field>
          </div>

          <Field label="Region">
            <select className={selectClass} value={form.region} onChange={e => set('region', e.target.value)}>
              <option value="bengali">Bengali</option>
              <option value="indian">Indian (North)</option>
              <option value="south-indian">South Indian</option>
              <option value="global">Global</option>
            </select>
          </Field>

          <Field label="Health Conditions (select all that apply)">
            <div className="flex flex-wrap gap-2 mt-1">
              {HEALTH_OPTIONS.map(cond => (
                <button
                  key={cond}
                  type="button"
                  onClick={() => toggleHealth(cond)}
                  className={`px-3 py-1.5 rounded-lg text-sm border transition-colors capitalize
                    ${form.health_conditions.includes(cond)
                      ? 'bg-green-500 text-white border-green-500'
                      : 'bg-gray-50 text-gray-600 border-gray-200 hover:border-green-300'}`}
                >
                  {cond}
                </button>
              ))}
            </div>
          </Field>
        </div>

        <button
          onClick={handleSubmit}
          disabled={loading}
          className="mt-7 w-full bg-green-500 hover:bg-green-600 disabled:opacity-60 text-white font-semibold py-3 rounded-xl transition-colors flex items-center justify-center gap-2"
        >
          {loading ? <><Loader2 size={18} className="animate-spin" /> Saving...</> : 'Save Profile & Get Diet Plan →'}
        </button>
      </div>
    </div>
  );
}