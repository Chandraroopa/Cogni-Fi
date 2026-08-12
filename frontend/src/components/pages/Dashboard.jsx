import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useNavigate } from 'react-router-dom';

function Dashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();
  // ============================================================
  // STATE
  // ============================================================

  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [scanning, setScanning] = useState(false);
  const [networks, setNetworks] = useState([]);
  const [selectedNetwork, setSelectedNetwork] = useState(null);

  // ============================================================
  // TEMPORARY WIFI DATA
  // Replace this later with Flask API response
  // ============================================================

  const mockNetworks = [
    {
      id: 1,
      name: 'Cafe_Free_WiFi',
      type: 'Open Network',
      signal: 92,
      security: 'Open',
      channel: 6,
    },
    {
      id: 2,
      name: 'Canara_Engineering',
      type: 'Saved Network',
      signal: 78,
      security: 'WPA2',
      channel: 36,
    },
    {
      id: 3,
      name: 'Home_Network',
      type: 'Saved Network',
      signal: 64,
      security: 'WPA2',
      channel: 11,
    },
    {
      id: 4,
      name: 'Public_WiFi',
      type: 'Open Network',
      signal: 45,
      security: 'Open',
      channel: 1,
    },
    {
      id: 5,
      name: 'Office_Network',
      type: 'Saved Network',
      signal: 28,
      security: 'WPA3',
      channel: 149,
    },
    {
      id: 6,
      name: 'Guest_WiFi',
      type: 'Open Network',
      signal: 18,
      security: 'Open',
      channel: 6,
    },
  ];

  // ============================================================
  // MODULE 1: WIFI SCANNING
  // ============================================================

  const handleScan = () => {
    setScanning(true);
    setSelectedNetwork(null);

    // Temporary simulation.
    // Later this will call your Flask backend.
    setTimeout(() => {
      setNetworks(mockNetworks);
      setScanning(false);
    }, 1500);
  };

  // ============================================================
  // MODULE 2: NETWORK SELECTION
  // ============================================================

  const handleSelectNetwork = (network) => {
    setSelectedNetwork(network);
  };

  // ============================================================
  // MODULE 3: ANALYZE NETWORK
  // ============================================================

  const handleAnalyze = () => {
    if (!selectedNetwork) return;

    // Later:
    // POST selected network information
    // to Flask /analysis API.

    console.log('Analyzing network:', selectedNetwork);
  };

  // ============================================================
  // HELPERS
  // ============================================================

  const getSignalLabel = (signal) => {
    if (signal >= 80) return 'Excellent';
    if (signal >= 60) return 'Good';
    if (signal >= 40) return 'Fair';
    return 'Weak';
  };

  const getSignalTextColor = (signal) => {
    if (signal >= 80) return 'text-cyan-400';
    if (signal >= 60) return 'text-cyan-400';
    if (signal >= 40) return 'text-yellow-400';
    return 'text-pink-400';
  };

  const getSignalBarColor = (signal) => {
    if (signal >= 80) return 'bg-cyan-400';
    if (signal >= 60) return 'bg-cyan-400';
    if (signal >= 40) return 'bg-yellow-400';
    return 'bg-pink-500';
  };

  // ============================================================
  // ICON COMPONENT
  // ============================================================

  const Icon = ({ type, size = 22 }) => {
    const common = {
      width: size,
      height: size,
      viewBox: '0 0 24 24',
      fill: 'none',
      stroke: 'currentColor',
      strokeWidth: '1.7',
      strokeLinecap: 'round',
      strokeLinejoin: 'round',
    };

    switch (type) {
      case 'menu':
        return (
          <svg {...common}>
            <line x1="4" y1="6" x2="20" y2="6" />
            <line x1="4" y1="12" x2="20" y2="12" />
            <line x1="4" y1="18" x2="20" y2="18" />
          </svg>
        );

      case 'close':
        return (
          <svg {...common}>
            <line x1="6" y1="6" x2="18" y2="18" />
            <line x1="18" y1="6" x2="6" y2="18" />
          </svg>
        );

      case 'wifi':
        return (
          <svg {...common}>
            <path d="M5 12.55a11 11 0 0 1 14.08 0" />
            <path d="M1.42 9a16 16 0 0 1 21.16 0" />
            <path d="M8.53 16.11a6 6 0 0 1 6.95 0" />
            <line x1="12" y1="20" x2="12.01" y2="20" />
          </svg>
        );

      case 'shield':
        return (
          <svg {...common}>
            <path d="M12 3l7 4v5c0 4.5-3 7.8-7 9-4-1.2-7-4.5-7-9V7l7-4z" />
            <path d="m9 12 2 2 4-4" />
          </svg>
        );

      case 'alert':
        return (
          <svg {...common}>
            <path d="M10.3 3.8 2.2 18a2 2 0 0 0 1.7 3h16.2a2 2 0 0 0 1.7-3L13.7 3.8a2 2 0 0 0-3.4 0Z" />
            <line x1="12" y1="9" x2="12" y2="13" />
            <line x1="12" y1="17" x2="12.01" y2="17" />
          </svg>
        );

      case 'activity':
        return (
          <svg {...common}>
            <polyline points="3 12 7 12 10 5 14 19 17 12 21 12" />
          </svg>
        );

      case 'history':
        return (
          <svg {...common}>
            <circle cx="12" cy="12" r="9" />
            <polyline points="12 7 12 12 15 14" />
          </svg>
        );

      case 'bell':
        return (
          <svg {...common}>
            <path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9" />
            <path d="M10 21h4" />
          </svg>
        );

      case 'settings':
        return (
          <svg {...common}>
            <circle cx="12" cy="12" r="3" />
            <path d="M19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1-1.8 1.8-.1-.1a1.7 1.7 0 0 0-1.9-.3 1.7 1.7 0 0 0-1 1.5V22h-2.5v-.1a1.7 1.7 0 0 0-1-1.5 1.7 1.7 0 0 0-1.9.3l-.1.1-1.8-1.8.1-.1a1.7 1.7 0 0 0 .3-1.9 1.7 1.7 0 0 0-1.5-1H5V13.5h.1a1.7 1.7 0 0 0 1.5-1 1.7 1.7 0 0 0-.3-1.9l-.1-.1L8 8.7l.1.1a1.7 1.7 0 0 0 1.9.3 1.7 1.7 0 0 0 1-1.5V7h2.5v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.9-.3l.1-.1 1.8 1.8-.1.1a1.7 1.7 0 0 0-.3 1.9 1.7 1.7 0 0 0 1.5 1h.1V15h-.1a1.7 1.7 0 0 0-1.5 0Z" />
          </svg>
        );

      case 'user':
        return (
          <svg {...common}>
            <circle cx="12" cy="8" r="4" />
            <path d="M4 21a8 8 0 0 1 16 0" />
          </svg>
        );

      default:
        return null;
    }
  };

  // ============================================================
  // SIDEBAR ITEMS
  // ============================================================

  const sidebarItems = [
    {
      label: 'Dashboard',
      icon: 'activity',
      active: true,
    },
    {
      label: 'Wi-Fi Scan',
      icon: 'wifi',
    },
    {
      label: 'Analysis',
      icon: 'activity',
    },
    {
      label: 'History',
      icon: 'history',
    },
    {
      label: 'Alerts',
      icon: 'bell',
    },
    {
      label: 'Settings',
      icon: 'settings',
    },
  ];

  // ============================================================
  // RENDER
  // ============================================================

  return (
    <main className="relative min-h-screen overflow-x-hidden bg-[#020611] text-white">

      {/* ========================================================
          BACKGROUND GLOW
      ======================================================== */}

      <div className="pointer-events-none fixed left-1/2 top-0 h-[500px] w-[700px] -translate-x-1/2 rounded-full bg-cyan-950/20 blur-[150px]" />

      <div className="pointer-events-none fixed right-0 top-1/3 h-[400px] w-[400px] rounded-full bg-purple-950/20 blur-[150px]" />


      {/* ========================================================
          MODULE 0: EXPAND SIDEBAR BUTTON
      ======================================================== */}

      {!sidebarOpen && (
        <button
          type="button"
          onClick={() => setSidebarOpen(true)}
          className="fixed left-5 top-5 z-50 flex h-11 w-11 items-center justify-center rounded-xl border border-cyan-400/30 bg-slate-950/90 text-cyan-400 shadow-lg shadow-cyan-950/30 backdrop-blur-xl transition hover:border-cyan-400 hover:bg-cyan-400/10"
          aria-label="Open navigation"
        >
          <Icon type="menu" size={21} />
        </button>
      )}


      {/* ========================================================
          MODULE 0: SIDEBAR
      ======================================================== */}

      <aside
        className={`fixed left-0 top-0 z-40 h-screen w-[260px] border-r border-slate-800/80 bg-[#030a15]/95 backdrop-blur-2xl transition-transform duration-300 ${
          sidebarOpen
            ? 'translate-x-0'
            : '-translate-x-full'
        }`}
      >

        <div className="flex h-full flex-col">

          {/* Logo */}

          <div className="flex h-[90px] items-center justify-between border-b border-slate-800/70 px-6">

            <div>
              <div className="text-2xl font-bold tracking-tight">
                <span className="text-white">Cogni</span>
                <span className="text-cyan-400">F</span>
                <span className="text-purple-400">i</span>
              </div>

              <p className="mt-0.5 text-[9px] uppercase tracking-[0.3em] text-slate-600">
                Know your network
              </p>
            </div>

            <button
              type="button"
              onClick={() => setSidebarOpen(false)}
              className="flex h-9 w-9 items-center justify-center rounded-lg text-slate-500 transition hover:bg-white/5 hover:text-cyan-400"
              aria-label="Close navigation"
            >
              <Icon type="close" size={20} />
            </button>

          </div>


          {/* Navigation */}

          <nav className="flex-1 px-4 py-6">

            <p className="mb-3 px-3 text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-600">
              Navigation
            </p>

            <div className="space-y-2">

              {sidebarItems.map((item) => (
  <button
    key={item.label}
    type="button"
    onClick={() => {
  setSidebarOpen(false);

  if (item.label === 'Dashboard') {
    navigate('/dashboard');
  }

  if (item.label === 'Wi-Fi Scan') {
    navigate('/wifi-scan');
  }

  if (item.label === 'Analysis') {
    console.log('Analysis module coming next');
  }

  if (item.label === 'History') {
    console.log('History module coming later');
  }

  if (item.label === 'Alerts') {
    console.log('Alerts module coming later');
  }

  if (item.label === 'Settings') {
    console.log('Settings module coming later');
  }
}}
    className={`group flex w-full items-center gap-4 rounded-xl px-4 py-3.5 text-left transition ${
      item.active
        ? 'border border-cyan-400/20 bg-cyan-400/10 text-cyan-300 shadow-[0_0_20px_rgba(34,211,238,0.06)]'
        : 'text-slate-400 hover:bg-white/[0.03] hover:text-white'
    }`}
  >

                  <span
                    className={
                      item.active
                        ? 'text-cyan-400'
                        : 'text-slate-500 group-hover:text-cyan-400'
                    }
                  >
                    <Icon type={item.icon} size={20} />
                  </span>

                  <span className="text-sm font-medium">
                    {item.label}
                  </span>

                </button>

              ))}

            </div>

          </nav>


          {/* User */}

          <div className="border-t border-slate-800/70 p-4">

            <div className="flex items-center gap-3 rounded-xl border border-slate-800 bg-slate-950/50 p-3">

              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-slate-800 text-slate-300">
                <Icon type="user" size={20} />
              </div>

              <div className="min-w-0">
                <p className="truncate text-sm font-semibold text-white">
                  {user?.name || 'User'}
                </p>

                <p className="truncate text-xs text-slate-600">
                  {user?.email || 'user@example.com'}
                </p>
              </div>

            </div>

          </div>

        </div>

      </aside>


      {/* ========================================================
          SIDEBAR OVERLAY
      ======================================================== */}

      {sidebarOpen && (
        <div
          onClick={() => setSidebarOpen(false)}
          className="fixed inset-0 z-30 bg-black/40 backdrop-blur-[2px]"
        />
      )}


      {/* ========================================================
          MAIN CONTENT
      ======================================================== */}

      <section className="relative z-10 min-h-screen px-5 py-6 sm:px-8 lg:px-10">

        <div className="mx-auto max-w-[1500px]">


          {/* ====================================================
              MODULE 1: HEADER
          ==================================================== */}

          <header className="mb-7 flex items-start justify-between gap-5 pl-14 lg:pl-14">

            <div>

              <p className="mb-1 text-[11px] font-semibold uppercase tracking-[0.22em] text-cyan-400">
                Security Dashboard
              </p>

              <h1 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
                Dashboard
              </h1>

              <p className="mt-2 text-sm text-slate-400 sm:text-base">
                Scan and analyze Wi-Fi networks around you.
              </p>

            </div>


            {/* System status */}

            <div className="hidden items-center gap-3 sm:flex">

              <div className="flex items-center gap-2 rounded-xl border border-cyan-400/25 bg-cyan-400/5 px-4 py-2.5">

                <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-cyan-400/10 text-cyan-400">
                  <Icon type="shield" size={17} />
                </span>

                <span className="text-xs font-medium text-cyan-300">
                  System Protected
                </span>

              </div>

              <button
                type="button"
                className="relative flex h-11 w-11 items-center justify-center rounded-xl border border-slate-800 bg-slate-950/60 text-slate-400 transition hover:border-cyan-400/30 hover:text-cyan-400"
              >
                <Icon type="bell" size={20} />

                <span className="absolute right-2 top-2 h-2 w-2 rounded-full bg-pink-500 shadow-[0_0_8px_rgba(236,72,153,0.8)]" />
              </button>

            </div>

          </header>


          {/* ====================================================
              MODULE 2: SUMMARY CARDS
          ==================================================== */}

          <section className="mb-5 grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">

            {/* Networks Found */}

            <div className="rounded-2xl border border-cyan-400/15 bg-slate-950/60 p-5 shadow-xl shadow-black/20 backdrop-blur-xl">

              <div className="flex items-center gap-4">

                <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-full border border-cyan-400/30 bg-cyan-400/10 text-cyan-400 shadow-[0_0_25px_rgba(34,211,238,0.1)]">
                  <Icon type="wifi" size={29} />
                </div>

                <div>
                  <p className="text-sm text-slate-400">
                    Networks Found
                  </p>

                  <p className="mt-1 text-3xl font-bold text-white">
                    {networks.length || 0}
                  </p>

                  <p className="mt-1 text-xs text-slate-600">
                    {networks.length
                      ? 'Last scan: Just now'
                      : 'No scan performed'}
                  </p>
                </div>

              </div>

            </div>


            {/* Trusted */}

            <div className="rounded-2xl border border-purple-400/15 bg-slate-950/60 p-5 shadow-xl shadow-black/20 backdrop-blur-xl">

              <div className="flex items-center gap-4">

                <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-full border border-purple-400/25 bg-purple-400/10 text-purple-400">
                  <Icon type="shield" size={29} />
                </div>

                <div>
                  <p className="text-sm text-slate-400">
                    Trusted Networks
                  </p>

                  <p className="mt-1 text-3xl font-bold text-white">
                    {networks.filter(
                      (network) => network.security !== 'Open'
                    ).length}
                  </p>

                  <p className="mt-1 text-xs text-slate-600">
                    Secure networks
                  </p>
                </div>

              </div>

            </div>


            {/* Risks */}

            <div className="rounded-2xl border border-pink-400/15 bg-slate-950/60 p-5 shadow-xl shadow-black/20 backdrop-blur-xl">

              <div className="flex items-center gap-4">

                <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-full border border-pink-400/25 bg-pink-400/10 text-pink-400">
                  <Icon type="alert" size={29} />
                </div>

                <div>
                  <p className="text-sm text-slate-400">
                    Risks Detected
                  </p>

                  <p className="mt-1 text-3xl font-bold text-white">
                    0
                  </p>

                  <p className="mt-1 text-xs text-slate-600">
                    Awaiting analysis
                  </p>
                </div>

              </div>

            </div>


            {/* Trust Score */}

            <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-5 shadow-xl shadow-black/20 backdrop-blur-xl">

              <div className="flex items-center gap-4">

                <div className="relative flex h-16 w-16 shrink-0 items-center justify-center rounded-full border border-slate-700">

                  <div className="absolute inset-1 rounded-full border-2 border-cyan-400/70 border-r-transparent" />

                  <Icon type="shield" size={25} />

                </div>

                <div>
                  <p className="text-sm text-slate-400">
                    Your Trust Score
                  </p>

                  <p className="mt-1 text-3xl font-bold text-white">
                    --
                  </p>

                  <p className="mt-1 text-xs text-slate-600">
                    Analyze a network first
                  </p>
                </div>

              </div>

            </div>

          </section>


          {/* ====================================================
              MODULE 3 + 4
              WIFI SCANNER + SELECTED NETWORK
          ==================================================== */}

          <section className="grid grid-cols-1 gap-5 xl:grid-cols-[minmax(0,1.7fr)_minmax(320px,0.8fr)]">


            {/* ==================================================
                MODULE 3: WIFI SCANNER
            ================================================== */}

            <div className="rounded-2xl border border-cyan-400/15 bg-slate-950/60 p-5 shadow-xl shadow-black/20 backdrop-blur-xl sm:p-6">

              {/* Header */}

              <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">

                <div>

                  <h2 className="text-xl font-semibold text-cyan-400">
                    Scan for Available Wi-Fi Networks
                  </h2>

                  <p className="mt-1 text-sm text-slate-500">
                    Scan your surroundings to detect available wireless networks.
                  </p>

                </div>

                <button
                  type="button"
                  onClick={handleScan}
                  disabled={scanning}
                  className="flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-cyan-500 via-blue-500 to-fuchsia-500 px-6 py-3 text-sm font-semibold text-white shadow-[0_0_25px_rgba(34,211,238,0.15)] transition hover:scale-[1.02] hover:shadow-[0_0_30px_rgba(168,85,247,0.25)] disabled:cursor-not-allowed disabled:opacity-60"
                >

                  <Icon type="wifi" size={19} />

                  {scanning ? 'Scanning...' : 'Start Scan'}

                </button>

              </div>


              {/* Column headings */}

              {networks.length > 0 && !scanning && (

                <div className="mt-7 hidden grid-cols-[1.7fr_0.8fr_0.6fr_0.4fr_0.4fr] gap-4 px-3 text-[11px] font-medium uppercase tracking-wider text-slate-500 md:grid">

                  <span>Network Name</span>
                  <span>Signal</span>
                  <span>Security</span>
                  <span>Ch.</span>
                  <span />

                </div>

              )}


              {/* Initial state */}

              {!scanning && networks.length === 0 && (

                <div className="mt-6 flex min-h-[400px] flex-col items-center justify-center rounded-xl border border-dashed border-slate-800 bg-slate-900/20 px-5 text-center">

                  <div className="mb-5 flex h-20 w-20 items-center justify-center rounded-full border border-cyan-400/20 bg-cyan-400/5 text-cyan-400">
                    <Icon type="wifi" size={38} />
                  </div>

                  <h3 className="text-lg font-semibold text-slate-300">
                    No networks scanned yet
                  </h3>

                  <p className="mt-2 max-w-md text-sm text-slate-600">
                    Click Start Scan to discover available Wi-Fi networks around you.
                  </p>

                </div>

              )}


              {/* Scanning */}

              {scanning && (

                <div className="mt-6 flex min-h-[400px] flex-col items-center justify-center rounded-xl border border-cyan-400/10 bg-cyan-400/[0.02]">

                  <div className="relative mb-6">

                    <div className="h-20 w-20 animate-ping rounded-full border border-cyan-400/20" />

                    <div className="absolute inset-0 flex items-center justify-center text-cyan-400">
                      <Icon type="wifi" size={36} />
                    </div>

                  </div>

                  <p className="text-sm font-medium text-cyan-300">
                    Scanning for available networks...
                  </p>

                  <p className="mt-2 text-xs text-slate-600">
                    Searching nearby wireless networks
                  </p>

                </div>

              )}


              {/* Network list */}

              {!scanning && networks.length > 0 && (

                <div className="mt-4 space-y-2">

                  {networks.map((network) => {

                    const selected =
                      selectedNetwork?.id === network.id;

                    return (

                      <div
                        key={network.id}
                        className={`grid grid-cols-1 gap-4 rounded-xl border p-4 transition md:grid-cols-[1.7fr_0.8fr_0.6fr_0.4fr_0.4fr] md:items-center ${
                          selected
                            ? 'border-cyan-400/70 bg-cyan-400/[0.06] shadow-[0_0_20px_rgba(34,211,238,0.07)]'
                            : 'border-transparent bg-slate-900/40 hover:border-slate-700 hover:bg-slate-900/60'
                        }`}
                      >

                        {/* Network */}

                        <div className="flex items-center gap-3">

                          <div
                            className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-full ${
                              selected
                                ? 'bg-cyan-400/15 text-cyan-400'
                                : 'bg-slate-800 text-slate-500'
                            }`}
                          >
                            <Icon type="wifi" size={19} />
                          </div>

                          <div className="min-w-0">

                            <p className="truncate text-sm font-semibold text-white">
                              {network.name}
                            </p>

                            <p className="mt-0.5 text-xs text-slate-500">
                              {network.type}
                            </p>

                          </div>

                        </div>


                        {/* Signal */}

                        <div className="flex items-center gap-3">

                          <div className="flex items-end gap-[3px]">

                            {[1, 2, 3, 4].map((bar) => {

                              const active =
                                network.signal >= bar * 25;

                              return (
                                <span
                                  key={bar}
                                  className={`w-[4px] rounded-sm ${
                                    bar === 1
                                      ? 'h-2'
                                      : bar === 2
                                        ? 'h-3'
                                        : bar === 3
                                          ? 'h-4'
                                          : 'h-5'
                                  } ${
                                    active
                                      ? getSignalBarColor(network.signal)
                                      : 'bg-slate-800'
                                  }`}
                                />
                              );
                            })}

                          </div>

                          <div>

                            <p
                              className={`text-sm font-semibold ${getSignalTextColor(
                                network.signal
                              )}`}
                            >
                              {network.signal}%
                            </p>

                            <p className="text-[10px] text-slate-600">
                              {getSignalLabel(network.signal)}
                            </p>

                          </div>

                        </div>


                        {/* Security */}

                        <div>

                          <span
                            className={`inline-flex rounded-lg border px-2.5 py-1 text-[11px] font-medium ${
                              network.security === 'Open'
                                ? 'border-cyan-400/30 bg-cyan-400/5 text-cyan-300'
                                : 'border-blue-500/30 bg-blue-500/5 text-blue-300'
                            }`}
                          >
                            {network.security}
                          </span>

                        </div>


                        {/* Channel */}

                        <div className="hidden text-sm text-slate-300 md:block">
                          {network.channel}
                        </div>


                        {/* Select */}

                        <div>

                          <button
                            type="button"
                            onClick={() =>
                              handleSelectNetwork(network)
                            }
                            className={`w-full rounded-lg px-4 py-2 text-xs font-semibold transition ${
                              selected
                                ? 'bg-gradient-to-r from-cyan-500 to-fuchsia-500 text-white'
                                : 'border border-cyan-400/30 bg-cyan-400/5 text-cyan-300 hover:bg-cyan-400/10'
                            }`}
                          >
                            {selected ? 'Selected' : 'Select'}
                          </button>

                        </div>

                      </div>

                    );
                  })}

                </div>

              )}

            </div>


            {/* ==================================================
                MODULE 4: SELECTED NETWORK
            ================================================== */}

            <div className="space-y-5">


              {/* Selected Network */}

              <div className="rounded-2xl border border-purple-400/20 bg-slate-950/60 p-6 shadow-xl shadow-black/20 backdrop-blur-xl">

                <h2 className="mb-6 text-lg font-semibold text-cyan-400">
                  Selected Network
                </h2>


                {selectedNetwork ? (

                  <>

                    <div className="flex items-center gap-4">

                      <div className="flex h-20 w-20 shrink-0 items-center justify-center rounded-full border border-cyan-400/40 bg-cyan-400/10 text-cyan-400 shadow-[0_0_25px_rgba(34,211,238,0.12)]">
                        <Icon type="wifi" size={36} />
                      </div>

                      <div className="min-w-0">

                        <h3 className="truncate text-xl font-bold text-white">
                          {selectedNetwork.name}
                        </h3>

                        <p className="mt-1 text-sm text-slate-500">
                          {selectedNetwork.security} Network
                          <span className="mx-2">•</span>
                          Ch. {selectedNetwork.channel}
                        </p>

                        <p className="mt-2 text-sm font-medium text-cyan-400">
                          Signal: {selectedNetwork.signal}% (
                          {getSignalLabel(selectedNetwork.signal)})
                        </p>

                      </div>

                    </div>


                    <button
                      type="button"
                      onClick={handleAnalyze}
                      className="mt-7 flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-cyan-500 via-blue-500 to-fuchsia-500 py-3.5 text-sm font-semibold text-white shadow-[0_0_25px_rgba(34,211,238,0.12)] transition hover:scale-[1.01] hover:shadow-[0_0_30px_rgba(168,85,247,0.2)]"
                    >
                      <Icon type="activity" size={20} />
                      Analyze Network
                    </button>

                    <p className="mt-3 text-center text-xs text-slate-600">
                      Start in-depth security analysis
                    </p>

                  </>

                ) : (

                  <div className="flex min-h-[230px] flex-col items-center justify-center text-center">

                    <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full border border-slate-800 bg-slate-900 text-slate-600">
                      <Icon type="wifi" size={28} />
                    </div>

                    <p className="text-sm font-medium text-slate-400">
                      No network selected
                    </p>

                    <p className="mt-2 max-w-xs text-xs leading-5 text-slate-600">
                      Scan for networks and select one to begin security analysis.
                    </p>

                  </div>

                )}

              </div>


              {/* ==================================================
                  MODULE 5: HOW IT WORKS
              ================================================== */}

              <div className="rounded-2xl border border-purple-400/20 bg-slate-950/60 p-6 shadow-xl shadow-black/20 backdrop-blur-xl">

                <h2 className="text-lg font-semibold text-cyan-400">
                  How It Works
                </h2>


                <div className="mt-6 space-y-7">

                  {/* Step 1 */}

                  <div className="relative flex gap-4">

                    <div className="relative z-10 flex h-10 w-10 shrink-0 items-center justify-center rounded-full border border-cyan-400/40 bg-cyan-400/10 text-sm font-bold text-cyan-400">
                      1
                    </div>

                    <div>
                      <h3 className="text-sm font-semibold text-white">
                        Scan Networks
                      </h3>

                      <p className="mt-1 text-xs leading-5 text-slate-600">
                        Find available Wi-Fi networks around you.
                      </p>
                    </div>

                  </div>


                  {/* Step 2 */}

                  <div className="relative flex gap-4">

                    <div className="absolute left-5 top-[-28px] h-7 w-px bg-gradient-to-b from-cyan-400/40 to-purple-400/40" />

                    <div className="relative z-10 flex h-10 w-10 shrink-0 items-center justify-center rounded-full border border-purple-400/40 bg-purple-400/10 text-sm font-bold text-purple-400">
                      2
                    </div>

                    <div>
                      <h3 className="text-sm font-semibold text-white">
                        Select & Analyze
                      </h3>

                      <p className="mt-1 text-xs leading-5 text-slate-600">
                        Choose a network to start security analysis.
                      </p>
                    </div>

                  </div>


                  {/* Step 3 */}

                  <div className="relative flex gap-4">

                    <div className="absolute left-5 top-[-28px] h-7 w-px bg-gradient-to-b from-purple-400/40 to-pink-400/40" />

                    <div className="relative z-10 flex h-10 w-10 shrink-0 items-center justify-center rounded-full border border-pink-400/40 bg-pink-400/10 text-sm font-bold text-pink-400">
                      3
                    </div>

                    <div>
                      <h3 className="text-sm font-semibold text-white">
                        Get Trust Score
                      </h3>

                      <p className="mt-1 text-xs leading-5 text-slate-600">
                        Receive an AI-powered risk score and recommendations.
                      </p>
                    </div>

                  </div>

                </div>

              </div>

            </div>

          </section>

        </div>

      </section>

    </main>
  );
}

export default Dashboard;