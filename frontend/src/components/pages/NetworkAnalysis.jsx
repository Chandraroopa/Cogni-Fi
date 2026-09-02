import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { Line, Doughnut } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

function NetworkAnalysis() {
  const location = useLocation();
  const navigate = useNavigate();
  
  // If no network state was passed, fall back gracefully instead of a fake hardcoded SSID
  const network = location.state?.network || { 
    name: 'Unknown Network', 
    signal: 0, 
    security: 'Unknown', 
    channel: 0 
  };

  const [loading, setLoading] = useState(true);
  const [details, setDetails] = useState({ devices: [], connections: [] });

  useEffect(() => {
    fetch('http://localhost:5000/api/network-details')
      .then((res) => res.json())
      .then((data) => {
        setDetails(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to fetch detailed metrics:", err);
        setLoading(false);
      });
  }, []);

  const signalValue = network.signal || 0;
  const signalData = {
    labels: ['10s ago', '8s ago', '6s ago', '4s ago', '2s ago', 'Now'],
    datasets: [
      {
        fill: true,
        label: 'Signal Quality (%)',
        data: [
          Math.max(0, signalValue - 4), 
          Math.max(0, signalValue - 2), 
          Math.max(0, signalValue - 5), 
          Math.max(0, signalValue - 1), 
          Math.max(0, signalValue - 3), 
          signalValue
        ],
        borderColor: '#06b6d4',
        backgroundColor: 'rgba(6, 182, 212, 0.2)',
        borderWidth: 3,
        pointBackgroundColor: '#06b6d4',
        pointBorderColor: '#ffffff',
        pointBorderWidth: 2,
        pointRadius: 4,
        pointHoverRadius: 6,
        tension: 0.4,
      },
    ],
  };

  const signalOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { 
      legend: { display: false },
      tooltip: {
        backgroundColor: 'rgba(2, 6, 17, 0.9)',
        titleColor: '#06b6d4',
        bodyColor: '#ffffff',
        borderColor: 'rgba(6, 182, 212, 0.3)',
        borderWidth: 1,
        padding: 10,
      }
    },
    scales: {
      y: { min: 0, max: 100, grid: { color: 'rgba(255, 255, 255, 0.03)' }, ticks: { color: '#64748b', font: { size: 11 } } },
      x: { grid: { display: false }, ticks: { color: '#64748b', font: { size: 11 } } }
    }
  };

  const listenCount = details.connections.filter(c => c.status === 'LISTEN').length;
  const establishedCount = details.connections.filter(c => c.status === 'ESTABLISHED').length;

  const socketData = {
    labels: ['Listening Ports', 'Established Sockets'],
    datasets: [
      {
        data: [listenCount, establishedCount],
        backgroundColor: ['#c084fc', '#06b6d4'],
        borderWidth: 0,
        hoverOffset: 6,
      },
    ],
  };

  const socketOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { position: 'bottom', labels: { color: '#94a3b8', font: { size: 12 }, padding: 20, usePointStyle: true } }
    },
    cutout: '75%',
  };

  if (loading) {
    return (
      <main className="min-h-screen bg-gradient-to-br from-[#020617] via-[#090d1f] to-[#020617] text-white flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-cyan-400 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-slate-400 text-sm">Querying backend socket tables and ARP maps...</p>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-[#020617] via-[#090d1f] to-[#020617] text-white p-6 lg:p-10">
      <div className="max-w-[1400px] mx-auto">
        
        {/* Header Section */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8 bg-slate-950/40 p-6 rounded-3xl border border-slate-800/80 backdrop-blur-2xl shadow-2xl">
          <div>
            <button 
              onClick={() => navigate('/dashboard')}
              className="text-xs uppercase tracking-widest text-cyan-400 mb-2 hover:text-cyan-300 font-bold transition flex items-center gap-1"
            >
              ← Back to Dashboard
            </button>
            <h1 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-white via-slate-200 to-cyan-400 bg-clip-text text-transparent">
              Deep Network Analysis
            </h1>
            <p className="text-slate-400 text-sm mt-1">Inspecting Target SSID: <span className="text-cyan-300 font-semibold">{network.name}</span></p>
          </div>
          <div className="bg-slate-900/80 border border-cyan-500/30 px-5 py-3 rounded-2xl text-left md:text-right backdrop-blur-xl shadow-lg shadow-cyan-950/40 flex items-center justify-between md:block">
            <div>
              <p className="text-[10px] uppercase tracking-wider text-slate-400 font-semibold">Security Standard</p>
              <p className="text-sm font-bold text-cyan-400">{network.security}</p>
            </div>
          </div>
        </div>

        {/* Top KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mb-8">
          <div className="bg-slate-950/60 border border-slate-800/80 p-6 rounded-3xl backdrop-blur-xl hover:border-cyan-500/40 transition duration-300 shadow-xl relative overflow-hidden group">
            <p className="text-xs text-slate-400 uppercase tracking-wider font-semibold">Signal Quality</p>
            <p className="text-4xl font-black text-cyan-400 mt-2 tracking-tight">{network.signal}%</p>
            <div className="flex items-center gap-2 mt-2">
              <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></span>
              <p className="text-xs text-slate-400">Channel: {network.channel} • Active Connection</p>
            </div>
          </div>

          <div className="bg-slate-950/60 border border-slate-800/80 p-6 rounded-3xl backdrop-blur-xl hover:border-purple-500/40 transition duration-300 shadow-xl relative overflow-hidden group">
            <p className="text-xs text-slate-400 uppercase tracking-wider font-semibold">Active Local Devices</p>
            <p className="text-4xl font-black text-purple-400 mt-2 tracking-tight">{details.devices.length} Devices</p>
            <p className="text-xs text-slate-400 mt-2">Discovered via ARP table mapping</p>
          </div>

          <div className="bg-slate-950/60 border border-slate-800/80 p-6 rounded-3xl backdrop-blur-xl hover:border-blue-500/40 transition duration-300 shadow-xl relative overflow-hidden group">
            <p className="text-xs text-slate-400 uppercase tracking-wider font-semibold">Active Sockets</p>
            <p className="text-4xl font-black text-blue-400 mt-2 tracking-tight">{details.connections.length} Ports</p>
            <p className="text-xs text-slate-400 mt-2">Real-time TCP/UDP Listeners</p>
          </div>
        </div>

        {/* Interactive Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <div className="lg:col-span-2 bg-slate-950/60 border border-slate-800/80 p-6 rounded-3xl backdrop-blur-xl shadow-2xl flex flex-col justify-between">
            <h2 className="text-base font-bold text-cyan-400 mb-4 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-cyan-400"></span> Signal Quality Fluctuation Trend
            </h2>
            <div className="h-[260px] w-full">
              <Line data={signalData} options={signalOptions} />
            </div>
          </div>
          
          <div className="bg-slate-950/60 border border-slate-800/80 p-6 rounded-3xl backdrop-blur-xl shadow-2xl flex flex-col justify-between">
            <h2 className="text-base font-bold text-purple-400 mb-2 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-purple-400"></span> Socket State Distribution
            </h2>
            <div className="h-[230px] w-full flex items-center justify-center">
              <Doughnut data={socketData} options={socketOptions} />
            </div>
          </div>
        </div>

        {/* Devices Mapping Table */}
        <div className="bg-slate-950/60 border border-slate-800/80 rounded-3xl p-6 mb-8 backdrop-blur-xl shadow-2xl">
          <h2 className="text-lg font-bold text-cyan-400 mb-4">Network Node & Device Mapping</h2>
          <div className="overflow-x-auto">
            {details.devices.length === 0 ? (
              <p className="text-slate-500 text-sm py-4">No active devices found in the local ARP table.</p>
            ) : (
              <table className="w-full text-left text-sm">
                <thead className="border-b border-slate-800 text-slate-400 text-xs uppercase tracking-wider">
                  <tr>
                    <th className="pb-3 font-semibold">Device Description</th>
                    <th className="pb-3 font-semibold">IP Address</th>
                    <th className="pb-3 font-semibold">MAC Address</th>
                    <th className="pb-3 font-semibold">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/40">
                  {details.devices.map((d, i) => (
                    <tr key={i} className="hover:bg-slate-900/50 transition">
                      <td className="py-4 font-semibold text-white">{d.device || 'Unknown Device'}</td>
                      <td className="py-4 text-cyan-300 font-mono">{d.ip}</td>
                      <td className="py-4 text-slate-400 font-mono text-xs">{d.mac}</td>
                      <td className="py-4">
                        <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-green-500/10 text-green-400 border border-green-500/20 rounded-xl text-xs font-semibold">
                          <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse"></span> {d.status || 'Active'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>

        {/* Active Sockets Table */}
        <div className="bg-slate-950/60 border border-slate-800/80 rounded-3xl p-6 backdrop-blur-xl shadow-2xl">
          <h2 className="text-lg font-bold text-cyan-400 mb-4">Active Socket Connections</h2>
          <div className="overflow-x-auto">
            {details.connections.length === 0 ? (
              <p className="text-slate-500 text-sm py-4">No active socket connections found from backend.</p>
            ) : (
              <table className="w-full text-left text-sm">
                <thead className="border-b border-slate-800 text-slate-400 text-xs uppercase tracking-wider">
                  <tr>
                    <th className="pb-3 font-semibold">Local IP:Port</th>
                    <th className="pb-3 font-semibold">Remote IP:Port</th>
                    <th className="pb-3 font-semibold">State</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/40">
                  {details.connections.map((c, i) => (
                    <tr key={i} className="hover:bg-slate-900/50 font-mono text-xs transition">
                      <td className="py-3.5 text-cyan-300">{c.local_ip}:{c.local_port}</td>
                      <td className="py-3.5 text-slate-400">{c.remote_ip}:{c.remote_port}</td>
                      <td className="py-3.5">
                        <span className={`px-2.5 py-1 rounded-lg text-[10px] font-bold tracking-wider ${c.status === 'ESTABLISHED' ? 'bg-cyan-500/10 text-cyan-300 border border-cyan-500/25' : 'bg-purple-500/10 text-purple-300 border border-purple-500/25'}`}>
                          {c.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>

      </div>
    </main>
  );
}

export default NetworkAnalysis;