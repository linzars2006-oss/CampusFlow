import React, { useState, useEffect } from 'react';
import { 
  AlertCircle, 
  CheckCircle, 
  Clock, 
  BrainCircuit, 
  Search, 
  Plus, 
  ChevronRight, 
  X, 
  FileText, 
  UserCheck, 
  Sparkles,
  BookOpen,
  Send,
  HelpCircle
} from 'lucide-react';

export default function FacultyDashboard({ apiBase, currentUser }) {
  const [activeTab, setActiveTab] = useState('risk');
  const [students, setStudents] = useState([]);
  const [predictions, setPredictions] = useState([]);
  const [selectedSubject, setSelectedSubject] = useState(1);
  const [loading, setLoading] = useState(true);

  // Attendance states
  const [attendanceWeek, setAttendanceWeek] = useState(1);
  const [attendanceRoster, setAttendanceRoster] = useState({});
  const [attendanceSavedMsg, setAttendanceSavedMsg] = useState('');

  // Explainability drawer
  const [selectedStudentForExplain, setSelectedStudentForExplain] = useState(null);

  // Intervention modal
  const [showInterventionModal, setShowInterventionModal] = useState(false);
  const [interventionStudent, setInterventionStudent] = useState(null);
  const [interventionNote, setInterventionNote] = useState('');
  const [interventionList, setInterventionList] = useState([]);

  useEffect(() => {
    fetchFacultyData();
  }, [selectedSubject]);

  const fetchFacultyData = async () => {
    setLoading(true);
    try {
      const [predRes, stuRes, intRes] = await Promise.all([
        fetch(`${apiBase}/faculty/risk-dashboard/?subject_id=${selectedSubject}`),
        fetch(`${apiBase}/students/`),
        fetch(`${apiBase}/interventions/`)
      ]);

      if (predRes.ok) setPredictions(await predRes.json());
      if (stuRes.ok) {
        const sData = await stuRes.json();
        setStudents(sData);
        // Initialize attendance roster as all present
        const initialRoster = {};
        sData.forEach(s => { initialRoster[s.id] = 'present'; });
        setAttendanceRoster(initialRoster);
      }
      if (intRes.ok) setInterventionList(await intRes.json());
    } catch (err) {
      console.error("Error fetching faculty data:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleAttendance = (studentId) => {
    setAttendanceRoster(prev => ({
      ...prev,
      [studentId]: prev[studentId] === 'present' ? 'absent' : 'present'
    }));
  };

  const handleMarkAllPresent = () => {
    const updated = {};
    students.forEach(s => { updated[s.id] = 'present'; });
    setAttendanceRoster(updated);
  };

  const handleSaveAttendance = async () => {
    const records = Object.entries(attendanceRoster).map(([sId, status]) => ({
      student_id: parseInt(sId),
      status: status
    }));

    try {
      const res = await fetch(`${apiBase}/attendance/bulk/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          subject_id: selectedSubject,
          week_number: attendanceWeek,
          records: records
        })
      });
      if (res.ok) {
        setAttendanceSavedMsg(`Attendance for Week ${attendanceWeek} saved and synced to Atlas!`);
        setTimeout(() => setAttendanceSavedMsg(''), 3000);
      }
    } catch (err) {
      alert("Error saving attendance: " + err.message);
    }
  };

  const handleSaveIntervention = async (e) => {
    e.preventDefault();
    if (!interventionNote || !interventionStudent) return;

    try {
      const res = await fetch(`${apiBase}/interventions/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          student: interventionStudent.id,
          faculty: currentUser?.faculty_id || 1,
          note: interventionNote
        })
      });
      if (res.ok) {
        setShowInterventionModal(false);
        setInterventionNote('');
        fetchFacultyData();
      }
    } catch (err) {
      alert("Error saving remark");
    }
  };

  const getRiskBadge = (level) => {
    const l = level?.toLowerCase();
    if (l === 'high') {
      return <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-500/15 text-rose-400 border border-rose-500/30">High Risk</span>;
    } else if (l === 'medium') {
      return <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-500/15 text-amber-400 border border-amber-500/30">Medium Risk</span>;
    }
    return <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">Low Risk</span>;
  };

  const getModelBadge = (model) => {
    const m = model?.toLowerCase();
    if (m === 'dl' || m?.includes('lstm')) {
      return <span className="px-2 py-0.5 rounded text-[10px] font-mono font-medium bg-sky-500/10 text-sky-400 border border-sky-500/20">LSTM (Deep Learning)</span>;
    } else if (m === 'ml' || m?.includes('xgboost')) {
      return <span className="px-2 py-0.5 rounded text-[10px] font-mono font-medium bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">XGBoost (Classical)</span>;
    }
    return <span className="px-2 py-0.5 rounded text-[10px] font-mono font-medium bg-slate-700 text-slate-300">Rule-Based</span>;
  };

  return (
    <div className="space-y-6 animate-fade-in">
      
      {/* Top Banner with Subject Picker */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-6 rounded-2xl bg-gradient-to-r from-slate-900 via-slate-900 to-indigo-950/30 border border-slate-800">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Faculty Academic Command Center</h1>
          <p className="text-sm text-slate-400 mt-1">
            Weekly continuous evaluation, attendance tracking, and early risk detection powered by Sequential LSTM.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <label className="text-xs text-slate-400 font-medium">Subject:</label>
          <select 
            value={selectedSubject}
            onChange={(e) => setSelectedSubject(parseInt(e.target.value))}
            className="px-3 py-2 rounded-xl bg-slate-800 border border-slate-700 text-xs font-semibold text-white focus:outline-none focus:border-sky-500"
          >
            <option value={1}>CS101 - Data Structures & Algorithms</option>
            <option value={2}>CS102 - Database Management Systems</option>
            <option value={3}>CS103 - Artificial Intelligence & ML</option>
          </select>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex items-center space-x-2 border-b border-slate-800 pb-2">
        <button
          onClick={() => setActiveTab('risk')}
          className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
            activeTab === 'risk'
              ? 'bg-sky-500/15 text-sky-400 border border-sky-500/30 shadow-sm'
              : 'text-slate-400 hover:text-white hover:bg-slate-900'
          }`}
        >
          <BrainCircuit className="w-4 h-4" />
          <span>Academic Risk Intelligence Table</span>
        </button>

        <button
          onClick={() => setActiveTab('attendance')}
          className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
            activeTab === 'attendance'
              ? 'bg-sky-500/15 text-sky-400 border border-sky-500/30 shadow-sm'
              : 'text-slate-400 hover:text-white hover:bg-slate-900'
          }`}
        >
          <UserCheck className="w-4 h-4" />
          <span>Weekly Attendance (Bulk)</span>
        </button>

        <button
          onClick={() => setActiveTab('interventions')}
          className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
            activeTab === 'interventions'
              ? 'bg-sky-500/15 text-sky-400 border border-sky-500/30 shadow-sm'
              : 'text-slate-400 hover:text-white hover:bg-slate-900'
          }`}
        >
          <FileText className="w-4 h-4" />
          <span>Intervention Logs ({interventionList.length})</span>
        </button>
      </div>

      {/* Tab 1: Risk Intelligence Table */}
      {activeTab === 'risk' && (
        <div className="glass-card rounded-2xl border border-slate-800 overflow-hidden">
          <div className="p-5 border-b border-slate-800 flex items-center justify-between">
            <div>
              <h3 className="text-sm font-semibold text-white">Student Risk Trajectory Roster</h3>
              <p className="text-xs text-slate-400">Sequential evaluation across 16 weeks showing model attribution</p>
            </div>
            <div className="text-xs text-slate-400">
              Total Monitored: <span className="font-bold text-white">{predictions.length || students.length}</span>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-900/80 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
                <tr>
                  <th className="py-3.5 px-4">Student</th>
                  <th className="py-3.5 px-4">Class</th>
                  <th className="py-3.5 px-4">Model Used</th>
                  <th className="py-3.5 px-4">Predicted Risk</th>
                  <th className="py-3.5 px-4">Confidence</th>
                  <th className="py-3.5 px-4">Primary Factors (SHAP/Attn)</th>
                  <th className="py-3.5 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {predictions.length === 0 ? (
                  <tr>
                    <td colSpan="7" className="text-center py-8 text-slate-500">
                      No prediction records available yet.
                    </td>
                  </tr>
                ) : (
                  predictions.map((p) => {
                    const topF = p.top_factors || [];
                    return (
                      <tr key={p.id} className="hover:bg-slate-800/40 transition-colors">
                        <td className="py-3.5 px-4">
                          <div className="font-medium text-white">{p.student_name}</div>
                          <div className="text-[11px] font-mono text-slate-400">{p.roll_no}</div>
                        </td>
                        <td className="py-3.5 px-4 text-slate-400">CSE-A</td>
                        <td className="py-3.5 px-4">{getModelBadge(p.model_used)}</td>
                        <td className="py-3.5 px-4">{getRiskBadge(p.risk_level)}</td>
                        <td className="py-3.5 px-4 font-mono font-semibold">
                          {(p.confidence_score * 100).toFixed(1)}%
                        </td>
                        <td className="py-3.5 px-4 max-w-xs truncate">
                          {topF.length > 0 ? (
                            <span className="text-slate-300 text-[11px]">
                              {topF[0]?.label || topF[0]?.feature}
                            </span>
                          ) : (
                            <span className="text-slate-500">Normal metrics</span>
                          )}
                        </td>
                        <td className="py-3.5 px-4 text-right space-x-2">
                          <button
                            onClick={() => setSelectedStudentForExplain(p)}
                            className="px-2.5 py-1.5 rounded-lg bg-sky-500/10 hover:bg-sky-500/20 text-sky-400 border border-sky-500/20 text-xs font-medium transition-all"
                          >
                            Explain Factors
                          </button>
                          <button
                            onClick={() => {
                              setInterventionStudent({ id: p.student, name: p.student_name });
                              setShowInterventionModal(true);
                            }}
                            className="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 text-xs font-medium transition-all"
                          >
                            + Remark
                          </button>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab 2: Bulk Attendance Marker */}
      {activeTab === 'attendance' && (
        <div className="glass-card p-6 rounded-2xl border border-slate-800 space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h3 className="text-base font-bold text-white">Bulk Weekly Class Attendance Marker</h3>
              <p className="text-xs text-slate-400 mt-1">
                Toggle present/absent for each student in the course roster.
              </p>
            </div>

            <div className="flex items-center space-x-3">
              <span className="text-xs text-slate-400">Week:</span>
              <select
                value={attendanceWeek}
                onChange={(e) => setAttendanceWeek(parseInt(e.target.value))}
                className="px-3 py-1.5 rounded-xl bg-slate-800 border border-slate-700 text-xs font-bold text-sky-400"
              >
                {Array.from({ length: 16 }, (_, i) => i + 1).map(w => (
                  <option key={w} value={w}>Week {w}</option>
                ))}
              </select>

              <button
                onClick={handleMarkAllPresent}
                className="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold"
              >
                Mark All Present
              </button>

              <button
                onClick={handleSaveAttendance}
                className="px-4 py-1.5 rounded-xl bg-sky-500 hover:bg-sky-400 text-white text-xs font-bold shadow-lg shadow-sky-500/25"
              >
                Save Attendance
              </button>
            </div>
          </div>

          {attendanceSavedMsg && (
            <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold flex items-center space-x-2">
              <CheckCircle className="w-4 h-4" />
              <span>{attendanceSavedMsg}</span>
            </div>
          )}

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
            {students.map(s => {
              const isPresent = attendanceRoster[s.id] === 'present';
              return (
                <div
                  key={s.id}
                  onClick={() => handleToggleAttendance(s.id)}
                  className={`p-3.5 rounded-xl border cursor-pointer transition-all flex items-center justify-between ${
                    isPresent
                      ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
                      : 'bg-rose-500/10 border-rose-500/30 text-rose-300'
                  }`}
                >
                  <div>
                    <div className="font-medium text-xs text-white">{s.name}</div>
                    <div className="text-[10px] font-mono text-slate-400">{s.roll_no}</div>
                  </div>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                    isPresent ? 'bg-emerald-500/20 text-emerald-300' : 'bg-rose-500/20 text-rose-300'
                  }`}>
                    {isPresent ? 'Present' : 'Absent'}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Tab 3: Intervention History */}
      {activeTab === 'interventions' && (
        <div className="glass-card p-6 rounded-2xl border border-slate-800 space-y-4">
          <h3 className="text-base font-bold text-white">Documented Faculty Interventions & Advising Notes</h3>
          <p className="text-xs text-slate-400">
            Immutable audit record of support meetings and mentoring interventions.
          </p>

          <div className="space-y-3 mt-4">
            {interventionList.length === 0 ? (
              <p className="text-xs text-slate-500 py-6 text-center">No intervention remarks recorded yet.</p>
            ) : (
              interventionList.map(int => (
                <div key={int.id} className="p-4 rounded-xl bg-slate-900 border border-slate-800 text-xs">
                  <div className="flex justify-between items-center mb-1">
                    <span className="font-bold text-white">{int.student_name}</span>
                    <span className="text-[11px] text-slate-500 font-mono">
                      {new Date(int.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  <p className="text-slate-300 mt-1">{int.note}</p>
                  <p className="text-[10px] text-sky-400 mt-2 font-medium">Logged by: {int.faculty_name}</p>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Explainability Slide-out Modal */}
      {selectedStudentForExplain && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4">
          <div className="w-full max-w-xl rounded-2xl bg-slate-900 border border-slate-700 p-6 shadow-2xl animate-scale-up max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-start mb-4 border-b border-slate-800 pb-3">
              <div>
                <div className="flex items-center space-x-2">
                  <h3 className="text-base font-bold text-white">{selectedStudentForExplain.student_name}</h3>
                  <span className="text-xs font-mono text-sky-400">[{selectedStudentForExplain.roll_no}]</span>
                </div>
                <p className="text-xs text-slate-400 mt-0.5">Sequential Risk Attribution & SHAP/Attention Decomposition</p>
              </div>
              <button 
                onClick={() => setSelectedStudentForExplain(null)}
                className="text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4 text-xs">
              
              {/* Risk Level Badge & Model Tag */}
              <div className="flex items-center justify-between p-3.5 rounded-xl bg-slate-800/80 border border-slate-700">
                <div>
                  <span className="text-slate-400">Overall Assigned Status:</span>
                  <div className="mt-1">{getRiskBadge(selectedStudentForExplain.risk_level)}</div>
                </div>
                <div className="text-right">
                  <span className="text-slate-400">Model Evaluator:</span>
                  <div className="mt-1">{getModelBadge(selectedStudentForExplain.model_used)}</div>
                </div>
              </div>

              {/* Primary Contributing Factors */}
              <div>
                <h4 className="font-semibold text-white mb-2 flex items-center space-x-1.5">
                  <Sparkles className="w-4 h-4 text-sky-400" />
                  <span>Key Contributing Adverse Factors (Ranked)</span>
                </h4>

                <div className="space-y-2">
                  {(selectedStudentForExplain.top_factors || []).map((f, i) => (
                    <div key={i} className="p-3 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-between">
                      <div>
                        <div className="font-medium text-slate-200">{f.label || f.feature}</div>
                        <div className="text-[10px] text-slate-400 font-mono">Factor ID: {f.feature}</div>
                      </div>
                      <div className="text-right">
                        <span className="text-xs font-bold text-amber-400">
                          {(f.impact_score * 100).toFixed(1)}%
                        </span>
                        <div className="text-[10px] text-slate-500">Impact Weight</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Matched Recommendations */}
              <div>
                <h4 className="font-semibold text-white mb-2">Prescriptive Pedagogical Recommendations</h4>
                <div className="p-3.5 rounded-xl bg-sky-500/10 border border-sky-500/20 text-sky-200 leading-relaxed">
                  {selectedStudentForExplain.recommendations?.length > 0 ? (
                    selectedStudentForExplain.recommendations.map((r, i) => (
                      <p key={i} className="mb-1">
                        • {r.recommendation_text}
                      </p>
                    ))
                  ) : (
                    <p>• Schedule a review session to review midterm assessment concepts.</p>
                  )}
                </div>
              </div>

              <div className="pt-2 flex justify-end">
                <button
                  onClick={() => setSelectedStudentForExplain(null)}
                  className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-medium"
                >
                  Close Explanation
                </button>
              </div>

            </div>
          </div>
        </div>
      )}

      {/* Intervention Modal */}
      {showInterventionModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4">
          <div className="w-full max-w-md rounded-2xl bg-slate-900 border border-slate-700 p-6 shadow-2xl">
            <div className="flex justify-between items-center mb-3">
              <h3 className="text-base font-bold text-white">Document Intervention Remark</h3>
              <button onClick={() => setShowInterventionModal(false)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>
            <p className="text-xs text-slate-400 mb-3">
              Logging remark for <strong className="text-white">{interventionStudent?.name}</strong>.
            </p>

            <form onSubmit={handleSaveIntervention} className="space-y-4 text-xs">
              <textarea
                required
                rows={4}
                value={interventionNote}
                onChange={(e) => setInterventionNote(e.target.value)}
                placeholder="Detail the discussion, agreed action items, or special circumstances (e.g. medical leave, extra mentoring)..."
                className="w-full p-3 rounded-xl bg-slate-800 border border-slate-700 text-white focus:outline-none focus:border-sky-500"
              />

              <div className="flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowInterventionModal(false)}
                  className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-sky-500 hover:bg-sky-400 text-white font-semibold shadow-lg shadow-sky-500/25"
                >
                  Save Remark
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}
