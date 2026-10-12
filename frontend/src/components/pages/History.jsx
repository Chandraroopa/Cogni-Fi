import React from 'react';
import { useNavigate } from 'react-router-dom';

function History() {
    const navigate = useNavigate();
  return (
    <main className="min-h-screen bg-[#020611] px-5 py-10 text-white sm:px-8">
      <div className="mx-auto max-w-6xl">
        <p className="text-xs font-semibold uppercase tracking-[0.22em] text-cyan-400">
          Network Security
        </p>

        <h1 className="mt-2 text-3xl font-bold">Scan History</h1>

        <p className="mt-2 text-slate-400">
          Review your previous Wi-Fi scans and their results.
        </p>

        <button
  onClick={() => navigate('/dashboard')}
  className="mt-5 rounded-lg border border-cyan-500/40 px-4 py-2 text-sm font-medium text-cyan-400 transition hover:bg-cyan-500/10"
>
  ← Back to Dashboard
</button>

        <div className="mt-8 rounded-2xl border border-slate-800 bg-slate-950/60 p-8 text-center">
          <h2 className="text-lg font-semibold text-slate-200">
            No scan history available
          </h2>
          <p className="mt-2 text-sm text-slate-500">
            Scan records will appear here once scan history is stored.
          </p>
        </div>
      </div>
    </main>
  );
}

export default History;