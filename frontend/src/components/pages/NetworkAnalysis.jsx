
import api from '../../services/api';
import React, { useState, useEffect, useCallback } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { Line, Doughnut } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  Tooltip,
  Legend,
  Filler
);

function NetworkAnalysis() {
  const location = useLocation();
  const navigate = useNavigate();

  const analysisResult = location.state?.analysisResult;
  const risk = analysisResult?.risk ?? null;

  const network = location.state?.network || {
    name: 'Unknown Network',
    signal: null,
    security: 'Unknown',
    channel: null,
  };

  const networkName =
    network?.name ||
    network?.ssid ||
    network?.network_name ||
    'Unknown Network';

  const encryption =
    network?.encryption ||
    network?.security ||
    'Unknown';

  const [loading, setLoading] = useState(true);
  const [apiError, setApiError] = useState('');
  const [signalHistory, setSignalHistory] = useState([]);

  const [details, setDetails] = useState({
    devices: [],
    connections: [],
    dns_latency: null,
    gateway_rtt: null,
    beacon_interval: null,
    packet_rate: null,
    total_packets: null,
  });

  const fetchNetworkDetails = useCallback(async () => {
    setLoading(true);
    setApiError('');

    try {
      const response = await api.get('/network-details');
      const data = response.data;

      if (!data || data.success !== true) {
        throw new Error('Network details API returned unsuccessful data.');
      }

      setDetails({
        ...data,
        devices: Array.isArray(data.devices) ? data.devices : [],
        connections: Array.isArray(data.connections)
          ? data.connections
          : [],
      });
    } catch (error) {
      console.error('Failed to fetch network details:', error);
      setApiError(
        'Unable to load network details. Please check the backend and try again.'
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchNetworkDetails();
  }, [fetchNetworkDetails]);

  // Collect genuine Windows Wi-Fi signal readings.
  // Prefer RSSI in dBm; use the real signal percentage when RSSI is unavailable.
  useEffect(() => {
    let cancelled = false;
    let requestInProgress = false;
    let intervalId;

    const fetchWifiSignal = async () => {
      if (cancelled || requestInProgress) return;

      requestInProgress = true;

      try {
        const response = await api.get('/wifi-signal');
        const data = response.data;

        if (cancelled || data?.available !== true) {
          return;
        }

        const hasRssi =
          typeof data.rssi_dbm === 'number' &&
          Number.isFinite(data.rssi_dbm) &&
          data.rssi_dbm <= 0 &&
          data.rssi_dbm >= -100;

        const hasSignalPercent =
          typeof data.signal_percent === 'number' &&
          Number.isFinite(data.signal_percent) &&
          data.signal_percent >= 0 &&
          data.signal_percent <= 100;

        // Ignore responses without a valid real measurement.
        if (!hasRssi && !hasSignalPercent) {
          return;
        }

        const parsedTimestamp = data.timestamp
          ? Date.parse(data.timestamp)
          : Date.now();

        const point = {
          timestamp: Number.isFinite(parsedTimestamp)
            ? parsedTimestamp
            : Date.now(),
          signal: hasRssi ? data.rssi_dbm : data.signal_percent,
          signalPercent: hasSignalPercent ? data.signal_percent : null,
          unit: hasRssi ? 'dBm' : '%',
        };

        setSignalHistory((previous) => {
          // Do not mix dBm and percentage values on the same vertical axis.
          // Start a new trend if the measurement unit changes.
          if (
            previous.length > 0 &&
            previous[previous.length - 1].unit !== point.unit
          ) {
            return [point];
          }

          return [...previous, point].slice(-60);
        });
      } catch (error) {
        if (!cancelled) {
          console.error('Failed to fetch Windows Wi-Fi signal:', error);
        }
      } finally {
        requestInProgress = false;
      }
    };

    fetchWifiSignal();
    intervalId = setInterval(fetchWifiSignal, 2000);

    return () => {
      cancelled = true;
      clearInterval(intervalId);
    };
  }, []);

  const formatMetric = (value, suffix = '') => {
    if (
      value === null ||
      value === undefined ||
      value === '' ||
      !Number.isFinite(Number(value))
    ) {
      return '—';
    }

    return `${Number(value).toLocaleString(undefined, {
      maximumFractionDigits: 2,
    })}${suffix}`;
  };

  const encryptionInfo = `${network.encryption || ''} ${
    network.security || ''
  }`
    .trim()
    .toUpperCase();

  const encryptionStatus =
    encryptionInfo.includes('WEP')
      ? {
          title: 'Weak Encryption',
          label: 'WEP',
          description:
            'This network uses WEP encryption, which is outdated and should not be relied on for security.',
          color: 'red',
        }
      : !encryptionInfo ||
          encryptionInfo.includes('UNKNOWN') ||
          encryptionInfo.includes('OPEN') ||
          encryptionInfo === 'NONE'
        ? {
            title: 'Open or Unknown Encryption',
            label: 'Needs Attention',
            description:
              'Encryption is open or could not be verified. Confirm the network security before using sensitive services.',
            color: 'red',
          }
        : encryptionInfo.includes('WPA3') ||
            encryptionInfo.includes('WPA2')
          ? {
              title: 'Encryption Detected',
              label: 'Threat Status Unverified',
              description:
                'WPA encryption is detected. This indicates link protection, but does not prove that the network is free of threats.',
              color: 'amber',
            }
          : {
              title: 'Encryption Needs Review',
              label: 'Threat Status Unverified',
              description:
                'The encryption type is not recognized by this check. A network-specific threat assessment is not available.',
              color: 'amber',
            };

  const statusColors = {
    red: {
      border: 'border-red-400/30',
      background: 'bg-red-400/10',
      icon: 'bg-red-400/15 text-red-300',
      title: 'text-red-300',
      badge: 'border-red-400/30 text-red-300',
    },
    amber: {
      border: 'border-amber-400/30',
      background: 'bg-amber-400/10',
      icon: 'bg-amber-400/15 text-amber-300',
      title: 'text-amber-300',
      badge: 'border-amber-400/30 text-amber-300',
    },
  };

  const statusColor = statusColors[encryptionStatus.color];

  const latestSignal = signalHistory.length
    ? signalHistory[signalHistory.length - 1]
    : null;

  const hasCurrentSignal = latestSignal !== null;
  const rawSignalValue = latestSignal?.signal;
  const currentSignalPercent = latestSignal?.signalPercent;
  const hasSignalHistory = signalHistory.length > 0;
  const signalUnit = latestSignal?.unit || 'dBm';
  const isRssiChart = signalUnit === 'dBm';

  const signalData = {
    labels: signalHistory.map((point) =>
      new Date(point.timestamp).toLocaleTimeString([], {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
      })
    ),
    datasets: [
      {
        fill: false,
        label: `Windows Wi-Fi Signal (${signalUnit})`,
        data: signalHistory.map((point) => point.signal),
        borderColor: '#06b6d4',
        backgroundColor: 'rgba(6, 182, 212, 0.18)',
        borderWidth: 2,
        pointBackgroundColor: '#06b6d4',
        pointBorderColor: '#ffffff',
        pointBorderWidth: 2,
        pointRadius: 2,
        pointHoverRadius: 6,
        pointHitRadius: 10,
        tension: 0,
        spanGaps: false,
      },
    ],
  };

  const signalOptions = {
    responsive: true,
    maintainAspectRatio: false,
    animation: { duration: 300 },
    plugins: {
      legend: { display: false },
      tooltip: {
        enabled: true,
        callbacks: {
          label: (context) => {
            const point = signalHistory[context.dataIndex];
            return `Signal: ${context.parsed.y} ${point?.unit || signalUnit}`;
          },
        },
      },
    },
    scales: {
      y: {
        min: isRssiChart ? -100 : 0,
        max: isRssiChart ? 0 : 100,
        title: {
          display: true,
          text: isRssiChart
            ? 'Signal strength (dBm)'
            : 'Signal strength (%)',
          color: '#94a3b8',
        },
        ticks: {
          stepSize: 10,
          color: '#64748b',
          font: { size: 11 },
        },
        grid: { color: 'rgba(255, 255, 255, 0.06)' },
      },
      x: {
        grid: { display: false },
        ticks: {
          color: '#64748b',
          font: { size: 11 },
          maxTicksLimit: 8,
          autoSkip: true,
        },
      },
    },
  };

  const listenCount = details.connections.filter(
    (connection) =>
      String(connection.status || '').toUpperCase() === 'LISTEN'
  ).length;

  const establishedCount = details.connections.filter(
    (connection) =>
      String(connection.status || '').toUpperCase() === 'ESTABLISHED'
  ).length;

  const otherSocketCount = details.connections.filter((connection) => {
    const status = String(connection.status || '').toUpperCase();
    return status !== 'LISTEN' && status !== 'ESTABLISHED';
  }).length;

  const socketTotal =
    listenCount + establishedCount + otherSocketCount;

  const socketData = {
    labels: ['Listening', 'Established', 'Other / Unknown'],
    datasets: [
      {
        data: [listenCount, establishedCount, otherSocketCount],
        backgroundColor: ['#c084fc', '#06b6d4', '#64748b'],
        borderColor: '#020617',
        borderWidth: 2,
        hoverOffset: 6,
      },
    ],
  };

  const socketOptions = {
    responsive: true,
    maintainAspectRatio: false,
    animation: { duration: 300 },
    plugins: {
      legend: {
        display: true,
        position: 'bottom',
        labels: {
          color: '#cbd5e1',
          padding: 16,
          usePointStyle: true,
        },
      },
      tooltip: {
        enabled: true,
        callbacks: {
          label: (context) => `${context.label}: ${context.raw}`,
        },
      },
    },
    cutout: '68%',
  };

  // Deduplicate returned IP/MAC pairs.
  const uniqueDevices = details.devices.filter(
    (device, index, devices) =>
      devices.findIndex(
        (item) => item.ip === device.ip && item.mac === device.mac
      ) === index
  );

  const classifyDevice = (device) => {
    const ip = String(device.ip || '');

    if (
      ip.startsWith('224.') ||
      ip.startsWith('239.') ||
      ip === '255.255.255.255'
    ) {
      return 'Multicast / Broadcast';
    }

    const lastOctet = ip.split('.').pop();

    if (/^\d+\.\d+\.\d+\.\d+$/.test(ip) && lastOctet === '255') {
      return 'Possible Broadcast';
    }

    return device.device || 'Subnet Node';
  };

  if (loading) {
    return (
      <main className="min-h-screen bg-gradient-to-br from-[#020617] via-[#090d1f] to-[#020617] text-white flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-cyan-400 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-slate-400 text-sm">
            Loading network details...
          </p>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-[#020617] via-[#090d1f] to-[#020617] text-white p-6 lg:p-10">
      <div className="max-w-[1400px] mx-auto">
        <header className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8 bg-slate-950/40 p-6 rounded-3xl border border-slate-800/85 shadow-2xl">
          <div>
            <button
              onClick={() => navigate('/dashboard')}
              className="text-xs uppercase tracking-widest text-cyan-400 mb-2 hover:text-cyan-300 font-bold transition"
            >
              ← Back to Dashboard
            </button>
            <h1 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-white via-slate-200 to-cyan-400 bg-clip-text text-transparent">
              Deep Network Behavioral Analysis
            </h1>
            <p className="mt-2 text-sm text-slate-400">
              Selected network: {networkName}
            </p>
          </div>

          <button
            onClick={fetchNetworkDetails}
            className="rounded-xl border border-cyan-400/30 bg-cyan-400/10 px-4 py-2 text-sm font-semibold text-cyan-300 hover:bg-cyan-400/20"
          >
            Retry network details
          </button>
        </header>

        {/* Network Security Status */}
        <section
          className={`mb-6 rounded-2xl border ${statusColor.border} ${statusColor.background} p-5`}
        >
          <div className="flex items-start gap-3">
            <div
              className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-full ${statusColor.icon}`}
            >
              <span className="text-2xl font-bold">!</span>
            </div>

            <div className="min-w-0 flex-1">
              <div className="flex flex-wrap items-center gap-2">
                <h2 className={`text-lg font-bold ${statusColor.title}`}>
                  {encryptionStatus.title}
                </h2>
                <span
                  className={`rounded-full border px-2.5 py-1 text-xs font-semibold ${statusColor.badge}`}
                >
                  {encryptionStatus.label}
                </span>
              </div>

              <p className="mt-2 text-sm leading-relaxed text-slate-300">
                Selected network:{' '}
                <span className="font-semibold text-white">
                  {networkName}
                </span>
              </p>

              <p className="mt-1 text-sm leading-relaxed text-slate-300">
                Encryption:{' '}
                <span className="font-semibold text-white">
                  {encryption}
                </span>
              </p>

              <p className="mt-2 text-sm leading-relaxed text-slate-400">
                {encryptionStatus.description}
              </p>

              {risk && (
                <>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-4">
                    <div className="rounded-xl bg-slate-950/50 p-4">
                      <p className="text-xs uppercase tracking-wider text-slate-400">
                        Risk Score
                      </p>
                      <p className="text-2xl font-bold text-amber-300 mt-1">
                        {formatMetric(risk.risk_score)}
                      </p>
                    </div>

                    <div className="rounded-xl bg-slate-950/50 p-4">
                      <p className="text-xs uppercase tracking-wider text-slate-400">
                        Trust Score
                      </p>
                      <p className="text-2xl font-bold text-cyan-300 mt-1">
                        {formatMetric(risk.trust_score)}
                      </p>
                    </div>
                  </div>


                </>
              )}
            </div>
          </div>
        </section>

        {apiError && (
          <div className="mb-6 rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-red-300">
            {apiError}
          </div>
        )}

        {/* Metrics */}
        <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 mb-8">
          <MetricCard
            title="Signal Strength"
            value={
              hasCurrentSignal
                ? `${rawSignalValue} ${signalUnit}`
                : 'Unavailable'
            }
            description={
              hasCurrentSignal
                ? signalUnit === 'dBm'
                  ? `Windows Wi-Fi RSSI${
                      typeof currentSignalPercent === 'number'
                        ? ` • ${currentSignalPercent}% signal`
                        : ''
                    }`
                  : 'Windows Wi-Fi signal percentage'
                : 'Waiting for Windows Wi-Fi telemetry'
            }
            color="text-cyan-400"
          />

          <MetricCard
            title="DNS Latency"
            value={
              apiError ? '—' : formatMetric(details.dns_latency, ' ms')
            }
            description="Backend-reported name-resolution delay"
            color="text-blue-400"
          />

          <MetricCard
            title="Gateway RTT"
            value={
              apiError ? '—' : formatMetric(details.gateway_rtt, ' ms')
            }
            description="Backend-reported gateway round-trip time"
            color="text-purple-400"
          />

          <MetricCard
            title="Beacon Interval"
            value={
              apiError ? '—' : formatMetric(details.beacon_interval)
            }
            description="Backend-reported value; unit not verified"
            color="text-emerald-400"
          />

          <MetricCard
            title="Packet Rate"
            value={
              apiError ? '—' : formatMetric(details.packet_rate, ' pkts/s')
            }
            description={`Total Packets: ${
              apiError ? '—' : formatMetric(details.total_packets)
            }`}
            color="text-amber-400"
          />

          <MetricCard
            title="Socket Entries"
            value={
              apiError
                ? '—'
                : details.connections.length.toLocaleString()
            }
            description="Entries reported by the local connection API"
            color="text-indigo-400"
          />
        </section>

        {/* Charts */}
        <section className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <div className="lg:col-span-2 min-w-0 bg-slate-950/60 border border-slate-800/80 p-6 rounded-3xl shadow-2xl">
            <h2 className="text-base font-bold text-cyan-400 mb-2">
              Signal Strength Trend
            </h2>
            <div className="h-[260px] w-full relative">
              {hasSignalHistory ? (
                <Line
                  data={signalData}
                  options={signalOptions}
                  role="img"
                  aria-label={`Windows Wi-Fi signal trend in ${signalUnit}`}
                />
              ) : (
                <div className="absolute inset-0 flex flex-col items-center justify-center rounded-xl border border-dashed border-slate-800 bg-slate-900/30 px-5 text-center">
                  <span className="text-sm font-semibold text-slate-300">
                    Signal strength unavailable
                  </span>
                  <span className="mt-2 max-w-md text-xs leading-relaxed text-slate-500">
                    Waiting for real Windows Wi-Fi measurements. Readings
                    are requested every two seconds.
                  </span>
                </div>
              )}
            </div>
          </div>

          <div className="min-w-0 bg-slate-950/60 border border-slate-800/80 p-6 rounded-3xl shadow-2xl">
            <h2 className="text-base font-bold text-purple-400 mb-2">
              Socket State Distribution
            </h2>
            <p className="text-xs text-slate-500 mb-4">
              Local machine socket states, not a device count for the selected
              Wi-Fi.
            </p>

            <div className="relative h-[230px] w-full flex items-center justify-center">
              {socketTotal > 0 ? (
                <Doughnut
                  data={socketData}
                  options={socketOptions}
                  role="img"
                  aria-label="Local machine socket state distribution chart"
                />
              ) : (
                <p className="text-sm text-slate-500 text-center">
                  No socket-state data is available.
                </p>
              )}
            </div>

            <div className="mt-3 text-center text-xs text-slate-400">
              {listenCount} listening · {establishedCount} established ·{' '}
              {otherSocketCount} other
            </div>
          </div>
        </section>

        {/* Local Subnet Nodes */}
        <section className="bg-slate-950/60 border border-slate-800/80 rounded-3xl p-6 mb-8 shadow-2xl">
          <h2 className="text-lg font-bold text-cyan-400 mb-2">
            Local Subnet Nodes
          </h2>
          <p className="text-xs text-slate-500 mb-4">
            Duplicate IP/MAC pairs are removed. Multicast and broadcast
            addresses are identified separately where possible. Entries are
            not necessarily confirmed Wi-Fi clients.
          </p>

          <div className="overflow-x-auto">
            {apiError ? (
              <p className="text-slate-500 text-sm py-4">
                Device information is unavailable because the API request
                failed.
              </p>
            ) : uniqueDevices.length === 0 ? (
              <p className="text-slate-500 text-sm py-4">
                No subnet nodes were returned by the backend.
              </p>
            ) : (
              <table className="w-full text-left text-sm">
                <thead className="border-b border-slate-800 text-slate-400 text-xs uppercase tracking-wider">
                  <tr>
                    <th className="pb-3 pr-4 font-semibold">
                      Device Description
                    </th>
                    <th className="pb-3 pr-4 font-semibold">IP Address</th>
                    <th className="pb-3 pr-4 font-semibold">MAC Address</th>
                    <th className="pb-3 font-semibold">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/40">
                  {uniqueDevices.map((device, index) => (
                    <tr
                      key={`${device.mac || 'no-mac'}-${device.ip || 'no-ip'}-${index}`}
                      className="hover:bg-slate-900/50 transition"
                    >
                      <td className="py-4 pr-4 font-semibold text-white">
                        {classifyDevice(device)}
                      </td>
                      <td className="py-4 pr-4 text-cyan-300 font-mono">
                        {device.ip || '—'}
                      </td>
                      <td className="py-4 pr-4 text-slate-400 font-mono text-xs">
                        {device.mac || '—'}
                      </td>
                      <td className="py-4">
                        <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-slate-500/10 text-slate-300 border border-slate-500/20 rounded-xl text-xs font-semibold">
                          {device.status || 'Unknown'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </section>
      </div>
    </main>
  );
}

function MetricCard({ title, value, description, color }) {
  return (
    <div className="bg-slate-950/60 border border-slate-800/80 p-6 rounded-3xl shadow-xl hover:border-slate-700 transition">
      <p className="text-xs text-slate-400 uppercase tracking-wider font-semibold">
        {title}
      </p>
      <p className={`text-3xl font-black mt-2 tracking-tight ${color}`}>
        {value}
      </p>
      <p className="text-xs text-slate-400 mt-2">{description}</p>
    </div>
  );
}

export default NetworkAnalysis;
