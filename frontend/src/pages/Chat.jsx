import ChatBox from '../components/ChatBox';
import { BookOpen } from 'lucide-react';

const topics = [
  'BMI & calorie calculation',
  'Bengali & Indian food nutrition',
  'Weight loss & gain strategies',
  'Diabetes-friendly foods',
  'Protein sources for vegetarians',
  'Meal timing & frequency',
];

export default function Chat() {
  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <div className="grid md:grid-cols-3 gap-6">
        <div className="md:col-span-2">
          <div className="mb-4">
            <h1 className="text-2xl font-bold text-gray-900">Nutrition AI Chat</h1>
            <p className="text-gray-500 text-sm mt-1">Powered by RAG + OpenAI • Knowledge base includes Indian & Bengali nutrition</p>
          </div>
          <ChatBox />
        </div>

        {/* Sidebar */}
        <div className="space-y-4">
          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
            <div className="flex items-center gap-2 mb-4">
              <BookOpen size={16} className="text-green-500" />
              <h3 className="font-semibold text-sm text-gray-900">Topics I Know About</h3>
            </div>
            <div className="space-y-2">
              {topics.map(t => (
                <div key={t} className="flex items-center gap-2 text-sm text-gray-600">
                  <div className="w-1.5 h-1.5 bg-green-400 rounded-full flex-shrink-0"></div>
                  {t}
                </div>
              ))}
            </div>
          </div>

          <div className="bg-gradient-to-br from-green-50 to-emerald-50 border border-green-100 rounded-2xl p-5">
            <h3 className="font-semibold text-sm text-gray-900 mb-2">How RAG Works</h3>
            <div className="space-y-2 text-xs text-gray-600">
              {['Your question is embedded', 'Similar docs retrieved from FAISS', 'Context sent to GPT-3.5', 'Grounded answer generated'].map((step, i) => (
                <div key={step} className="flex items-start gap-2">
                  <span className="font-bold text-green-600 flex-shrink-0">{i + 1}.</span>
                  <span>{step}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}