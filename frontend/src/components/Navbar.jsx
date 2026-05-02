import { Link, useLocation } from 'react-router-dom';
import { Heart, LayoutDashboard, User, MessageCircle, Utensils } from 'lucide-react';

const navItems = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/profile', label: 'Profile', icon: User },
  { path: '/recommend', label: 'Diet Plan', icon: Utensils },
  { path: '/chat', label: 'AI Chat', icon: MessageCircle },
];

export default function Navbar() {
  const location = useLocation();
  return (
    <nav className="bg-white border-b border-gray-100 shadow-sm sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-4 flex items-center justify-between h-16">
        <Link to="/" className="flex items-center gap-2 font-bold text-xl text-green-600">
          <Heart size={24} className="text-green-500" fill="currentColor" />
          NutriGen
        </Link>
        <div className="flex items-center gap-1">
          {navItems.map(({ path, label, icon: Icon }) => (
            <Link
              key={path}
              to={path}
              className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200
                ${location.pathname === path
                  ? 'bg-green-50 text-green-700'
                  : 'text-gray-500 hover:text-gray-900 hover:bg-gray-50'}`}
            >
              <Icon size={16} />
              <span className="hidden sm:block">{label}</span>
            </Link>
          ))}
        </div>
      </div>
    </nav>
  );
}