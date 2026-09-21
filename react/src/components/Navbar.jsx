import React, { useState, useEffect } from 'react';
import { 
  GraduationCap, 
  BrainCircuit, 
  ShieldCheck, 
  UserCheck, 
  Users, 
  Database, 
  LogOut, 
  Sparkles,
  ChevronDown
} from 'lucide-react';

export default function Navbar({ currentUser, onRoleSwitch, onLogout, systemStatus }) {
  const [showRoleMenu, setShowRoleMenu] = useState(false);

  const roles = [
    { id: 'admin', label: 'Administrator', icon: ShieldCheck, desc: 'Manage users, CSV import, analytics' },
    { id: 'faculty', label: 'Faculty / Professor', icon: UserCheck, desc: 'Mark attendance, score tests, risk table' },
    { id: 'student', label: 'Student Portal', icon: Users, desc: '16-wk trend charts, explainability, AI chat' }
  ];

  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-800/80 bg-slate-950/85 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Brand Logo */}
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-sky-600 via-indigo-600 to-purple-600 flex items-center justify-center shadow-lg shadow-sky-500/20">
            <BrainCircuit className="w-6 h-6 text-white animate-pulse" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xl font-bold tracking-tight bg-gradient-to-r from-white via-slate-200 to-sky-400 bg-clip-text text-transparent">
                SmartEdu AI
              </span>
              <span className="px-2 py-0.5 text-[10px] font-semibold tracking-wide uppercase bg-sky-500/10 text-sky-400 border border-sky-500/20 rounded-full">
                Deep Learning LSTM
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-medium">
              Sequential Academic Risk Intelligence
            </p>
          </div>
        </div>

        {/* MongoDB Atlas Live Badge & Demo Role Switcher */}
        <div className="flex items-center space-x-4">
          
          {/* Atlas Cloud Status Indicator */}
          <div className="hidden md:flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-300">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <Database className="w-3.5 h-3.5 text-emerald-400" />
            <span className="font-mono text-[11px] text-emerald-300">Atlas: smartedu</span>
          </div>

          {/* Role Switcher Pill */}
          <div className="relative">
            <button 
              onClick={() => setShowRoleMenu(!showRoleMenu)}
              className="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-750 text-slate-200 border border-slate-700 text-xs font-medium transition-colors"
            >
              <span className="capitalize text-sky-400 font-semibold">{currentUser?.role || 'Guest'}</span>
              <span className="text-slate-400 text-[10px]">• Switch Role</span>
              <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
            </button>

            {showRoleMenu && (
              <div className="absolute right-0 mt-2 w-64 rounded-xl bg-slate-900 border border-slate-700 shadow-2xl p-2 z-50">
                <div className="px-2 py-1.5 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                  Test Personas
                </div>
                {roles.map(r => {
                  const Icon = r.icon;
                  const isActive = currentUser?.role === r.id;
                  return (
                    <button
                      key={r.id}
                      onClick={() => {
                        onRoleSwitch(r.id);
                        setShowRoleMenu(false);
                      }}
                      className={`w-full flex items-start space-x-3 p-2 rounded-lg text-left transition-all ${
                        isActive 
                          ? 'bg-sky-500/15 text-sky-300 border border-sky-500/30' 
                          : 'hover:bg-slate-800 text-slate-300'
                      }`}
                    >
                      <Icon className={`w-5 h-5 mt-0.5 ${isActive ? 'text-sky-400' : 'text-slate-400'}`} />
                      <div>
                        <div className="font-medium text-xs text-white">{r.label}</div>
                        <div className="text-[10px] text-slate-400">{r.desc}</div>
                      </div>
                    </button>
                  );
                })}
              </div>
            )}
          </div>

          {/* User Account / Sign Out */}
          {currentUser && (
            <div className="flex items-center space-x-3 pl-2 border-l border-slate-800">
              <div className="hidden sm:block text-right">
                <div className="text-xs font-medium text-white">{currentUser.name}</div>
                <div className="text-[10px] text-slate-400">{currentUser.email}</div>
              </div>
              <button 
                onClick={onLogout}
                title="Logout"
                className="p-2 rounded-lg bg-slate-900 hover:bg-rose-500/10 hover:text-rose-400 text-slate-400 border border-slate-800 transition-colors"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          )}

        </div>

      </div>
    </header>
  );
}
