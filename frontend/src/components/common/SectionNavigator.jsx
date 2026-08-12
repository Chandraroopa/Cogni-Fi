import React, { useState } from 'react';
import {
  Plus,
  X,
  Home,
  Shield,
  Network,
  Activity,
  Info,
} from 'lucide-react';

function SectionNavigator() {
  const [open, setOpen] = useState(false);

  const sections = [
    {
      id: 'home',
      label: 'Home',
      icon: Home,
    },
    {
      id: 'features',
      label: 'Features',
      icon: Shield,
    },
    {
      id: 'how-it-works',
      label: 'How It Works',
      icon: Network,
    },
    {
      id: 'trust-score',
      label: 'Trust Score',
      icon: Activity,
    },
  ];

  const scrollToSection = (id) => {
    const element = document.getElementById(id);

    if (element) {
      element.scrollIntoView({
        behavior: 'smooth',
        block: 'start',
      });
    }

    setOpen(false);
  };

  return (
    <div className="fixed bottom-6 right-6 z-[90] flex flex-col items-end gap-3">
      <div
        className={`flex flex-col items-end gap-3 transition-all duration-300 ${
          open
            ? 'visible translate-y-0 opacity-100'
            : 'invisible translate-y-4 opacity-0 pointer-events-none'
        }`}
      >
        {sections.map(({ id, label, icon: Icon }) => (
            <button
                key={id}
                onClick={() => scrollToSection(id)}
                className="group relative flex items-center"
                >
                <span className="pointer-events-none absolute right-14 whitespace-nowrap rounded-md border border-white/10 bg-black/80 px-3 py-2 text-xs font-medium text-slate-300 opacity-0 backdrop-blur-xl transition-all duration-200 group-hover:translate-x-0 group-hover:opacity-100 translate-x-2">
                    {label}
                </span>

                <span className="flex h-10 w-10 items-center justify-center rounded-full border border-white/10 bg-black/70 text-slate-300 backdrop-blur-xl transition duration-200 group-hover:border-cyan-400/50 group-hover:bg-cyan-400/10 group-hover:text-cyan-400">
                    <Icon size={17} />
                </span>
            </button>
        ))}
      </div>

      <button
        onClick={() => setOpen(!open)}
        className="flex h-14 w-14 items-center justify-center rounded-full border border-cyan-400/40 bg-black/70 text-cyan-400 shadow-[0_0_25px_rgba(34,211,238,0.15)] backdrop-blur-xl transition duration-300 hover:scale-110 hover:border-cyan-400 hover:bg-cyan-400/10"
        aria-label="Section navigation"
      >
        {open ? (
          <X size={24} />
        ) : (
          <Plus size={24} />
        )}
      </button>
    </div>
  );
}

export default SectionNavigator;