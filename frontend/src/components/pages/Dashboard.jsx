import React, { useState, useEffect } from 'react';

// ============================================================================
// 20. Centralized Mock Data / Future API Layer Gateway (services/api.js)
// ============================================================================
const COGNIFY_API_BASE = 'http://localhost:5000/api'; // Toggle to true production endpoint later

export const mockCentralData = {
  currentNetwork: {
    ssid: 'Cafe_Free_WiFi',
    bssid: '3C:5A:B4:9F:E1:11:02',
    status: 'Scanned',
    connectionStatus: 'Connected',
    signalStrength: '-58 dBm',
    encryption: 'WPA2 / Open Portal',
    channel: 6,
    band: '2.4 GHz',
    connectionDuration: '03:07 PM',
    gatewayLatency: '42 ms',
    dnsResponseTime: '125 ms',
    beaconInterval: '102 ms',
    securityStatusFlag: 'UNENCRYPTED SSID',
    trustScore: 64,
    classification: 'CAUTION',
    modelConfidence: 87,
    threatsCount: 2,
    anomalyScore: 43
  },
  trustScoreAnalysis: {
    score: 64,
    classification: 'Caution',
    confidence: 87,
    factors: [
      { name: 'Signal Stability', score: 82, text: 'Minor signal drops noticed but within baseline thresholds.' },
      { name: 'DNS Integrity', score: 58, text: 'DNS responses show unusual redirect mutations or unexpected resolver paths.' },
      { name: 'BSSID Consistency', score: 74, text: 'BSSID signatures map to expected vendor ranges but broadcast profiles vary.' },
      { name: 'Reconnect Pattern', score: 66, text: 'Moderate re-association loops intercepted within a short cycle window.' },
      { name: 'Traffic Anomaly', score: 43, text: 'Packet delivery rates deviate marginally from ordinary user behaviors.' }
    ]
  },
  mlBehavioralAnalysis: {
    model: 'Random Forest',
    prediction: 'Suspicious Behavior',
    confidence: 87,
    anomalyScore: 73,
    featuresAnalyzedCount: 12,
    topFeatures: [
      { label: 'DNS Response Pattern', weight: 92 },
      { label: 'Traffic Rate', weight: 78 },
      { label: 'BSSID Consistency', weight: 71 },
      { label: 'Packet Flow', weight: 54 },
      { label: 'Reconnect Frequency', weight: 48 }
    ]
  },
  trafficAnalysis: {
    currentRate: '181 KB/s',
    averageRate: '131 KB/s',
    peakRate: '181 KB/s',
    anomalyPercentage: 43,
    isAnomalous: true,
    timeline: [
      { label: '00:00', packetRate: 45, upload: 12, download: 33, isAnomaly: false },
      { label: '04:00', packetRate: 30, upload: 8, download: 22, isAnomaly: false },
      { label: '08:00', packetRate: 95, upload: 40, download: 55, isAnomaly: false },
      { label: '12:00', packetRate: 181, upload: 86, download: 95, isAnomaly: true },
      { label: '16:00', packetRate: 110, upload: 45, download: 65, isAnomaly: false },
      { label: '20:00', packetRate: 135, upload: 50, download: 85, isAnomaly: false },
      { label: '24:00', packetRate: 88, upload: 32, download: 56, isAnomaly: false }
    ]
  },
  riskDistribution: {
    summary: '100+ NETWORKS ANALYZED',
    categories: [
      { name: 'Safe', percentage: 62, color: '#10b981', networks: ['Home_Router_2.4G', 'Canara_Campus_Net', 'Secure_Corporate_Enterprise', 'Lab_Access_Point_Alpha'] },
      { name: 'Caution', percentage: 24, color: '#f59e0b', networks: ['Cafe_Free_WiFi', 'Library_Guest_Portal', 'Transit_Terminal_Common'] },
      { name: 'High Risk', percentage: 10, color: '#ef4444', networks: ['Free_Airport_WiFi', 'Local_Market_Hotspot'] },
      { name: 'Critical', percentage: 4, color: '#e11d48', networks: ['Attacker_Portal_Setup', 'Malicious_Twin_Node'] }
    ]
  },
  threatsList: [
    { type: 'DNS Anomaly', desc: 'Unusual DNS response behavior detected. Mismatch in authoritative paths.', severity: 'MEDIUM', time: '2 min ago', status: 'Active', network: 'Cafe_Free_WiFi' },
    { type: 'Evil Twin Detection', desc: 'No matching trusted BSSID / suspicious duplicate signature monitored.', severity: 'HIGH', time: '12 min ago', status: 'Active', network: 'Cafe_Free_WiFi' },
    { type: 'Captive Portal', desc: 'Open public network vector operating without downstream cryptographic tunnels.', severity: 'LOW', time: '1 hr ago', status: 'Resolved', network: 'Library_Guest_Portal' },
    { type: 'Traffic Anomaly', desc: 'Unusual rapid surge in transmission packet burst metrics.', severity: 'MEDIUM', time: '3 hr ago', status: 'Active', network: 'Cafe_Free_WiFi' },
    { type: 'Reconnect Anomaly', desc: 'Repeated micro-second handshake reconnect behaviors detected.', severity: 'CRITICAL', time: '1 day ago', status: 'Active', network: 'Malicious_Twin_Node' }
  ],
  evilTwinMetrics: {
    currentBssid: '3C:5A:B4:9F:E1:11:02',
    nearbySimilarSsids: 2,
    bssidMatchStatus: 'No suspicious match',
    beaconDeviation: 'Medium',
    status: 'No Evil Twin Detected'
  },
  dnsBehaviorMetrics: {
    responseTime: '125 ms',
    expectedRange: '20–80 ms',
    deviation: '+56%',
    integrity: '58%',
    status: 'Suspicious DNS Behavior',
    chartData: [25, 32, 110, 125, 95, 45, 60]
  },
  connectionBehaviorMetrics: {
    duration: '42 min',
    attempts: 7,
    avgInterval: '6 min',
    anomalyScore: 66,
    timeline: [1, 2, 1, 3, 7, 2, 1]
  },
  scannerData: [
    { ssid: 'Home_Router_2.4G', bssid: 'A4:B2:C1:DF:78:90', signal: '-45 dBm', encryption: 'Private WPA3', trustScore: 94, risk: 'Low', status: 'Safe' },
    { ssid: 'Canara_Campus_Net', bssid: 'F0:18:98:CB:A2:34', signal: '-52 dBm', encryption: 'Enterprise WPA2', trustScore: 81, risk: 'Low', status: 'Safe' },
    { ssid: 'Cafe_Free_WiFi', bssid: '3C:5A:B4:9F:E1:11:02', signal: '-58 dBm', encryption: 'WPA2 / Open Portal', trustScore: 64, risk: 'Medium', status: 'Caution' },
    { ssid: 'Free_Airport_WiFi', bssid: '9E:F1:A2:34:BC:DE', signal: '-82 dBm', encryption: 'Public Open', trustScore: 31, risk: 'High', status: 'High Risk' }
  ],
  recommendations: [
    { id: 1, type: 'DNS Security', text: 'DNS behavior is suspicious. Avoid sensitive activities on this network.', severity: 'WARNING', reviewed: false },
    { id: 2, type: 'Wi-Fi Encryption', text: 'This network does not provide strong encryption. Avoid banking or sensitive transactions.', severity: 'HIGH', reviewed: false },
    { id: 3, type: 'Evil Twin Protection', text: 'Potential Evil Twin network detected. Disconnect and verify the legitimate access point.', severity: 'CRITICAL', reviewed: false },
    { id: 4, type: 'Traffic Anomaly', text: 'Unusual traffic behavior detected. Consider disconnecting from this network.', severity: 'INFO', reviewed: false }
  ],
  recentActivity: [
    { icon: '🔍', desc: 'Network metadata sweep executed', network: 'Cafe_Free_WiFi', time: 'Just now', severity: 'INFO' },
    { icon: '🛡️', desc: 'Trust score structural evaluation output generated', network: 'Cafe_Free_WiFi', time: '2 min ago', severity: 'INFO' },
    { icon: '🚨', desc: 'DNS hijacking signature anomaly flagged', network: 'Cafe_Free_WiFi', time: '5 min ago', severity: 'HIGH' },
    { icon: '📶', desc: 'Authenticated terminal trace profile bound to node', network: 'Cafe_Free_WiFi', time: '12 min ago', severity: 'INFO' }
  ]
};

