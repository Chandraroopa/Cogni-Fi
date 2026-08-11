import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, ShieldCheck } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

function CTASection() {
  const { isAuthenticated } = useAuth();

  return (
    <section className="bg-black px-6 py-16 md:px-12 lg:px-20">
      <div className="relative mx-auto max-w-[1200px] overflow-hidden rounded-2xl border border-cyan-400/20 bg-gradient-to-r from-cyan-400/10 via-blue-500/10 to-fuchsia-500/10 px-6 py-8 md:px-10 md:py-10">
        <div className="absolute -right-20 -top-20 h-56 w-56 rounded-full bg-cyan-400/10 blur-[100px]" />
        <div className="absolute -bottom-20 left-1/3 h-48 w-48 rounded-full bg-fuchsia-500/10 blur-[90px]" />

        <div className="relative z-10 flex flex-col items-start justify-between gap-7 md:flex-row md:items-center">
          <div className="flex items-start gap-4">
            <div className="hidden h-11 w-11 shrink-0 items-center justify-center rounded-xl border border-cyan-400/20 bg-cyan-400/10 text-cyan-400 sm:flex">
              <ShieldCheck size={21} />
            </div>

            <div>
              <h2 className="text-xl font-semibold text-white md:text-2xl">
                Know your network before you trust it.
              </h2>

              <p className="mt-1 max-w-xl text-sm leading-6 text-slate-400">
                Analyze network behavior and make safer connectivity decisions
                with CogniFi.
              </p>
            </div>
          </div>

          <Link
            to={isAuthenticated ? '/dashboard' : '/signup'}
            className="group flex shrink-0 items-center gap-2 rounded-md bg-cyan-400 px-6 py-3 text-sm font-semibold text-black no-underline transition hover:bg-cyan-300 hover:shadow-[0_0_25px_rgba(34,211,238,0.3)]"
          >
            {isAuthenticated ? 'Dashboard' : 'Get Started'}
            <ArrowRight
              size={17}
              className="transition-transform group-hover:translate-x-1"
            />
          </Link>
        </div>
      </div>
    </section>
  );
}

export default CTASection;