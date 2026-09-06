import re

with open("src/App.tsx", "r") as f:
    content = f.read()

# 1. Imports
content = content.replace("from 'lucide-react';", "MessageSquare } from 'lucide-react';").replace("Clock } from", "Clock, ")
# actually let's just do a string replace for lucide-react imports:
content = re.sub(
    r"import \{ (.*?) \} from 'lucide-react';",
    r"import { \1, MessageSquare } from 'lucide-react';",
    content
)

# 2. Sidebar
content = content.replace(
    "{ name: 'Generated Reports', path: '/reports', icon: <FileBarChart size={20} /> },",
    "{ name: 'Generated Reports', path: '/reports', icon: <FileBarChart size={20} /> },\n    { name: 'Chat AI', path: '/chat', icon: <MessageSquare size={20} /> },"
)

# 3. ChatAssistant Component
chat_component = """
function ChatAssistant() {
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const sendMessage = async (e: any) => {
    e.preventDefault();
    if (!input.trim()) return;
    
    const userMsg = { role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch(`${API_BASE}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: userMsg.content })
      });
      const data = await res.json();
      setMessages(prev => [...prev, { role: 'ai', content: data.response }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'ai', content: "Error communicating with server." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-2rem)] m-4 bg-white rounded-xl shadow-sm border border-slate-200">
      <div className="p-6 border-b border-slate-100">
        <h2 className="text-2xl font-bold text-slate-800">AI Chat Assistant</h2>
        <p className="text-slate-500 text-sm">Ask natural language questions about your IVR call logs.</p>
      </div>
      
      <div className="flex-1 p-6 overflow-y-auto space-y-4">
        {messages.length === 0 && (
            <div className="text-slate-400 text-center mt-10">
                Ask something like: "What is the average call duration?" or "How many calls were abandoned?"
            </div>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[70%] p-4 rounded-xl ${m.role === 'user' ? 'bg-blue-600 text-white rounded-tr-none' : 'bg-slate-100 text-slate-800 rounded-tl-none'}`}>
              {m.content}
            </div>
          </div>
        ))}
        {loading && (
            <div className="flex justify-start">
                <div className="max-w-[70%] p-4 rounded-xl bg-slate-100 text-slate-500 rounded-tl-none animate-pulse">
                Thinking...
                </div>
            </div>
        )}
      </div>

      <div className="p-4 border-t border-slate-100">
        <form onSubmit={sendMessage} className="flex gap-2">
          <input 
            type="text" 
            value={input} 
            onChange={e => setInput(e.target.value)} 
            placeholder="Type your question..." 
            className="flex-1 px-4 py-2 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button type="submit" disabled={loading} className="px-6 py-2 bg-slate-900 text-white rounded-lg hover:bg-slate-800 transition-colors font-medium disabled:opacity-50">
            Send
          </button>
        </form>
      </div>
    </div>
  );
}
"""

content = content.replace("function App() {", chat_component + "\nfunction App() {")

# 4. App Routes
content = content.replace(
    '<Route path="/reports" element={<Reports />} />',
    '<Route path="/reports" element={<Reports />} />\n            <Route path="/chat" element={<ChatAssistant />} />'
)

# 5. Dashboard Date Filters
dashboard_old = """function Dashboard() {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_BASE}/analytics`)
      .then(res => res.json())
      .then(data => {
        setStats(data);
        setLoading(false);
      });
  }, []);"""

dashboard_new = """function Dashboard() {
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
  }, [startDate, endDate]);"""
content = content.replace(dashboard_old, dashboard_new)

dashboard_header_old = """<h2 className="text-2xl font-bold text-slate-800 mb-6">Overview Analytics</h2>"""
dashboard_header_new = """<div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-slate-800">Overview Analytics</h2>
        <div className="flex gap-4 items-center bg-white p-2 rounded-lg border border-slate-200 shadow-sm">
            <span className="text-sm font-medium text-slate-500">Filter by Date:</span>
            <input type="date" value={startDate} onChange={e => setStartDate(e.target.value)} className="text-sm border-slate-200 rounded px-2 py-1 outline-none focus:ring-1 focus:ring-blue-500" />
            <span className="text-slate-400">to</span>
            <input type="date" value={endDate} onChange={e => setEndDate(e.target.value)} className="text-sm border-slate-200 rounded px-2 py-1 outline-none focus:ring-1 focus:ring-blue-500" />
        </div>
      </div>"""
