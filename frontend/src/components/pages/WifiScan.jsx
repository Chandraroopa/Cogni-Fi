import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function WifiScan() {
  const navigate = useNavigate();

  const [scanning, setScanning] = useState(false);
  const [networks, setNetworks] = useState([]);
  const [selectedNetwork, setSelectedNetwork] = useState(null);

  // Temporary data.
  // Later this will come from the Flask/Python Wi-Fi scanner.
  const mockNetworks = [
    {
      id: 1,
      name: 'Cafe_Free_WiFi',
      signal: 92,
      security: 'Open',
      frequency: '2.4 GHz',
      channel: 6,
    },
    {
      id: 2,
      name: 'Canara_Engineering',
      signal: 78,
      security: 'WPA2',
      frequency: '5 GHz',
      channel: 36,
    },
    {
      id: 3,
      name: 'Home_Network',
      signal: 64,
      security: 'WPA2',
      frequency: '5 GHz',
      channel: 11,
    },
    {
      id: 4,
      name: 'Public_WiFi',
      signal: 45,
      security: 'Open',
      frequency: '2.4 GHz',
      channel: 1,
    },
    {
      id: 5,
      name: 'Office_Network',
      signal: 28,
      security: 'WPA3',
      frequency: '5 GHz',
      channel: 149,
    },
  ];

  // ------------------------------------------------------------
  // START WIFI SCAN
  // ------------------------------------------------------------

  const handleScan = () => {
    setScanning(true);
    setSelectedNetwork(null);

    // Temporary simulation
    setTimeout(() => {
      setNetworks(mockNetworks);
      setScanning(false);
    }, 1800);
  };

  // ------------------------------------------------------------
  // SELECT NETWORK
  // ------------------------------------------------------------

  const handleSelect = (network) => {
    setSelectedNetwork(network);
  };

  // ------------------------------------------------------------
  // SIGNAL HELPERS
  // ------------------------------------------------------------

  const getSignalLabel = (signal) => {
    if (signal >= 80) return 'Excellent';
    if (signal >= 60) return 'Good';
    if (signal >= 40) return 'Fair';
    return 'Weak';
  };

  const getSignalColor = (signal) => {
    if (signal >= 60) return 'text-cyan-400';
    if (signal >= 40) return 'text-yellow-400';
    return 'text-pink-400';
  };

  const getSignalBarColor = (signal) => {
    if (signal >= 60) return 'bg-cyan-400';
    if (signal >= 40) return 'bg-yellow-400';
    return 'bg-pink-500';
  };

  // ------------------------------------------------------------
  // WIFI ICON
  // ------------------------------------------------------------

  const WifiIcon = ({ size = 24 }) => (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M5 12.55a11 11 0 0 1 14.08 0" />
      <path d="M1.42 9a16 16 0 0 1 21.16 0" />
      <path d="M8.53 16.11a6 6 0 0 1 6.95 0" />
      <line x1="12" y1="20" x2="12.01" y2="20" />
    </svg>
  );

  // ------------------------------------------------------------
  // SHIELD ICON
  // ------------------------------------------------------------

  const ShieldIcon = ({ size = 24 }) => (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M12 3l7 4v5c0 4.5-3 7.8-7 9-4-1.2-7-4.5-7-9V7l7-4z" />
      <path d="m9 12 2 2 4-4" />
    </svg>
  );

  // ------------------------------------------------------------
  // RENDER
  // ------------------------------------------------------------

  return (
    <main className="min-h-screen bg-[#020611] px-5 py-8 text-white sm:px-8 lg:px-10">

      {/* Background glow */}

      <div className="pointer-events-none fixed left-1/2 top-0 h-[500px] w-[700px] -translate-x-1/2 rounded-full bg-cyan-950/20 blur-[150px]" />

      <div className="pointer-events-none fixed right-0 top-1/3 h-[400px] w-[400px] rounded-full bg-purple-950/20 blur-[150px]" />

      <div className="relative z-10 mx-auto max-w-[1400px]">

        {/* =====================================================
            HEADER
        ===================================================== */}

        <div className="mb-8">

          <button
            type="button"
            onClick={() => navigate('/dashboard')}
            className="mb-5 text-sm text-slate-500 transition hover:text-cyan-400"
          >
            ← Back to Dashboard
          </button>

          <p className="mb-1 text-[11px] font-semibold uppercase tracking-[0.22em] text-cyan-400">
            Network Security
          </p>

          <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">
            Wi-Fi Scanner
          </h1>

          <p className="mt-2 max-w-2xl text-sm text-slate-400 sm:text-base">
            Discover available wireless networks and select a network
            for security analysis.
          </p>

        </div>


        {/* =====================================================
            SCANNER CONTROL
        ===================================================== */}

        <section className="mb-6 rounded-2xl border border-cyan-400/15 bg-slate-950/60 p-6 shadow-xl shadow-black/20 backdrop-blur-xl">

          <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">

            <div className="flex items-center gap-4">

              <div className="flex h-14 w-14 items-center justify-center rounded-xl border border-cyan-400/25 bg-cyan-400/10 text-cyan-400">
                <WifiIcon size={28} />
              </div>

              <div>

                <h2 className="text-lg font-semibold text-white">
                  Scan Nearby Networks
                </h2>

                <p className="mt-1 text-sm text-slate-500">
                  Search for Wi-Fi networks available in your surroundings.
                </p>

              </div>

            </div>


            <button
              type="button"
              onClick={handleScan}
              disabled={scanning}
              className="flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-cyan-500 via-blue-500 to-fuchsia-500 px-7 py-3.5 text-sm font-semibold text-white shadow-[0_0_25px_rgba(34,211,238,0.15)] transition hover:scale-[1.02] disabled:cursor-not-allowed disabled:opacity-60"
            >

              {scanning ? (
                <>
                  <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                  Scanning...
                </>
              ) : (
                <>
                  <WifiIcon size={18} />
                  Start Scan
                </>
              )}

            </button>

          </div>

        </section>


        {/* =====================================================
            SCAN STATUS
        ===================================================== */}

        {scanning && (

          <section className="mb-6 flex min-h-[280px] flex-col items-center justify-center rounded-2xl border border-cyan-400/15 bg-slate-950/60 backdrop-blur-xl">

            <div className="relative mb-6">

              <div className="h-20 w-20 animate-ping rounded-full border border-cyan-400/20" />

              <div className="absolute inset-0 flex items-center justify-center text-cyan-400">
                <WifiIcon size={35} />
              </div>

            </div>

            <h3 className="text-lg font-semibold text-cyan-300">
              Scanning for Wi-Fi networks
            </h3>

            <p className="mt-2 text-sm text-slate-600">
              Searching for available wireless networks...
            </p>

          </section>

        )}


        {/* =====================================================
            NETWORK RESULTS
        ===================================================== */}

        {!scanning && networks.length > 0 && (

          <section className="rounded-2xl border border-slate-800 bg-slate-950/60 p-5 shadow-xl shadow-black/20 backdrop-blur-xl sm:p-6">

            {/* Results header */}

            <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">

              <div>

                <h2 className="text-xl font-semibold text-cyan-400">
                  Available Networks
                </h2>

                <p className="mt-1 text-sm text-slate-500">
                  {networks.length} networks detected
                </p>

              </div>

              <div className="rounded-lg border border-cyan-400/20 bg-cyan-400/5 px-3 py-2 text-xs text-cyan-300">
                Select a network to continue
              </div>

            </div>


            {/* Column headings */}

            <div className="mb-3 hidden grid-cols-[1.7fr_0.8fr_0.7fr_0.5fr_0.5fr] gap-4 px-4 text-[10px] font-semibold uppercase tracking-wider text-slate-600 md:grid">

              <span>Network</span>
              <span>Signal</span>
              <span>Security</span>
              <span>Channel</span>
              <span />

            </div>


            {/* Network rows */}

            <div className="space-y-2">

              {networks.map((network) => {

                const selected =
                  selectedNetwork?.id === network.id;

                return (

                  <div
                    key={network.id}
                    className={`rounded-xl border p-4 transition ${
                      selected
                        ? 'border-cyan-400/60 bg-cyan-400/[0.06] shadow-[0_0_25px_rgba(34,211,238,0.07)]'
                        : 'border-slate-800/60 bg-slate-900/30 hover:border-slate-700 hover:bg-slate-900/60'
                    }`}
                  >

                    <div className="grid grid-cols-1 gap-4 md:grid-cols-[1.7fr_0.8fr_0.7fr_0.5fr_0.5fr] md:items-center">

                      {/* Network name */}

                      <div className="flex items-center gap-4">

                        <div
                          className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-xl ${
                            selected
                              ? 'bg-cyan-400/15 text-cyan-400'
                              : 'bg-slate-800 text-slate-500'
                          }`}
                        >
                          <WifiIcon size={21} />
                        </div>

                        <div className="min-w-0">

                          <p className="truncate text-sm font-semibold text-white">
                            {network.name}
                          </p>

                          <p className="mt-1 text-xs text-slate-600">
                            {network.frequency}
                          </p>

                        </div>

                      </div>


                      {/* Signal */}

                      <div className="flex items-center gap-3">

                        <div className="flex items-end gap-1">

                          {[1, 2, 3, 4].map((bar) => (

                            <span
                              key={bar}
                              className={`w-1 rounded-sm ${
                                bar === 1
                                  ? 'h-2'
                                  : bar === 2
                                    ? 'h-3'
                                    : bar === 3
                                      ? 'h-4'
                                      : 'h-5'
                              } ${
                                network.signal >= bar * 25
                                  ? getSignalBarColor(network.signal)
                                  : 'bg-slate-800'
                              }`}
                            />

                          ))}

                        </div>

                        <div>

                          <p
                            className={`text-sm font-semibold ${getSignalColor(
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
                              ? 'border-pink-400/25 bg-pink-400/5 text-pink-300'
                              : 'border-cyan-400/25 bg-cyan-400/5 text-cyan-300'
                          }`}
                        >
                          {network.security}
                        </span>

                      </div>


                      {/* Channel */}

                      <div className="text-sm text-slate-400">
                        Ch. {network.channel}
                      </div>


                      {/* Select */}

                      <button
                        type="button"
                        onClick={() => handleSelect(network)}
                        className={`rounded-lg px-4 py-2 text-xs font-semibold transition ${
                          selected
                            ? 'bg-gradient-to-r from-cyan-500 to-fuchsia-500 text-white'
                            : 'border border-cyan-400/25 bg-cyan-400/5 text-cyan-300 hover:bg-cyan-400/10'
                        }`}
                      >
                        {selected ? 'Selected' : 'Select'}
                      </button>

                    </div>

                  </div>

                );
              })}

            </div>

          </section>

        )}


        {/* =====================================================
            INITIAL STATE
        ===================================================== */}

        {!scanning && networks.length === 0 && (

          <section className="flex min-h-[450px] flex-col items-center justify-center rounded-2xl border border-dashed border-slate-800 bg-slate-950/50 px-5 text-center backdrop-blur-xl">

            <div className="mb-6 flex h-24 w-24 items-center justify-center rounded-full border border-cyan-400/20 bg-cyan-400/5 text-cyan-400">
              <WifiIcon size={42} />
            </div>

            <h2 className="text-xl font-semibold text-slate-300">
              Ready to scan
            </h2>

            <p className="mt-2 max-w-md text-sm leading-6 text-slate-600">
              Start a Wi-Fi scan to discover available networks.
              Once a network is selected, you can proceed with
              security analysis.
            </p>

          </section>

        )}


        {/* =====================================================
            SELECTED NETWORK
        ===================================================== */}

        {selectedNetwork && !scanning && (

          <section className="mt-6 rounded-2xl border border-purple-400/20 bg-slate-950/70 p-6 shadow-xl shadow-black/20 backdrop-blur-xl">

            <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">

              <div className="flex items-center gap-5">

                <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-full border border-cyan-400/30 bg-cyan-400/10 text-cyan-400">
                  <WifiIcon size={30} />
                </div>

                <div>

                  <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-cyan-400">
                    Selected Network
                  </p>

                  <h2 className="mt-1 text-xl font-bold text-white">
                    {selectedNetwork.name}
                  </h2>

                  <div className="mt-2 flex flex-wrap gap-3 text-xs text-slate-500">

                    <span>
                      {selectedNetwork.security}
                    </span>

                    <span>•</span>

                    <span>
                      {selectedNetwork.frequency}
                    </span>

                    <span>•</span>

                    <span>
                      Channel {selectedNetwork.channel}
                    </span>

                    <span>•</span>

                    <span
                      className={getSignalColor(
                        selectedNetwork.signal
                      )}
                    >
                      Signal {selectedNetwork.signal}%
                    </span>

                  </div>

                </div>

              </div>


              {/* Security status */}

              <div className="flex items-center gap-4">

                <div className="hidden h-12 w-px bg-slate-800 lg:block" />

                <div className="flex items-center gap-3">

                  <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-purple-400/25 bg-purple-400/10 text-purple-400">
                    <ShieldIcon size={22} />
                  </div>

                  <div>

                    <p className="text-xs text-slate-600">
                      Next Step
                    </p>

                    <p className="text-sm font-semibold text-slate-300">
                      Security Analysis
                    </p>

                  </div>

                </div>

                <button
                type="button"
                onClick={() => {
        
                navigate('/network-analysis', {
                state: {
                network: selectedNetwork,
                },
                });
                    }}
                className="rounded-xl bg-gradient-to-r from-cyan-500 via-blue-500 to-fuchsia-500 px-6 py-3 text-sm font-semibold text-white shadow-[0_0_25px_rgba(34,211,238,0.12)] transition hover:scale-[1.02]"
                >
                Analyze Network
              </button>

              </div>

            </div>

          </section>

        )}

      </div>

    </main>
  );
}

export default WifiScan;