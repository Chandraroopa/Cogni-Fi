import React, { useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { supabase } from '../../services/supabaseClient';
import { useAuth } from '../../context/AuthContext';

function Alerts() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [busyId, setBusyId] = useState(null);

  const loadAlerts = useCallback(async () => {
    if (!user?.id) {
      setAlerts([]);
      setError('Sign in to view your security alerts.');
      setLoading(false);
      return;
    }
    setLoading(true);
    setError('');
    try {
      const { data: auth, error: authError } = await supabase.auth.getUser();
      if (authError || auth?.user?.id !== user.id) throw new Error('Your session has expired.');
      const { data, error: queryError } = await supabase
        .from('alerts')
        .select('id, user_id, scan_id, created_at, severity, title, risk_score, trust_score, attack_type, confidence, reasons, assessment, provisional, is_read')
        .eq('user_id', user.id)
        .order('created_at', { ascending: false });
      if (queryError) throw queryError;
      setAlerts(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error('Alert loading failed:', err);
      setError(`Unable to load alerts: ${err.message}`);
      setAlerts([]);
    } finally {
      setLoading(false);
    }
  }, [user?.id]);

  useEffect(() => { loadAlerts(); }, [loadAlerts]);

  const markAsRead = async (alert) => {
    if (alert.is_read || busyId) return;
    setBusyId(alert.id);
    setError('');
    try {
      const { error: updateError } = await supabase.from('alerts')
        .update({ is_read: true })
        .eq('id', alert.id)
        .eq('user_id', user.id);
      if (updateError) throw updateError;
      setAlerts(old => old.map(a => a.id === alert.id ? { ...a, is_read: true } : a));
    } catch (err) {
      setError(`Could not mark alert as read: ${err.message}`);
    } finally {
      setBusyId(null);
    }
  };

  return (
    <main className="min-h-screen bg-[#020611] px-5 py-10 text-white sm:px-8">
      <div className="mx-auto max-w-6xl">
        <p className="text-xs font-semibold uppercase tracking-[0.22em] text-cyan-400">Network Security</p>
        <h1 className="mt-2 text-3xl font-bold">Security Alerts</h1>
        <p className="mt-2 text-slate-400">Alerts generated from saved Wi-Fi assessments.</p>
        <div className="mt-5 flex flex-wrap gap-3">
          <button onClick={() => navigate('/dashboard')} className="rounded-lg border border-cyan-500/40 px-4 py-2 text-sm font-medium text-cyan-400 hover:bg-cyan-500/10">← Back to Dashboard</button>
          <button onClick={loadAlerts} className="rounded-lg border border-slate-600 px-4 py-2 text-sm font-medium text-slate-200 hover:bg-slate-800">Refresh alerts</button>
        </div>
        {error && <p role="alert" className="mt-5 rounded-lg border border-red-500/40 p-3 text-sm text-red-300">{error}</p>}
        {loading ? (
          <p className="mt-8 text-slate-400">Loading your alerts...</p>
        ) : alerts.length === 0 ? (
          <div className="mt-8 rounded-2xl border border-slate-800 bg-slate-950/60 p-8 text-center">
            <h2 className="text-lg font-semibold text-slate-200">No saved alerts available</h2>
            <p className="mt-2 text-sm text-slate-500">Alerts appear here when a saved assessment contains a real Suspicious or Risky alert. Unverified by itself does not create an alert.</p>
          </div>
        ) : (
          <div className="mt-8 space-y-4">
            <p className="text-sm text-slate-400">{alerts.length} saved alert{alerts.length === 1 ? '' : 's'}</p>
            {alerts.map(alert => (
              <article key={alert.id} className={`rounded-2xl border p-5 ${alert.is_read ? 'border-slate-800 bg-slate-950/60' : 'border-amber-500/40 bg-slate-900/80'}`}>
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <p className="text-xs uppercase tracking-wide text-slate-400">{alert.severity} severity {alert.provisional ? '· Provisional assessment' : ''}</p>
                    <h2 className="mt-1 text-lg font-semibold">{alert.title}</h2>
                    <p className="mt-1 text-sm text-slate-400">{new Date(alert.created_at).toLocaleString()}</p>
                  </div>
                  <span className="rounded-full border border-slate-600 px-3 py-1 text-xs text-slate-200">{alert.is_read ? 'Read' : 'Unread'}</span>
                </div>
                <div className="mt-3 flex flex-wrap gap-5 text-sm text-slate-200">
                  <span>Risk: {alert.risk_score ?? 'Not recorded'}</span>
                  <span>Trust: {alert.trust_score ?? 'Not recorded'}</span>
                  <span>Attack: {alert.attack_type || 'Not specified'}</span>
                  <span>Assessment: {alert.assessment}</span>
                </div>
                {Array.isArray(alert.reasons) && alert.reasons.length > 0 && (
                  <ul className="mt-3 list-disc space-y-1 pl-5 text-sm text-slate-300">{alert.reasons.map((reason, i) => <li key={i}>{String(reason)}</li>)}</ul>
                )}
                {!alert.is_read && (
                  <button disabled={busyId === alert.id} onClick={() => markAsRead(alert)} className="mt-4 rounded-lg border border-cyan-500/40 px-4 py-2 text-sm text-cyan-300 disabled:opacity-50">Mark as read</button>
                )}
              </article>
            ))}
          </div>
        )}
      </div>
    </main>
  );
}

export default Alerts;
