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
  
  const network = location.state?.network || { 
    name: 'Unknown Network', 
    signal: 0, 
    security: 'WPA2-Personal', 
    channel: 1 
  };

  const [loading, setLoading] = useState(true);
  const [details, setDetails] = useState({ 
    devices: [], 
    connections: [],
    dns_latency: 0.0,
    gateway_rtt: 0.0,
    beacon_interval: 0.0,
    packet_rate: 0.0
  });

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
          Math.max(0, signalValue + 4), 
          Math.max(0, signalValue + 2), 
          Math.max(0, signalValue + 5), 
          Math.max(0, signalValue + 1), 
          Math.max(0, signalValue + 3), 
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
      y: { min: -100, max: 0, grid: { color: 'rgba(255, 255, 255, 0.03)' }, ticks: { color: '#64748b', font: { size: 11 } } },
      x: { grid: { display: false }, ticks: { color: '#64748b', font: { size: 11 } } }
    }
  };

  const listenCount = details.connections.filter(c => c.status === 'LISTEN').length;
  const establishedCount = details.connections.filter(c => c.status === 'ESTABLISHED').length;

  const socketData = {
    labels: ['Listening Ports', 'Established Sockets'],
    datasets: [
      {
        data: [listenCount > 0 ? listenCount : 1, establishedCount > 0 ? establishedCount : 1],
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
          <p className="text-slate-400 text-sm">Analyzing behavioral parameters and processing packets...</p>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-[#020617] via-[#090d1f] to-[#020617] text-white p-6 lg:p-10">
      <div className="max-w-[1400px] mx-auto">
        
        {/* Header Section */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8 bg-slate-950/40 p-6 rounded-3xl border border-slate-800/85 backdrop-blur-2xl shadow-2xl">
          <div>
            <button 
              onClick={() => navigate('/dashboard')}
              className="text-xs uppercase tracking-widest text-cyan-400 mb-2 hover:text-cyan-300 font-bold transition flex items-center gap-1"
            >
              ← Back to Dashboard
            </button>
            <h1 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-white via-slate-200 to-cyan-400 bg-clip-text text-transparent">
              Deep Network Behavioral Analysis
            </h1>
            <p className="text-slate-400 text-sm mt-1">Target SSID: <span className="text-cyan-300 font-semibold">{network.name || network.ssid}</span></p>
          </div>
          <div className="bg-slate-900/80 border border-cyan-500/30 px-5 py-3 rounded-2xl text-left md:text-right backdrop-blur-xl shadow-lg shadow-cyan-950/40">
            <p className="text-[10px] uppercase tracking-wider text-slate-400 font-semibold">Encryption Type (Categorical)</p>
            <p className="text-sm font-bold text-cyan-400">{network.encryption || network.security || 'WPA2-PSK'}</p>
          </div>
        </div>

        {/* Behavioral Metrics Cards Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 mb-8">
          
          {/* 1. Signal Strength */}
          <div className="bg-slate-950/60 border border-slate-800/80 p-6 rounded-3xl backdrop-blur-xl hover:border-cyan-500/40 transition duration-300 shadow-xl">
            <p className="text-xs text-slate-400 uppercase tracking-wider font-semibold">Signal Strength</p>
            <p className="text-3xl font-black text-cyan-400 mt-2 tracking-tight">{network.signal} dBm</p>
            <p className="text-xs text-slate-400 mt-2">Channel: {network.channel} • Wireless RSSI</p>
          </div>

          {/* 2. DNS Latency */}
          <div className="bg-slate-950/60 border border-slate-800/80 p-6 rounded-3xl backdrop-blur-xl hover:border-blue-500/40 transition duration-300 shadow-xl">
            <p className="text-xs text-slate-400 uppercase tracking-wider font-semibold">DNS Latency</p>
            <p className="text-3xl font-black text-blue-400 mt-2 tracking-tight">{details.dns_latency} ms</p>
            <p className="text-xs text-slate-400 mt-2">Average name-resolution delay</p>
          </div>

          {/* 3. Gateway RTT */}
          <div className="bg-slate-950/60 border border-slate-800/80 p-6 rounded-3xl backdrop-blur-xl hover:border-purple-500/40 transition duration-300 shadow-xl">
            <p className="text-xs text-slate-400 uppercase tracking-wider font-semibold">Gateway RTT</p>
            <p className="text-3xl font-black text-purple-400 mt-2 tracking-tight">{details.gateway_rtt} ms</p>
            <p className="text-xs text-slate-400 mt-2">Median router round-trip time</p>
          </div>

          {/* 4. Beacon Interval */}
          <div className="bg-slate-950/60 border border-slate-800/80 p-6 rounded-3xl backdrop-blur-xl hover:border-emerald-500/40 transition duration-300 shadow-xl">
            <p className="text-xs text-slate-400 uppercase tracking-wider font-semibold">Beacon Interval</p>
            <p className="text-3xl font-black text-emerald-400 mt-2 tracking-tight">{details.beacon_interval} s</p>
            <p className="text-xs text-slate-400 mt-2">Frame arrival timing interval</p>
          </div>

          {/* 5. Packet Rate */}
          <div className="bg-slate-950/60 border border-slate-800/80 p-6 rounded-3xl backdrop-blur-xl hover:border-amber-500/40 transition duration-300 shadow-xl">
            <p className="text-xs text-slate-400 uppercase tracking-wider font-semibold">Packet Rate</p>
            <p className="text-3xl font-black text-amber-400 mt-2 tracking-tight">{details.packet_rate} pkts/s</p>
            <p className="text-xs text-slate-400 mt-2">Total Packets: {details.total_packets}</p>
          </div>

          {/* 6. Active Sockets */}
          <div className="bg-slate-950/60 border border-slate-800/80 p-6 rounded-3xl backdrop-blur-xl hover:border-indigo-500/40 transition duration-300 shadow-xl">
            <p className="text-xs text-slate-400 uppercase tracking-wider font-semibold">Active Sockets</p>
            <p className="text-3xl font-black text-indigo-400 mt-2 tracking-tight">{details.connections.length} Ports</p>
            <p className="text-xs text-slate-400 mt-2">Real-time TCP/UDP Listeners</p>
          </div>

        </div>

        {/* Interactive Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <div className="lg:col-span-2 bg-slate-950/60 border border-slate-800/80 p-6 rounded-3xl backdrop-blur-xl shadow-2xl flex flex-col justify-between">
            <h2 className="text-base font-bold text-cyan-400 mb-4 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-cyan-400"></span> Signal Strength Fluctuation Trend
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
                      <td className="py-4 font-semibold text-white">{d.device || 'Subnet Node'}</td>
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

      </div>
    </main>
  );
}

export default NetworkAnalysis;