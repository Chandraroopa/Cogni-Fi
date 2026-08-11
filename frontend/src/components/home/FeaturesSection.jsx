import React from 'react';
import {
  Activity,
  BrainCircuit,
  Gauge,
  LockKeyhole,
  Network,
  ShieldAlert
} from 'lucide-react';

const features = [
  {
    icon: Network,
    title: 'Wi-Fi Behavior Analysis',
    description:
      'Analyzes network metadata and behavioral patterns to understand how a Wi-Fi network behaves.',
  },
  {
    icon: ShieldAlert,
    title: 'Threat Detection',
    description:
      'Identifies suspicious patterns associated with threats such as evil twin networks, DNS spoofing, and MITM activity.',
  },
  {
    icon: Gauge,
    title: 'Trust Score',
    description:
      'Converts multiple network signals into an easy-to-understand trust score from 0 to 100.',
  },
  {
    icon: BrainCircuit,
    title: 'Intelligent Detection',
    description:
      'Uses machine learning models to recognize abnormal network behavior and improve threat classification.',
  },
  {
    icon: Activity,
    title: 'Real-Time Monitoring',
    description:
      'Continuously observes network behavior and provides security insights as conditions change.',
  },
  {
    icon: LockKeyhole,
    title: 'Privacy-Aware',
    description:
      'Focuses on network metadata and behavioral signals without inspecting the actual content of user communications.',
  },
];

function FeaturesSection() {
  return (
    <section id="features" className="relative overflow-hidden bg-black px-6 py-16 md:px-12 lg:px-20">
      <div className="absolute left-1/4 top-1/3 h-72 w-72 rounded-full bg-cyan-500/5 blur-[120px]" />
      <div className="absolute right-1/4 bottom-0 h-72 w-72 rounded-full bg-fuchsia-500/5 blur-[120px]" />

      <div className="relative z-10 mx-auto max-w-[1200px]">
        <div className="mx-auto max-w-2xl text-center">
          <span className="text-xs font-medium tracking-[0.2em] text-cyan-400">
            WHY COGNIFI
          </span>

          <h2 className="mt-4 text-3xl font-semibold tracking-tight text-white md:text-5xl">
            Security insights without the
            <span className="bg-gradient-to-r from-cyan-400 to-fuchsia-500 bg-clip-text text-transparent">
              {' '}complexity.
            </span>
          </h2>

          <p className="mt-5 text-base leading-7 text-slate-400 md:text-lg">
            CogniFi combines behavioral analysis, active verification, and
            machine learning to help you understand whether a network is safe
            before you trust it.
          </p>
        </div>

        <div className="mt-16 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((feature, index) => {
            const Icon = feature.icon;

            return (
              <div
                key={feature.title}
                className="group relative rounded-2xl border border-white/10 bg-white/[0.03] p-6 backdrop-blur-sm transition duration-300 hover:-translate-y-1 hover:border-cyan-400/30 hover:bg-cyan-400/[0.04]"
              >
                <div className="mb-6 flex h-11 w-11 items-center justify-center rounded-xl border border-cyan-400/20 bg-cyan-400/10 text-cyan-400 transition group-hover:border-cyan-400/40 group-hover:shadow-[0_0_20px_rgba(34,211,238,0.15)]">
                  <Icon size={21} />
                </div>

                <span className="absolute right-5 top-5 text-xs font-medium text-slate-700">
                  0{index + 1}
                </span>

                <h3 className="text-lg font-semibold text-white">
                  {feature.title}
                </h3>

                <p className="mt-3 text-sm leading-6 text-slate-400">
                  {feature.description}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}

export default FeaturesSection;