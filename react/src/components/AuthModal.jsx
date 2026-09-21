import React, { useState } from 'react';
import { X, Lock, Mail, User, ShieldCheck, UserCheck, Users, Sparkles } from 'lucide-react';

export default function AuthModal({ isOpen, onClose, onLoginSuccess, apiBase }) {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    role: 'student',
    name: ''
  });
  const [errorMsg, setErrorMsg] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    setIsLoading(true);

    const endpoint = isLogin ? `${apiBase}/auth/login/` : `${apiBase}/auth/register/`;
    const payload = isLogin
      ? { username: formData.username || formData.email, password: formData.password }
      : {
          username: formData.username || formData.email.split('@')[0],
          email: formData.email,
          password: formData.password,
          role: formData.role,
          first_name: formData.name
        };

    try {
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (res.ok) {
        localStorage.setItem('smartedu_token', data.access);
        onLoginSuccess(data.user);
        onClose();
      } else {
        setErrorMsg(data.error || data.detail || JSON.stringify(data));
      }
    } catch (err) {
      setErrorMsg("Network error connecting to backend: " + err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const quickLogin = (role) => {
    if (role === 'admin') {
      setFormData({ username: 'admin', password: 'Admin@123', email: 'admin@smartedu.edu', role: 'admin', name: 'Admin' });
    } else if (role === 'faculty') {
      setFormData({ username: 'faculty', password: 'Faculty@123', email: 'faculty@smartedu.edu', role: 'faculty', name: 'Prof. Rajesh Kumar' });
    } else {
      setFormData({ username: 'student', password: 'Student@123', email: 'student@smartedu.edu', role: 'student', name: 'Arjun Verma' });
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-4 animate-fade-in">
      <div className="w-full max-w-md rounded-2xl bg-slate-900 border border-slate-700 p-6 shadow-2xl relative">
        
        {/* Close button */}
        <button 
          onClick={onClose}
          className="absolute right-4 top-4 text-slate-400 hover:text-white transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="text-center mb-6">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-sky-500 to-indigo-600 flex items-center justify-center mx-auto mb-3 shadow-lg shadow-sky-500/20">
            <Lock className="w-6 h-6 text-white" />
          </div>
          <h2 className="text-xl font-bold text-white tracking-tight">
            {isLogin ? "Sign in to SmartEdu AI" : "Create SmartEdu Account"}
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            {isLogin ? "Access student records, LSTM risk intelligence & dashboards" : "Register as Admin, Faculty, or Student"}
          </p>
        </div>

        {/* Demo Quick Sign-In Pills */}
        {isLogin && (
          <div className="mb-5 p-3 rounded-xl bg-slate-950/80 border border-slate-800">
            <div className="text-[11px] font-semibold text-sky-400 flex items-center space-x-1 mb-2">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Instant Demo Personas (One-Click Fill)</span>
            </div>
            <div className="grid grid-cols-3 gap-2">
              <button
                type="button"
                onClick={() => quickLogin('admin')}
                className="px-2 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-750 text-slate-200 border border-slate-700 text-[11px] font-medium flex items-center justify-center space-x-1"
              >
                <ShieldCheck className="w-3 h-3 text-sky-400" />
                <span>Admin</span>
              </button>
              <button
                type="button"
                onClick={() => quickLogin('faculty')}
                className="px-2 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-750 text-slate-200 border border-slate-700 text-[11px] font-medium flex items-center justify-center space-x-1"
              >
                <UserCheck className="w-3 h-3 text-indigo-400" />
                <span>Faculty</span>
              </button>
              <button
                type="button"
                onClick={() => quickLogin('student')}
                className="px-2 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-750 text-slate-200 border border-slate-700 text-[11px] font-medium flex items-center justify-center space-x-1"
              >
                <Users className="w-3 h-3 text-emerald-400" />
                <span>Student</span>
              </button>
            </div>
          </div>
        )}

        {errorMsg && (
          <div className="mb-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs">
            {errorMsg}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4 text-xs">
          {!isLogin && (
            <div>
              <label className="block text-slate-400 mb-1">Full Name</label>
              <input
                type="text"
                required
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                placeholder="e.g. Arjun Verma"
                className="w-full p-2.5 rounded-xl bg-slate-800 border border-slate-700 text-white focus:outline-none focus:border-sky-500"
              />
            </div>
          )}

          <div>
            <label className="block text-slate-400 mb-1">{isLogin ? "Username or Email" : "Username"}</label>
            <input
              type="text"
              required
              value={formData.username}
              onChange={(e) => setFormData({...formData, username: e.target.value})}
              placeholder="e.g. admin or faculty or student"
              className="w-full p-2.5 rounded-xl bg-slate-800 border border-slate-700 text-white focus:outline-none focus:border-sky-500"
            />
          </div>

          {!isLogin && (
            <>
              <div>
                <label className="block text-slate-400 mb-1">Email Address</label>
                <input
                  type="email"
                  required
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  placeholder="name@smartedu.edu"
                  className="w-full p-2.5 rounded-xl bg-slate-800 border border-slate-700 text-white focus:outline-none focus:border-sky-500"
                />
              </div>

              <div>
                <label className="block text-slate-400 mb-1">System Role</label>
                <select
                  value={formData.role}
                  onChange={(e) => setFormData({...formData, role: e.target.value})}
                  className="w-full p-2.5 rounded-xl bg-slate-800 border border-slate-700 text-white focus:outline-none focus:border-sky-500"
                >
                  <option value="student">Student</option>
                  <option value="faculty">Faculty Member</option>
                  <option value="admin">Institutional Administrator</option>
                </select>
              </div>
            </>
          )}

          <div>
            <label className="block text-slate-400 mb-1">Password</label>
            <input
              type="password"
              required
              value={formData.password}
              onChange={(e) => setFormData({...formData, password: e.target.value})}
              placeholder="••••••••"
              className="w-full p-2.5 rounded-xl bg-slate-800 border border-slate-700 text-white focus:outline-none focus:border-sky-500"
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-3 rounded-xl bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 text-white font-semibold shadow-lg shadow-sky-500/25 transition-all disabled:opacity-50 text-xs"
          >
            {isLoading ? "Authenticating..." : isLogin ? "Sign In" : "Create Account"}
          </button>
        </form>

        <div className="mt-4 text-center">
          <button
            type="button"
            onClick={() => { setIsLogin(!isLogin); setErrorMsg(''); }}
            className="text-xs text-sky-400 hover:text-sky-300 font-medium"
          >
            {isLogin ? "Need a new account? Register here" : "Already have an account? Sign in"}
          </button>
        </div>

      </div>
    </div>
  );
}