// ============================================================================
// SERVICE HANDLERS (21. Front-end API endpoints bindings ready for substitution)
// ============================================================================
export const ApiService = {
  isBackendConnected: false, // Flip flag when integrating live Flask instance

  async getNetworkCurrent() {
    if (!this.isBackendConnected) return mockCentralData.currentNetwork;
    return fetch(`${COGNIFY_API_BASE}/network/current`).then(res => res.json());
  },
  async getNetworkScan() {
    if (!this.isBackendConnected) return mockCentralData.scannerData;
    return fetch(`${COGNIFY_API_BASE}/network/scan`).then(res => res.json());
  },
  async getTrustScore() {
    if (!this.isBackendConnected) return mockCentralData.trustScoreAnalysis;
    return fetch(`${COGNIFY_API_BASE}/trust-score`).then(res => res.json());
  },
  async getMlAnalysis() {
    if (!this.isBackendConnected) return mockCentralData.mlBehavioralAnalysis;
    return fetch(`${COGNIFY_API_BASE}/ml-analysis`).then(res => res.json());
  },
  async getTraffic() {
    if (!this.isBackendConnected) return mockCentralData.trafficAnalysis;
    return fetch(`${COGNIFY_API_BASE}/traffic`).then(res => res.json());
  },
  async getThreats() {
    if (!this.isBackendConnected) return mockCentralData.threatsList;
    return fetch(`${COGNIFY_API_BASE}/threats`).then(res => res.json());
  },
  async getRecommendations() {
    if (!this.isBackendConnected) return mockCentralData.recommendations;
    return fetch(`${COGNIFY_API_BASE}/recommendations`).then(res => res.json());
  }
};

