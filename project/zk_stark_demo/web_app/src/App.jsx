
import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import io from "socket.io-client";
import { Terminal, Play, CheckCircle, Activity, ChevronRight } from "lucide-react";
import "./App.css";

// Configure API URL
const API_URL = "http://127.0.0.1:5000";

const socket = io(API_URL);

function App() {
  const [implementations, setImplementations] = useState([]);
  const [selectedImpl, setSelectedImpl] = useState(null);
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    fetchImplementations();

    socket.on("connect", () => {
      console.log("Connected to server");
    });

    socket.on("log", (data) => {
      setLogs((prev) => [...prev, data]);
    });

    return () => {
      socket.off("connect");
      socket.off("log");
    };
  }, []);

  useEffect(() => {
    // Auto-scroll logs
    const consoleEl = document.getElementById("log-console");
    if (consoleEl) {
      consoleEl.scrollTop = consoleEl.scrollHeight;
    }
  }, [logs]);

  const fetchImplementations = async () => {
    try {
      const res = await axios.get(`${API_URL}/api/implementations`);
      setImplementations(res.data);
      if (res.data.length > 0) {
        setSelectedImpl(res.data[0]);
      }
    } catch (err) {
      console.error("Failed to fetch implementations", err);
    }
  };

  return (
    <div className="layout">
      <Sidebar
        implementations={implementations}
        selected={selectedImpl}
        onSelect={setSelectedImpl}
      />

      <div className="main-content">
        {selectedImpl ? (
          <div className="split-view">
            <Panel
              type="prover"
              implementation={selectedImpl}
              icon={<Activity />}
            />
            <Panel
              type="verifier"
              implementation={selectedImpl}
              icon={<CheckCircle />}
            />
          </div>
        ) : (
          <div className="welcome-screen">
            <h2>Select an implementation to begin</h2>
          </div>
        )}

        <LogConsole logs={logs} />
      </div>
    </div>
  );
}

const Sidebar = ({ implementations, selected, onSelect }) => (
  <div className="sidebar">
    <div className="sidebar-title">ZK-STARK Demo</div>
    <div className="impl-list">
      {implementations.map((impl) => (
        <button
          key={impl}
          className={`impl-btn ${selected === impl ? "active" : ""}`}
          onClick={() => onSelect(impl)}
        >
          {impl}
        </button>
      ))}
    </div>
  </div>
);

const Panel = ({ type, implementation, icon }) => {
  const [schema, setSchema] = useState(null);
  const [formData, setFormData] = useState({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchSchema = async () => {
      try {
        const res = await axios.get(`${API_URL}/api/schema/${implementation}/${type}`);
        setSchema(res.data);

        // Initialize defaults
        const defaults = {};
        res.data.arguments.forEach(arg => {
          defaults[arg.name] = arg.default;
        });
        setFormData(defaults);

      } catch (err) {
        console.error(`Failed to fetch ${type} schema`, err);
        setSchema(null);
      }
    };

    if (implementation) {
      fetchSchema();
    }
  }, [implementation, type]);

  const handleChange = (name, value) => {
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async () => {
    setLoading(true);
    try {
      await axios.post(`${API_URL}/api/run`, {
        implementation,
        type,
        args: formData
      });
    } catch (err) {
      console.error("Failed to start run", err);
    } finally {
      setLoading(false);
    }
  };

  if (!schema) return <div className="panel">Loading...</div>;
  if (schema.error) return <div className="panel">Not available for this implementation</div>;

  return (
    <div className="panel">
      <div className={`panel-header ${type}-header`}>
        {icon}
        {type.charAt(0).toUpperCase() + type.slice(1)}
      </div>

      <p style={{ color: '#94a3b8', marginBottom: '2rem' }}>{schema.description}</p>

      <div className="form-container">
        {schema.arguments.map(arg => {
          // Skip help
          if (arg.name === 'help') return null;

          return (
            <div key={arg.name} className="form-group">
              <label className="form-label">
                {arg.name} {arg.required && '*'}
              </label>
              <input
                className="form-input"
                type={arg.type === 'number' ? 'number' : 'text'}
                value={formData[arg.name] || ''}
                onChange={(e) => handleChange(arg.name, arg.type === 'number' ? parseInt(e.target.value) : e.target.value)}
                disabled={loading}
              />
              <small style={{ color: '#64748b', fontSize: '0.75rem' }}>
                {arg.help} {arg.default !== undefined && `(Default: ${arg.default})`}
              </small>
            </div>
          )
        })}

        <button
          className={`action-btn ${type}-btn`}
          onClick={handleSubmit}
          disabled={loading}
        >
          {loading ? "Running..." : `Run ${type.charAt(0).toUpperCase() + type.slice(1)}`}
        </button>
      </div>
    </div>
  );
};

const LogConsole = ({ logs }) => {
  return (
    <div className="log-console" id="log-console">
      {logs.length === 0 && <div className="log-entry" style={{ color: '#64748b' }}>Ready for execution...</div>}
      {logs.map((log, i) => (
        <div key={i} className="log-entry">
          <span className={`log-source ${log.source.toLowerCase().includes('prover') ? 'prover' : 'verifier'}`}>
            {log.source}
          </span>
          <span className="log-message">{log.message}</span>
        </div>
      ))}
    </div>
  );
};

export default App;
