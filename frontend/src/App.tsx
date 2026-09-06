import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, Table, FileBarChart, PlayCircle, PhoneCall, CheckCircle2, XCircle, Clock , MessageSquare } from 'lucide-react';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

const API_BASE = "http://localhost:8000/api";

function Sidebar() {
  const location = useLocation();
  const navItems = [
    { name: 'Dashboard', path: '/', dotColor: 'bg-gray-500' },
    { name: 'Data Table', path: '/table', dotColor: 'bg-teal-500' },
    { name: 'Generate Report', path: '/reports', dotColor: 'bg-orange-500' },
    { name: 'Artifacts Archive', path: '/artifacts', dotColor: 'bg-blue-500' },
    { name: 'Email Agent', path: '/email', dotColor: 'bg-green-500' },
  ];

  return (
    <div className="w-64 bg-[#111827] text-slate-300 min-h-screen flex flex-col shadow-xl font-sans">
      <div className="p-6 border-b border-slate-800 flex items-center gap-3">
        <PhoneCall className="text-blue-400" />
        <h1 className="text-xl font-bold tracking-tight text-white">IVR Analytics</h1>
      </div>
      <nav className="flex-1 px-4 py-4 space-y-1">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.name}
              to={item.path}
              className={`flex items-center justify-between px-4 py-3 rounded-xl transition-colors ${
                isActive ? 'bg-[#1F2937] text-white' : 'hover:bg-slate-800 hover:text-white'
              }`}
            >
              <div className="flex items-center gap-3">
                <div className={`w-2.5 h-2.5 rounded-full ${item.dotColor}`}></div>
                <span className="font-medium text-sm">{item.name}</span>
              </div>
              {!isActive && <span className="text-slate-600 text-lg">&rarr;</span>}
            </Link>
          );
        })}
      </nav>
    </div>
  );
}

function StatCard({ title, value, subtitle, icon, color }: any) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex items-start gap-4 transition-all hover:shadow-md">
      <div className={`p-3 rounded-lg ${color}`}>{icon}</div>
      <div>
        <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wider">{title}</h3>
        <p className="text-3xl font-bold text-slate-800 mt-1">{value}</p>
        <p className="text-sm text-slate-400 mt-1">{subtitle}</p>
      </div>
    </div>
  );
}

