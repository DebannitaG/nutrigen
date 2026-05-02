import { useState } from 'react';
import { ThumbsUp, ThumbsDown } from 'lucide-react';
import { submitFeedback } from '../services/api';

export default function MealCard({ meal, userId }) {
  const [feedback, setFeedback] = useState(null);

  const handleFeedback = async (type) => {
    setFeedback(type);
    try {
      await submitFeedback({
        user_id: userId || 'anonymous',
        meal_name: meal.food_name,
        feedback: type
      });
    } catch (e) {
      console.error('Feedback error:', e);
    }
  };

  const regionColors = {
    bengali: 'bg-orange-50 text-orange-700 border-orange-200',
    indian: 'bg-yellow-50 text-yellow-700 border-yellow-200',
    'south-indian': 'bg-red-50 text-red-700 border-red-200',
    global: 'bg-blue-50 text-blue-700 border-blue-200'
  };

  return (
    <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-4 hover:shadow-md transition-shadow duration-200">
      <div className="flex items-start justify-between mb-3">
        <div>
          <h4 className="font-semibold text-gray-900 text-sm">{meal.food_name}</h4>
          <div className="flex items-center gap-2 mt-1">
            <span className={`text-xs px-2 py-0.5 rounded-full border font-medium ${regionColors[meal.region] || regionColors.global}`}>
              {meal.region}
            </span>
            <span className={`text-xs px-2 py-0.5 rounded-full ${meal.category === 'veg' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>
              {meal.category}
            </span>
          </div>
        </div>
        <span className="text-lg font-bold text-green-600">{meal.calories}</span>
      </div>

      <div className="grid grid-cols-3 gap-2 mb-3">
        {[
          { label: 'Protein', val: meal.protein, unit: 'g', color: 'text-blue-600' },
          { label: 'Carbs', val: meal.carbs, unit: 'g', color: 'text-yellow-600' },
          { label: 'Fat', val: meal.fat, unit: 'g', color: 'text-red-500' },
        ].map(({ label, val, unit, color }) => (
          <div key={label} className="text-center bg-gray-50 rounded-lg p-2">
            <p className={`text-xs font-semibold ${color}`}>{val}{unit}</p>
            <p className="text-xs text-gray-400">{label}</p>
          </div>
        ))}
      </div>

      <div className="flex items-center gap-2 justify-end">
        <button
          onClick={() => handleFeedback('like')}
          className={`p-1.5 rounded-lg transition-colors ${feedback === 'like' ? 'bg-green-100 text-green-600' : 'text-gray-400 hover:text-green-600 hover:bg-green-50'}`}
        >
          <ThumbsUp size={14} />
        </button>
        <button
          onClick={() => handleFeedback('dislike')}
          className={`p-1.5 rounded-lg transition-colors ${feedback === 'dislike' ? 'bg-red-100 text-red-600' : 'text-gray-400 hover:text-red-600 hover:bg-red-50'}`}
        >
          <ThumbsDown size={14} />
        </button>
      </div>
    </div>
  );
}