content = content.replace(dashboard_header_old, dashboard_header_new)

# 6. Reports presets
reports_old = """const handleTrigger = async () => {
    setTriggering(true);
    try {
      await fetch(`${API_BASE}/run-pipeline`, { method: "POST" });
      setTimeout(fetchReports, 3000);
    } catch (e) {
      console.error(e);
    } finally {
      setTimeout(() => setTriggering(false), 2000);
    }
  };"""

reports_new = """const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");

  const handleTrigger = async (preset?: string) => {
    setTriggering(true);
    try {
      let sd = startDate;
      let ed = endDate;
      
      if (preset === 'daily') {
          const today = new Date().toISOString().split('T')[0];
          sd = today; ed = today;
      } else if (preset === 'weekly') {
          const today = new Date();
          const lastWeek = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
          sd = lastWeek.toISOString().split('T')[0];
          ed = today.toISOString().split('T')[0];
      } else if (preset === 'monthly') {
          const today = new Date();
          const lastMonth = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000);
          sd = lastMonth.toISOString().split('T')[0];
          ed = today.toISOString().split('T')[0];
      }
      
      await fetch(`${API_BASE}/run-pipeline`, { 
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ start_date: sd, end_date: ed })
      });
      setTimeout(fetchReports, 3000);
    } catch (e) {
      console.error(e);
    } finally {
      setTimeout(() => setTriggering(false), 2000);
    }
  };"""
content = content.replace(reports_old, reports_new)

reports_button_old = """<button 
          onClick={handleTrigger}
          disabled={triggering}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-white font-medium transition-all ${
              triggering ? 'bg-blue-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700 shadow-md hover:shadow-lg'
          }`}
        >
          <PlayCircle size={18} className={triggering ? "animate-spin" : ""} />
          {triggering ? 'Pipeline Running...' : 'Trigger Pipeline'}
        </button>"""

reports_button_new = """<div className="flex gap-2">
          <button onClick={() => handleTrigger('daily')} disabled={triggering} className="px-3 py-1.5 text-sm bg-white border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors disabled:opacity-50">Daily</button>
          <button onClick={() => handleTrigger('weekly')} disabled={triggering} className="px-3 py-1.5 text-sm bg-white border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors disabled:opacity-50">Weekly</button>
          <button onClick={() => handleTrigger('monthly')} disabled={triggering} className="px-3 py-1.5 text-sm bg-white border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors disabled:opacity-50">Monthly</button>
          
          <button 
            onClick={() => handleTrigger()}
            disabled={triggering}
            className={`flex items-center gap-2 px-4 py-1.5 ml-2 rounded-lg text-white font-medium transition-all ${
                triggering ? 'bg-blue-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700 shadow-md hover:shadow-lg'
            }`}
          >
            <PlayCircle size={18} className={triggering ? "animate-spin" : ""} />
            {triggering ? 'Running...' : 'Custom Run'}
          </button>
        </div>"""
content = content.replace(reports_button_old, reports_button_new)

# DataTable filter
table_old = """const [records, setRecords] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 10;

  useEffect(() => {
    fetch(`${API_BASE}/records`)
      .then(res => res.json())
      .then(data => {
        setRecords(data.records);
        setLoading(false);
      });
  }, []);"""

table_new = """const [records, setRecords] = useState<any[]>([]);
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
  }, [startDate, endDate]);"""
content = content.replace(table_old, table_new)

table_header_old = """<h2 className="text-2xl font-bold text-slate-800">Call Records</h2>"""
table_header_new = """<div className="flex gap-4 items-center">
          <h2 className="text-2xl font-bold text-slate-800">Call Records</h2>
          <div className="flex gap-2 items-center bg-white p-1.5 rounded-lg border border-slate-200 shadow-sm ml-4">
              <input type="date" value={startDate} onChange={e => setStartDate(e.target.value)} className="text-xs border-slate-200 rounded px-2 py-1 outline-none" />
              <span className="text-slate-400 text-xs">to</span>
              <input type="date" value={endDate} onChange={e => setEndDate(e.target.value)} className="text-xs border-slate-200 rounded px-2 py-1 outline-none" />
          </div>
        </div>"""
content = content.replace(table_header_old, table_header_new)

with open("src/App.tsx", "w") as f:
    f.write(content)

