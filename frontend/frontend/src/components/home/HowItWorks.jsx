import React from 'react';
import {
  ScanLine,
  Database,
  BrainCircuit,
  Gauge,
  ShieldCheck
} from 'lucide-react';

const steps = [
  {
    number: '01',
    icon: ScanLine,
    title: 'Scan Network',
    description:
      'CogniFi identifies the connected Wi-Fi network and collects relevant network characteristics.',
  },
  {
    number: '02',
    icon: Database,
    title: 'Collect Metadata',
    description:
      'Network metadata such as DNS response time, gateway latency, encryption status, BSSID, and traffic patterns is collected.',
  },
  {
    number: '03',
    icon: BrainCircuit,
    title: 'Analyze Behavior',
    description:
      'Behavioral signals are evaluated to identify patterns that differ from expected network behavior.',
  },
  {
    number: '04',
    icon: Gauge,
    title: 'Calculate Trust Score',
    description:
      'The analyzed signals are combined into a trust score between 0 and 100.',
  },
  {
    number: '05',
    icon: ShieldCheck,
    title: 'Show Risk',
    description:
      'CogniFi presents the network status as Safe, Suspicious, or Risky so users can make informed decisions.',
  }
];

function HowItWorks() {
  return (
    <section
      id="how-it-works"
      className="relative overflow-hidden bg-black px-6 py-16 md:px-12 lg:px-20"
    >
      <div className="absolute left-0 top-1/2 h-80 w-80 -translate-y-1/2 rounded-full bg-blue-500/5 blur-[130px]" />
      <div className="absolute right-0 top-1/3 h-72 w-72 rounded-full bg-cyan-400/5 blur-[120px]" />

      <div className="relative z-10 mx-auto max-w-[1200px]">
        <div className="mx-auto max-w-2xl text-center">
          <div className="mb-7 inline-flex items-center gap-2 rounded-full border border-cyan-400/30 bg-cyan-400/5 px-4 py-2 text-sm font-medium tracking-[0.15em] text-cyan-300">
            HOW COGNIFI WORKS
          </div>
          

          <h2 className="mt-4 text-3xl font-semibold tracking-tight text-white md:text-5xl">
            From network signals to
            <span className="bg-gradient-to-r from-cyan-400 via-blue-400 to-fuchsia-500 bg-clip-text text-transparent">
              {' '}security insight.
            </span>
          </h2>

          <p className="mt-5 max-w-xl text-base leading-7 text-slate-400 md:text-lg">
            CogniFi follows a multi-stage process to transform network
            behavior into an understandable security assessment.
          </p>
        </div>

        <div className="relative mt-16">
          <div className="absolute left-6 top-0 hidden h-full w-px bg-gradient-to-b from-cyan-400/50 via-blue-500/20 to-transparent md:block" />

          <div className="space-y-5">
            {steps.map((step) => {
              const Icon = step.icon;

              return (
                <div
                  key={step.number}
                  className="group relative flex gap-5 rounded-2xl border border-white/10 bg-white/[0.03] p-5 backdrop-blur-sm transition duration-300 hover:border-cyan-400/30 hover:bg-cyan-400/[0.03] md:gap-7 md:p-6"
                >
                  <div className="relative z-10 flex h-12 w-12 shrink-0 items-center justify-center rounded-xl border border-cyan-400/20 bg-black text-cyan-400 transition group-hover:border-cyan-400/50 group-hover:shadow-[0_0_20px_rgba(34,211,238,0.15)]">
                    <Icon size={21} />
                  </div>

                  <div className="flex-1">
                    <div className="flex flex-wrap items-center gap-3">
                      <span className="text-xs font-medium tracking-widest text-fuchsia-400">
                        {step.number}
                      </span>

                      <h3 className="text-lg font-semibold text-white">
                        {step.title}
                      </h3>
                    </div>

                    <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">
                      {step.description}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}

export default HowItWorks;