import React from 'react';

function TrustScoreSection() {
  return (
    <section className="relative overflow-hidden bg-black px-6 py-16 md:px-12 lg:px-20">
      <div className="absolute left-1/2 top-1/2 h-80 w-[700px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-cyan-500/5 blur-[120px]" />

      <div className="relative z-10 mx-auto max-w-[1200px]">
        <div className="text-center">
          <span className="text-xs font-medium tracking-[0.25em] text-cyan-400">
            TRUST SCORE
          </span>

          <h2 className="mt-4 text-3xl font-semibold tracking-tight text-white md:text-5xl">
            Know how much you can
            <span className="bg-gradient-to-r from-cyan-400 via-blue-400 to-fuchsia-500 bg-clip-text text-transparent">
              {' '}trust your network.
            </span>
          </h2>

          <p className="mx-auto mt-4 max-w-2xl text-sm leading-6 text-slate-400 md:text-base">
            CogniFi combines network behavior and security signals into a
            simple score from 0 to 100.
          </p>
        </div>

        <div className="mt-10 rounded-2xl border border-white/10 bg-white/[0.02] px-6 py-10 backdrop-blur-sm md:px-16">
          <div className="mx-auto max-w-4xl">
            <div className="mb-4 flex items-center justify-between text-sm font-medium text-slate-400">
              <span>0</span>
              <span>100</span>
            </div>

            <div className="relative h-4 overflow-hidden rounded-full bg-slate-900">
              <div className="absolute inset-0 bg-gradient-to-r from-red-500 via-yellow-500 via-blue-500 to-cyan-400" />
              <div className="absolute inset-[2px] rounded-full bg-gradient-to-r from-red-500 via-yellow-500 via-blue-500 to-cyan-400 opacity-80 blur-[2px]" />
            </div>

            <div className="mt-5 grid grid-cols-3 text-center">
              <div>
                <p className="text-sm font-semibold text-red-400 md:text-base">
                  Risky
                </p>
                <p className="mt-1 text-xs text-slate-600">0 – 30</p>
              </div>

              <div>
                <p className="text-sm font-semibold text-yellow-400 md:text-base">
                  Suspicious
                </p>
                <p className="mt-1 text-xs text-slate-600">30 – 70</p>
              </div>

              <div>
                <p className="text-sm font-semibold text-cyan-400 md:text-base">
                  Safe
                </p>
                <p className="mt-1 text-xs text-slate-600">70 – 100</p>
              </div>
            </div>

            <div className="mt-10 grid gap-4 border-t border-white/10 pt-7 sm:grid-cols-3">
              <div className="text-center">
                <p className="text-xs font-medium uppercase tracking-wider text-red-400">
                  Risky
                </p>
                <p className="mt-2 text-sm text-slate-500">
                  Strong indicators of potentially unsafe network behavior.
                </p>
              </div>

              <div className="border-white/10 text-center sm:border-x">
                <p className="text-xs font-medium uppercase tracking-wider text-yellow-400">
                  Suspicious
                </p>
                <p className="mt-2 text-sm text-slate-500">
                  Unusual behavior detected. Additional caution is advised.
                </p>
              </div>

              <div className="text-center">
                <p className="text-xs font-medium uppercase tracking-wider text-cyan-400">
                  Safe
                </p>
                <p className="mt-2 text-sm text-slate-500">
                  Network behavior currently appears trustworthy.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default TrustScoreSection;