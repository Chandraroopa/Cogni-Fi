import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowRight, Menu, X } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

import cognifiLogo from '../../assets/cognifi-logo.png';

function Navbar() {
  const { isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  const [menuOpen, setMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    setMenuOpen(false);
    navigate('/');
  };

  const closeMenu = () => {
    setMenuOpen(false);
  };

  return (
    <>
      <nav className="relative z-50 w-full border-b border-white/10 bg-black/70 backdrop-blur-xl">

        <div className="mx-auto flex h-[72px] max-w-7xl items-center justify-between px-5 sm:px-8 lg:px-10">

          {/* ================= LOGO ================= */}
          <Link
            to="/"
            onClick={closeMenu}
            className="flex items-center gap-2 no-underline"
          >
            <img
              src={cognifiLogo}
              alt="CogniFi"
              className="h-15 w-30 object-contain"
            />
          </Link>


          {/* ================= DESKTOP NAVIGATION ================= */}
          <div className="hidden items-center gap-8 md:flex">

            <Link
              to="/"
              className="relative py-2 text-sm font-medium text-cyan-400 no-underline"
            >
              Home
              <span className="absolute bottom-0 left-0 h-[2px] w-full bg-cyan-400" />
            </Link>

            <a
              href="#features"
              className="text-sm font-medium text-slate-300 no-underline transition hover:text-cyan-400"
            >
              Features
            </a>

            <a
              href="#how-it-works"
              className="text-sm font-medium text-slate-300 no-underline transition hover:text-cyan-400"
            >
              How It Works
            </a>

            <a
              href="#about"
              className="text-sm font-medium text-slate-300 no-underline transition hover:text-cyan-400"
            >
              About
            </a>

            {isAuthenticated && (
              <Link
                to="/dashboard"
                className="text-sm font-medium text-slate-300 no-underline transition hover:text-cyan-400"
              >
                Dashboard
              </Link>
            )}

          </div>


          {/* ================= DESKTOP ACTION ================= */}
          <div className="hidden items-center gap-3 md:flex">

            {isAuthenticated ? (
              <button
                onClick={handleLogout}
                className="group flex items-center gap-2 rounded-md border border-cyan-400/60 bg-cyan-400/10 px-5 py-2.5 text-sm font-medium text-cyan-300 transition hover:bg-cyan-400 hover:text-black"
              >
                Logout

                <ArrowRight
                  size={16}
                  className="transition-transform group-hover:translate-x-1"
                />
              </button>
            ) : (
              <Link
                to="/signup"
                className="group flex items-center gap-2 rounded-md border border-cyan-400 bg-cyan-400 px-5 py-2.5 text-sm font-semibold text-black no-underline transition hover:bg-cyan-300"
              >
                Get Started

                <ArrowRight
                  size={16}
                  className="transition-transform group-hover:translate-x-1"
                />
              </Link>
            )}

          </div>


          {/* ================= MOBILE MENU BUTTON ================= */}
          <button
            onClick={() => setMenuOpen(true)}
            className="flex items-center justify-center rounded-md border border-white/10 bg-white/5 p-2 text-white transition hover:bg-white/10 md:hidden"
            aria-label="Open menu"
          >
            <Menu size={24} />
          </button>

        </div>
      </nav>


      {/* ========================================================= */}
      {/* MOBILE MENU                                               */}
      {/* ========================================================= */}

      {menuOpen && (
        <div className="fixed inset-0 z-[100] bg-black/95 backdrop-blur-xl md:hidden">

          <div className="flex h-full flex-col">

            {/* Mobile header */}
            <div className="flex h-[72px] items-center justify-between border-b border-white/10 px-5">

              <Link
                to="/"
                onClick={closeMenu}
                className="flex items-center gap-2 no-underline"
              >
                <img
                  src={cognifiLogo}
                  alt="CogniFi"
                  className="h-9 w-9 object-contain"
                />

                <span className="text-xl font-semibold text-white">
                  Cogni
                  <span className="text-cyan-400">Fi</span>
                </span>
              </Link>

              <button
                onClick={closeMenu}
                className="rounded-md border border-white/10 bg-white/5 p-2 text-white"
                aria-label="Close menu"
              >
                <X size={24} />
              </button>

            </div>


            {/* Mobile links */}
            <div className="flex flex-col px-6 pt-10">

              <Link
                to="/"
                onClick={closeMenu}
                className="border-b border-white/10 py-5 text-lg font-medium text-cyan-400 no-underline"
              >
                Home
              </Link>

              <a
                href="#features"
                onClick={closeMenu}
                className="border-b border-white/10 py-5 text-lg text-slate-300 no-underline"
              >
                Features
              </a>

              <a
                href="#how-it-works"
                onClick={closeMenu}
                className="border-b border-white/10 py-5 text-lg text-slate-300 no-underline"
              >
                How It Works
              </a>

              <a
                href="#about"
                onClick={closeMenu}
                className="border-b border-white/10 py-5 text-lg text-slate-300 no-underline"
              >
                About
              </a>

              {isAuthenticated && (
                <Link
                  to="/dashboard"
                  onClick={closeMenu}
                  className="border-b border-white/10 py-5 text-lg text-slate-300 no-underline"
                >
                  Dashboard
                </Link>
              )}

            </div>


            {/* Mobile CTA */}
            <div className="mt-auto p-6">

              {isAuthenticated ? (
                <button
                  onClick={handleLogout}
                  className="flex w-full items-center justify-center gap-2 rounded-md bg-cyan-400 py-3 font-semibold text-black transition hover:bg-cyan-300"
                >
                  Logout
                  <ArrowRight size={18} />
                </button>
              ) : (
                <Link
                  to="/signup"
                  onClick={closeMenu}
                  className="flex w-full items-center justify-center gap-2 rounded-md bg-cyan-400 py-3 font-semibold text-black no-underline transition hover:bg-cyan-300"
                >
                  Get Started
                  <ArrowRight size={18} />
                </Link>
              )}

            </div>

          </div>
        </div>
      )}
    </>
  );
}

export default Navbar;