function Dashboard() {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");

  const loadData = () => {
    setLoading(true);
    const params = new URLSearchParams();
    if (startDate) params.append("start_date", startDate);
    if (endDate) params.append("end_date", endDate);
    
    fetch(`${API_BASE}/analytics?${params.toString()}`)
      .then(res => res.json())
      .then(data => {
        setStats(data);
        setLoading(false);
      });
  };

  useEffect(() => {
    loadData();
  }, [startDate, endDate]);

  if (loading) return <div className="p-8 text-center text-slate-500">Loading analytics...</div>;

  return (
    <div className="p-8 bg-slate-50 min-h-full">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-slate-800">Overview Analytics</h2>
        <div className="flex gap-4 items-center bg-white p-2 rounded-lg border border-slate-200 shadow-sm">
            <span className="text-sm font-medium text-slate-500">Filter by Date:</span>
            <input type="date" value={startDate} onChange={e => setStartDate(e.target.value)} className="text-sm border-slate-200 rounded px-2 py-1 outline-none focus:ring-1 focus:ring-blue-500" />
            <span className="text-slate-400">to</span>
            <input type="date" value={endDate} onChange={e => setEndDate(e.target.value)} className="text-sm border-slate-200 rounded px-2 py-1 outline-none focus:ring-1 focus:ring-blue-500" />
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard 
          title="Total Calls" 
          value={stats.total_calls} 
          subtitle="Processed in dataset"
          icon={<PhoneCall size={24} className="text-blue-600" />}
          color="bg-blue-100"
        />
        <StatCard 
          title="Avg Duration" 
          value={`${stats.avg_duration}s`} 
          subtitle="Average Handle Time"
          icon={<Clock size={24} className="text-indigo-600" />}
          color="bg-indigo-100"
        />
        <StatCard 
          title="Containment" 
          value={`${stats.containment_rate}%`} 
          subtitle="Resolved by IVR"
          icon={<CheckCircle2 size={24} className="text-emerald-600" />}
          color="bg-emerald-100"
        />
        <StatCard 
          title="Abandonment" 
          value={`${stats.abandonment_rate}%`} 
          subtitle="Hung up early"
          icon={<XCircle size={24} className="text-rose-600" />}
          color="bg-rose-100"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
          <h3 className="text-lg font-bold text-slate-800 mb-4">Intent Distribution</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={stats.intent_distribution}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {stats.intent_distribution?.map((_: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="flex flex-wrap gap-4 justify-center mt-4">
            {stats.intent_distribution?.map((entry: any, index: number) => (
              <div key={index} className="flex items-center gap-2 text-sm text-slate-600">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: COLORS[index % COLORS.length] }}></div>
                <span className="capitalize">{entry.name.replace(/_/g, ' ')}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200 flex flex-col justify-center items-center text-center">
            <div className="w-16 h-16 bg-blue-50 text-blue-500 rounded-full flex items-center justify-center mb-4">
               <FileBarChart size={32} />
            </div>
            <h3 className="text-xl font-bold text-slate-800 mb-2">Automated Multi-Agent Reporting</h3>
            <p className="text-slate-500 mb-6 max-w-md">
                Our LangGraph pipeline consists of Table, Analysis, Visualization, and Email agents that work sequentially to ingest data and produce rich reports.
            </p>
            <Link to="/reports" className="px-6 py-2 bg-slate-900 text-white rounded-lg hover:bg-slate-800 transition-colors font-medium">
                View Generated Reports
            </Link>
        </div>
      </div>
    </div>
  );
}

function DataTable() {
  const [records, setRecords] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const pageSize = 10;

  const loadData = () => {
    setLoading(true);
    const params = new URLSearchParams();
    if (startDate) params.append("start_date", startDate);
    if (endDate) params.append("end_date", endDate);
    
    fetch(`${API_BASE}/records?${params.toString()}`)
      .then(res => res.json())
      .then(data => {
        setRecords(data.records);
        setLoading(false);
      });
  };

  useEffect(() => {
    loadData();
  }, [startDate, endDate]);

  const filteredRecords = records.filter(rec => 
    rec.id.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const totalPages = Math.ceil(filteredRecords.length / pageSize);
  const paginatedRecords = filteredRecords.slice(
    (currentPage - 1) * pageSize,
    currentPage * pageSize
  );

  return (
    <div className="p-8 bg-slate-50 min-h-full">
      <div className="flex justify-between items-center mb-6">
        <div className="flex gap-4 items-center">
          <h2 className="text-2xl font-bold text-slate-800">Call Records</h2>
          <div className="flex gap-2 items-center bg-white p-1.5 rounded-lg border border-slate-200 shadow-sm ml-4">
              <input type="date" value={startDate} onChange={e => setStartDate(e.target.value)} className="text-xs border-slate-200 rounded px-2 py-1 outline-none" />
              <span className="text-slate-400 text-xs">to</span>
              <input type="date" value={endDate} onChange={e => setEndDate(e.target.value)} className="text-xs border-slate-200 rounded px-2 py-1 outline-none" />
          </div>
        </div>
        <div className="flex gap-4 items-center">
          <input
            type="text"
            placeholder="Search Call ID..."
            value={searchQuery}
            onChange={e => { setSearchQuery(e.target.value); setCurrentPage(1); }}
            className="px-4 py-2 rounded-lg border border-slate-300 shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
          />
          <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-medium">
            Showing {filteredRecords.length} records
          </span>
        </div>
      </div>
      
      {loading ? (
        <div className="p-8 text-center text-slate-500 bg-white rounded-xl shadow-sm border border-slate-200">Loading data...</div>
      ) : (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-50 text-slate-600 text-sm uppercase tracking-wider">
                  <th className="p-4 border-b border-slate-200 font-semibold">Call ID</th>
                  <th className="p-4 border-b border-slate-200 font-semibold">Timestamp</th>
                  <th className="p-4 border-b border-slate-200 font-semibold">Intent</th>
                  <th className="p-4 border-b border-slate-200 font-semibold">Duration (s)</th>
                  <th className="p-4 border-b border-slate-200 font-semibold">Disposition</th>
                  <th className="p-4 border-b border-slate-200 font-semibold text-center">Fallbacks</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700">
                {paginatedRecords.map((rec, i) => (
                  <tr key={i} className="hover:bg-slate-50 transition-colors">
                    <td className="p-4 font-mono text-xs text-slate-500">{rec.id.substring(0, 8)}...</td>
                    <td className="p-4 whitespace-nowrap">{new Date(rec.timestamp).toLocaleString()}</td>
                    <td className="p-4 capitalize">
                        <span className="px-2 py-1 bg-slate-100 rounded-md text-xs font-medium border border-slate-200">
                            {rec.intent.replace(/_/g, ' ')}
                        </span>
                    </td>
                    <td className="p-4 font-medium">{rec.duration.toFixed(1)}</td>
                    <td className="p-4">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            rec.disposition === 'resolved' ? 'bg-emerald-100 text-emerald-700' :
                            rec.disposition === 'abandoned' ? 'bg-rose-100 text-rose-700' :
                            'bg-amber-100 text-amber-700'
                        }`}>
                            {rec.disposition}
                        </span>
                    </td>
                    <td className="p-4 text-center">
                        {rec.fallback_count > 0 ? (
                            <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-rose-100 text-rose-600 text-xs font-bold">
                                {rec.fallback_count}
                            </span>
                        ) : (
                            <span className="text-slate-300">-</span>
                        )}
                    </td>
                  </tr>
                ))}
                {paginatedRecords.length === 0 && (
                    <tr>
                        <td colSpan={6} className="p-8 text-center text-slate-500">No records found matching your search.</td>
                    </tr>
                )}
              </tbody>
            </table>
          </div>
          {totalPages > 1 && (
            <div className="p-4 border-t border-slate-200 flex justify-center gap-2">
              {Array.from({ length: totalPages }, (_, i) => i + 1).map(page => (
                <button
                  key={page}
                  onClick={() => setCurrentPage(page)}
                  className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                    currentPage === page
                      ? 'bg-blue-600 text-white shadow-sm'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  {page}
                </button>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function Artifacts() {
  const [reports, setReports] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [triggering, setTriggering] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");

  const fetchReports = () => {
    fetch(`${API_BASE}/reports`)
      .then(res => res.json())
      .then(data => {
        setReports(data.reports);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchReports();
    const interval = setInterval(fetchReports, 5000);
    return () => clearInterval(interval);
  }, []);

  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");

  const handleTrigger = async (preset?: string) => {
    setTriggering(true);
    try {
      let sd = startDate;
      let ed = endDate;
      let rType = 'custom';
      
      if (preset === 'daily') {
          const today = new Date().toISOString().split('T')[0];
          sd = today; ed = today; rType = 'daily';
      } else if (preset === 'weekly') {
          const today = new Date();
          const lastWeek = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
          sd = lastWeek.toISOString().split('T')[0];
          ed = today.toISOString().split('T')[0];
          rType = 'weekly';
      } else if (preset === 'monthly') {
          const today = new Date();
          const lastMonth = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000);
          sd = lastMonth.toISOString().split('T')[0];
          ed = today.toISOString().split('T')[0];
          rType = 'monthly';
      }
      
      await fetch(`${API_BASE}/run-pipeline`, { 
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ start_date: sd, end_date: ed, report_type: rType })
      });
      setTimeout(fetchReports, 3000);
    } catch (e) {
      console.error(e);
    } finally {
      setTimeout(() => setTriggering(false), 2000);
    }
  };

  return (
    <div className="p-8 bg-slate-50 min-h-full">
      <div className="flex justify-between items-center mb-8">
        <div>
            <h2 className="text-2xl font-bold text-slate-800">Artifacts Archive</h2>
            <p className="text-slate-500 mt-1">Artifacts produced by the LLM Agents</p>
        </div>
        <div className="w-64">
            <input 
                type="text" 
                placeholder="Search artifacts..." 
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
                className="w-full px-4 py-2 rounded-lg border border-slate-300 shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
            />
        </div>
      </div>

      {loading ? (
        <div className="p-8 text-center text-slate-500 bg-white rounded-xl shadow-sm border border-slate-200">Loading reports...</div>
      ) : reports.length === 0 ? (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-12 text-center flex flex-col items-center">
            <FileBarChart size={48} className="text-slate-300 mb-4" />
            <h3 className="text-lg font-bold text-slate-700 mb-2">No Reports Generated Yet</h3>
            <p className="text-slate-500 mb-6 max-w-md text-center">Trigger the LangGraph pipeline to process call logs, generate narratives with Ollama, and produce charts.</p>
            <button onClick={handleTrigger} className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium transition-colors">
                Trigger Analysis Now
            </button>
        </div>
      ) : (
        <div className="space-y-8">
          {['daily', 'weekly', 'monthly', 'custom', 'other'].map(group => {
              const filtered = reports.filter(r => r.name.toLowerCase().includes(searchQuery.toLowerCase()) || r.type.toLowerCase().includes(searchQuery.toLowerCase()));
              const groupReports = filtered.filter(r => {
                  if (group === 'other') return !r.name.startsWith('daily') && !r.name.startsWith('weekly') && !r.name.startsWith('monthly') && !r.name.startsWith('custom');
                  return r.name.startsWith(group);
              });
              
              if (groupReports.length === 0) return null;
              
              return (
                  <div key={group} className="mb-8">
                      <h3 className="text-xl font-bold text-slate-800 capitalize mb-4 pb-2 border-b border-slate-200">{group} Reports</h3>
                      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
                        {groupReports.map((report, i) => (
                          <div key={i} className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden flex flex-col">
                            <div className="p-4 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
                              <h3 className="font-semibold text-slate-700 flex items-center gap-2">
                                  <FileBarChart size={16} className="text-blue-500" />
                                  {report.name}
                              </h3>
                              <span className="text-xs font-medium px-2 py-1 bg-slate-100 text-slate-600 rounded uppercase">
                                  {report.type}
                              </span>
                            </div>
                            <div className="p-4 flex-1 bg-slate-50/20 flex items-center justify-center">
                              {report.type === 'image' ? (
                                <img src={report.url} alt={report.name} className="max-h-80 object-contain rounded border border-slate-200 shadow-sm" />
                              ) : (
                                <div className="w-full h-80 rounded border border-slate-200 bg-white overflow-hidden shadow-sm">
                                  <iframe src={report.url} className="w-full h-full" title={report.name} />
                                </div>
                              )}
                            </div>
                            <div className="p-4 border-t border-slate-100 flex gap-4">
                              <a href={report.url} target="_blank" rel="noreferrer" className="text-sm font-medium text-blue-600 hover:text-blue-800 hover:underline">
                                Open full size &rarr;
                              </a>
                              <a href={`${API_BASE}/download/${report.name}`} className="text-sm font-medium text-emerald-600 hover:text-emerald-800 hover:underline">
                                Download
                              </a>
                            </div>
                          </div>
                        ))}
                      </div>
                  </div>
              );
          })}
        </div>
      )}
    </div>
  );
}




function GenerateReport() {
  const [startDate, setStartDate] = useState(() => sessionStorage.getItem("gr_startDate") || "");
  const [endDate, setEndDate] = useState(() => sessionStorage.getItem("gr_endDate") || "");
  const [triggering, setTriggering] = useState(() => sessionStorage.getItem("gr_triggering") === "true");
  const [activeReport, setActiveReport] = useState<string | null>(() => sessionStorage.getItem("gr_activeReport"));
  
  // Save to session storage whenever they change
  useEffect(() => { sessionStorage.setItem("gr_startDate", startDate); }, [startDate]);
  useEffect(() => { sessionStorage.setItem("gr_endDate", endDate); }, [endDate]);
  useEffect(() => { sessionStorage.setItem("gr_triggering", triggering.toString()); }, [triggering]);
  useEffect(() => { 
      if (activeReport) sessionStorage.setItem("gr_activeReport", activeReport); 
      else sessionStorage.removeItem("gr_activeReport");
  }, [activeReport]);

  const pollForReport = (expectedFilename: string) => {
      let attempts = 0;
      setTriggering(true);
      const interval = setInterval(async () => {
          attempts++;
          try {
              const res = await fetch(`${API_BASE}/reports`);
              const data = await res.json();
              const checkExists = data.reports.find((r: any) => r.name === expectedFilename);
              
              if (checkExists) {
                  clearInterval(interval);
                  setActiveReport(checkExists.url);
                  setTriggering(false);
                  sessionStorage.removeItem("gr_expectedFilename");
              } else if (attempts >= 45) { // 90 seconds max
                  clearInterval(interval);
                  setActiveReport("error");
                  setTriggering(false);
                  sessionStorage.removeItem("gr_expectedFilename");
              }
          } catch (e) {
              console.error(e);
          }
      }, 2000);
  };

  // Resume polling on mount if we were triggering
  useEffect(() => {
      if (triggering) {
          const expected = sessionStorage.getItem("gr_expectedFilename");
          if (expected) pollForReport(expected);
          else setTriggering(false);
      }
  }, []);

  const handleTrigger = async (preset?: string) => {
    try {
      let sd = startDate;
      let ed = endDate;
      let rType = 'custom';
      
      if (preset === 'daily') {
          const today = new Date().toISOString().split('T')[0];
          sd = today; ed = today; rType = 'daily';
      } else if (preset === 'weekly') {
          const today = new Date();
          const lastWeek = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
          sd = lastWeek.toISOString().split('T')[0];
          ed = today.toISOString().split('T')[0];
          rType = 'weekly';
      } else if (preset === 'monthly') {
          const today = new Date();
          const lastMonth = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000);
          sd = lastMonth.toISOString().split('T')[0];
          ed = today.toISOString().split('T')[0];
          rType = 'monthly';
      }
      
      const getReadableFilename = (rt: string, sd: string) => {
          if (sd === 'all' || !sd) return `${rt.charAt(0).toUpperCase() + rt.slice(1)}_Report_report.html`;
          if (rt === 'daily') return `Daily_${sd}_report.html`;
          
          const [year, month, day] = sd.split('-');
          const d = new Date(parseInt(year), parseInt(month)-1, parseInt(day));
          
          if (rt === 'monthly') {
              const months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
              return `${months[d.getMonth()]}_${d.getFullYear()}_report.html`;
          } else if (rt === 'weekly') {
              const date = new Date(d.getTime());
              date.setHours(0, 0, 0, 0);
              date.setDate(date.getDate() + 3 - (date.getDay() + 6) % 7);
              const week1 = new Date(date.getFullYear(), 0, 4);
              const weekNum = 1 + Math.round(((date.getTime() - week1.getTime()) / 86400000 - 3 + (week1.getDay() + 6) % 7) / 7);
              return `Week_${weekNum}_${date.getFullYear()}_report.html`;
          }
          return `${rt}_${sd}_report.html`;
      };
      
      const expectedFilename = getReadableFilename(rType, sd);
      
      // Check if it already exists
      const res = await fetch(`${API_BASE}/reports`);
      const data = await res.json();
      const exists = data.reports.find((r: any) => r.name === expectedFilename);
      
      if (exists) {
         setActiveReport(exists.url);
         setTriggering(false);
         return;
      }
      
      sessionStorage.setItem("gr_expectedFilename", expectedFilename);
      pollForReport(expectedFilename);
      
      await fetch(`${API_BASE}/run-pipeline`, { 
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ start_date: sd, end_date: ed, report_type: rType })
      });
      
    } catch (e) {
      console.error(e);
      setTriggering(false);
    }
  };

  return (
    <div className="p-8 bg-slate-50 min-h-full flex flex-col">
      <div className="flex justify-between items-center mb-8">
        <div>
            <h2 className="text-2xl font-bold text-slate-800">Generate Report</h2>
            <p className="text-slate-500 mt-1">Select a time period to generate and view analysis.</p>
        </div>
        <div className="flex gap-2 items-center bg-white p-2 rounded-lg border border-slate-200 shadow-sm">
          <input type="date" value={startDate} onChange={e => setStartDate(e.target.value)} className="text-sm border-slate-200 rounded px-2 py-1 outline-none" />
          <span className="text-slate-400 text-sm">to</span>
          <input type="date" value={endDate} onChange={e => setEndDate(e.target.value)} className="text-sm border-slate-200 rounded px-2 py-1 outline-none" />
          <button 
            onClick={() => handleTrigger()}
            disabled={triggering}
            className="flex items-center gap-2 px-4 py-1.5 ml-2 rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-700 shadow-sm transition-all disabled:opacity-50"
          >
            {triggering ? 'Running...' : 'Custom Run'}
          </button>
        </div>
      </div>
      
      <div className="flex gap-4 mb-6 border-b border-slate-200 pb-6">
          <button onClick={() => handleTrigger('daily')} disabled={triggering} className="flex-1 py-4 bg-white border border-slate-200 text-slate-700 rounded-xl hover:bg-blue-50 hover:border-blue-200 hover:text-blue-700 transition-all shadow-sm disabled:opacity-50 font-semibold text-lg flex items-center justify-center gap-2">
            Today
          </button>
          <button onClick={() => handleTrigger('weekly')} disabled={triggering} className="flex-1 py-4 bg-white border border-slate-200 text-slate-700 rounded-xl hover:bg-blue-50 hover:border-blue-200 hover:text-blue-700 transition-all shadow-sm disabled:opacity-50 font-semibold text-lg flex items-center justify-center gap-2">
            This Week
          </button>
          <button onClick={() => handleTrigger('monthly')} disabled={triggering} className="flex-1 py-4 bg-white border border-slate-200 text-slate-700 rounded-xl hover:bg-blue-50 hover:border-blue-200 hover:text-blue-700 transition-all shadow-sm disabled:opacity-50 font-semibold text-lg flex items-center justify-center gap-2">
            This Month
          </button>
      </div>
      
      <div className="flex-1 bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden min-h-[600px] flex">
        {triggering ? (
            <div className="flex-1 flex flex-col items-center justify-center text-slate-500">
                <PlayCircle size={48} className="animate-spin text-blue-500 mb-4" />
                <h3 className="text-xl font-bold text-slate-700 mb-2">Analyzing Data...</h3>
                <p>LangGraph pipeline is querying records and generating LLM insights.</p>
            </div>
        ) : activeReport === "error" ? (
            <div className="flex-1 flex flex-col items-center justify-center text-rose-500">
                <XCircle size={64} className="mb-4 opacity-50" />
                <h3 className="text-xl font-bold text-rose-700 mb-2">Report Generation Failed</h3>
                <p className="text-slate-500">The pipeline took too long or encountered an error.</p>
            </div>
        ) : activeReport ? (
            <iframe src={activeReport} className="w-full h-full min-h-[600px]" title="Active Report" />
        ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-slate-400">
                <FileBarChart size={64} className="mb-4 opacity-50" />
                <h3 className="text-xl font-bold text-slate-600 mb-2">No Report Selected</h3>
                <p>Click a preset above or use custom dates to generate a report.</p>
            </div>
        )}
      </div>
    </div>
  );
}
function EmailAgent() {
  const [logs, setLogs] = useState<any[]>([]);

  // We could fetch actual logs from a new API endpoint, but for now we'll just show it's automated
  
  return (
    <div className="p-8 bg-slate-50 min-h-full">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h2 className="text-2xl font-bold text-slate-800">Email Agent (Automated)</h2>
          <p className="text-slate-500 mt-1">Runs autonomously at the end of the pipeline.</p>
        </div>
      </div>
      
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-8 max-w-4xl text-center">
        <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <Mail className="text-green-600" size={32} />
        </div>
        <h3 className="text-2xl font-bold text-slate-700 mb-2">Fully Automated Delivery</h3>
        <p className="text-slate-500 mb-8 max-w-lg mx-auto">
            The Email Agent no longer requires human-in-the-loop approval. It now automatically compiles the final narrative and charts into a polished HTML email and sends it directly to your inbox immediately after the Visualization Agent finishes.
        </p>
        
        <div className="bg-slate-50 rounded-lg p-6 text-left border border-slate-200">
            <h4 className="font-semibold text-slate-700 mb-4 flex items-center gap-2">
                <CheckCircle size={18} className="text-green-500" /> Agent Responsibilities
            </h4>
            <ul className="space-y-3 text-sm text-slate-600">
                <li className="flex items-start gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-blue-400 mt-1.5 shrink-0"></span>
                    <span>Takes the Analysis agent's narrative summary and the Visualization agent's chart images.</span>
                </li>
                <li className="flex items-start gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-blue-400 mt-1.5 shrink-0"></span>
                    <span>Formats them into a formal HTML email with inline CID embedded charts.</span>
                </li>
                <li className="flex items-start gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-blue-400 mt-1.5 shrink-0"></span>
                    <span>Sends it to the configured recipient list via the Resend API.</span>
                </li>
                <li className="flex items-start gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-blue-400 mt-1.5 shrink-0"></span>
                    <span>Logs the delivery status back to the Postgres database.</span>
                </li>
            </ul>
        </div>
      </div>
    </div>
  );
}

function App() {
  return (
    <Router>
      <div className="flex h-screen overflow-hidden bg-slate-50 font-sans">
        <Sidebar />
        <main className="flex-1 overflow-x-hidden overflow-y-auto">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/table" element={<DataTable />} />
            <Route path="/reports" element={<GenerateReport />} />
            <Route path="/artifacts" element={<Artifacts />} />
            <Route path="/email" element={<EmailAgent />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
