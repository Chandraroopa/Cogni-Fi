import React, { useEffect, useMemo, useState } from 'react';

import { useLocation, useNavigate } from 'react-router-dom';

import {
  connectToPacketStream,
  disconnectFromPacketStream,
} from "../../services/websocket";

import {
  ArrowLeft,
  Wifi,
  ShieldCheck,
  ShieldAlert,
  ShieldX,
  Users,
  Clock3,
  AlertTriangle,
  Activity,
  CheckCircle2,
  LockKeyhole,
  Radio,
  Signal,
  Server,
  BarChart3,
  ChevronRight,
  RefreshCw,
} from 'lucide-react';

function NetworkAnalysis() {
  const [packets, setPackets] = useState([]);
const [connectionStatus, setConnectionStatus] = useState("connecting");
useEffect(() => {
  const handlePacket = (packet) => {
    setPackets((previousPackets) => {
      const updatedPackets = [packet, ...previousPackets];

      return updatedPackets.slice(0, 100);
    });
  };

  const handleStatus = (status) => {
    setConnectionStatus(status);
  };

  connectToPacketStream(handlePacket, handleStatus);

  return () => {
    disconnectFromPacketStream();
  };
}, []);
  const location = useLocation();
  const navigate = useNavigate();

  const selectedNetwork = location.state?.network;

  /*
   * =========================================================
   * TIME RANGE
   * =========================================================
   */

  const [timeRange, setTimeRange] = useState('30 min');

  /*
   * =========================================================
   * TEMPORARY FRONTEND ANALYSIS DATA
   *
   * Later these values will come from Flask + ML backend.
   * =========================================================
   */

  const analysis = {
    riskScore: 18,

    connectedDevices: 19,

    averageTime: '24 min',

    unusualActivity: 2,

    signalStrength: selectedNetwork?.signal || 92,

    activityData: {
      '10 min': [
        { time: '2:21', devices: 14 },
        { time: '2:23', devices: 16 },
        { time: '2:25', devices: 15 },
        { time: '2:27', devices: 18 },
        { time: '2:29', devices: 17 },
        { time: '2:30', devices: 19 },
      ],

      '30 min': [
        { time: '2:00', devices: 8 },
        { time: '2:05', devices: 11 },
        { time: '2:10', devices: 14 },
        { time: '2:15', devices: 12 },
        { time: '2:20', devices: 17 },
        { time: '2:25', devices: 15 },
        { time: '2:30', devices: 19 },
      ],

      '1 hour': [
        { time: '1:30', devices: 6 },
        { time: '1:40', devices: 9 },
        { time: '1:50', devices: 12 },
        { time: '2:00', devices: 8 },
        { time: '2:10', devices: 14 },
        { time: '2:20', devices: 17 },
        { time: '2:30', devices: 19 },
      ],

      '6 hours': [
        { time: '8 AM', devices: 4 },
        { time: '9 AM', devices: 7 },
        { time: '10 AM', devices: 13 },
        { time: '11 AM', devices: 18 },
        { time: '12 PM', devices: 15 },
        { time: '1 PM', devices: 21 },
        { time: '2 PM', devices: 19 },
      ],
    },

    recentActivity: [
      {
        type: 'success',
        title: 'Network scan completed',
        description: 'No major security concerns were found.',
        time: '2 min ago',
      },

      {
        type: 'success',
        title: '19 devices connected',
        description: 'The number of connected devices is within the normal range.',
        time: '5 min ago',
      },

      {
        type: 'warning',
        title: 'Unusual activity noticed',
        description: 'A small change in network behavior was detected.',
        time: '7 min ago',
      },

      {
        type: 'success',
        title: 'Network activity is stable',
        description: 'No major interruptions were detected.',
        time: '10 min ago',
      },
    ],
  };

  /*
   * =========================================================
   * RISK STATUS
   * =========================================================
   */

  const riskStatus = useMemo(() => {
    const score = analysis.riskScore;

    if (score <= 30) {
      return {
        title: 'SAFE TO CONNECT',
        label: 'Low Risk',
        message:
          'This network currently shows low-risk behavior.',
        icon: ShieldCheck,

        container:
          'border-emerald-400/30 bg-emerald-950/20',

        iconBox:
          'bg-emerald-400/10 text-emerald-400',

        titleColor:
          'text-emerald-400',

        badge:
          'border-emerald-400/30 bg-emerald-400/10 text-emerald-300',

        scoreColor:
          'text-emerald-400',
      };
    }

    if (score <= 70) {
      return {
        title: 'USE WITH CAUTION',
        label: 'Moderate Risk',
        message:
          'Some unusual activity has been detected on this network.',
        icon: ShieldAlert,

        container:
          'border-yellow-400/30 bg-yellow-950/20',

        iconBox:
          'bg-yellow-400/10 text-yellow-400',

        titleColor:
          'text-yellow-400',

        badge:
          'border-yellow-400/30 bg-yellow-400/10 text-yellow-300',

        scoreColor:
          'text-yellow-400',
      };
    }

    return {
      title: 'NOT RECOMMENDED',
      label: 'High Risk',
      message:
        'Suspicious behavior has been detected. We recommend avoiding this network.',
      icon: ShieldX,

      container:
        'border-red-400/30 bg-red-950/20',

      iconBox:
        'bg-red-400/10 text-red-400',

      titleColor:
        'text-red-400',

      badge:
        'border-red-400/30 bg-red-400/10 text-red-300',

      scoreColor:
        'text-red-400',
    };
  }, [analysis.riskScore]);

  /*
   * =========================================================
   * NO NETWORK SELECTED
   * =========================================================
   */

  if (!selectedNetwork) {
    return (
      <main className="min-h-screen bg-[#020611] px-6 py-10 text-white">

        <div className="mx-auto flex min-h-[70vh] max-w-xl flex-col items-center justify-center text-center">

          <div className="flex h-20 w-20 items-center justify-center rounded-2xl border border-cyan-400/20 bg-cyan-400/10 text-cyan-400">
            <Wifi size={38} />
          </div>

          <h1 className="mt-6 text-2xl font-bold">
            No Network Selected
          </h1>

          <p className="mt-3 text-sm leading-6 text-slate-500">
            Select a Wi-Fi network from the scanner to view
            its security analysis.
          </p>

          <button
            onClick={() => navigate('/wifi-scan')}
            className="mt-7 flex items-center gap-2 rounded-xl bg-gradient-to-r from-cyan-500 via-blue-500 to-fuchsia-500 px-6 py-3 text-sm font-semibold transition hover:scale-[1.02]"
          >
            <Wifi size={17} />
            Scan Networks
          </button>

        </div>

      </main>
    );
  }

  /*
   * =========================================================
   * CURRENT GRAPH DATA
   * =========================================================
   */

  const currentActivity =
    analysis.activityData[timeRange];

  const maxDevices = Math.max(
    30,
    ...currentActivity.map((item) => item.devices)
  );

  const peakDevices = Math.max(
    ...currentActivity.map((item) => item.devices)
  );

  /*
   * =========================================================
   * GRAPH DIMENSIONS
   * =========================================================
   */

  const chartWidth = 900;
  const chartHeight = 260;

  const points = currentActivity
    .map((item, index) => {

      const x =
        (index / (currentActivity.length - 1)) *
        chartWidth;

      const y =
        chartHeight -
        (item.devices / maxDevices) *
          chartHeight;

      return `${x},${y}`;
    })
    .join(' ');

  /*
   * =========================================================
   * MAIN DASHBOARD
   * =========================================================
   */

  return (
    <main className="min-h-screen bg-[#020611] px-5 py-7 text-white sm:px-8 lg:px-10">

      {/* Background glow */}

      <div className="pointer-events-none fixed left-1/2 top-0 h-[450px] w-[700px] -translate-x-1/2 rounded-full bg-cyan-950/20 blur-[160px]" />

      <div className="pointer-events-none fixed bottom-0 right-0 h-[400px] w-[400px] rounded-full bg-purple-950/20 blur-[160px]" />

      <div className="relative z-10 mx-auto max-w-[1400px]">

        {/* =====================================================
            HEADER
        ===================================================== */}

        <div className="mb-7 flex flex-col gap-4 border-b border-slate-800/70 pb-5 sm:flex-row sm:items-center sm:justify-between">

          <button
            onClick={() => navigate('/wifi-scan')}
            className="flex w-fit items-center gap-2 text-sm text-slate-500 transition hover:text-cyan-400"
          >
            <ArrowLeft size={16} />
            Back to Wi-Fi Scan
          </button>

          <div className="flex items-center gap-3 text-xs text-slate-600">

            <span>
              Analysis updated 2 min ago
            </span>

            <RefreshCw size={14} />

          </div>

        </div>


        {/* =====================================================
            SELECTED NETWORK
        ===================================================== */}

        <section className="mb-6">

          <div className="flex items-center gap-4">

            <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-full border border-cyan-400/30 bg-cyan-400/10 text-cyan-400">
              <Wifi size={32} />
            </div>

            <div className="min-w-0">

              <h1 className="truncate text-2xl font-bold tracking-tight sm:text-3xl">
                {selectedNetwork.name}
              </h1>

              <div className="mt-2 flex flex-wrap items-center gap-2 text-xs text-slate-500 sm:text-sm">

                <span>
                  {selectedNetwork.type || 'Wi-Fi Network'}
                </span>

                <span>•</span>

                <span>
                  {selectedNetwork.frequency || '2.4 GHz'}
                </span>

                <span>•</span>

                <span>
                  Channel {selectedNetwork.channel || '—'}
                </span>

                <span>•</span>

                <span>
                  {selectedNetwork.security || 'Unknown Security'}
                </span>

              </div>

            </div>

          </div>

        </section>


        {/* =====================================================
            RISK STATUS - FIRST THING USER SEES
        ===================================================== */}

        <section
          className={`mb-6 overflow-hidden rounded-2xl border ${riskStatus.container}`}
        >

          <div className="p-6 sm:p-7">

            <div className="flex flex-col gap-7 lg:flex-row lg:items-center lg:justify-between">

              {/* Status */}

              <div className="flex items-center gap-5">

                <div
                  className={`flex h-20 w-20 shrink-0 items-center justify-center rounded-full ${riskStatus.iconBox}`}
                >
                  <riskStatus.icon size={46} />
                </div>

                <div>

                  <div className="flex flex-wrap items-center gap-3">

                    <h2
                      className={`text-2xl font-bold sm:text-3xl ${riskStatus.titleColor}`}
                    >
                      {riskStatus.title}
                    </h2>

                    <span
                      className={`rounded-full border px-3 py-1 text-xs font-medium ${riskStatus.badge}`}
                    >
                      {riskStatus.label}
                    </span>

                  </div>

                  <p className="mt-2 max-w-xl text-sm leading-6 text-slate-400">
                    {riskStatus.message}
                  </p>

                </div>

              </div>


              {/* Risk Score */}

              <div className="border-t border-slate-800/70 pt-5 lg:border-l lg:border-t-0 lg:pl-10 lg:pt-0">

                <p className="text-sm font-medium text-slate-400">
                  Risk Score
                </p>

                <div className="mt-1 flex items-baseline gap-1">

                  <span
                    className={`text-5xl font-bold ${riskStatus.scoreColor}`}
                  >
                    {analysis.riskScore}
                  </span>

                  <span className="text-xl text-slate-500">
                    /100
                  </span>

                </div>

                <p className="mt-1 text-xs text-slate-600">
                  Lower score means lower risk
                </p>

              </div>

            </div>


            {/* Risk scale */}

            <div className="mt-8">

              <div className="relative h-2 rounded-full bg-gradient-to-r from-emerald-400 via-yellow-400 to-red-500">

                <div
                  className="absolute top-1/2 h-5 w-5 -translate-y-1/2 rounded-full border-4 border-white bg-slate-900 shadow-lg transition-all duration-500"
                  style={{
                    left: `${analysis.riskScore}%`,
                  }}
                />

              </div>

              <div className="mt-3 grid grid-cols-3 text-[10px] font-medium sm:text-xs">

                <span className="text-emerald-400">
                  0–30 Safe
                </span>

                <span className="text-center text-yellow-400">
                  31–70 Suspicious
                </span>

                <span className="text-right text-red-400">
                  71–100 Dangerous
                </span>

              </div>

            </div>

          </div>

        </section>


        {/* =====================================================
            QUICK METRICS
        ===================================================== */}

        <section className="mb-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">

          <MetricCard
            icon={<Users size={24} />}
            iconClass="bg-blue-400/10 text-blue-400"
            title="Connected Devices"
            value={analysis.connectedDevices}
            description="devices currently using this Wi-Fi"
          />

          <MetricCard
            icon={<Clock3 size={24} />}
            iconClass="bg-purple-400/10 text-purple-400"
            title="Average Time Connected"
            value={analysis.averageTime}
            description="average connection duration"
          />

          <MetricCard
            icon={<AlertTriangle size={24} />}
            iconClass="bg-yellow-400/10 text-yellow-400"
            title="Unusual Activity"
            value={analysis.unusualActivity}
            description="unusual events recently detected"
          />

          <MetricCard
            icon={<Signal size={24} />}
            iconClass="bg-emerald-400/10 text-emerald-400"
            title="Signal Strength"
            value={`${analysis.signalStrength}%`}
            description="current Wi-Fi signal"
          />

        </section>


        {/* =====================================================
            DEVICE ACTIVITY GRAPH
        ===================================================== */}

        <section className="mb-6 rounded-2xl border border-slate-800 bg-slate-950/70 p-5 backdrop-blur-xl sm:p-6">

          <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">

            <div>

              <div className="flex items-center gap-2">

                <Users
                  size={19}
                  className="text-cyan-400"
                />

                <h2 className="text-lg font-semibold">
                  Device Activity Over Time
                </h2>

              </div>

              <p className="mt-1 text-xs leading-5 text-slate-600">
                See how many devices are using this Wi-Fi over time.
              </p>

            </div>


            {/* Time range */}

            <div className="flex w-fit overflow-x-auto rounded-lg border border-slate-800 bg-slate-900/50 p-1">

              {[
                '10 min',
                '30 min',
                '1 hour',
                '6 hours',
              ].map((range) => (

                <button
                  key={range}
                  onClick={() => setTimeRange(range)}
                  className={`whitespace-nowrap rounded-md px-3 py-2 text-xs transition ${
                    timeRange === range
                      ? 'bg-gradient-to-r from-cyan-500 to-fuchsia-500 text-white shadow-lg shadow-cyan-500/10'
                      : 'text-slate-500 hover:text-white'
                  }`}
                >
                  {range}
                </button>

              ))}

            </div>

          </div>


          {/* Graph container */}

          <div className="relative mt-8 h-[310px] overflow-hidden rounded-xl border border-slate-800 bg-[#030914] p-5">

            {/* Grid */}

            <div className="absolute inset-x-5 bottom-12 top-6 flex flex-col justify-between">

              {[30, 20, 10, 0].map((number) => (

                <div
                  key={number}
                  className="flex items-center gap-3"
                >

                  <span className="w-6 text-[10px] text-slate-700">
                    {number}
                  </span>

                  <div className="h-px flex-1 border-t border-dashed border-slate-800" />

                </div>

              ))}

            </div>


            {/* SVG graph */}

            <div className="absolute bottom-12 left-14 right-5 top-6">

              <svg
                viewBox={`0 0 ${chartWidth} ${chartHeight}`}
                preserveAspectRatio="none"
                className="h-full w-full overflow-visible"
              >

                {/* Area */}

                <polygon
                  points={`0,${chartHeight} ${points} ${chartWidth},${chartHeight}`}
                  fill="rgba(34,211,238,0.06)"
                />

                {/* Main line */}

                <polyline
                  points={points}
                  fill="none"
                  stroke="rgb(34,211,238)"
                  strokeWidth="4"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />

                {/* Data points */}

                {currentActivity.map((item, index) => {

                  const x =
                    (index / (currentActivity.length - 1)) *
                    chartWidth;

                  const y =
                    chartHeight -
                    (item.devices / maxDevices) *
                      chartHeight;

                  return (
                    <g key={`${item.time}-${index}`}>

                      <circle
                        cx={x}
                        cy={y}
                        r="11"
                        fill="rgba(34,211,238,0.08)"
                      />

                      <circle
                        cx={x}
                        cy={y}
                        r="5"
                        fill="#020611"
                        stroke="rgb(34,211,238)"
                        strokeWidth="3"
                      />

                    </g>
                  );
                })}

              </svg>


              {/* Data labels */}

              <div className="absolute -bottom-7 left-0 right-0 flex justify-between">

                {currentActivity.map((item) => (

                  <span
                    key={item.time}
                    className="text-[9px] text-slate-600"
                  >
                    {item.time}
                  </span>

                ))}

              </div>


              {/* Device count labels */}

              <div className="absolute left-0 right-0 top-0 flex justify-between">

                {currentActivity.map((item, index) => (

                  <span
                    key={`${item.time}-label-${index}`}
                    className="rounded-md bg-slate-900/90 px-1.5 py-0.5 text-[10px] font-semibold text-slate-300"
                  >
                    {item.devices}
                  </span>

                ))}

              </div>

            </div>

          </div>


          {/* Graph summary */}

          <div className="mt-5 flex flex-col gap-3 text-xs sm:flex-row sm:items-center sm:justify-between">

            <div className="flex items-center gap-2 text-slate-500">

              <span className="h-2.5 w-2.5 rounded-full bg-cyan-400" />

              Connected devices

            </div>

            <div className="flex flex-wrap gap-5 text-slate-500">

              <span>
                Now:{' '}
                <strong className="text-slate-300">
                  {analysis.connectedDevices}
                </strong>
              </span>

              <span>
                Peak:{' '}
                <strong className="text-slate-300">
                  {peakDevices}
                </strong>
              </span>

              <span>
                Period:{' '}
                <strong className="text-slate-300">
                  {timeRange}
                </strong>
              </span>

            </div>

          </div>

        </section>


        {/* =====================================================
            INFORMATION CARDS
        ===================================================== */}

        <section className="mb-6 grid gap-5 lg:grid-cols-3">

          {/* Network Details */}

          <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-6">

            <SectionHeader
              icon={<Server size={18} />}
              title="Network Details"
            />

            <div className="mt-5 space-y-4">

              <InfoRow
                icon={<LockKeyhole size={16} />}
                label="Security"
                value={
                  selectedNetwork.security ||
                  'Unknown'
                }
              />

              <InfoRow
                icon={<Wifi size={16} />}
                label="Frequency"
                value={
                  selectedNetwork.frequency ||
                  '2.4 GHz'
                }
              />

              <InfoRow
                icon={<Radio size={16} />}
                label="Channel"
                value={
                  selectedNetwork.channel ||
                  '—'
                }
              />

              <InfoRow
                icon={<Signal size={16} />}
                label="Signal"
                value={`${analysis.signalStrength}%`}
                highlight
              />

            </div>

          </div>


          {/* Recent Activity */}

          <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-6">

            <SectionHeader
              icon={<Activity size={18} />}
              title="Recent Activity"
            />

            <div className="mt-5 space-y-4">

              {analysis.recentActivity.map(
                (item, index) => (

                  <div
                    key={index}
                    className="flex gap-3 border-b border-slate-800/60 pb-4 last:border-0"
                  >

                    <div
                      className={`mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-full ${
                        item.type === 'warning'
                          ? 'bg-yellow-400/10 text-yellow-400'
                          : 'bg-emerald-400/10 text-emerald-400'
                      }`}
                    >

                      {item.type === 'warning' ? (
                        <AlertTriangle size={14} />
                      ) : (
                        <CheckCircle2 size={14} />
                      )}

                    </div>

                    <div className="min-w-0 flex-1">

                      <div className="flex justify-between gap-2">

                        <p className="text-xs font-medium text-slate-300">
                          {item.title}
                        </p>

                        <span className="shrink-0 text-[9px] text-slate-700">
                          {item.time}
                        </span>

                      </div>

                      <p className="mt-1 text-[10px] leading-4 text-slate-600">
                        {item.description}
                      </p>

                    </div>

                  </div>

                )
              )}

            </div>

            <button className="mt-2 flex items-center gap-2 text-xs font-medium text-cyan-400 transition hover:text-cyan-300">
              View full activity log
              <ChevronRight size={14} />
            </button>

          </div>


          {/* Why this network is safe */}

          <div className="rounded-2xl border border-emerald-400/20 bg-emerald-950/10 p-6">

            <SectionHeader
              icon={<ShieldCheck size={18} />}
              title={
                analysis.riskScore <= 30
                  ? 'Why this network is safe'
                  : 'Why this network needs attention'
              }
              green={analysis.riskScore <= 30}
            />

            <div className="mt-5 space-y-4">

              {analysis.riskScore <= 30 ? (
                <>
                  <Reason text="The number of connected devices is currently within a normal range." />

                  <Reason text="Average connection duration appears normal." />

                  <Reason text="Only a small amount of unusual activity has been detected." />

                  <Reason
                    text={`The network uses ${selectedNetwork.security || 'a secured configuration'}.`}
                  />
                </>
              ) : analysis.riskScore <= 70 ? (
                <>
                  <Reason
                    text="Some unusual network behavior has been detected."
                  />

                  <Reason
                    text="The network should be monitored more closely."
                  />

                  <Reason
                    text="Avoid performing highly sensitive activities until the risk decreases."
                  />
                </>
              ) : (
                <>
                  <Reason
                    text="Suspicious network behavior has been detected."
                  />

                  <Reason
                    text="The current risk level is high."
                  />

                  <Reason
                    text="Avoid using this network for sensitive activities."
                  />
                </>
              )}

            </div>

            <button className="mt-5 flex items-center gap-2 text-xs font-medium text-cyan-400 transition hover:text-cyan-300">
              Learn more
              <ChevronRight size={14} />
            </button>

          </div>

        </section>
        {/* =====================================================
            FOOTER NOTE
        ===================================================== */}

        <div className="flex items-center justify-center gap-2 pb-5 text-[10px] text-slate-700">

          <ShieldCheck size={13} />

          Risk assessment is based on the current behavior of this network
          and may change over time.

        </div>

      </div>

    </main>
  );
}


