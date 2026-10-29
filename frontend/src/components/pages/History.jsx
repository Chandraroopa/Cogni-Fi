
import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { supabase } from '../../services/supabaseClient';
import { useAuth } from '../../context/AuthContext';

const STATUS_OPTIONS = [
  { value: 'all', label: 'All statuses' },
  { value: 'completed', label: 'Completed' },
  { value: 'in progress', label: 'In Progress' },
  { value: 'failed', label: 'Failed' },
  { value: 'incomplete', label: 'Incomplete' },
  { value: 'unknown', label: 'Unknown' },
];

const THREAT_OPTIONS = [
  { value: 'all', label: 'All classifications' },
  { value: 'threat', label: 'Threat Detected' },
  { value: 'normal', label: 'Normal' },
  { value: 'unavailable', label: 'Unavailable' },
];

function getTimestamp(record) {
  if (!record?.created_at) return null;

  const timestamp = new Date(record.created_at).getTime();
  return Number.isFinite(timestamp) ? timestamp : null;
}

function getStatus(record) {
  const raw = String(record?.status || '').trim().toLowerCase();

  if (['completed', 'complete', 'success', 'successful'].includes(raw)) {
    return 'completed';
  }

  if (['in progress', 'in_progress', 'running', 'pending'].includes(raw)) {
    return 'in progress';
  }

  if (['failed', 'error'].includes(raw)) return 'failed';
  if (['incomplete', 'partial'].includes(raw)) return 'incomplete';

  return 'unknown';
}

function getThreatClassification(record) {
  const status = String(record?.status || '').trim().toLowerCase();

  if (
    ['threat', 'risky', 'suspicious', 'malicious', 'threat detected'].includes(
      status
    )
  ) {
    return 'threat';
  }

  if (['normal', 'safe', 'no threat'].includes(status)) {
    return 'normal';
  }

  return 'unavailable';
}

function getNetworkName(record) {
  return record?.network_name || 'Network not recorded';
}

function getNumericScore(value) {
  if (value === null || value === undefined || value === '') return null;

  const number = Number(value);
  return Number.isFinite(number) ? number : null;
}

function formatScore(value) {
  const score = getNumericScore(value);
  return score === null ? 'Not recorded' : `${score}/100`;
}

function formatDate(value) {
  if (!value) return 'Date not recorded';

  const date = new Date(value);

  return Number.isFinite(date.getTime())
    ? date.toLocaleString()
    : 'Date not recorded';
}

function formatList(value) {
  if (value === null || value === undefined || value === '') {
    return 'Not recorded';
  }

  if (Array.isArray(value)) {
    return value.length ? value.map(String).join('; ') : 'None recorded';
  }

  if (typeof value === 'object') {
    return JSON.stringify(value, null, 2);
  }

  return String(value);
}

function getStatusStyle(status) {
  const styles = {
    completed: 'border-emerald-500/30 bg-emerald-500/10 text-emerald-300',
    'in progress': 'border-cyan-500/30 bg-cyan-500/10 text-cyan-300',
    failed: 'border-rose-500/30 bg-rose-500/10 text-rose-300',
    incomplete: 'border-amber-500/30 bg-amber-500/10 text-amber-300',
    unknown: 'border-slate-600 bg-slate-800 text-slate-300',
  };

  return styles[status] || styles.unknown;
}

function getThreatStyle(classification) {
  const styles = {
    threat: 'border-rose-500/30 bg-rose-500/10 text-rose-300',
    normal: 'border-emerald-500/30 bg-emerald-500/10 text-emerald-300',
    unavailable: 'border-slate-600 bg-slate-800 text-slate-300',
  };

  return styles[classification] || styles.unavailable;
}

