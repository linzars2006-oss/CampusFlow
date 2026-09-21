import React, { useState, useEffect } from 'react';
import { 
  TrendingUp, 
  CheckCircle, 
  AlertTriangle, 
  BookOpen, 
  BrainCircuit, 
  MessageSquare, 
  Send, 
  Sparkles, 
  HelpCircle,
  Clock,
  ShieldAlert,
  ArrowUpRight
} from 'lucide-react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip as RechartsTooltip, 
  Legend, 
  ResponsiveContainer 
} from 'recharts';

export default function StudentDashboard({ apiBase, currentUser }) {
  const [profileData, setProfileData] = useState(null);
  const [weeklyTrends, setWeeklyTrends] = useState([]);
  const [loading, setLoading] = useState(true);

  // Chat states
  const [messages, setMessages] = useState([
    {
      sender: 'ai',
      text: "Hello Arjun! I am your SmartEdu Academic Advisor. I have analyzed your 16-week attendance and test trajectory using our Sequential LSTM model. Ask me anything about your academic standing, risk factors, or how to improve!"
    }
  ]);
  const [chatInput, setChatInput] = useState('');
  const [isSending, setIsSending] = useState(false);

  useEffect(() => {
    fetchStudentData();
  }, [currentUser]);

  const fetchStudentData = async () => {
    setLoading(true);
    try {
      const studentId = currentUser?.student_id || 1;
      const [profRes, trendRes] = await Promise.all([
        fetch(`${apiBase}/student/my-risk/?student_id=${studentId}`),
        fetch(`${apiBase}/student/weekly-trends/?student_id=${studentId}`)
      ]);

      if (profRes.ok) setProfileData(await profRes.json());
      if (trendRes.ok) setWeeklyTrends(await trendRes.json());
    } catch (err) {
      console.error("Error fetching student profile:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async (msgText) => {
    const textToSend = msgText || chatInput;
    if (!textToSend.trim()) return;

    const userMsg = { sender: 'user', text: textToSend };
    setMessages(prev => [...prev, userMsg]);
    if (!msgText) setChatInput('');
    setIsSending(true);

    try {
      const studentId = currentUser?.student_id || 1;
      const res = await fetch(`${apiBase}/student/chat/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          student_id: studentId,
          message: textToSend
        })
      });
      const data = await res.json();
      if (res.ok) {
        setMessages(prev => [...prev, { sender: 'ai', text: data.reply }]);
      } else {
        setMessages(prev => [...prev, { sender: 'ai', text: "Service temporarily unavailable. Please try again." }]);
      }
    } catch (err) {
      setMessages(prev => [...prev, { sender: 'ai', text: "Error connecting to advisor engine." }]);
    } finally {
      setIsSending(false);
    }
  };

  const sampleQuestions = [
    "Why am I flagged as at-risk?",
    "What changed between week 4 and week 8?",
    "What is my current attendance percentage?",
    "What should I do to improve my marks?"
  ];

  const riskPred = profileData?.risk_prediction || {};
  const isHighRisk = riskPred.risk_level === 'high';
  const isMedRisk = riskPred.risk_level === 'medium';

  return (
    <div className="space-y-8 animate-fade-in">
      
      {/* Student Welcome Header */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-slate-900 via-slate-900 to-sky-950/40 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-2xl font-bold text-white tracking-tight">
              Welcome, {profileData?.student?.name || currentUser?.name || "Arjun Verma"}!
            </h1>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-semibold bg-sky-500/10 text-sky-400 border border-sky-500/20">
              {profileData?.student?.roll_no || "23CS001"}
            </span>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            Enrolled in <strong className="text-slate-200">{profileData?.student?.class_name || "CSE-A"}</strong> • Prior GPA: <strong className="text-emerald-400">{profileData?.student?.prev_gpa || "7.85"} / 10</strong>
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <div className="px-4 py-2 rounded-xl bg-slate-800/80 border border-slate-700 text-right">
            <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Evaluation Checkpoint</span>
            <span className="text-xs font-bold text-sky-400 font-mono">Semester Week 16</span>
          </div>
        </div>
      </div>

      {/* Academic Risk Status & Explainability Card */}
      <div className={`p-6 rounded-2xl border transition-all ${
        isHighRisk 
          ? 'bg-rose-950/20 border-rose-500/30' 
          : isMedRisk 
          ? 'bg-amber-950/20 border-amber-500/30' 
          : 'bg-emerald-950/20 border-emerald-500/30'
      }`}>
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4 border-b border-slate-800/80 pb-4">
          <div className="flex items-center space-x-3">
            <div className={`p-3 rounded-xl ${
              isHighRisk ? 'bg-rose-500/20 text-rose-400' : isMedRisk ? 'bg-amber-500/20 text-amber-400' : 'bg-emerald-500/20 text-emerald-400'
            }`}>
              <BrainCircuit className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">AI Risk Status:</span>
                <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold uppercase tracking-wider ${
                  isHighRisk 
                    ? 'bg-rose-500 text-white' 
                    : isMedRisk 
                    ? 'bg-amber-500 text-slate-950' 
                    : 'bg-emerald-500 text-slate-950'
                }`}>
                  {riskPred.risk_level || 'Low'} Risk
                </span>
                <span className="text-xs text-slate-400 font-mono">
                  ({((riskPred.confidence_score || 0.88) * 100).toFixed(0)}% Confidence)
                </span>
              </div>
              <p className="text-xs text-slate-300 mt-1">
                Model: <span className="font-mono text-sky-400 font-medium">Sequential Attention-LSTM</span> • Evaluated across your 16-week timeline
              </p>
            </div>
          </div>
        </div>

        {/* Explainability: Contributing Factors & Prescriptive Recommendations */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-4 text-xs">
          
          {/* Key Contributing Factors */}
          <div>
            <h3 className="font-semibold text-white mb-2 flex items-center space-x-1.5">
              <Sparkles className="w-4 h-4 text-sky-400" />
              <span>Key Factors Contributing to Your Standing:</span>
            </h3>
            <div className="space-y-2">
              {(riskPred.top_factors || []).map((f, idx) => (
                <div key={idx} className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 flex items-start space-x-2.5">
                  <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                  <div>
                    <div className="font-medium text-slate-200">{f.label || f.feature}</div>
                    <div className="text-[10px] text-slate-400 mt-0.5">
                      Attribution Impact: {(f.impact_score * 100).toFixed(0)}%
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Actionable Recommendations */}
          <div>
            <h3 className="font-semibold text-white mb-2 flex items-center space-x-1.5">
              <CheckCircle className="w-4 h-4 text-emerald-400" />
              <span>Recommended Action Plan:</span>
            </h3>
            <div className="space-y-2">
              {(profileData?.recommendations || []).map((rec, idx) => (
                <div key={idx} className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 text-slate-300 leading-relaxed">
                  • {rec.recommendation_text}
                </div>
              ))}
            </div>
          </div>

        </div>
      </div>

      {/* 16-Week Longitudinal Trend Chart */}
      <div className="glass-card p-6 rounded-2xl border border-slate-800 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h3 className="text-base font-bold text-white flex items-center space-x-2">
              <TrendingUp className="w-5 h-5 text-sky-400" />
              <span>16-Week Longitudinal Performance Trajectory</span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Weekly attendance rate %, cumulative assessment marks %, and assignment completion
            </p>
          </div>
          <div className="flex items-center space-x-4 text-xs font-mono">
            <span className="flex items-center space-x-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-400"></span>
              <span className="text-slate-300">Attendance %</span>
            </span>
            <span className="flex items-center space-x-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-sky-400"></span>
              <span className="text-slate-300">Scores %</span>
            </span>
            <span className="flex items-center space-x-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-purple-400"></span>
              <span className="text-slate-300">Submissions %</span>
            </span>
          </div>
        </div>

        <div className="h-72 w-full pt-4">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={weeklyTrends}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.4} />
              <XAxis dataKey="week" stroke="#94a3b8" fontSize={12} />
              <YAxis domain={[0, 100]} stroke="#94a3b8" fontSize={12} />
              <RechartsTooltip 
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px', color: '#fff', fontSize: '12px' }}
              />
              <Line 
                type="monotone" 
                dataKey="attendance_pct" 
                name="Attendance %" 
                stroke="#10b981" 
                strokeWidth={2.5} 
                dot={{ r: 3 }} 
              />
              <Line 
                type="monotone" 
                dataKey="score_avg" 
                name="Score Avg %" 
                stroke="#38bdf8" 
                strokeWidth={2.5} 
                dot={{ r: 3 }} 
              />
              <Line 
                type="monotone" 
                dataKey="submission_pct" 
                name="Submissions %" 
                stroke="#a855f7" 
                strokeWidth={2} 
                strokeDasharray="4 4" 
                dot={{ r: 2 }} 
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Scoped AI Academic Advisor Chatbot */}
      <div className="glass-card rounded-2xl border border-slate-800 overflow-hidden">
        
        {/* Chat Header */}
        <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-900/60">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-sky-500 to-indigo-600 flex items-center justify-center shadow-md">
              <MessageSquare className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-sm font-bold text-white">Scoped AI Academic Advisor</h3>
                <span className="px-2 py-0.5 text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded-full">
                  Strictly Grounded
                </span>
              </div>
              <p className="text-[11px] text-slate-400">
                Answers questions exclusively regarding your weekly academic metrics and risk factors
              </p>
            </div>
          </div>
        </div>

        {/* Quick Question Pills */}
        <div className="p-3 bg-slate-950/40 border-b border-slate-800/80 flex flex-wrap gap-2">
          {sampleQuestions.map((q, idx) => (
            <button
              key={idx}
              onClick={() => handleSendMessage(q)}
              className="px-3 py-1.5 rounded-lg bg-slate-800/90 hover:bg-slate-750 text-slate-300 hover:text-sky-300 border border-slate-700/80 text-[11px] font-medium transition-colors"
            >
              {q}
            </button>
          ))}
        </div>

        {/* Messages List */}
        <div className="p-4 space-y-3 max-h-80 overflow-y-auto">
          {messages.map((m, idx) => (
            <div
              key={idx}
              className={`flex items-start space-x-2.5 ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {m.sender === 'ai' && (
                <div className="w-7 h-7 rounded-lg bg-sky-600 flex items-center justify-center shrink-0 mt-0.5">
                  <BrainCircuit className="w-4 h-4 text-white" />
                </div>
              )}
              <div className={`p-3.5 rounded-2xl max-w-lg text-xs leading-relaxed ${
                m.sender === 'user'
                  ? 'bg-sky-600 text-white rounded-tr-none'
                  : 'bg-slate-900 border border-slate-800 text-slate-200 rounded-tl-none whitespace-pre-line'
              }`}>
                {m.text}
              </div>
            </div>
          ))}
          {isSending && (
            <div className="flex items-center space-x-2 text-xs text-slate-400">
              <span className="inline-block w-2 h-2 rounded-full bg-sky-400 animate-pulse"></span>
              <span>Advisor analyzing sequence data...</span>
            </div>
          )}
        </div>

        {/* Chat Input Bar */}
        <div className="p-3 bg-slate-900/60 border-t border-slate-800 flex items-center space-x-2">
          <input
            type="text"
            value={chatInput}
            onChange={(e) => setChatInput(e.target.value)}
            onKeyDown={(e) => { if (e.key === 'Enter') handleSendMessage(); }}
            placeholder="Ask your advisor about your attendance, score drops, or recommendations..."
            className="flex-1 px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-700 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-sky-500"
          />
          <button
            onClick={() => handleSendMessage()}
            disabled={isSending || !chatInput.trim()}
            className="p-2.5 rounded-xl bg-sky-500 hover:bg-sky-400 disabled:opacity-50 text-white shadow-lg shadow-sky-500/20 transition-colors"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>

      </div>

    </div>
  );
}
