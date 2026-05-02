import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2 } from 'lucide-react';
import { sendChat } from '../services/api';

export default function ChatBox() {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hello! I\'m NutriGen. I can answer questions about nutrition, diet plans, Bengali and Indian foods, calorie counting, and more. How can I help you today?' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;
    const userMsg = { role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const history = messages.slice(-8).map(m => ({ role: m.role, content: m.content }));
      const res = await sendChat({ message: input, conversation_history: history });
      setMessages(prev => [...prev, { role: 'assistant', content: res.data.response }]);
    } catch (e) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I had trouble connecting. Please check the server and try again.'
      }]);
    } finally {
      setLoading(false);
    }
  };

  const suggestions = [
    "What should I eat for weight loss?",
    "Explain Bengali diet benefits",
    "How much protein do I need daily?",
    "Best foods for diabetes?"
  ];

  return (
    <div className="flex flex-col h-[600px] bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
      <div className="px-5 py-4 border-b border-gray-100 bg-gradient-to-r from-green-50 to-emerald-50">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-green-500 rounded-full flex items-center justify-center">
            <Bot size={18} className="text-white" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">NutriGen</h3>
            <p className="text-xs text-gray-500">NutriGen • Powered by RAG</p>
          </div>
          <div className="ml-auto flex items-center gap-1.5">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-xs text-green-600 font-medium">Online</span>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-hide">
        {messages.map((msg, i) => (
          <div key={i} className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0
              ${msg.role === 'user' ? 'bg-green-500' : 'bg-gray-100'}`}>
              {msg.role === 'user'
                ? <User size={14} className="text-white" />
                : <Bot size={14} className="text-gray-600" />}
            </div>
            <div className={`max-w-[80%] px-4 py-2.5 rounded-2xl text-sm leading-relaxed
              ${msg.role === 'user'
                ? 'bg-green-500 text-white rounded-tr-sm'
                : 'bg-gray-50 text-gray-800 rounded-tl-sm border border-gray-100'}`}>
              {msg.content}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center">
              <Bot size={14} className="text-gray-600" />
            </div>
            <div className="bg-gray-50 border border-gray-100 rounded-2xl rounded-tl-sm px-4 py-3 flex items-center gap-2">
              <Loader2 size={14} className="animate-spin text-green-500" />
              <span className="text-sm text-gray-500">Thinking...</span>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {messages.length <= 1 && (
        <div className="px-4 pb-2 flex gap-2 flex-wrap">
          {suggestions.map((s, i) => (
            <button
              key={i}
              onClick={() => setInput(s)}
              className="text-xs bg-green-50 text-green-700 border border-green-100 px-3 py-1.5 rounded-full hover:bg-green-100 transition-colors"
            >
              {s}
            </button>
          ))}
        </div>
      )}

      <div className="p-4 border-t border-gray-100">
        <div className="flex items-center gap-3 bg-gray-50 rounded-xl px-4 py-2.5">
          <input
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && sendMessage()}
            placeholder="Ask me anything about nutrition..."
            className="flex-1 bg-transparent text-sm outline-none text-gray-800 placeholder-gray-400"
          />
          <button
            onClick={sendMessage}
            disabled={!input.trim() || loading}
            className="p-1.5 bg-green-500 hover:bg-green-600 disabled:opacity-40 rounded-lg transition-colors"
          >
            <Send size={14} className="text-white" />
          </button>
        </div>
      </div>
    </div>
  );
}