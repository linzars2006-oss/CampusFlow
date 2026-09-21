import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import AdminDashboard from './components/AdminDashboard';
import FacultyDashboard from './components/FacultyDashboard';
import StudentDashboard from './components/StudentDashboard';
import AuthModal from './components/AuthModal';
import { Sparkles, Database, BrainCircuit, Activity } from 'lucide-react';

const API_BASE = 'http://127.0.0.1:8000/api';

export default function App() {
  const [currentUser, setCurrentUser] = useState({
    id: 1,
    username: 'admin',
    name: 'System Administrator',
    email: 'admin@smartedu.edu',
    role: 'admin',
    student_id: 1,
    faculty_id: 1
  });

  const [showAuthModal, setShowAuthModal] = useState(false);
  const [systemStatus, setSystemStatus] = useState(null);

  useEffect(() => {
    // Check system status
    fetch(`${API_BASE}/system/status/`)
      .then(res => res.json())
      .then(data => setSystemStatus(data))
      .catch(err => console.warn("Backend not yet running:", err));
  }, []);

  const handleRoleSwitch = (newRole) => {
    if (newRole === 'admin') {
      setCurrentUser({
        id: 1,
        username: 'admin',
        name: 'System Administrator',
        email: 'admin@smartedu.edu',
        role: 'admin'
      });
    } else if (newRole === 'faculty') {
      setCurrentUser({
        id: 2,
        username: 'faculty',
        name: 'Dr. Rajesh Kumar',
        email: 'faculty@smartedu.edu',
        role: 'faculty',
        faculty_id: 1
      });
    } else {
      setCurrentUser({
        id: 3,
        username: 'student',
        name: 'Arjun Verma',
        email: 'student@smartedu.edu',
        role: 'student',
        student_id: 1,
        roll_no: '23CS001',
        class_name: 'CSE-A'
      });
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('smartedu_token');
    setShowAuthModal(true);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col selection:bg-sky-500 selection:text-white">
      
      {/* Navigation Header */}
      <Navbar
        currentUser={currentUser}
        onRoleSwitch={handleRoleSwitch}
        onLogout={handleLogout}
        systemStatus={systemStatus}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {currentUser?.role === 'admin' && (
          <AdminDashboard apiBase={API_BASE} />
        )}

        {currentUser?.role === 'faculty' && (
          <FacultyDashboard apiBase={API_BASE} currentUser={currentUser} />
        )}

        {currentUser?.role === 'student' && (
          <StudentDashboard apiBase={API_BASE} currentUser={currentUser} />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950/80 py-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center space-x-2">
            <BrainCircuit className="w-4 h-4 text-sky-400" />
            <span className="font-semibold text-slate-300">SmartEdu AI</span>
            <span>• Sequential Academic Risk Intelligence System</span>
          </div>

          <div className="flex items-center space-x-4 text-[11px] font-mono">
            <span className="flex items-center space-x-1.5 text-emerald-400">
              <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
              <span>MongoDB Atlas: Connected</span>
            </span>
            <span className="text-slate-600">|</span>
            <span className="text-sky-400">PyTorch LSTM + XGBoost Engine</span>
          </div>
        </div>
      </footer>

      {/* Authentication Modal */}
      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        onLoginSuccess={(user) => setCurrentUser(user)}
        apiBase={API_BASE}
      />

    </div>
  );
}
