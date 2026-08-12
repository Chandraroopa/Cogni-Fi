import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  Wifi,
  ShieldCheck,
  ShieldAlert,
  Activity,
  Network,
  Clock3,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Radio,
  Server,
  Gauge,
  ArrowLeft,
} from 'lucide-react';

function NetworkAnalysis() {
  const location = useLocation();
  const navigate = useNavigate();

  // Network selected from Wi-Fi Scan page
  const selectedNetwork = location.state?.network;

  // --------------------------------------------------
  // Temporary frontend analysis data
  // Later this will come from Flask/ML backend.
  // --------------------------------------------------

  const analysis = {
    trustScore: 28,
    status: 'Safe',

    latency: '24 ms',
    packetRate: '182 pkt/s',
    trafficDensity: 'Low',
    connectionFrequency: 'Normal',

    dnsResponse: 'Normal',
    gatewayConsistency: 'Stable',

    packetsAnalyzed: '12,480',
    anomaliesDetected: 2,
    threatsDetected: 0,

    encryption: selectedNetwork?.security || 'WPA2',
    authentication:
      selectedNetwork?.security === 'Open'
        ? 'Open'
        : 'Protected',

    recentActivity: [
      {
        time: 'Just now',
        title: 'Network scan completed',
        description:
          'Network characteristics successfully collected.',
        type: 'success',
      },
      {
        time: '1 min ago',
        title: 'DNS response verified',
        description:
          'DNS behavior is currently within the expected range.',
        type: 'success',
      },
      {
        time: '2 min ago',
        title: 'Gateway consistency checked',
        description:
          'Gateway behavior appears stable.',
        type: 'success',
      },
      {
        time: '3 min ago',
        title: 'Minor traffic anomaly detected',
        description:
          'Small deviation from the normal traffic baseline.',
        type: 'warning',
      },
    ],

    threats: [],
  };

  // --------------------------------------------------
  // If user directly opens dashboard without selecting
  // a network, show a helpful state.
  // --------------------------------------------------

  if (!selectedNetwork) {
    return (
      <main className="min-h-screen bg-[#020611] px-5 py-10 text-white sm:px-8">
        <div className="mx-auto flex min-h-[70vh] max-w-2xl flex-col items-center justify-center text-center">

          <div className="mb-6 flex h-20 w-20 items-center justify-center rounded-2xl border border-cyan-400/20 bg-cyan-400/10 text-cyan-400">
            <Wifi size={38} />
          </div>

          <h1 className="text-2xl font-bold">
            No Network Selected
          </h1>

          <p className="mt-3 max-w-md text-sm leading-6 text-slate-500">
            Select a Wi-Fi network from the scanner before viewing
            its security analysis.
          </p>

          <button
            type="button"
            onClick={() => navigate('/wifi-scan')}
            className="mt-7 flex items-center gap-2 rounded-xl bg-gradient-to-r from-cyan-500 via-blue-500 to-fuchsia-500 px-6 py-3 text-sm font-semibold"
          >
            <Wifi size={17} />
            Scan Networks
          </button>

        </div>
      </main>
    );
  }

  // --------------------------------------------------
  // Helpers
  // --------------------------------------------------

  const isSafe = analysis.status === 'Safe';

  const getActivityIcon = (type) => {
    if (type === 'warning') {
      return <AlertTriangle size={17} />;
    }

    return <CheckCircle2 size={17} />;
  };

  return (
    <main className="min-h-screen bg-[#020611] px-5 py-8 text-white sm:px-8 lg:px-10">

      {/* Background glow */}

      <div className="pointer-events-none fixed left-1/2 top-0 h-[500px] w-[700px] -translate-x-1/2 rounded-full bg-cyan-950/20 blur-[150px]" />

      <div className="pointer-events-none fixed bottom-0 right-0 h-[400px] w-[400px] rounded-full bg-purple-950/20 blur-[150px]" />

      <div className="relative z-10 mx-auto max-w-[1400px]">

        {/* ==================================================
            HEADER
        ================================================== */}

        <div className="mb-7 flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">

          <div>

            <button
              type="button"
              onClick={() => navigate('/wifi-scan')}
              className="mb-5 flex items-center gap-2 text-xs text-slate-500 transition hover:text-cyan-400"
            >
              <ArrowLeft size={14} />
              Back to Wi-Fi Scan
            </button>

            <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-cyan-400">
              Security Monitoring
            </p>

            <h1 className="mt-2 text-3xl font-bold tracking-tight sm:text-4xl">
              Network Analysis
            </h1>

            <p className="mt-2 text-sm text-slate-500">
              Behavioral security assessment of the selected Wi-Fi network.
            </p>

          </div>

          {/* Monitoring indicator */}

          <div className="flex w-fit items-center gap-3 rounded-xl border border-cyan-400/20 bg-cyan-400/5 px-4 py-3">

            <span className="relative flex h-2.5 w-2.5">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-cyan-400 opacity-60" />
              <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-cyan-400" />
            </span>

            <div>
              <p className="text-xs font-semibold text-cyan-300">
                Monitoring Active
              </p>

              <p className="text-[10px] text-slate-600">
                Real-time analysis
              </p>
            </div>

          </div>

        </div>


        {/* ==================================================
            SELECTED NETWORK
        ================================================== */}

        <section className="mb-6 rounded-2xl border border-cyan-400/15 bg-slate-950/60 p-5 shadow-xl shadow-black/20 backdrop-blur-xl sm:p-6">

          <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">

            <div className="flex items-center gap-4">

              <div className="flex h-14 w-14 items-center justify-center rounded-xl border border-cyan-400/25 bg-cyan-400/10 text-cyan-400">
                <Wifi size={27} />
              </div>

              <div>

                <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-600">
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

                  <span>
                    Signal {selectedNetwork.signal}%
                  </span>

                </div>

              </div>

            </div>

            <div className="flex items-center gap-3 rounded-xl border border-cyan-400/15 bg-cyan-400/5 px-4 py-3">

              <Radio size={19} className="text-cyan-400" />

              <div>

                <p className="text-[10px] uppercase tracking-wider text-slate-600">
                  Scan Status
                </p>

                <p className="text-sm font-semibold text-cyan-300">
                  Analysis Complete
                </p>

              </div>

            </div>

          </div>

        </section>


        {/* ==================================================
            TRUST SCORE + QUICK METRICS
        ================================================== */}

        <section className="mb-6 grid gap-5 lg:grid-cols-[1.1fr_2fr]">

          {/* Trust Score */}

          <div className="rounded-2xl border border-cyan-400/15 bg-slate-950/60 p-6 backdrop-blur-xl">

            <div className="flex items-center justify-between">

              <div>
                <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-cyan-400">
                  Current Trust Score
                </p>

                <h2 className="mt-2 text-lg font-semibold text-white">
                  Network Safety
                </h2>
              </div>

              <ShieldCheck
                size={24}
                className="text-cyan-400"
              />

            </div>

            <div className="mt-8 flex items-center justify-center">

              <div className="relative flex h-48 w-48 items-center justify-center rounded-full border-[14px] border-cyan-400/15">

                <div className="absolute inset-[-14px] rounded-full border-[14px] border-transparent border-t-cyan-400 border-r-cyan-400 rotate-[35deg]" />

                <div className="text-center">

                  <p className="text-5xl font-bold text-cyan-400">
                    {analysis.trustScore}
                  </p>

                  <p className="mt-1 text-xs uppercase tracking-widest text-slate-600">
                    / 100
                  </p>

                </div>

              </div>

            </div>

            <div className="mt-6 text-center">

              <span className="inline-flex items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-400/10 px-4 py-2 text-sm font-semibold text-cyan-300">

                <CheckCircle2 size={16} />

                {analysis.status}

              </span>

              <p className="mx-auto mt-3 max-w-xs text-xs leading-5 text-slate-600">
                Network behavior currently appears trustworthy.
              </p>

            </div>

          </div>


          {/* Quick metrics */}

          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">

            <MetricCard
              icon={<Activity size={19} />}
              label="Latency"
              value={analysis.latency}
              description="Gateway response"
            />

            <MetricCard
              icon={<Radio size={19} />}
              label="Packet Rate"
              value={analysis.packetRate}
              description="Current traffic"
            />

            <MetricCard
              icon={<Gauge size={19} />}
              label="Traffic"
              value={analysis.trafficDensity}
              description="Traffic density"
            />

            <MetricCard
              icon={<Network size={19} />}
              label="Connections"
              value={analysis.connectionFrequency}
              description="Behavior pattern"
            />

          </div>

        </section>


        {/* ==================================================
            NETWORK DETAILS + CONNECTION ANALYSIS
        ================================================== */}

        <section className="mb-6 grid gap-5 lg:grid-cols-2">

          {/* Network Details */}

          <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-6 backdrop-blur-xl">

            <div className="mb-5 flex items-center gap-3">

              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-cyan-400/10 text-cyan-400">
                <Server size={19} />
              </div>

              <div>

                <h2 className="font-semibold text-white">
                  Network Details
                </h2>

                <p className="text-xs text-slate-600">
                  Basic network characteristics
                </p>

              </div>

            </div>

            <div className="grid grid-cols-2 gap-x-6 gap-y-5">

              <DetailItem
                label="SSID"
                value={selectedNetwork.name}
              />

              <DetailItem
                label="Signal Strength"
                value={`${selectedNetwork.signal}%`}
              />

              <DetailItem
                label="Security"
                value={analysis.encryption}
              />

              <DetailItem
                label="Authentication"
                value={analysis.authentication}
              />

              <DetailItem
                label="Frequency"
                value={selectedNetwork.frequency}
              />

              <DetailItem
                label="Channel"
                value={selectedNetwork.channel}
              />

            </div>

          </div>


          {/* Connection Analysis */}

          <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-6 backdrop-blur-xl">

            <div className="mb-5 flex items-center gap-3">

              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-purple-400/10 text-purple-400">
                <Activity size={19} />
              </div>

              <div>

                <h2 className="font-semibold text-white">
                  Connection Analysis
                </h2>

                <p className="text-xs text-slate-600">
                  Behavioral network signals
                </p>

              </div>

            </div>

            <div className="space-y-4">

              <AnalysisRow
                label="DNS Response"
                value={analysis.dnsResponse}
                positive
              />

              <AnalysisRow
                label="Gateway Consistency"
                value={analysis.gatewayConsistency}
                positive
              />

              <AnalysisRow
                label="Traffic Density"
                value={analysis.trafficDensity}
                positive
              />

              <AnalysisRow
                label="Connection Frequency"
                value={analysis.connectionFrequency}
                positive
              />

            </div>

          </div>

        </section>


        {/* ==================================================
            BEHAVIORAL ANALYSIS GRAPH
        ================================================== */}

        <section className="mb-6 rounded-2xl border border-slate-800 bg-slate-950/60 p-6 backdrop-blur-xl">

          <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">

            <div>

              <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-cyan-400">
                Behavioral Analysis
              </p>

              <h2 className="mt-1 text-lg font-semibold text-white">
                Network Activity Pattern
              </h2>

              <p className="mt-1 text-xs text-slate-600">
                Observed traffic behavior compared with expected activity.
              </p>

            </div>

            <div className="flex items-center gap-4 text-[10px] text-slate-600">

              <span className="flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-cyan-400" />
                Normal
              </span>

              <span className="flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-fuchsia-400" />
                Anomaly
              </span>

            </div>

          </div>


          {/* Simple frontend chart */}

          <div className="relative mt-8 h-64 overflow-hidden rounded-xl border border-slate-800 bg-black/20 p-5">

            {/* Grid */}

            <div className="absolute inset-0 flex flex-col justify-between p-5 opacity-30">

              <span className="border-t border-slate-700" />
              <span className="border-t border-slate-700" />
              <span className="border-t border-slate-700" />
              <span className="border-t border-slate-700" />
              <span className="border-t border-slate-700" />

            </div>


            {/* SVG graph */}

            <svg
              className="relative h-full w-full"
              viewBox="0 0 1000 240"
              preserveAspectRatio="none"
            >

              <polyline
                points="0,170 80,150 160,158 240,130 320,145 400,110 480,120 560,92 640,105 720,75 800,95 880,65 1000,80"
                fill="none"
                stroke="rgb(34,211,238)"
                strokeWidth="4"
              />

              <polyline
                points="0,185 80,175 160,180 240,168 320,175 400,155 480,162 560,145 640,150 720,135 800,145 880,120 1000,130"
                fill="none"
                stroke="rgba(232,121,249,0.35)"
                strokeWidth="3"
                strokeDasharray="8 8"
              />

            </svg>

            <div className="absolute bottom-2 left-5 right-5 flex justify-between text-[9px] text-slate-700">

              <span>10 min ago</span>
              <span>8 min</span>
              <span>6 min</span>
              <span>4 min</span>
              <span>2 min</span>
              <span>Now</span>

            </div>

          </div>

        </section>


        {/* ==================================================
            THREAT DETECTION + STATISTICS
        ================================================== */}

        <section className="mb-6 grid gap-5 lg:grid-cols-[1.4fr_0.8fr]">

          {/* Threat Detection */}

          <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-6 backdrop-blur-xl">

            <div className="mb-5 flex items-center justify-between">

              <div className="flex items-center gap-3">

                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-cyan-400/10 text-cyan-400">
                  <ShieldCheck size={19} />
                </div>

                <div>

                  <h2 className="font-semibold text-white">
                    Threat Detection
                  </h2>

                  <p className="text-xs text-slate-600">
                    Machine-learning security assessment
                  </p>

                </div>

              </div>

              <span className="rounded-full border border-cyan-400/20 bg-cyan-400/10 px-3 py-1 text-[10px] font-semibold text-cyan-300">
                No Active Threats
              </span>

            </div>


            <div className="rounded-xl border border-cyan-400/15 bg-cyan-400/[0.03] p-5">

              <div className="flex items-start gap-4">

                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-cyan-400/10 text-cyan-400">
                  <CheckCircle2 size={20} />
                </div>

                <div>

                  <h3 className="text-sm font-semibold text-cyan-300">
                    Network behavior appears normal
                  </h3>

                  <p className="mt-1 text-xs leading-5 text-slate-600">
                    No active threat indicators have been detected
                    in the current analysis window.
                  </p>

                </div>

              </div>

            </div>

          </div>


          {/* Statistics */}

          <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-6 backdrop-blur-xl">

            <h2 className="font-semibold text-white">
              Analysis Statistics
            </h2>

            <div className="mt-5 space-y-4">

              <StatItem
                label="Packets Analyzed"
                value={analysis.packetsAnalyzed}
              />

              <StatItem
                label="Anomalies Detected"
                value={analysis.anomaliesDetected}
              />

              <StatItem
                label="Threats Detected"
                value={analysis.threatsDetected}
              />

            </div>

          </div>

        </section>


        {/* ==================================================
            RECENT ACTIVITY
        ================================================== */}

        <section className="rounded-2xl border border-slate-800 bg-slate-950/60 p-6 backdrop-blur-xl">

          <div className="mb-6 flex items-center gap-3">

            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-400/10 text-blue-400">
              <Clock3 size={19} />
            </div>

            <div>

              <h2 className="font-semibold text-white">
                Recent Activity
              </h2>

              <p className="text-xs text-slate-600">
                Latest network analysis events
              </p>

            </div>

          </div>


          <div className="space-y-4">

            {analysis.recentActivity.map((item, index) => (

              <div
                key={index}
                className="flex gap-4 rounded-xl border border-slate-800/70 bg-slate-900/20 p-4"
              >

                <div
                  className={`mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-full ${
                    item.type === 'warning'
                      ? 'bg-yellow-400/10 text-yellow-400'
                      : 'bg-cyan-400/10 text-cyan-400'
                  }`}
                >
                  {getActivityIcon(item.type)}
                </div>

                <div className="min-w-0 flex-1">

                  <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">

                    <h3 className="text-sm font-medium text-slate-300">
                      {item.title}
                    </h3>

                    <span className="text-[10px] text-slate-700">
                      {item.time}
                    </span>

                  </div>

                  <p className="mt-1 text-xs leading-5 text-slate-600">
                    {item.description}
                  </p>

                </div>

              </div>

            ))}

          </div>

        </section>

      </div>

    </main>
  );
}


