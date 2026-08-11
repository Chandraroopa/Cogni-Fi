import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, ShieldCheck } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import cognifiLogo from '../../assets/cognifi-logo.png';

function HeroSection() {
  const { isAuthenticated } = useAuth();

  return (
    <section className="relative min-h-[calc(100vh-72px)] overflow-hidden bg-black">

      <div className="absolute inset-0 bg-black/45" />
      <div className="absolute right-[15%] top-[25%] h-[420px] w-[420px] rounded-full bg-cyan-500/10 blur-[130px]" />
      <div className="absolute right-[5%] top-[45%] h-[300px] w-[300px] rounded-full bg-fuchsia-500/10 blur-[120px]" />

      <div className="relative z-10 mx-auto flex min-h-[calc(100vh-72px)] max-w-[1400px] items-center px-6 py-20 md:px-12 lg:px-20">
        <div className="grid w-full grid-cols-1 items-center gap-12 lg:grid-cols-2 lg:gap-4">
          <div className="max-w-2xl">
            <div className="mb-7 inline-flex items-center gap-2 rounded-full border border-cyan-400/30 bg-cyan-400/5 px-4 py-2 text-xs font-medium tracking-[0.15em] text-cyan-300">
              <ShieldCheck size={14} />
              AI POWERED
              <span className="text-slate-600">•</span>
              PRIVACY FIRST
            </div>

            <h1 className="text-4xl font-semibold leading-[1.1] tracking-tight text-white sm:text-5xl md:text-6xl lg:text-[62px]">
              Know Your Network.
              <br />
              Before You
              <span className="bg-gradient-to-r from-cyan-400 via-blue-400 to-fuchsia-500 bg-clip-text text-transparent">
                {' '}Trust It.
              </span>
            </h1>

            <p className="mt-7 max-w-xl text-base leading-7 text-slate-300 md:text-lg">
              CogniFi analyzes Wi-Fi behavior in real time, detects suspicious
              activity, and generates an intelligent trust score so you can
              stay safer on any network.
            </p>

            <div className="mt-9 flex flex-wrap items-center gap-4">
              <Link
                to={isAuthenticated ? '/dashboard' : '/signup'}
                className="group flex items-center gap-2 rounded-md bg-cyan-400 px-6 py-3 font-semibold text-black no-underline transition duration-300 hover:bg-cyan-300 hover:shadow-[0_0_30px_rgba(34,211,238,0.3)]"
              >
                {isAuthenticated ? 'Go to Dashboard' : 'Get Started'}
                <ArrowRight
                  size={18}
                  className="transition-transform duration-300 group-hover:translate-x-1"
                />
              </Link>

              <a
                href="#how-it-works"
                className="flex items-center gap-2 rounded-md border border-slate-600 bg-black/20 px-6 py-3 font-medium text-white no-underline backdrop-blur-sm transition duration-300 hover:border-cyan-400/60 hover:bg-cyan-400/5"
              >
                Learn More
              </a>
            </div>
          </div>

          <div className="relative flex min-h-[420px] items-center justify-center lg:min-h-[520px]">
            <div className="absolute h-[280px] w-[280px] rounded-full bg-cyan-400/15 blur-[100px] md:h-[380px] md:w-[380px]" />
            <div className="absolute right-0 h-[220px] w-[220px] rounded-full bg-fuchsia-500/15 blur-[90px]" />

            <div className="absolute mt-[-120px] h-[300px] w-[300px] rounded-full border border-cyan-400/20 md:h-[390px] md:w-[390px]" />
            <div className="absolute mt-[-120px] h-[230px] w-[230px] rounded-full border border-blue-500/20 md:h-[310px] md:w-[310px]" />

            <div className="relative mt-[-120px] flex h-[250px] w-[250px] items-center justify-center md:h-[340px] md:w-[340px]">
              <div className="absolute inset-10 rounded-full bg-cyan-400/10 blur-2xl" />
              <img
                src={cognifiLogo}
                alt="CogniFi"
                className="relative z-10 h-full w-full object-contain md:h-72 md:w-72"
              />
            </div>

            <span className="absolute left-[10%] top-[30%] h-2 w-2 rounded-full bg-cyan-400 shadow-[0_0_15px_#22d3ee]" />
            <span className="absolute right-[10%] top-[25%] h-2 w-2 rounded-full bg-fuchsia-400 shadow-[0_0_15px_#e879f9]" />
            <span className="absolute bottom-[20%] left-[20%] h-1.5 w-1.5 rounded-full bg-blue-400 shadow-[0_0_15px_#60a5fa]" />
            <span className="absolute bottom-[25%] right-[15%] h-2 w-2 rounded-full bg-cyan-400 shadow-[0_0_15px_#22d3ee]" />
          </div>
        </div>
      </div>

      <div className="absolute bottom-0 left-0 h-32 w-full bg-gradient-to-t from-black to-transparent" />
    </section>
  );
}

export default HeroSection;