export default function Dashboard() {
  // Navigation Router & Interactive State Management
  const [activeTab, setActiveTab] = useState('Overview');
  const [selectedRiskCategory, setSelectedRiskCategory] = useState(null);
  const [activeAlertFilter, setActiveAlertFilter] = useState('All');
  const [trustScorePopup, setTrustScorePopup] = useState(false);
  const [calculationExplanation, setCalculationExplanation] = useState(false);
  const [modelDetailsPopup, setModelDetailsPopup] = useState(false);
  
  // Scanning Sub-system State Tracker
  const [isScanning, setIsScanning] = useState(false);
  const [scanProgress, setScanProgress] = useState(0);
  const [scanExecuted, setScanExecuted] = useState(false);
  
  // Dynamic Comparison Engine Vector Arrays
  const [comparisonList, setComparisonList] = useState([]);
  const [localRecommendations, setLocalRecommendations] = useState(mockCentralData.recommendations);

  // Settings state matrix
  const [settings, setSettings] = useState({
    autoMitigate: true,
    heuristicEngine: false,
    notifyThreats: true
  });

  const toggleSetting = (key) => {
    setSettings(prev => ({ ...prev, [key]: !prev[key] }));
  };

  const handleMarkReview = (id) => {
    setLocalRecommendations(prev => prev.map(rec => rec.id === id ? { ...rec, reviewed: true } : rec));
  };

  const toggleComparisonSelection = (network) => {
    setComparisonList(prev => {
      const exists = prev.find(item => item.ssid === network.ssid);
      if (exists) return prev.filter(item => item.ssid !== network.ssid);
      if (prev.length >= 3) return prev; // Upper cap boundary constraints
      return [...prev, network];
    });
  };

  const startScanSequence = () => {
    setIsScanning(true);
    setScanProgress(0);
    setScanExecuted(false);
    const interval = setInterval(() => {
      setScanProgress(p => {
        if (p >= 100) {
          clearInterval(interval);
          setIsScanning(false);
          setScanExecuted(true);
          return 100;
        }
        return p + 20;
      });
    }, 200);
  };

  // Nav Items Definitions Grid mapping
  const navItems = [
    { name: 'Overview', icon: '💻' },
    { name: 'Scan Network', icon: '📶' },
    { name: 'My Networks', icon: '📋' },
    { name: 'Alerts', icon: '🔔', badge: 3 },
    { name: 'History', icon: '⏱️' },
    { name: 'Recommendations', icon: '🛡️' },
    { name: 'Settings', icon: '⚙️' },
    { name: 'Profile', icon: '👤' }
  ];

  return (
    <div className="h-screen w-screen bg-[#060b13] flex text-slate-100 font-sans overflow-hidden select-none">
      
      {/* ================= SIDEBAR NAVIGATION CONTAINER ================= */}
      <aside className="w-[240px] border-r border-slate-900 bg-[#090f1c]/40 flex flex-col justify-between p-4 flex-shrink-0 z-20">
        <div className="space-y-6">
          <div className="flex items-center gap-3 px-2 py-1">
            <div className="h-8 w-8 bg-blue-600 rounded-xl flex items-center justify-center text-white font-bold text-lg shadow-md shadow-blue-600/20">🛡️</div>
            <div>
              <span className="text-xl font-bold tracking-wide bg-gradient-to-r from-white to-slate-300 bg-clip-text text-transparent block leading-none">Cognify</span>
              <span className="text-[7px] text-blue-400 font-bold tracking-widest uppercase mt-1 block">ML Risk Analyzer</span>
            </div>
          </div>

          <nav className="space-y-1">
            {navItems.map((item) => {
              const isActive = activeTab === item.name;
              return (
                <button
                  key={item.name}
                  onClick={() => setActiveTab(item.name)}
                  className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-medium transition-all group ${
                    isActive ? 'bg-blue-600 text-white shadow-md shadow-blue-600/10 font-semibold' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/50'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <span className={`text-base ${isActive ? 'text-white' : 'text-slate-500'}`}>{item.icon}</span>
                    <span>{item.name}</span>
                  </div>
                  {item.badge && (
                    <span className={`h-4 min-w-4 px-1 flex items-center justify-center rounded-full text-[9px] font-bold ${isActive ? 'bg-white text-blue-600' : 'bg-rose-500/20 text-rose-400'}`}>
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>
        </div>

        <div className="space-y-3">
          {/* 18. PRIVACY PROTECTION DATA INDICATOR BADGE */}
          <div className="border border-slate-900/60 bg-[#070d18] rounded-xl p-2.5 text-center">
            <div className="text-[8px] font-extrabold text-emerald-400 tracking-wider uppercase mb-1">🔒 PRIVACY PROTECTED</div>
            <p className="text-[9px] text-slate-500 leading-normal font-medium">Only network metadata is analyzed. User content is not inspected.</p>
          </div>

          <div className="border border-slate-900 bg-[#0b1424]/40 rounded-xl p-3 flex items-center justify-between">
            <div className="flex items-center gap-2.5 min-w-0">
              <div className="h-7 w-7 rounded-lg bg-emerald-500/10 flex items-center justify-center border border-emerald-500/20 text-emerald-400 text-sm">🛡️</div>
              <div className="min-w-0">
                <p className="text-[10px] font-bold text-slate-200 tracking-wide">System Status</p>
                <p className="text-[9px] text-emerald-400 font-medium truncate">All Components Active</p>
              </div>
            </div>
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse ring-4 ring-emerald-500/10"></span>
          </div>
        </div>
      </aside>

      {/* ================= ENGINE PIPELINE MONITOR CONTAINER ================= */}
      <main className="flex-grow p-5 overflow-hidden flex flex-col justify-between relative z-10">
        
        {/* TOP LEVEL DESKTOP APP GLOBAL HEADER BANNER */}
        <header className="flex h-10 items-center justify-between border-b border-slate-900 pb-3 flex-shrink-0">
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base font-bold text-white tracking-wide">{activeTab}</h1>
              {/* 19. REAL-TIME API BACKEND INTERFACE ENGINE STATUS INDICATORS */}
              <div className="flex items-center gap-1.5 px-2 py-0.5 rounded bg-slate-950 border border-slate-900 text-[8px] font-mono text-slate-400">
                <span className="h-1 w-1 rounded-full bg-blue-500 animate-pulse"></span>
                <span>Live Monitoring: <span className="text-blue-400 font-bold">ACTIVE</span></span>
              </div>
            </div>
            <p className="text-[10px] text-slate-500 font-medium">Intelligent Behavioral Analysis of Public Wi-Fi Networks using Machine Learning</p>
          </div>
          <div className="flex items-center gap-3">
            <div className="text-right hidden sm:block">
              <span className="text-[8px] font-mono block text-slate-500">API STRATIFIED BOUND:</span>
              <span className="text-[9px] text-slate-400 font-semibold">{ApiService.isBackendConnected ? '⚡ FLASK LIVE' : '📦 MOCK SERVICE ENVELOPE'}</span>
            </div>
            <div className="h-8 w-8 rounded-full bg-gradient-to-tr from-blue-600 to-indigo-500 border border-slate-800 flex items-center justify-center font-bold text-xs text-white">U</div>
          </div>
        </header>

        {/* ====================================================================
            ROUTE SWITCHER PANELS VIEWPORTS
        ==================================================================== */}
        
        {/* RENDER VIEWPORT MAP: TAB 1 (MAIN SECURITY METADATA WORKSPACE OVERVIEW) */}
        {activeTab === 'Overview' && (
          <div className="flex-grow flex flex-col gap-4 mt-4 overflow-y-auto pr-1">
            
            {/* 25. EMBEDDED DYNAMIC CONCEPT PIPELINE MAP COMPONENT BAR */}
            <div className="rounded-xl border border-blue-900/20 bg-blue-950/5 px-3 py-2 flex flex-wrap items-center justify-between text-[8px] font-bold tracking-wider text-slate-400 gap-2">
              <div className="flex items-center gap-1"><span className="text-blue-400">PUBLIC WI-FI</span> <span>➔</span></div>
              <div className="flex items-center gap-1"><span className="text-blue-400">METADATA</span> <span>➔</span></div>
              <div className="flex items-center gap-1"><span className="text-blue-400">PREPROCESSING</span> <span>➔</span></div>
              <div className="flex items-center gap-1"><span className="text-blue-400">FEATURE EXTRACTION</span> <span>➔</span></div>
              <div className="flex items-center gap-1"><span className="text-indigo-400">BEHAVIORAL ANALYSIS</span> <span>➔</span></div>
              <div className="flex items-center gap-1"><span className="text-indigo-400">ML MODEL (RF/XGB)</span> <span>➔</span></div>
              <div className="flex items-center gap-1"><span className="text-amber-400">ANOMALY DETECT</span> <span>➔</span></div>
              <div className="flex items-center gap-1"><span className="text-amber-400">TRUST SCORE</span> <span>➔</span></div>
              <div className="flex items-center gap-1"><span className="text-rose-400">CLASSIFICATION</span> <span>➔</span></div>
              <div className="flex items-center gap-1"><span className="text-rose-500">THREAT ALERT</span></div>
            </div>

            {/* 1. OVERVIEW TOP QUADRANT CARD METRIC DECK */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 flex-shrink-0">
              
              {/* CARD 1: CURRENT NETWORK PROFILE */}
              <div className="rounded-xl border border-slate-900 bg-[#0b1424] p-4 flex flex-col justify-between group hover:border-slate-800 transition-colors">
                <div className="flex items-center justify-between border-b border-slate-900 pb-1.5 mb-1.5">
                  <span className="text-[9px] font-extrabold uppercase text-slate-500 tracking-wider">Current Network</span>
                  <span className="text-[8px] font-bold px-1.5 py-0.5 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 rounded uppercase tracking-wider">{mockCentralData.currentNetwork.status}</span>
                </div>
                <div className="space-y-1">
                  <h3 className="text-xs font-extrabold text-white truncate">{mockCentralData.currentNetwork.ssid}</h3>
                  <div className="flex justify-between items-center text-[10px] pt-1">
                    <span className="text-slate-500">State:</span>
                    <span className="text-slate-300 font-semibold">{mockCentralData.currentNetwork.connectionStatus}</span>
                  </div>
                  <div className="flex justify-between items-center text-[10px]">
                    <span className="text-slate-500">RSSI Power:</span>
                    <span className="text-amber-400 font-mono font-bold">{mockCentralData.currentNetwork.signalStrength}</span>
                  </div>
                </div>
              </div>

              {/* CARD 2: RADIAL AI TRUST SCORE GAUGES */}
              <div className="rounded-xl border border-slate-900 bg-[#0b1424] p-4 flex flex-col justify-between group hover:border-slate-800 transition-colors">
                <div className="flex items-center justify-between border-b border-slate-900 pb-1.5 mb-1.5">
                  <span className="text-[9px] font-extrabold uppercase text-slate-500 tracking-wider">AI Trust Score</span>
                  <span className="text-[8px] font-extrabold text-amber-500 uppercase tracking-widest">{mockCentralData.currentNetwork.classification}</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="relative h-12 w-12 flex-shrink-0">
                    <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                      <circle cx="18" cy="18" r="16" fill="none" stroke="#0f172a" strokeWidth="3" />
                      <circle cx="18" cy="18" r="16" fill="none" stroke="#f59e0b" strokeWidth="3" strokeDasharray="100" strokeDashoffset={100 - mockCentralData.currentNetwork.trustScore} />
                    </svg>
                    <div className="absolute inset-0 flex items-center justify-center font-mono font-bold text-xs text-white">
                      {mockCentralData.currentNetwork.trustScore}
                    </div>
                  </div>
                  <div className="flex-grow min-w-0">
                    <div className="text-[10px] text-slate-400 font-medium">Confidence: <span className="font-mono text-white font-bold">{mockCentralData.currentNetwork.modelConfidence}%</span></div>
                    <button 
                      onClick={() => setTrustScorePopup(true)} 
                      className="mt-1 w-full text-center py-1 bg-blue-600/10 hover:bg-blue-600 text-blue-400 hover:text-white rounded text-[8px] font-bold border border-blue-500/10 transition-colors"
                    >
                      View Analysis
                    </button>
                  </div>
                </div>
              </div>

              {/* CARD 3: SECURITY VECTOR ALERT THRESHOLDS */}
              <div className="rounded-xl border border-slate-900 bg-[#0b1424] p-4 flex flex-col justify-between group hover:border-slate-800 transition-colors">
                <div className="flex items-center justify-between border-b border-slate-900 pb-1.5 mb-1.5">
                  <span className="text-[9px] font-extrabold uppercase text-slate-500 tracking-wider">Security Status</span>
                  <span className="h-2 w-2 rounded-full bg-amber-500 animate-pulse"></span>
                </div>
                <div>
                  <div className="text-sm font-black text-amber-500 uppercase tracking-wide">{mockCentralData.currentNetwork.classification}</div>
                  <p className="text-[10px] text-slate-400 mt-1 font-medium">Threats Detected: <span className="font-mono text-white font-black">{mockCentralData.currentNetwork.threatsCount}</span></p>
                </div>
              </div>

              {/* CARD 4: BEHAVIORAL ANOMALY PROFILES */}
              <div className="rounded-xl border border-slate-900 bg-[#0b1424] p-4 flex flex-col justify-between group hover:border-slate-800 transition-colors">
                <div className="flex items-center justify-between border-b border-slate-900 pb-1.5 mb-1.5">
                  <span className="text-[9px] font-extrabold uppercase text-slate-500 tracking-wider">Risk Level</span>
                  <span className="text-[8px] font-bold text-slate-400 font-mono">🎛️ SCALE ALPHA</span>
                </div>
                <div>
                  <div className="text-sm font-black text-slate-200 uppercase tracking-wide">Medium</div>
                  <p className="text-[10px] text-slate-400 mt-1 font-medium">Anomaly Score: <span className="font-mono text-rose-400 font-bold">{mockCentralData.currentNetwork.anomalyScore}%</span></p>
                </div>
              </div>

            </div>

            {/* MIDDLE QUADRANT GRID MODULE ROW: TRAFFIC GRAPHS + RISK DISPERSION MATRIX */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 flex-shrink-0">
              
              {/* 4. NETWORK TRAFFIC BEHAVIORAL MATRIX ANALYSIS */}
              <div className="rounded-xl border border-slate-900 bg-[#0b1424] p-4 lg:col-span-8 flex flex-col justify-between min-h-[260px]">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div>
                    <h3 className="text-xs font-bold text-slate-200 tracking-wide">Network Traffic Analysis</h3>
                    <p className="text-[9px] text-slate-500 font-medium mt-0.5">Behavioral traffic patterns over time</p>
                  </div>
                  <div className="flex self-end sm:self-auto rounded-lg bg-[#060b13] p-0.5 border border-slate-900 text-[9px] font-semibold">
                    <button className="rounded-md bg-blue-600 px-3 py-1 text-white shadow-md shadow-blue-600/15">24h</button>
                    <button className="px-3 py-1 text-slate-500 cursor-not-allowed">7d</button>
                    <button className="px-3 py-1 text-slate-500 cursor-not-allowed">30d</button>
                  </div>
                </div>

                <div className="relative flex-grow mt-4 flex items-end justify-between h-[110px] px-2 border-b border-slate-900/80">
                  {/* Internal custom dynamic vector bars scaling with anomaly markers */}
                  {mockCentralData.trafficAnalysis.timeline.map((t, idx) => (
                    <div key={idx} className="flex flex-col items-center flex-grow group max-w-[48px] px-0.5">
                      <div className="w-full flex items-end gap-[2px] h-20 relative">
                        {t.isAnomaly && (
                          <span className="absolute -top-3 left-1/2 transform -translate-x-1/2 text-[7px] text-rose-500 font-extrabold uppercase animate-bounce">🚨 ANOMALY</span>
                        )}
                        <div className="w-1/3 bg-blue-500 rounded-t-xs" style={{ height: `${(t.upload/181)*100}%` }}></div>
                        <div className="w-1/3 bg-indigo-500 rounded-t-xs" style={{ height: `${(t.download/181)*100}%` }}></div>
                        <div className={`w-1/3 rounded-t-xs ${t.isAnomaly ? 'bg-rose-500 animate-pulse' : 'bg-slate-700'}`} style={{ height: `${(t.packetRate/181)*100}%` }}></div>
                      </div>
                      <span className="text-[8px] font-mono text-slate-600 mt-1">{t.label}</span>
                    </div>
                  ))}
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-3 mt-2 border-t border-slate-900/50 text-[10px] font-medium">
                  <div><span className="text-slate-500 block text-[8px]">Current Rate</span><span className="text-white font-mono font-bold">{mockCentralData.trafficAnalysis.currentRate}</span></div>
                  <div><span className="text-slate-500 block text-[8px]">Average Base</span><span className="text-slate-300 font-mono">{mockCentralData.trafficAnalysis.averageRate}</span></div>
                  <div><span className="text-slate-500 block text-[8px]">Peak Stream</span><span className="text-slate-300 font-mono">{mockCentralData.trafficAnalysis.peakRate}</span></div>
                  <div>
                    <span className="text-slate-500 block text-[8px]">Traffic Anomaly</span>
                    <span className="text-rose-400 font-mono font-bold">{mockCentralData.trafficAnalysis.anomalyPercentage}%</span>
                    {mockCentralData.trafficAnalysis.isAnomalous && <span className="text-[7px] text-rose-500 font-bold block leading-none mt-0.5">Anomalous behavior detected</span>}
                  </div>
                </div>
              </div>

              {/* 5. RISK ANALYSIS CATEGORIZATION MATRIX DONUT PANEL */}
              <div className="rounded-xl border border-slate-900 bg-[#0b1424] p-4 lg:col-span-4 flex flex-col justify-between min-h-[260px]">
                <div>
                  <h3 className="text-xs font-bold text-slate-200 tracking-wide">Risk Analysis</h3>
                  <p className="text-[9px] text-slate-500 font-medium mt-0.5">Networks grouped by classification threshold</p>
                </div>

                <div className="flex items-center justify-center py-2">
                  <div className="relative h-24 w-24">
                    <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                      <circle cx="18" cy="18" r="15.9" fill="none" stroke="#10b981" strokeWidth="4.2" strokeDasharray="62 38" />
                      <circle cx="18" cy="18" r="15.9" fill="none" stroke="#f59e0b" strokeWidth="4.2" strokeDasharray="24 76" strokeDashoffset="-62" />
                      <circle cx="18" cy="18" r="15.9" fill="none" stroke="#ef4444" strokeWidth="4.2" strokeDasharray="10 90" strokeDashoffset="-86" />
                      <circle cx="18" cy="18" r="15.9" fill="none" stroke="#e11d48" strokeWidth="4.2" strokeDasharray="4 96" strokeDashoffset="-96" />
                    </svg>
                    <div className="absolute inset-0 flex flex-col items-center justify-center text-center p-1">
                      <span className="text-xs font-black text-white leading-none">100+</span>
                      <span className="text-[6px] text-slate-500 font-extrabold uppercase tracking-wide mt-0.5">NETWORKS ANALYZED</span>
                    </div>
                  </div>
                </div>

                {/* Clickable category indicators node blocks */}
                <div className="space-y-1">
                  <div className="text-[7px] text-slate-500 uppercase tracking-widest text-center font-bold mb-1">💡 Click tags below to filter node scopes</div>
                  <div className="grid grid-cols-2 gap-1.5">
                    {mockCentralData.riskDistribution.categories.map((c, idx) => (
                      <button 
                        key={idx}
                        onClick={() => setSelectedRiskCategory(selectedRiskCategory === c.name ? null : c.name)}
                        className={`p-1 rounded border text-[9px] text-left flex justify-between items-center transition-all ${
                          selectedRiskCategory === c.name ? 'border-blue-500 bg-blue-950/20' : 'border-slate-900 bg-[#060b13]/40 hover:border-slate-800'
                        }`}
                      >
                        <span className="text-slate-400 flex items-center gap-1.5 truncate">
                          <span className="h-1.5 w-1.5 rounded-full block flex-shrink-0" style={{ backgroundColor: c.color }}></span>
                          {c.name}
                        </span>
                        <span className="font-mono font-bold text-white text-[8px]">{c.percentage}%</span>
                      </button>
                    ))}
                  </div>
                </div>
              </div>

            </div>

            {/* DYNAMIC TOGGLED DISPLAY ELEMENT: RISK CATEGORIES LIST POPUPS */}
            {selectedRiskCategory && (
              <div className="rounded-xl border border-blue-500/20 bg-blue-950/5 p-3 flex flex-col gap-1.5 animate-fadeIn">
                <div className="flex justify-between items-center border-b border-slate-900 pb-1 mb-1">
                  <span className="text-[9px] font-bold text-slate-300">Catalogued Node Mappings tagged as: <span className="text-blue-400 uppercase font-black">{selectedRiskCategory}</span></span>
                  <button onClick={() => setSelectedRiskCategory(null)} className="text-[8px] font-bold text-rose-400 hover:underline">Clear Filter ✕</button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {mockCentralData.riskDistribution.categories.find(c => c.name === selectedRiskCategory)?.networks.map((net, i) => (
                    <span key={i} className="px-2 py-0.5 rounded bg-slate-950 border border-slate-900 text-[9px] font-mono text-slate-300">📶 {net}</span>
                  ))}
                </div>
              </div>
            )}

            {/* LOWER BEHAVIORAL BLOCK MODULES GRID: DEEP COMPONENT ARRAYS */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 flex-shrink-0">
              
              {/* 3. ML BEHAVIORAL ANALYSIS PARADIGMS PANEL */}
              <div className="rounded-xl border border-slate-900 bg-[#0b1424] p-4 flex flex-col justify-between group hover:border-slate-800 transition-colors">
                <div className="flex items-center justify-between border-b border-slate-900 pb-2 mb-2">
                  <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">ML Behavioral Analysis</h4>
                  <span className="text-[8px] font-mono px-1.5 py-0.5 bg-blue-500/10 text-blue-400 rounded border border-blue-500/10 font-bold">CORE MODEL</span>
                </div>
                
                <div className="grid grid-cols-2 gap-2 text-[10px] font-medium my-1">
                  <div className="bg-[#060b13]/50 border border-slate-900/60 p-1.5 rounded">
                    <span className="text-slate-500 text-[8px] block">MODEL REGISTRY</span>
                    <span className="text-white font-bold">{mockCentralData.mlBehavioralAnalysis.model}</span>
                  </div>
                  <div className="bg-[#060b13]/50 border border-slate-900/60 p-1.5 rounded">
                    <span className="text-slate-500 text-[8px] block">PREDICTION STATUS</span>
                    <span className="text-rose-400 font-bold truncate block">{mockCentralData.mlBehavioralAnalysis.prediction}</span>
                  </div>
                  <div className="bg-[#060b13]/50 border border-slate-900/60 p-1.5 rounded">
                    <span className="text-slate-500 text-[8px] block">CONFIDENCE ACCURACY</span>
                    <span className="text-emerald-400 font-mono font-bold">{mockCentralData.mlBehavioralAnalysis.confidence}%</span>
                  </div>
                  <div className="bg-[#060b13]/50 border border-slate-900/60 p-1.5 rounded">
                    <span className="text-slate-500 text-[8px] block">ANOMALY INDEX</span>
                    <span className="text-rose-400 font-mono font-bold">{mockCentralData.mlBehavioralAnalysis.anomalyScore} / 100</span>
                  </div>
                </div>

                <div className="space-y-1.5 my-2">
                  <div className="text-[8px] font-bold text-slate-500 uppercase tracking-wider">Top Contributing Structural Features ({mockCentralData.mlBehavioralAnalysis.featuresAnalyzedCount} Parsed)</div>
                  {mockCentralData.mlBehavioralAnalysis.topFeatures.map((feat, idx) => (
                    <div key={idx} className="space-y-0.5 text-[9px]">
                      <div className="flex justify-between text-slate-300 font-medium">
                        <span>{feat.label}</span>
                        <span className="font-mono text-[8px] text-slate-500">{feat.weight}%</span>
                      </div>
                      <div className="h-1 w-full bg-slate-950 rounded-full overflow-hidden border border-slate-900">
                        <div className="h-full bg-indigo-500" style={{ width: `${feat.weight}%` }}></div>
                      </div>
                    </div>
                  ))}
                </div>

                <button 
                  onClick={() => setModelDetailsPopup(true)}
                  className="w-full text-center py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-[10px] font-bold shadow-md transition-all active:scale-98 mt-1"
                >
                  View Model Details
                </button>
              </div>

              {/* 6. EXTENDED TECHNICAL METADATA NETWORK DETAILS CARD */}
              <div className="rounded-xl border border-slate-900 bg-[#0b1424] p-4 flex flex-col justify-between group hover:border-slate-800 transition-colors">
                <div className="flex items-center justify-between border-b border-slate-900 pb-2 mb-2">
                  <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Network Metadata Details</h4>
                  <span className="text-[8px] px-1.5 py-0.5 bg-rose-500/10 border border-rose-500/20 text-rose-400 rounded font-black tracking-wide uppercase">{mockCentralData.currentNetwork.securityStatusFlag}</span>
                </div>

                <div className="grid grid-cols-2 gap-x-3 gap-y-1.5 text-[10px] font-medium flex-grow justify-center py-1">
                  <div className="flex justify-between border-b border-slate-900/50 pb-0.5"><span className="text-slate-500">SSID:</span><span className="text-white font-semibold truncate max-w-[70px]">{mockCentralData.currentNetwork.ssid}</span></div>
                  <div className="flex justify-between border-b border-slate-900/50 pb-0.5"><span className="text-slate-500">BSSID:</span><span className="text-slate-400 font-mono text-[9px] truncate max-w-[70px]">{mockCentralData.currentNetwork.bssid}</span></div>
                  <div className="flex justify-between border-b border-slate-900/50 pb-0.5"><span className="text-slate-500">Encryption:</span><span className="text-slate-300 truncate max-w-[70px]">{mockCentralData.currentNetwork.encryption}</span></div>
                  <div className="flex justify-between border-b border-slate-900/50 pb-0.5"><span className="text-slate-500">RSSI RSS:</span><span className="text-amber-400 font-mono font-bold">{mockCentralData.currentNetwork.signalStrength}</span></div>
                  <div className="flex justify-between border-b border-slate-900/50 pb-0.5"><span className="text-slate-500">Channel:</span><span className="text-slate-300 font-mono">{mockCentralData.currentNetwork.channel}</span></div>
                  <div className="flex justify-between border-b border-slate-900/50 pb-0.5"><span className="text-slate-500">Band Matrix:</span><span className="text-slate-300 font-mono">{mockCentralData.currentNetwork.band}</span></div>
                  <div className="flex justify-between border-b border-slate-900/50 pb-0.5"><span className="text-slate-500">Bound Log:</span><span className="text-slate-400 font-mono text-[9px]">{mockCentralData.currentNetwork.connectionDuration}</span></div>
                  <div className="flex justify-between border-b border-slate-900/50 pb-0.5"><span className="text-slate-500">GW Latency:</span><span className="text-slate-300 font-mono">{mockCentralData.currentNetwork.gatewayLatency}</span></div>
                  <div className="flex justify-between border-b border-slate-900/50 pb-0.5"><span className="text-slate-500">DNS Delta:</span><span className="text-slate-300 font-mono">{mockCentralData.currentNetwork.dnsResponseTime}</span></div>
                  <div className="flex justify-between border-b border-slate-900/50 pb-0.5"><span className="text-slate-500">Beacon Gap:</span><span className="text-slate-300 font-mono">{mockCentralData.currentNetwork.beaconInterval}</span></div>
                </div>

                <div className="mt-2 p-2 bg-slate-950 rounded border border-slate-900/60 flex items-center justify-between text-[9px]">
                  <span className="text-slate-500 font-medium">Network Security State:</span>
                  <span className="text-rose-500 font-extrabold uppercase">{mockCentralData.currentNetwork.securityStatusFlag}</span>
                </div>
              </div>

              {/* 8. EVIL TWIN ATTACK DETECTION RADAR CARD */}
              <div className="rounded-xl border border-slate-900 bg-[#0b1424] p-4 flex flex-col justify-between group hover:border-slate-800 transition-colors">
                <div className="flex items-center justify-between border-b border-slate-900 pb-2 mb-2">
                  <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Evil Twin Detection</h4>
                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-400"></span>
                </div>

                <div className="space-y-2 text-[10px] font-medium my-auto">
                  <div className="flex justify-between"><span className="text-slate-500">Active Node BSSID:</span><span className="text-slate-300 font-mono text-[9px]">{mockCentralData.evilTwinMetrics.currentBssid}</span></div>
                  <div className="flex justify-between"><span className="text-slate-500">Nearby Cloned SSIDs:</span><span className="text-amber-400 font-mono font-bold">{mockCentralData.evilTwinMetrics.nearbySimilarSsids} instances</span></div>
                  <div className="flex justify-between"><span className="text-slate-500">Signature Sync:</span><span className="text-emerald-400 font-semibold">{mockCentralData.evilTwinMetrics.bssidMatchStatus}</span></div>
                  <div className="flex justify-between"><span className="text-slate-500">Beacon Shift Delta:</span><span className="text-slate-300 font-bold">{mockCentralData.evilTwinMetrics.beaconDeviation} Threshold</span></div>
                </div>

                <div className="mt-3 p-2 rounded bg-emerald-950/10 border border-emerald-900/20 text-center font-bold text-[10px] text-emerald-400">
                  🛡️ {mockCentralData.evilTwinMetrics.status}
                </div>
              </div>

            </div>

            {/* DYNAMIC METRIC ARRAYS ROW: DNS INTERCEPTORS + TIMELINE RECONNECT TRACKERS */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 flex-shrink-0">
              
              {/* 9. DNS BEHAVIOR ANALYSIS CARD WITH INLINE SPARKLINES */}
              <div className="rounded-xl border border-slate-900 bg-[#0b1424] p-4 flex flex-col justify-between group hover:border-slate-800 transition-colors">
                <div className="flex items-center justify-between border-b border-slate-900 pb-2 mb-2">
                  <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">DNS Behavior Analysis</h4>
                  <span className="text-[8px] font-mono font-extrabold text-amber-500 bg-amber-500/10 px-1.5 py-0.5 rounded border border-amber-500/10">SUSPICIOUS PROFILE</span>
                </div>

                <div className="grid grid-cols-2 gap-3 text-[10px] font-medium my-2">
                  <div className="space-y-1.5">
                    <div className="flex justify-between"><span className="text-slate-500">Resolver Delta:</span><span className="text-white font-mono font-bold">{mockCentralData.dnsBehaviorMetrics.responseTime}</span></div>
                    <div className="flex justify-between"><span className="text-slate-500">Expected Scope:</span><span className="text-slate-400 font-mono">{mockCentralData.dnsBehaviorMetrics.expectedRange}</span></div>
                    <div className="flex justify-between"><span className="text-slate-500">Path Deviation:</span><span className="text-rose-400 font-mono font-bold">{mockCentralData.dnsBehaviorMetrics.deviation}</span></div>
                    <div className="flex justify-between"><span className="text-slate-500">DNS Integrity:</span><span className="text-amber-400 font-mono font-bold">{mockCentralData.dnsBehaviorMetrics.integrity}</span></div>
                  </div>

                  {/* Tiny simulated vector bounding line chart representing DNS delays */}
                  <div className="bg-slate-950 rounded border border-slate-900 p-2 flex items-end justify-between h-[64px]">
                    {mockCentralData.dnsBehaviorMetrics.chartData.map((val, i) => (
                      <div key={i} className="w-2 bg-blue-600 rounded-t-xs" style={{ height: `${(val/125)*100}%` }} title={`${val} ms`}></div>
                    ))}
                  </div>
                </div>

                <div className="p-1.5 rounded bg-amber-950/10 border border-amber-900/20 text-center text-[9px] font-extrabold text-amber-400 uppercase tracking-wide">
                  ⚠️ STATUS: {mockCentralData.dnsBehaviorMetrics.status}
                </div>
              </div>

              {/* 10. RECONNECT / SESSION TIMELINE CONNECTION BEHAVIOR CARD */}
              <div className="rounded-xl border border-slate-900 bg-[#0b1424] p-4 flex flex-col justify-between group hover:border-slate-800 transition-colors">
                <div className="flex items-center justify-between border-b border-slate-900 pb-2 mb-2">
                  <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Connection Behavior</h4>
                  <span className="text-[8px] text-slate-400 font-mono">FLOW TIMELINE</span>
                </div>

                <div className="grid grid-cols-2 gap-3 text-[10px] font-medium my-2">
                  <div className="space-y-1.5">
                    <div className="flex justify-between"><span className="text-slate-500">Flow Session:</span><span className="text-white font-mono">{mockCentralData.connectionBehaviorMetrics.duration}</span></div>
                    <div className="flex justify-between"><span className="text-slate-500">Handshake Loops:</span><span className="text-amber-400 font-mono font-bold">{mockCentralData.connectionBehaviorMetrics.attempts} retries</span></div>
                    <div className="flex justify-between"><span className="text-slate-500">Avg Loop Window:</span><span className="text-slate-400 font-mono">{mockCentralData.connectionBehaviorMetrics.avgInterval}</span></div>
                    <div className="flex justify-between"><span className="text-slate-500">Loop Anomaly:</span><span className="text-rose-400 font-mono font-bold">{mockCentralData.connectionBehaviorMetrics.anomalyScore}%</span></div>
                  </div>

                  {/* Reconnect timeline mini graph bar chart layout structure */}
                  <div className="bg-slate-950 rounded border border-slate-900 p-2 flex items-end justify-between h-[64px]">
                    {mockCentralData.connectionBehaviorMetrics.timeline.map((val, i) => (
                      <div key={i} className="w-2 bg-indigo-500 rounded-t-xs" style={{ height: `${(val/7)*100}%` }}></div>
                    ))}
                  </div>
                </div>

                <div className="p-1.5 bg-slate-950 rounded border border-slate-900 text-slate-400 font-medium text-[9px] text-center truncate">
                  🔄 Iterative Frame Re-association Rhythm Analysis Complete
                </div>
              </div>

            </div>

            {/* 7. DETAILED RECENT LOG THREAT DETECTION ALERTS BLOCK */}
            <div className="rounded-xl border border-slate-900 bg-[#0b1424] p-4 flex-shrink-0">
              <div className="flex justify-between items-center border-b border-slate-900 pb-2 mb-3">
                <div>
                  <h4 className="text-xs font-bold text-slate-200 tracking-wide">Threat Detection Feed</h4>
                  <p className="text-[9px] text-slate-500 font-medium">Categorized vectors tracked across active environment frames</p>
                </div>
                <span className="text-[8px] text-slate-500 font-mono font-bold">REAL-TIME THREAT LEDGER</span>
              </div>

              <div className="space-y-2 max-h-[180px] overflow-y-auto pr-1">
                {mockCentralData.threatsList.slice(0, 3).map((threat, idx) => (
                  <div key={idx} className="p-2.5 rounded-xl bg-[#060b13]/60 border border-slate-900 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-[10px] font-medium hover:border-slate-800 transition-colors">
                    <div className="flex items-start gap-2.5 min-w-0">
                      <span className="text-xs flex-shrink-0 mt-0.5">{threat.severity === 'CRITICAL' || threat.severity === 'HIGH' ? '🚨' : '⚠️'}</span>
                      <div className="min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="font-extrabold text-white">{threat.type}</span>
                          <span className="text-[8px] font-mono text-slate-500">({threat.network})</span>
                          <span className={`text-[7px] font-extrabold px-1.5 py-0.2 rounded border ${
                            threat.severity === 'CRITICAL' ? 'bg-red-500/10 border-red-500/20 text-red-400' :
                            threat.severity === 'HIGH' ? 'bg-rose-500/10 border-rose-500/20 text-rose-400' :
                            'bg-amber-500/10 border-amber-500/20 text-amber-400'
                          }`}>{threat.severity}</span>
                        </div>
                        <p className="text-[9px] text-slate-400 mt-0.5 leading-normal">{threat.desc}</p>
                      </div>
                    </div>
                    <div className="text-right flex-shrink-0 self-end sm:self-auto text-[8px] font-mono text-slate-500">
                      <div>{threat.time}</div>
                      <div className="mt-0.5 text-blue-400 font-sans font-bold uppercase">{threat.status}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* 14. BOTTOM STATUS/ACTIVITY STREAM LOGGER RECENT BANNER */}
            <div className="rounded-xl border border-slate-900 bg-[#0b1424] p-3 flex-shrink-0">
              <div className="text-[8px] font-bold text-slate-500 uppercase tracking-widest mb-2">🐾 Real-time Pipeline Pipeline Audits</div>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2 text-[9px] font-medium">
                {mockCentralData.recentActivity.map((act, i) => (
                  <div key={i} className="flex items-center gap-2 bg-[#060b13]/60 border border-slate-900/50 p-1.5 rounded-lg truncate">
                    <span className="flex-shrink-0">{act.icon}</span>
                    <div className="truncate min-w-0">
                      <p className="text-slate-200 truncate leading-none font-bold">{act.desc}</p>
                      <span className="text-[7px] text-slate-500 font-mono mt-0.5 block">{act.time} • {act.network}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

          </div>
        )}

        {/* RENDER VIEWPORT MAP: TAB 2 (11. IMPROVED WIRELESS ENVIRONMENT METADATA SCANNER VIEW) */}
        {activeTab === 'Scan Network' && (
          <div className="flex-grow flex flex-col justify-center items-center gap-5 bg-[#0b1424] rounded-xl border border-slate-900 p-6 mt-4 max-w-4xl mx-auto w-full">
            
            <div className="relative flex items-center justify-center">
              <div className={`h-28 w-28 rounded-full border-2 border-dashed border-blue-500/30 flex items-center justify-center text-3xl bg-blue-500/5 ${isScanning ? 'animate-spin border-blue-500' : ''}`}>
                <span>📶</span>
              </div>
              {isScanning && (
                <div className="absolute text-xs font-mono font-bold text-blue-400 mt-20 bg-slate-950 px-1.5 py-0.5 rounded border border-slate-800">
                  {scanProgress}%
                </div>
              )}
            </div>

            <div className="text-center max-w-md">
              <h2 className="text-sm font-bold text-white tracking-wide">
                {isScanning ? 'Extracting Micro-Frames & Intercepting Handshakes...' : scanExecuted ? 'Scan Protocol Mapping Complete' : 'Metadata Feature Data Acquisition Radar'}
              </h2>
              <p className="text-[10px] text-slate-500 mt-1 leading-relaxed font-medium">
                {isScanning 
                  ? 'Compiling wireless beacon intervals, grouping BSSID consistency matrices, and assessing traffic flow fluctuations without checking payload data arrays...' 
                  : scanExecuted 
                  ? 'Discovered active network topologies within range boundaries. Review localized AI risk valuations below.'
                  : 'Triggers a passive, metadata-driven environmental probe across current airspace frequency boundaries to pipe metrics directly into Random Forest / XGBoost models.'}
              </p>
            </div>

            {!isScanning && !scanExecuted && (
              <button 
                onClick={startScanSequence} 
                className="px-6 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-bold text-xs shadow-md shadow-blue-600/10 active:scale-95 transition-all"
              >
                Launch Wireless Metadata Scan
              </button>
            )}

            {scanExecuted && !isScanning && (
              <div className="w-full space-y-3 animate-fadeIn">
                <div className="flex justify-between items-center border-b border-slate-900 pb-1.5">
                  <span className="text-[10px] font-bold text-slate-300">Environment Node Discoveries ({mockCentralData.scannerData.length} Indexed)</span>
                  <button onClick={startScanSequence} className="text-[9px] font-bold text-blue-400 hover:underline">🔄 Rescan Airspace</button>
                </div>

                <div className="overflow-x-auto border border-slate-900 rounded-xl bg-slate-950/40">
                  <table className="w-full text-left border-collapse text-[10px] font-medium">
                    <thead>
                      <tr className="border-b border-slate-900 bg-[#060b13] text-slate-500 text-[9px] font-bold uppercase tracking-wider">
                        <th className="p-3">Compare</th>
                        <th className="p-3">SSID MAPPING</th>
                        <th className="p-3">BSSID SPEC</th>
                        <th className="p-3">RSSI POWER</th>
                        <th className="p-3">ENCRYPTION TYPE</th>
                        <th className="p-3 text-center">TRUST PROFILE</th>
                        <th className="p-3 text-right">RISK VALUE</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-900/60 font-mono text-slate-300">
                      {mockCentralData.scannerData.map((node, i) => {
                        const isCompared = comparisonList.some(c => c.ssid === node.ssid);
                        return (
                          <tr key={i} className="hover:bg-[#0b1424]/40 transition-colors">
                            <td className="p-3">
                              <input 
                                type="checkbox" 
                                checked={isCompared}
                                onChange={() => toggleComparisonSelection(node)}
                                className="rounded bg-slate-900 border-slate-800 text-blue-600 focus:ring-0" 
                              />
                            </td>
                            <td className="p-3 font-sans font-bold text-white">{node.ssid}</td>
                            <td className="p-3 text-slate-500 text-[9px]">{node.bssid}</td>
                            <td className="p-3 text-slate-400">{node.signal}</td>
                            <td className="p-3 font-sans text-slate-400 text-[9px]">{node.encryption}</td>
                            <td className="p-3 text-center">
                              <span className="px-2 py-0.5 rounded bg-slate-900 border border-slate-900 text-white font-bold">{node.trustScore}/100</span>
                            </td>
                            <td className="p-3 text-right font-sans">
                              <span className={`text-[8px] font-extrabold px-1.5 py-0.2 rounded border ${
                                node.status === 'Safe' ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' :
                                node.status === 'Caution' ? 'bg-amber-500/10 border-amber-500/20 text-amber-400' :
                                'bg-rose-500/10 border-rose-500/20 text-rose-400'
                              }`}>{node.status}</span>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>

                {/* 12. NETWORK METADATA DYNAMIC DRIVEN COMPARISON VIEWBLOCK ENGINE */}
                {comparisonList.length >= 2 && (
                  <div className="p-4 rounded-xl border border-blue-900/40 bg-blue-950/10 mt-4 space-y-3 animate-slideUp">
                    <div className="flex justify-between items-center border-b border-blue-900/30 pb-1.5">
                      <span className="text-[10px] font-bold text-blue-400 uppercase tracking-wider flex items-center gap-1">📊 Side-by-Side Model Differential Matrix</span>
                      <button onClick={() => setComparisonList([])} className="text-[9px] font-bold text-rose-400 hover:underline">Reset Matrix</button>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-[10px] font-medium">
                      {comparisonList.map((net, i) => (
                        <div key={i} className="p-3 rounded-xl bg-slate-950 border border-slate-900 space-y-2">
                          <h5 className="font-sans font-bold text-white text-xs border-b border-slate-900 pb-1">{net.ssid}</h5>
                          <div className="space-y-1 text-slate-400">
                            <div className="flex justify-between"><span className="text-slate-500">AI Trust Score:</span><span className="font-bold text-white">{net.trustScore}/100</span></div>
                            <div className="flex justify-between"><span className="text-slate-500">RSSI Power:</span><span className="text-amber-400">{net.signal}</span></div>
                            <div className="flex justify-between"><span className="text-slate-500">Encryption:</span><span className="truncate max-w-[90px] text-[9px]">{net.encryption}</span></div>
                            <div className="flex justify-between"><span className="text-slate-500">Classification:</span><span className="font-bold text-slate-200">{net.status}</span></div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                {comparisonList.length === 1 && (
                  <p className="text-[9px] text-blue-400 font-medium text-center bg-blue-950/5 p-2 rounded border border-blue-900/10">💡 Select at least one more network checkbox above to compile the side-by-side behavioral comparison matrix view.</p>
                )}
              </div>
            )}
          </div>
        )}

        {/* RENDER VIEWPORT MAP: TAB 3 (MY NETWORKS SAVED HISTORY RECORD REGISTRY) */}
        {activeTab === 'My Networks' && (
          <div className="flex-grow flex flex-col gap-3 mt-4 overflow-y-auto pr-1 max-w-4xl mx-auto w-full">
            <p className="text-[10px] text-slate-500 font-medium">Manage and view structural risk classifications for access profiles mapped to this terminal device.</p>
            <div className="grid grid-cols-1 gap-2.5">
              {mockCentralData.scannerData.map((net, idx) => (
                <div key={idx} className="rounded-xl border border-slate-900 bg-[#0b1424] p-3.5 flex items-center justify-between hover:border-slate-800 transition-colors">
                  <div className="flex items-center gap-3 min-w-0">
                    <div className="h-8 w-8 rounded-lg bg-slate-950 flex items-center justify-center text-sm flex-shrink-0">📶</div>
                    <div className="min-w-0">
                      <h3 className="text-xs font-bold text-white truncate">{net.ssid}</h3>
                      <p className="text-[9px] font-mono text-slate-500 truncate">{net.bssid} • <span className="text-slate-400 font-sans font-medium">{net.encryption}</span></p>
                    </div>
                  </div>
                  <div className="text-right flex-shrink-0">
                    <span className={`text-[8px] font-extrabold px-2 py-0.5 rounded border tracking-wider uppercase ${
                      net.status === 'Safe' ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' : 'bg-amber-500/10 border-amber-500/20 text-amber-400'
                    }`}>{net.status}</span>
                    <p className="text-[10px] text-slate-300 font-bold font-mono mt-1">{net.trustScore}/100</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* RENDER VIEWPORT MAP: TAB 4 (15. ENHANCED ADVANCED ALERTS LEDGER FILTER SYSTEM) */}
        {activeTab === 'Alerts' && (
          <div className="flex-grow flex flex-col gap-3 mt-4 overflow-y-auto pr-1 max-w-4xl mx-auto w-full">
            <div className="flex rounded-xl bg-slate-950 p-1 border border-slate-900 overflow-x-auto text-[9px] font-bold tracking-wide gap-1">
              {['All', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'Resolved'].map((filter) => (
                <button
                  key={filter}
                  onClick={() => setActiveAlertFilter(filter)}
                  className={`px-3 py-1.5 rounded-lg whitespace-nowrap transition-all ${
                    activeAlertFilter === filter ? 'bg-blue-600 text-white shadow' : 'text-slate-500 hover:text-slate-300'
                  }`}
                >
                  {filter}
                </button>
              ))}
            </div>

            <div className="space-y-2.5 mt-2">
              {mockCentralData.threatsList
                .filter(t => activeAlertFilter === 'All' ? true : activeAlertFilter === 'Resolved' ? t.status === 'Resolved' : t.severity === activeAlertFilter && t.status !== 'Resolved')
                .map((alert, idx) => (
                  <div key={idx} className="rounded-xl border border-slate-900 bg-[#0b1424] p-4 flex gap-3 items-start hover:border-slate-800 transition-colors">
                    <span className="text-base text-rose-500 flex-shrink-0">🚨</span>
                    <div className="flex-grow min-w-0 grid sm:grid-cols-4 gap-2 items-center text-[10px] font-medium">
                      <div className="sm:col-span-2 min-w-0">
                        <div className="flex items-center gap-2">
                          <h4 className="font-bold text-slate-200 truncate">{alert.type}</h4>
                          <span className="text-[7px] font-mono bg-slate-950 px-1 py-0.2 rounded border border-slate-900 text-slate-400 truncate">{alert.network}</span>
                        </div>
                        <p className="text-[9px] text-slate-400 mt-1 leading-relaxed">{alert.desc}</p>
                      </div>
                      <div className="text-slate-500 font-mono text-[9px] sm:text-center">{alert.time}</div>
                      <div className="sm:text-right flex items-center sm:justify-end gap-2 flex-wrap">
                        <span className="text-[7px] font-black px-1.5 py-0.5 rounded uppercase bg-rose-500/10 text-rose-400 border border-rose-500/15">{alert.severity}</span>
                        <span className="text-[8px] font-bold uppercase text-blue-400">{alert.status}</span>
                      </div>
                    </div>
                  </div>
                ))}
              {mockCentralData.threatsList.filter(t => activeAlertFilter === 'All' ? true : activeAlertFilter === 'Resolved' ? t.status === 'Resolved' : t.severity === activeAlertFilter && t.status !== 'Resolved').length === 0 && (
                <div className="p-6 text-center text-slate-500 text-[10px] font-medium bg-slate-950 rounded-xl border border-slate-900">
                  🍃 No flagged micro-frame alert states conform to this feature filter envelope.
                </div>
              )}
            </div>
          </div>
        )}

        {/* RENDER VIEWPORT MAP: TAB 5 (16. HISTORICAL PREDICTIVE OPERATIONS DECK MONITOR) */}
        {activeTab === 'History' && (
          <div className="flex-grow flex flex-col gap-4 mt-4 overflow-y-auto pr-1 max-w-4xl mx-auto w-full">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-center text-[10px] font-bold">
              <div className="bg-[#0b1424] border border-slate-900 p-3 rounded-xl"><span className="text-slate-500 block text-[8px] mb-0.5">TREND SCORE ACCUMULATION</span><span className="text-white font-mono text-xs">64 ➔ 81 ➔ 94</span></div>
              <div className="bg-[#0b1424] border border-slate-900 p-3 rounded-xl"><span className="text-slate-500 block text-[8px] mb-0.5">RISK PROFILE ENHANCEMENT</span><span className="text-emerald-400 text-xs">Improving Base</span></div>
              <div className="bg-[#0b1424] border border-slate-900 p-3 rounded-xl"><span className="text-slate-500 block text-[8px] mb-0.5">THREAT RECOGNITION TALLY</span><span className="text-rose-500 font-mono text-xs">5 Vectors Logged</span></div>
            </div>

            <div className="rounded-xl border border-slate-900 bg-[#0b1424] p-4 flex-grow flex flex-col">
              <div className="flex justify-between text-slate-500 border-b border-slate-900 pb-2 text-[9px] font-bold tracking-wider uppercase">
                <span>SECURITY OPERATION AUDIT SPEC</span>
                <span className="w-24 text-center">TIMESTAMP</span>
                <span className="w-24 text-right">ML PREDICTION</span>
              </div>
              <div className="divide-y divide-slate-900/50 flex-grow flex flex-col justify-around font-mono text-[9px] py-2 gap-2">
                <div className="flex justify-between items-center py-1.5 text-slate-300">
                  <span className="truncate font-sans font-medium text-slate-200">🔍 Airspace frame metadata sweep parsed — 4 Access Hubs Indexed</span>
                  <span className="w-24 text-center text-slate-500">2:40 PM</span>
                  <span className="w-24 text-right text-emerald-400 font-bold uppercase">Normal Base</span>
                </div>
                <div className="flex justify-between items-center py-1.5 text-slate-300">
                  <span className="truncate font-sans font-medium text-slate-200">🔒 XGBoost model pipeline validation check executed</span>
                  <span className="w-24 text-center text-slate-500">2:14 PM</span>
                  <span className="w-24 text-right text-blue-400 font-bold uppercase">Synced</span>
                </div>
                <div className="flex justify-between items-center py-1.5 text-slate-300">
                  <span className="truncate font-sans font-medium text-slate-200">🚨 Mitigated rogue duplicate broadcast twin frame vector anomaly</span>
                  <span className="w-24 text-center text-slate-500">1:05 PM</span>
                  <span className="w-24 text-right text-rose-500 font-bold uppercase">Suspicious</span>
                </div>
                <div className="flex justify-between items-center py-1.5 text-slate-300">
                  <span className="truncate font-sans font-medium text-slate-200">📶 Network profile tracking instantiated: Cafe_Free_WiFi</span>
                  <span className="w-24 text-center text-slate-500">12:54 PM</span>
                  <span className="w-24 text-right text-amber-500 font-bold uppercase">Suspicious</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* RENDER VIEWPORT MAP: TAB 6 (13 & 17. AUTOMATED RISK DRIVEN RECOMMENDATIONS ENGINE) */}
        {activeTab === 'Recommendations' && (
          <div className="flex-grow flex flex-col gap-3 mt-4 overflow-y-auto pr-1 max-w-4xl mx-auto w-full">
            <p className="text-[10px] text-slate-500 font-medium">Automated cryptographic & architectural adaptations generated from active micro-feature network classifications.</p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {localRecommendations.map((rec) => (
                <div 
                  key={rec.id} 
                  className={`rounded-xl border p-4 flex flex-col justify-between group transition-all ${
                    rec.reviewed ? 'border-slate-900 bg-[#0b1424]/40 opacity-50' : 'border-slate-900 bg-[#0b1424] hover:border-blue-500/20'
                  }`}
                >
                  <div>
                    <div className="flex items-center justify-between border-b border-slate-900 pb-1.5 mb-2">
                      <span className="text-[9px] font-extrabold text-white uppercase tracking-wider">📁 {rec.type}</span>
                      <span className={`text-[7px] font-black px-1.5 py-0.2 rounded ${
                        rec.severity === 'CRITICAL' ? 'bg-red-500/20 text-red-400' :
                        rec.severity === 'HIGH' ? 'bg-rose-500/20 text-rose-400' :
                        rec.severity === 'WARNING' ? 'bg-amber-500/20 text-amber-400' :
                        'bg-blue-500/20 text-blue-400'
                      }`}>{rec.severity}</span>
                    </div>
                    <p className="text-[10px] text-slate-300 leading-relaxed font-medium">{rec.text}</p>
                  </div>
                  <button 
                    disabled={rec.reviewed}
                    onClick={() => handleMarkReview(rec.id)}
                    className={`mt-4 w-full py-1.5 rounded-lg font-bold text-[10px] border transition-all ${
                      rec.reviewed 
                        ? 'bg-slate-950 border-slate-900 text-slate-600 cursor-not-allowed' 
                        : 'bg-blue-600/10 hover:bg-blue-600 text-blue-400 hover:text-white border-blue-500/10'
                    }`}
                  >
                    {rec.reviewed ? '✓ Reviewed & Logged' : 'Mark as Reviewed'}
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* RENDER VIEWPORT MAP: TAB 7 (OPERATOR ENGINE PREFERENCE SETTINGS CONSTRAINTS) */}
        {activeTab === 'Settings' && (
          <div className="flex-grow flex flex-col gap-3 mt-4 max-w-2xl mx-auto w-full">
            <div className="rounded-xl border border-slate-900 bg-[#0b1424] p-4 space-y-4 text-xs font-medium">
              <div className="flex justify-between items-center border-b border-slate-900/60 pb-3">
                <div>
                  <h4 className="text-slate-200 font-bold">Automated Threat Mitigation Action</h4>
                  <p className="text-[9px] text-slate-500 mt-0.5">Sever connections instantly if rogue broadcast frames or twin anomalies scale beyond threshold.</p>
                </div>
                <button 
                  onClick={() => toggleSetting('autoMitigate')}
                  className={`w-9 h-5 rounded-full p-0.5 transition-colors relative flex items-center ${settings.autoMitigate ? 'bg-blue-600 justify-end' : 'bg-slate-800 justify-start'}`}
                >
                  <span className="h-4 w-4 bg-white rounded-full shadow-md"></span>
                </button>
              </div>

              <div className="flex justify-between items-center border-b border-slate-900/60 pb-3">
                <div>
                  <h4 className="text-slate-200 font-bold">Deep Heuristic Anomaly Parser</h4>
                  <p className="text-[9px] text-slate-500 mt-0.5">Run intensive mathematical classification matrices across passive ambient network signals.</p>
                </div>
                <button 
                  onClick={() => toggleSetting('heuristicEngine')}
                  className={`w-9 h-5 rounded-full p-0.5 transition-colors relative flex items-center ${settings.heuristicEngine ? 'bg-blue-600 justify-end' : 'bg-slate-800 justify-start'}`}
                >
                  <span className="h-4 w-4 bg-white rounded-full shadow-md"></span>
                </button>
              </div>

              <div className="flex justify-between items-center">
                <div>
                  <h4 className="text-slate-200 font-bold">System Warning Push Framework</h4>
                  <p className="text-[9px] text-slate-500 mt-0.5">Emit low-level desktop shell warnings immediately when features drop below basic trust profiles.</p>
                </div>
                <button 
                  onClick={() => toggleSetting('notifyThreats')}
                  className={`w-9 h-5 rounded-full p-0.5 transition-colors relative flex items-center ${settings.notifyThreats ? 'bg-blue-600 justify-end' : 'bg-slate-800 justify-start'}`}
                >
                  <span className="h-4 w-4 bg-white rounded-full shadow-md"></span>
                </button>
              </div>
            </div>
          </div>
        )}

        {/* RENDER VIEWPORT MAP: TAB 8 (OPERATOR SYSTEM CREDENTIAL CLEARANCE PROFILE) */}
        {activeTab === 'Profile' && (
          <div className="flex-grow flex flex-col justify-center items-center mt-4">
            <div className="rounded-xl border border-slate-900 bg-[#0b1424] p-5 text-center max-w-xs w-full shadow-xl">
              <div className="h-14 w-14 bg-gradient-to-tr from-blue-600 to-indigo-500 rounded-2xl flex items-center justify-center text-lg font-bold mx-auto mb-3 text-white shadow-lg">U</div>
              <h3 className="text-xs font-bold text-white tracking-wide">Security Dashboard Operator</h3>
              <p className="text-[8px] text-slate-500 font-mono mt-0.5">ID: COGNIFY-849-FEE</p>
              
              <div className="mt-4 pt-3 border-t border-slate-900 text-left space-y-2 text-[10px] font-medium">
                <div className="flex justify-between"><span className="text-slate-500">Security Clearance</span><span className="text-blue-400 font-bold">Root Admin</span></div>
                <div className="flex justify-between"><span className="text-slate-500">Inspected Access Hubs</span><span className="text-white font-mono">142 Scanned</span></div>
                <div className="flex justify-between"><span className="text-slate-500">Account License</span><span className="text-emerald-400 font-bold">Active</span></div>
              </div>
            </div>
          </div>
        )}

        {/* ====================================================================
            MODAL OVERLAYS AND EXPANDABLE DETAILED PANELS
        ==================================================================== */}
        
        {/* 2. DEDICATED MODEL DIALOG: AI TRUST SCORE ANALYSIS OVERLAY */}
        {trustScorePopup && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 p-4 backdrop-blur-xs animate-fadeIn">
            <div className="w-full max-w-lg rounded-2xl border border-slate-800 bg-[#0b1424] p-5 shadow-2xl relative space-y-4">
              <div className="flex justify-between items-center border-b border-slate-900 pb-2.5">
                <div>
                  <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">AI Trust Score Analysis</h3>
                  <p className="text-[10px] text-slate-500 font-medium">Granular metadata parameter distribution score updates</p>
                </div>
                <button onClick={() => setTrustScorePopup(false)} className="text-[11px] font-bold text-slate-400 hover:text-white">✕ Close</button>
              </div>

              <div className="flex items-center justify-between p-3 bg-slate-950 rounded-xl border border-slate-900 text-[10px] font-medium">
                <div><span className="text-slate-500 text-[8px] block">OVERALL SCORE</span><span className="text-white font-mono text-sm font-black">{mockCentralData.trustScoreAnalysis.score} / 100</span></div>
                <div><span className="text-slate-500 text-[8px] block">CLASSIFICATION</span><span className="text-amber-500 font-extrabold text-xs uppercase">{mockCentralData.trustScoreAnalysis.classification}</span></div>
                <div><span className="text-slate-500 text-[8px] block">MODEL CONFIDENCE</span><span className="text-emerald-400 font-mono text-xs font-bold">{mockCentralData.trustScoreAnalysis.confidence}%</span></div>
              </div>

              <div className="space-y-2.5 max-h-[220px] overflow-y-auto pr-1">
                {mockCentralData.trustScoreAnalysis.factors.map((factor, i) => (
                  <div key={i} className="text-[10px] font-medium space-y-1">
                    <div className="flex justify-between items-baseline">
                      <span className="text-slate-200 font-bold">{factor.name}</span>
                      <span className="font-mono font-bold text-blue-400">{factor.score}%</span>
                    </div>
                    <div className="h-1.5 w-full bg-slate-950 rounded-full overflow-hidden border border-slate-900">
                      <div className="h-full bg-blue-500" style={{ width: `${factor.score}%` }}></div>
                    </div>
                    <p className="text-[9px] text-slate-400 leading-normal">{factor.text}</p>
                  </div>
                ))}
              </div>

              <div className="pt-2 border-t border-slate-900 flex justify-between items-center">
                <button 
                  onClick={() => setCalculationExplanation(!calculationExplanation)} 
                  className="text-[9px] text-blue-400 font-bold hover:underline"
                >
                  {calculationExplanation ? 'Hide Computation Protocol ▲' : 'How is this score calculated? ▼'}
                </button>
              </div>

              {calculationExplanation && (
                <div className="p-3 bg-slate-950 rounded-xl border border-slate-900 text-[9px] text-slate-400 leading-relaxed font-medium animate-slideUp">
                  ℹ️ This metric is calculated by extraction of behavioral network features mapped across live weights against static models. It monitors structural transformations inside frames rather than tracking cleartext contents.
                </div>
              )}
            </div>
          </div>
        )}

        {/* MODAL OVERLAY: MACHINE LEARNING METRIC DETAILS COMPONENT */}
        {modelDetailsPopup && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 p-4 backdrop-blur-xs animate-fadeIn">
            <div className="w-full max-w-sm rounded-2xl border border-slate-800 bg-[#0b1424] p-5 shadow-2xl space-y-4">
              <div className="flex justify-between items-center border-b border-slate-900 pb-2">
                <h4 className="text-xs font-bold text-white tracking-wide">Model Details Envelope</h4>
                <button onClick={() => setModelDetailsPopup(false)} className="text-[10px] font-bold text-slate-400 hover:text-white">✕ Close</button>
              </div>
              <p className="text-[10px] text-slate-400 leading-relaxed font-medium">
                The integrated setup routes preprocessed metadata vectors through trained <span className="text-white font-bold">Random Forest</span> and <span className="text-white font-bold">XGBoost</span> hyper-parameter profiles.
              </p>
              <div className="bg-slate-950 p-3 rounded-xl border border-slate-900 space-y-1 text-[9px] text-slate-500 font-mono">
                <div>[INFO] pipeline initialized ... OK</div>
                <div>[INFO] local model fallback synced ... OK</div>
                <div>[WARN] backend api endpoint disconnected.</div>
                <div className="text-blue-400 font-bold mt-2">➔ Frontend API endpoints prepared for immediate Flask server substitution.</div>
              </div>
            </div>
          </div>
        )}

      </main>
    </div>
  );
}