function Badge({ children, className = '' }) {
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-medium ${className}`}
    >
      {children}
    </span>
  );
}

function SummaryCard({ label, value, description, icon, accent }) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-950/80 p-5 shadow-lg shadow-black/10">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm text-slate-400">{label}</p>
          <p className="mt-3 text-3xl font-semibold tracking-tight text-white">
            {value}
          </p>
        </div>
        <span
          className={`flex h-11 w-11 items-center justify-center rounded-xl text-lg ${accent}`}
          aria-hidden="true"
        >
          {icon}
        </span>
      </div>
      <p className="mt-3 text-xs text-slate-500">{description}</p>
    </div>
  );
}

function DetailRow({ label, value }) {
  return (
    <div className="min-w-0 rounded-xl border border-slate-800 bg-slate-900/60 p-4">
      <dt className="text-xs font-medium uppercase tracking-wide text-slate-500">
        {label}
      </dt>
      <dd className="mt-2 break-words whitespace-pre-wrap text-sm text-slate-200">
        {value === null || value === undefined || value === ''
          ? 'Not recorded'
          : String(value)}
      </dd>
    </div>
  );
}

function History() {
  const navigate = useNavigate();
  const { user } = useAuth();

  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [threatFilter, setThreatFilter] = useState('all');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [sortOrder, setSortOrder] = useState('newest');
  const [selected, setSelected] = useState(null);

  const loadHistory = useCallback(async () => {
    if (!user?.id) {
      setRecords([]);
      setError('Sign in to view your saved scan history.');
      setLoading(false);
      console.warn('[History Debug] No user ID available from AuthContext.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      // TEMPORARY DEBUGGING: Check the authenticated Supabase user.
      const { data: authData, error: authError } =
        await supabase.auth.getUser();

      console.log(
        '[History Debug] Authenticated user ID:',
        authData?.user?.id ?? null
      );

      console.log('[History Debug] Auth error:', authError);

      // Keep the existing history query unchanged.
      const { data, error: queryError } = await supabase
        .from('scan_history')
        .select(
          'id, user_id, created_at, network_name, security_type, risk_score, trust_score, status, assessment, attack_type, attack_confidence, factors, reasons, recommendations'
        )
        .eq('user_id', user.id)
        .order('created_at', { ascending: false });

      // TEMPORARY DEBUGGING: Show query errors and returned row count.
      console.log('[History Debug] Query error:', queryError);
      console.log(
        '[History Debug] Rows returned:',
        Array.isArray(data) ? data.length : null
      );

      if (queryError) throw queryError;

      setRecords(Array.isArray(data) ? data : []);
    } catch (err) {
      setRecords([]);
      setError(
        'We could not load saved history. Please retry. If the problem continues, contact the project owner.'
      );
      console.error('[History Debug] History load failed:', err);
    } finally {
      setLoading(false);
    }
  }, [user?.id]);

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  const filtered = useMemo(() => {
    const query = search.trim().toLowerCase();

    return records
      .filter((record) => {
        const searchableText = [
          record.network_name,
          record.security_type,
          record.id,
          record.status,
          record.assessment,
          record.attack_type,
        ]
          .filter((value) => value !== null && value !== undefined)
          .join(' ')
          .toLowerCase();

        if (query && !searchableText.includes(query)) return false;

        if (statusFilter !== 'all' && getStatus(record) !== statusFilter) {
          return false;
        }

        if (
          threatFilter !== 'all' &&
          getThreatClassification(record) !== threatFilter
        ) {
          return false;
        }

        const timestamp = getTimestamp(record);

        if (startDate) {
          const start = new Date(`${startDate}T00:00:00`).getTime();
          if (timestamp === null || timestamp < start) return false;
        }

        if (endDate) {
          const end = new Date(`${endDate}T23:59:59.999`).getTime();
          if (timestamp === null || timestamp > end) return false;
        }

        return true;
      })
      .sort((a, b) => {
        const left = getTimestamp(a);
        const right = getTimestamp(b);

        if (left === null && right === null) return 0;
        if (left === null) return 1;
        if (right === null) return -1;

        return sortOrder === 'newest' ? right - left : left - right;
      });
  }, [
    records,
    search,
    statusFilter,
    threatFilter,
    startDate,
    endDate,
    sortOrder,
  ]);

  const summary = useMemo(() => {
    const completed = records.filter(
      (record) => getStatus(record) === 'completed'
    ).length;

    const threats = records.filter(
      (record) => getThreatClassification(record) === 'threat'
    ).length;

    const latest = records.reduce((latestRecord, record) => {
      if (!latestRecord) return record;

      const currentTime = getTimestamp(record);
      const latestTime = getTimestamp(latestRecord);

      if (currentTime === null) return latestRecord;
      if (latestTime === null || currentTime > latestTime) return record;

      return latestRecord;
    }, null);

    return {
      total: records.length,
      completed,
      threats,
      latest: latest ? formatDate(latest.created_at) : 'No saved scans',
    };
  }, [records]);

  const clearFilters = () => {
    setSearch('');
    setStatusFilter('all');
    setThreatFilter('all');
    setStartDate('');
    setEndDate('');
    setSortOrder('newest');
  };

  const handleStartDateChange = (value) => {
    setStartDate(value);
    if (endDate && value && value > endDate) setEndDate(value);
  };

  const handleEndDateChange = (value) => {
    setEndDate(value);
    if (startDate && value && value < startDate) setStartDate(value);
  };

  const selectedThreat = selected
    ? getThreatClassification(selected)
    : 'unavailable';

  return (
    <main className="min-h-screen bg-[#020611] px-4 py-8 text-white sm:px-6 lg:px-8">
      <div className="mx-auto max-w-7xl">
        <header className="flex flex-col justify-between gap-5 sm:flex-row sm:items-end">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-cyan-400">
              Network Security
            </p>
            <h1 className="mt-2 text-3xl font-bold tracking-tight sm:text-4xl">
              Scan History
            </h1>
            <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-400">
              Review previously saved Wi-Fi assessments, their recorded risk
              levels, and available threat evidence.
            </p>
          </div>

          <div className="flex flex-wrap gap-3">
            <button
              type="button"
              onClick={() => navigate('/dashboard')}
              className="rounded-xl border border-slate-700 px-4 py-2.5 text-sm font-medium text-slate-300 transition hover:border-cyan-500/50 hover:text-white"
            >
              ← Dashboard
            </button>
            <button
              type="button"
              onClick={() => navigate('/wifi-scan')}
              className="rounded-xl bg-cyan-400 px-4 py-2.5 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300"
            >
              + New scan
            </button>
          </div>
        </header>

        <section
          aria-label="History summary"
          className="mt-8 grid gap-4 sm:grid-cols-2 xl:grid-cols-4"
        >
          <SummaryCard
            label="Total saved scans"
            value={summary.total}
            description="Records returned from saved history"
            icon="▤"
            accent="bg-cyan-400/10 text-cyan-300"
          />
          <SummaryCard
            label="Completed scans"
            value={summary.completed}
            description="Records explicitly marked completed"
            icon="✓"
            accent="bg-emerald-400/10 text-emerald-300"
          />
          <SummaryCard
            label="Threats detected"
            value={summary.threats}
            description="Records with a recognized threat status"
            icon="!"
            accent="bg-rose-400/10 text-rose-300"
          />
          <SummaryCard
            label="Latest saved scan"
            value={summary.total ? summary.latest : '—'}
            description="Based on recorded timestamps"
            icon="◷"
            accent="bg-violet-400/10 text-violet-300"
          />
        </section>

        <section className="mt-8 rounded-2xl border border-slate-800 bg-slate-950/70 p-4 sm:p-5">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-end">
            <div className="min-w-0 flex-1">
              <label
                htmlFor="history-search"
                className="mb-2 block text-xs font-medium text-slate-400"
              >
                Search history
              </label>
              <input
                id="history-search"
                type="search"
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                placeholder="Search network, ID, status, or attack type..."
                className="w-full rounded-xl border border-slate-700 bg-[#080f1e] px-4 py-3 text-sm text-white outline-none placeholder:text-slate-600 focus:border-cyan-400"
              />
            </div>

            <div className="grid gap-4 sm:grid-cols-2 lg:w-[420px]">
              <div>
                <label
                  htmlFor="history-status"
                  className="mb-2 block text-xs font-medium text-slate-400"
                >
                  Saved status
                </label>
                <select
                  id="history-status"
                  value={statusFilter}
                  onChange={(event) => setStatusFilter(event.target.value)}
                  className="w-full rounded-xl border border-slate-700 bg-[#080f1e] px-3 py-3 text-sm text-white outline-none focus:border-cyan-400"
                >
                  {STATUS_OPTIONS.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label
                  htmlFor="history-threat"
                  className="mb-2 block text-xs font-medium text-slate-400"
                >
                  Threat classification
                </label>
                <select
                  id="history-threat"
                  value={threatFilter}
                  onChange={(event) => setThreatFilter(event.target.value)}
                  className="w-full rounded-xl border border-slate-700 bg-[#080f1e] px-3 py-3 text-sm text-white outline-none focus:border-cyan-400"
                >
                  {THREAT_OPTIONS.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-[1fr_1fr_220px_auto] lg:items-end">
            <div>
              <label
                htmlFor="history-start-date"
                className="mb-2 block text-xs font-medium text-slate-400"
              >
                From date
              </label>
              <input
                id="history-start-date"
                type="date"
                value={startDate}
                max={endDate || undefined}
                onChange={(event) =>
                  handleStartDateChange(event.target.value)
                }
                className="w-full rounded-xl border border-slate-700 bg-[#080f1e] px-3 py-3 text-sm text-white outline-none focus:border-cyan-400"
              />
            </div>

            <div>
              <label
                htmlFor="history-end-date"
                className="mb-2 block text-xs font-medium text-slate-400"
              >
                To date
              </label>
              <input
                id="history-end-date"
                type="date"
                value={endDate}
                min={startDate || undefined}
                onChange={(event) =>
                  handleEndDateChange(event.target.value)
                }
                className="w-full rounded-xl border border-slate-700 bg-[#080f1e] px-3 py-3 text-sm text-white outline-none focus:border-cyan-400"
              />
            </div>

            <div>
              <label
                htmlFor="history-sort"
                className="mb-2 block text-xs font-medium text-slate-400"
              >
                Sort by date
              </label>
              <select
                id="history-sort"
                value={sortOrder}
                onChange={(event) => setSortOrder(event.target.value)}
                className="w-full rounded-xl border border-slate-700 bg-[#080f1e] px-3 py-3 text-sm text-white outline-none focus:border-cyan-400"
              >
                <option value="newest">Newest first</option>
                <option value="oldest">Oldest first</option>
              </select>
            </div>

            <button
              type="button"
              onClick={clearFilters}
              className="rounded-xl border border-slate-700 px-4 py-3 text-sm font-medium text-slate-300 transition hover:border-cyan-500/50 hover:text-white"
            >
              Clear filters
            </button>
          </div>

          <div className="mt-4 flex flex-wrap items-center justify-between gap-2 border-t border-slate-800 pt-4 text-xs text-slate-500">
            <span>
              Showing {filtered.length} of {records.length} saved records
            </span>
            <span>Only stored records are shown</span>
          </div>
        </section>

        {loading ? (
          <div
            className="mt-6 rounded-2xl border border-slate-800 bg-slate-950/70 p-12 text-center"
            role="status"
          >
            <div className="mx-auto h-8 w-8 animate-spin rounded-full border-2 border-slate-700 border-t-cyan-400" />
            <p className="mt-4 text-sm text-slate-300">
              Loading saved scan history...
            </p>
          </div>
        ) : error ? (
          <div
            className="mt-6 rounded-2xl border border-amber-500/30 bg-amber-500/5 p-6"
            role="alert"
          >
            <h2 className="font-semibold text-amber-200">
              History could not be loaded
            </h2>
            <p className="mt-2 text-sm leading-6 text-slate-400">{error}</p>
            <button
              type="button"
              onClick={loadHistory}
              className="mt-4 rounded-xl border border-amber-500/40 px-4 py-2 text-sm font-medium text-amber-200 transition hover:bg-amber-500/10"
            >
              Retry
            </button>
          </div>
        ) : records.length === 0 ? (
          <div className="mt-6 rounded-2xl border border-slate-800 bg-slate-950/70 px-5 py-14 text-center">
            <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl border border-cyan-500/20 bg-cyan-500/5 text-2xl text-cyan-300">
              ◷
            </div>
            <h2 className="mt-5 text-xl font-semibold">No saved scans yet</h2>
            <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-slate-400">
              When scan assessments are saved to your account, they will appear
              here. Starting a scan does not automatically mean a history
              record has been saved.
            </p>
            <button
              type="button"
              onClick={() => navigate('/wifi-scan')}
              className="mt-6 rounded-xl bg-cyan-400 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300"
            >
              Start a Wi-Fi scan
            </button>
          </div>
        ) : filtered.length === 0 ? (
          <div className="mt-6 rounded-2xl border border-slate-800 bg-slate-950/70 p-10 text-center">
            <h2 className="text-lg font-semibold">No matching records</h2>
            <p className="mt-2 text-sm text-slate-400">
              Try changing your search or filters.
            </p>
            <button
              type="button"
              onClick={clearFilters}
              className="mt-4 rounded-xl border border-slate-700 px-4 py-2 text-sm text-slate-300 hover:text-white"
            >
              Clear filters
            </button>
          </div>
        ) : (
          <section className="mt-6 overflow-hidden rounded-2xl border border-slate-800 bg-slate-950/70">
            <div className="flex flex-col gap-2 border-b border-slate-800 px-5 py-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <h2 className="font-semibold">Saved assessments</h2>
                <p className="mt-1 text-xs text-slate-500">
                  Select a record to view its stored details.
                </p>
              </div>
              <span className="text-xs text-slate-500">
                {filtered.length} record{filtered.length === 1 ? '' : 's'}
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full min-w-[900px] text-left text-sm">
                <thead className="bg-slate-900/80 text-xs uppercase tracking-wide text-slate-500">
                  <tr>
                    <th className="px-5 py-4 font-medium">Network</th>
                    <th className="px-5 py-4 font-medium">Status</th>
                    <th className="px-5 py-4 font-medium">Classification</th>
                    <th className="px-5 py-4 font-medium">Risk score</th>
                    <th className="px-5 py-4 font-medium">Trust score</th>
                    <th className="px-5 py-4 font-medium">Recorded at</th>
                    <th className="px-5 py-4 font-medium">Details</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/80">
                  {filtered.map((record) => {
                    const status = getStatus(record);
                    const threat = getThreatClassification(record);

                    return (
                      <tr
                        key={record.id}
                        className="transition hover:bg-cyan-500/[0.035]"
                      >
                        <td className="px-5 py-4">
                          <p className="max-w-[210px] truncate font-medium text-slate-200">
                            {getNetworkName(record)}
                          </p>
                          {record.security_type && (
                            <p className="mt-1 text-xs text-slate-500">
                              {record.security_type}
                            </p>
                          )}
                        </td>
                        <td className="px-5 py-4">
                          <Badge className={getStatusStyle(status)}>
                            {status === 'in progress'
                              ? 'In Progress'
                              : status.charAt(0).toUpperCase() +
                                status.slice(1)}
                          </Badge>
                        </td>
                        <td className="px-5 py-4">
                          <Badge className={getThreatStyle(threat)}>
                            {threat === 'threat'
                              ? 'Threat Detected'
                              : threat === 'normal'
                                ? 'Normal'
                                : 'Unavailable'}
                          </Badge>
                        </td>
                        <td className="px-5 py-4 text-slate-300">
                          {formatScore(record.risk_score)}
                        </td>
                        <td className="px-5 py-4 text-slate-300">
                          {formatScore(record.trust_score)}
                        </td>
                        <td className="whitespace-nowrap px-5 py-4 text-xs text-slate-400">
                          {formatDate(record.created_at)}
                        </td>
                        <td className="px-5 py-4">
                          <button
                            type="button"
                            onClick={() => setSelected(record)}
                            className="rounded-lg border border-cyan-500/30 px-3 py-2 text-xs font-semibold text-cyan-300 transition hover:bg-cyan-500/10"
                            aria-label={`View details for ${getNetworkName(record)}`}
                          >
                            View details
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </section>
        )}
      </div>

      {selected && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto bg-black/75 p-4 backdrop-blur-sm"
          onClick={() => setSelected(null)}
        >
          <section
            role="dialog"
            aria-modal="true"
            aria-labelledby="history-detail-title"
            className="my-auto max-h-[90vh] w-full max-w-3xl overflow-y-auto rounded-2xl border border-slate-700 bg-[#070d19] shadow-2xl shadow-black/50"
            onClick={(event) => event.stopPropagation()}
          >
            <header className="flex items-start justify-between gap-4 border-b border-slate-800 p-5 sm:p-6">
              <div className="min-w-0">
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-cyan-400">
                  Saved record
                </p>
                <h2
                  id="history-detail-title"
                  className="mt-2 break-words text-xl font-semibold sm:text-2xl"
                >
                  {getNetworkName(selected)}
                </h2>
                <p className="mt-2 text-sm text-slate-400">
                  {formatDate(selected.created_at)}
                </p>
              </div>
              <button
                type="button"
                onClick={() => setSelected(null)}
                className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-slate-700 text-xl text-slate-400 hover:text-white"
                aria-label="Close assessment details"
              >
                ×
              </button>
            </header>

            <div className="space-y-6 p-5 sm:p-6">
              <div className="flex flex-wrap gap-2">
                <Badge className={getStatusStyle(getStatus(selected))}>
                  {getStatus(selected) === 'unknown'
                    ? 'Status unavailable'
                    : getStatus(selected)}
                </Badge>
                <Badge className={getThreatStyle(selectedThreat)}>
                  {selectedThreat === 'threat'
                    ? 'Threat Detected'
                    : selectedThreat === 'normal'
                      ? 'Normal'
                      : 'Classification unavailable'}
                </Badge>
              </div>

              <div className="grid gap-3 sm:grid-cols-2">
                <DetailRow
                  label="Risk score"
                  value={formatScore(selected.risk_score)}
                />
                <DetailRow
                  label="Trust score"
                  value={formatScore(selected.trust_score)}
                />
                <DetailRow
                  label="Security type"
                  value={selected.security_type}
                />
                <DetailRow
                  label="Assessment"
                  value={selected.assessment}
                />
                <DetailRow
                  label="Attack type"
                  value={selected.attack_type}
                />
                <DetailRow
                  label="Attack confidence"
                  value={
                    selected.attack_confidence == null
                      ? 'Not recorded'
                      : selected.attack_confidence
                  }
                />
                <DetailRow label="Record ID" value={selected.id} />
                <DetailRow label="User ID" value={selected.user_id} />
                <DetailRow
                  label="Recorded at"
                  value={formatDate(selected.created_at)}
                />
              </div>

              <div>
                <h3 className="text-sm font-semibold text-slate-200">
                  Saved evidence
                </h3>
                <p className="mt-2 text-xs leading-5 text-slate-500">
                  These are the values saved in this history record. Missing
                  information is not treated as proof that the network is safe.
                </p>
                <div className="mt-3 grid gap-3 sm:grid-cols-2">
                  <DetailRow
                    label="Factors"
                    value={formatList(selected.factors)}
                  />
                  <DetailRow
                    label="Reasons"
                    value={formatList(selected.reasons)}
                  />
                  <DetailRow
                    label="Recommendations"
                    value={formatList(selected.recommendations)}
                  />
                </div>
              </div>

              <div className="flex justify-end border-t border-slate-800 pt-4">
                <button
                  type="button"
                  onClick={() => setSelected(null)}
                  className="rounded-xl bg-cyan-400 px-5 py-2.5 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300"
                >
                  Close details
                </button>
              </div>
            </div>
          </section>
        </div>
      )}
    </main>
  );
}

export default History;