// ======================================================
// SMALL COMPONENTS
// ======================================================

function MetricCard({ icon, label, value, description }) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-5 backdrop-blur-xl">

      <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-cyan-400/10 text-cyan-400">
        {icon}
      </div>

      <p className="mt-5 text-xs text-slate-600">
        {label}
      </p>

      <p className="mt-1 text-lg font-bold text-slate-200">
        {value}
      </p>

      <p className="mt-1 text-[10px] text-slate-700">
        {description}
      </p>

    </div>
  );
}


function DetailItem({ label, value }) {
  return (
    <div>

      <p className="text-[10px] uppercase tracking-wider text-slate-600">
        {label}
      </p>

      <p className="mt-1 truncate text-sm font-medium text-slate-300">
        {value}
      </p>

    </div>
  );
}


function AnalysisRow({ label, value, positive }) {
  return (
    <div className="flex items-center justify-between border-b border-slate-800/60 pb-3">

      <span className="text-xs text-slate-500">
        {label}
      </span>

      <span
        className={`flex items-center gap-2 text-xs font-medium ${
          positive
            ? 'text-cyan-300'
            : 'text-yellow-300'
        }`}
      >

        {positive ? (
          <CheckCircle2 size={14} />
        ) : (
          <AlertTriangle size={14} />
        )}

        {value}

      </span>

    </div>
  );
}


function StatItem({ label, value }) {
  return (
    <div className="flex items-center justify-between rounded-xl border border-slate-800 bg-slate-900/20 px-4 py-3">

      <span className="text-xs text-slate-500">
        {label}
      </span>

      <span className="text-sm font-bold text-cyan-300">
        {value}
      </span>

    </div>
  );
}

export default NetworkAnalysis;