/*
============================================================
METRIC CARD
============================================================
*/

function MetricCard({
  icon,
  iconClass,
  title,
  value,
  description,
}) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-5 backdrop-blur-xl transition hover:border-slate-700">

      <div
        className={`flex h-11 w-11 items-center justify-center rounded-xl ${iconClass}`}
      >
        {icon}
      </div>

      <p className="mt-5 text-xs font-medium text-slate-500">
        {title}
      </p>

      <p className="mt-1 text-2xl font-bold text-white">
        {value}
      </p>

      <p className="mt-1 text-[10px] leading-4 text-slate-600">
        {description}
      </p>

    </div>
  );
}


/*
============================================================
SECTION HEADER
============================================================
*/

function SectionHeader({
  icon,
  title,
  green = false,
}) {
  return (
    <div className="flex items-center gap-3">

      <div
        className={`flex h-9 w-9 items-center justify-center rounded-lg ${
          green
            ? 'bg-emerald-400/10 text-emerald-400'
            : 'bg-cyan-400/10 text-cyan-400'
        }`}
      >
        {icon}
      </div>

      <h2 className="font-semibold text-white">
        {title}
      </h2>

    </div>
  );
}


/*
============================================================
INFO ROW
============================================================
*/

function InfoRow({
  icon,
  label,
  value,
  highlight = false,
}) {
  return (
    <div className="flex items-center justify-between border-b border-slate-800/60 pb-3 last:border-0">

      <div className="flex items-center gap-3">

        <span className="text-slate-600">
          {icon}
        </span>

        <span className="text-xs text-slate-500">
          {label}
        </span>

      </div>

      <span
        className={`text-xs font-medium ${
          highlight
            ? 'text-emerald-400'
            : 'text-slate-300'
        }`}
      >
        {value}
      </span>

    </div>
  );
}


/*
============================================================
REASON
============================================================
*/

function Reason({ text }) {
  return (
    <div className="flex items-start gap-3">

      <div className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-emerald-400/10 text-emerald-400">

        <CheckCircle2 size={13} />

      </div>

      <p className="text-xs leading-5 text-slate-400">
        {text}
      </p>

    </div>
  );
}


export default NetworkAnalysis;