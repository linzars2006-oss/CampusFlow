import React, { useState, useEffect } from 'react';
import { 
  Users, 
  UserCheck, 
  BookOpen, 
  TrendingUp, 
  AlertTriangle, 
  Upload, 
  Plus, 
  Trash2, 
  Search, 
  CheckCircle2, 
  FileSpreadsheet,
  X,
  Sparkles
} from 'lucide-react';
import { 
  PieChart, 
  Pie, 
  Cell, 
  ResponsiveContainer, 
  Tooltip as RechartsTooltip, 
  Legend,
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid 
} from 'recharts';

export default function AdminDashboard({ apiBase }) {
  const [analytics, setAnalytics] = useState(null);
  const [students, setStudents] = useState([]);
  const [faculty, setFaculty] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);

  // Modals
  const [showAddModal, setShowAddModal] = useState(false);
  const [showImportModal, setShowImportModal] = useState(false);
  const [newStudent, setNewStudent] = useState({
    name: '',
    roll_no: '',
    class_name: 'CSE-A',
    section: '1',
    prev_gpa: 8.0,
    email: ''
  });
  const [csvFile, setCsvFile] = useState(null);
  const [importStatus, setImportStatus] = useState('');

  useEffect(() => {
    fetchAdminData();
  }, []);

  const fetchAdminData = async () => {
    setLoading(true);
    try {
      const [anaRes, stuRes, facRes, subRes] = await Promise.all([
        fetch(`${apiBase}/admin/analytics/`),
        fetch(`${apiBase}/students/`),
        fetch(`${apiBase}/faculty/`),
        fetch(`${apiBase}/subjects/`)
      ]);

      if (anaRes.ok) setAnalytics(await anaRes.json());
      if (stuRes.ok) setStudents(await stuRes.json());
      if (facRes.ok) setFaculty(await facRes.json());
      if (subRes.ok) setSubjects(await subRes.json());
    } catch (err) {
      console.error("Error fetching admin data:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddStudent = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`${apiBase}/students/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newStudent)
      });
      if (res.ok) {
        setShowAddModal(false);
        setNewStudent({ name: '', roll_no: '', class_name: 'CSE-A', section: '1', prev_gpa: 8.0, email: '' });
        fetchAdminData();
      } else {
        alert("Failed to create student record");
      }
    } catch (err) {
      alert("Error adding student: " + err.message);
    }
  };

  const handleDeleteStudent = async (id) => {
    if (!window.confirm("Are you sure you want to remove this student record?")) return;
    try {
      const res = await fetch(`${apiBase}/students/${id}/`, { method: 'DELETE' });
      if (res.ok) {
        setStudents(students.filter(s => s.id !== id));
      }
    } catch (err) {
      alert("Error deleting student");
    }
  };

  const handleBulkImport = async (e) => {
    e.preventDefault();
    if (!csvFile) return alert("Please select a CSV file");

    const formData = new FormData();
    formData.append('file', csvFile);
    setImportStatus('Uploading and synchronizing with MongoDB Atlas...');

    try {
      const res = await fetch(`${apiBase}/admin/bulk-import/`, {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      if (res.ok) {
        setImportStatus(`Success! ${data.count} student records processed.`);
        setTimeout(() => {
          setShowImportModal(false);
          setImportStatus('');
          setCsvFile(null);
          fetchAdminData();
        }, 1500);
      } else {
        setImportStatus('Import failed: ' + (data.error || 'Server error'));
      }
    } catch (err) {
      setImportStatus('Import error: ' + err.message);
    }
  };

  const filteredStudents = students.filter(s => 
    s.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    s.roll_no?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    s.class_name?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-8 animate-fade-in">
      
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 rounded-2xl bg-gradient-to-r from-slate-900 via-slate-900 to-sky-950/40 border border-slate-800">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Institutional Operations & Analytics</h1>
          <p className="text-sm text-slate-400 mt-1">
            Global cohort surveillance, batch student provisioning, and continuous academic risk monitoring.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowImportModal(true)}
            className="flex items-center space-x-2 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-semibold shadow-sm transition-all"
          >
            <Upload className="w-4 h-4 text-sky-400" />
            <span>Bulk CSV Import</span>
          </button>
          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center space-x-2 px-4 py-2 rounded-xl bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 text-white text-xs font-semibold shadow-lg shadow-sky-500/25 transition-all"
          >
            <Plus className="w-4 h-4" />
            <span>Add Student</span>
          </button>
        </div>
      </div>

      {/* Analytics KPI Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        
        <div className="glass-card p-5 rounded-2xl relative overflow-hidden">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">Total Enrolled</p>
              <p className="text-2xl font-bold text-white mt-1">{analytics?.total_students || students.length}</p>
              <p className="text-[11px] text-emerald-400 mt-1 font-medium">✓ Active Cohort</p>
            </div>
            <div className="p-3 rounded-xl bg-sky-500/10 text-sky-400 border border-sky-500/20">
              <Users className="w-5 h-5" />
            </div>
          </div>
        </div>

        <div className="glass-card p-5 rounded-2xl relative overflow-hidden">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">Faculty & Mentors</p>
              <p className="text-2xl font-bold text-white mt-1">{analytics?.total_faculty || faculty.length}</p>
              <p className="text-[11px] text-slate-400 mt-1">Across 4 Departments</p>
            </div>
            <div className="p-3 rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              <UserCheck className="w-5 h-5" />
            </div>
          </div>
        </div>

        <div className="glass-card p-5 rounded-2xl relative overflow-hidden">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">Cohort Attendance</p>
              <p className="text-2xl font-bold text-emerald-400 mt-1">{analytics?.overall_attendance_rate || 86.4}%</p>
              <p className="text-[11px] text-slate-400 mt-1">Institution Threshold: 75%</p>
            </div>
            <div className="p-3 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <CheckCircle2 className="w-5 h-5" />
            </div>
          </div>
        </div>

        <div className="glass-card p-5 rounded-2xl relative overflow-hidden">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">Avg Cumulative Score</p>
              <p className="text-2xl font-bold text-white mt-1">{analytics?.average_score || 74.2}%</p>
              <p className="text-[11px] text-sky-400 mt-1">16-Week Continuous Tests</p>
            </div>
            <div className="p-3 rounded-xl bg-purple-500/10 text-purple-400 border border-purple-500/20">
              <TrendingUp className="w-5 h-5" />
            </div>
          </div>
        </div>

      </div>

      {/* Analytics Recharts Visualizers */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Risk Breakdown Pie Chart */}
        <div className="glass-card p-6 rounded-2xl border border-slate-800">
          <h3 className="text-sm font-semibold text-white mb-1 flex items-center space-x-2">
            <AlertTriangle className="w-4 h-4 text-amber-400" />
            <span>Multi-Tier Academic Risk Distribution</span>
          </h3>
          <p className="text-xs text-slate-400 mb-4">Classified via Deep Learning LSTM & Baselines</p>

          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={analytics?.risk_distribution || [
                    { name: "Low Risk", value: 14, color: "#10b981" },
                    { name: "Medium Risk", value: 5, color: "#f59e0b" },
                    { name: "High Risk", value: 3, color: "#ef4444" }
                  ]}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={80}
                  paddingAngle={5}
                >
                  {(analytics?.risk_distribution || [
                    { color: "#10b981" },
                    { color: "#f59e0b" },
                    { color: "#ef4444" }
                  ]).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <RechartsTooltip 
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Class Breakdown Bar Chart */}
        <div className="lg:col-span-2 glass-card p-6 rounded-2xl border border-slate-800">
          <h3 className="text-sm font-semibold text-white mb-1 flex items-center space-x-2">
            <BookOpen className="w-4 h-4 text-sky-400" />
            <span>Class-wise Student Enrollment</span>
          </h3>
          <p className="text-xs text-slate-400 mb-4">Distribution across active sections</p>

          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={analytics?.class_breakdown || [
                { class_name: "CSE-A", student_count: 12 },
                { class_name: "CSE-B", student_count: 8 }
              ]}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.5} />
                <XAxis dataKey="class_name" stroke="#94a3b8" fontSize={12} />
                <YAxis stroke="#94a3b8" fontSize={12} />
                <RechartsTooltip 
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                />
                <Bar dataKey="student_count" fill="#38bdf8" radius={[6, 6, 0, 0]} barSize={40} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>

      {/* Student Management Table */}
      <div className="glass-card rounded-2xl border border-slate-800 overflow-hidden">
        
        <div className="p-5 border-b border-slate-800/80 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h3 className="text-base font-semibold text-white">Enrolled Students Directory</h3>
            <p className="text-xs text-slate-400">Live roster synchronized with MongoDB Atlas cluster</p>
          </div>
          
          <div className="relative w-full sm:w-64">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search student or roll..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-1.5 rounded-xl bg-slate-900 border border-slate-700 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-sky-500"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/80 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
              <tr>
                <th className="py-3.5 px-4">Roll No</th>
                <th className="py-3.5 px-4">Name</th>
                <th className="py-3.5 px-4">Class / Section</th>
                <th className="py-3.5 px-4">Prior GPA</th>
                <th className="py-3.5 px-4">Email</th>
                <th className="py-3.5 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {filteredStudents.length === 0 ? (
                <tr>
                  <td colSpan="6" className="text-center py-8 text-slate-500">
                    No students match your query.
                  </td>
                </tr>
              ) : (
                filteredStudents.map((s) => (
                  <tr key={s.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3 px-4 font-mono font-semibold text-sky-400">{s.roll_no}</td>
                    <td className="py-3 px-4 font-medium text-white">{s.name}</td>
                    <td className="py-3 px-4">
                      <span className="px-2 py-0.5 rounded-md bg-slate-800 text-slate-300 text-[11px] font-mono">
                        {s.class_name} • Sec {s.section}
                      </span>
                    </td>
                    <td className="py-3 px-4 font-semibold text-emerald-400">{s.prev_gpa} / 10</td>
                    <td className="py-3 px-4 text-slate-400">{s.email || `${s.roll_no?.toLowerCase()}@smartedu.edu`}</td>
                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={() => handleDeleteStudent(s.id)}
                        className="p-1.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
                        title="Delete Student"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

      </div>

      {/* Add Student Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="w-full max-w-md rounded-2xl bg-slate-900 border border-slate-700 p-6 shadow-2xl animate-scale-up">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-base font-bold text-white">Enroll New Student</h3>
              <button onClick={() => setShowAddModal(false)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>
            <form onSubmit={handleAddStudent} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-400 mb-1">Student Full Name</label>
                <input
                  type="text"
                  required
                  value={newStudent.name}
                  onChange={(e) => setNewStudent({...newStudent, name: e.target.value})}
                  placeholder="e.g. Aditi Sharma"
                  className="w-full p-2.5 rounded-xl bg-slate-800 border border-slate-700 text-white focus:outline-none focus:border-sky-500"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 mb-1">Roll Number</label>
                  <input
                    type="text"
                    required
                    value={newStudent.roll_no}
                    onChange={(e) => setNewStudent({...newStudent, roll_no: e.target.value})}
                    placeholder="e.g. 23CS015"
                    className="w-full p-2.5 rounded-xl bg-slate-800 border border-slate-700 text-white focus:outline-none focus:border-sky-500"
                  />
                </div>
                <div>
                  <label className="block text-slate-400 mb-1">Prior GPA (0-10)</label>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    max="10"
                    required
                    value={newStudent.prev_gpa}
                    onChange={(e) => setNewStudent({...newStudent, prev_gpa: parseFloat(e.target.value)})}
                    className="w-full p-2.5 rounded-xl bg-slate-800 border border-slate-700 text-white focus:outline-none focus:border-sky-500"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 mb-1">Class / Branch</label>
                  <select
                    value={newStudent.class_name}
                    onChange={(e) => setNewStudent({...newStudent, class_name: e.target.value})}
                    className="w-full p-2.5 rounded-xl bg-slate-800 border border-slate-700 text-white focus:outline-none focus:border-sky-500"
                  >
                    <option value="CSE-A">CSE-A</option>
                    <option value="CSE-B">CSE-B</option>
                  </select>
                </div>
                <div>
                  <label className="block text-slate-400 mb-1">Section</label>
                  <input
                    type="text"
                    value={newStudent.section}
                    onChange={(e) => setNewStudent({...newStudent, section: e.target.value})}
                    className="w-full p-2.5 rounded-xl bg-slate-800 border border-slate-700 text-white focus:outline-none focus:border-sky-500"
                  />
                </div>
              </div>
              <div>
                <label className="block text-slate-400 mb-1">Institutional Email</label>
                <input
                  type="email"
                  value={newStudent.email}
                  onChange={(e) => setNewStudent({...newStudent, email: e.target.value})}
                  placeholder="e.g. aditi.sharma@smartedu.edu"
                  className="w-full p-2.5 rounded-xl bg-slate-800 border border-slate-700 text-white focus:outline-none focus:border-sky-500"
                />
              </div>
              <div className="pt-2 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-sky-500 hover:bg-sky-400 text-white font-semibold shadow-lg shadow-sky-500/25"
                >
                  Save Student
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Bulk CSV Import Modal */}
      {showImportModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="w-full max-w-lg rounded-2xl bg-slate-900 border border-slate-700 p-6 shadow-2xl">
            <div className="flex justify-between items-center mb-4">
              <div className="flex items-center space-x-2">
                <FileSpreadsheet className="w-5 h-5 text-sky-400" />
                <h3 className="text-base font-bold text-white">Bulk Student CSV Import</h3>
              </div>
              <button onClick={() => setShowImportModal(false)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <p className="text-xs text-slate-400 mb-4">
              Upload a CSV file containing columns: <code className="text-sky-300 font-mono">roll_no, name, class_name, section, prev_gpa, email</code>.
              Records are automatically synced to the MongoDB Atlas cluster.
            </p>

            <form onSubmit={handleBulkImport} className="space-y-4 text-xs">
              <div className="border-2 border-dashed border-slate-700 hover:border-sky-500 rounded-2xl p-6 text-center transition-colors">
                <Upload className="w-8 h-8 text-slate-500 mx-auto mb-2" />
                <label className="cursor-pointer font-medium text-sky-400 hover:text-sky-300">
                  <span>Choose CSV file</span>
                  <input
                    type="file"
                    accept=".csv"
                    onChange={(e) => setCsvFile(e.target.files[0])}
                    className="hidden"
                  />
                </label>
                {csvFile && (
                  <p className="text-xs text-emerald-400 mt-2 font-mono">Selected: {csvFile.name}</p>
                )}
              </div>

              {importStatus && (
                <div className="p-3 rounded-xl bg-slate-800 border border-slate-700 text-xs font-mono text-sky-300">
                  {importStatus}
                </div>
              )}

              <div className="pt-2 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowImportModal(false)}
                  className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium"
                >
                  Close
                </button>
                <button
                  type="submit"
                  disabled={!csvFile}
                  className="px-4 py-2 rounded-xl bg-sky-500 hover:bg-sky-400 disabled:opacity-50 text-white font-semibold shadow-lg shadow-sky-500/25"
                >
                  Start Import
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}
