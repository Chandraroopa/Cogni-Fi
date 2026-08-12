import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowRight, Menu, X } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

function Navbar() {
  const { isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);
  const [showNavbar, setShowNavbar] = useState(true);

  const handleLogout = () => {
    logout();
    setMenuOpen(false);
    navigate('/');
  };

  const closeMenu = () => {
    setMenuOpen(false);
  };

  useEffect(() => {
    let lastScrollY = window.scrollY;

    const handleScroll = () => {
      const currentScrollY = window.scrollY;

      if (currentScrollY < 80) {
        setShowNavbar(true);
      } else if (currentScrollY > lastScrollY) {
        setShowNavbar(false);
      } else {
        setShowNavbar(true);
      }

      lastScrollY = currentScrollY;
    };

    const handleMouseMove = (e) => {
      if (e.clientY <= 80) {
        setShowNavbar(true);
      }
    };

    window.addEventListener('scroll', handleScroll);
    window.addEventListener('mousemove', handleMouseMove);

    return () => {
      window.removeEventListener('scroll', handleScroll);
      window.removeEventListener('mousemove', handleMouseMove);
    };
  }, []);

  return (
    <>
      <nav
        className={`sticky top-0 z-50 w-full border-b border-white/10 bg-black/70 backdrop-blur-xl transition-transform duration-300 ${
          showNavbar ? 'translate-y-0' : '-translate-y-full'
        }`}
      >
        <div className="flex h-[72px] w-full items-center justify-between px-4 sm:px-6 lg:px-8">
          <Link
            to="/"
            onClick={closeMenu}
            className="flex items-center gap-2 no-underline"
          >
            <img
              src="/android-chrome-192x192.png"
              alt="CogniFi logo"
              className="h-10 w-10 object-contain"
            />
            <span className="text-xl font-semibold text-white">
              Cogni<span className="text-cyan-400">Fi</span>
            </span>
          </Link>

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

            {isAuthenticated && (
              <Link
                to="/dashboard"
                className="text-sm font-medium text-slate-300 no-underline transition hover:text-cyan-400"
              >
                Dashboard
              </Link>
            )}
          </div>

          <div className="hidden items-center gap-3 md:flex">
            {!isAuthenticated && (
              <Link
                to="/login"
                className="rounded-md border border-white/20 bg-white/5 px-5 py-2.5 text-sm font-medium text-slate-200 no-underline transition hover:border-cyan-400/50 hover:bg-cyan-400/10 hover:text-cyan-400"
              >
                Sign In
              </Link>
            )}

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

          <button
            onClick={() => setMenuOpen(true)}
            className="flex items-center justify-center rounded-md border border-white/10 bg-white/5 p-2 text-white transition hover:bg-white/10 md:hidden"
            aria-label="Open menu"
          >
            <Menu size={24} />
          </button>
        </div>
      </nav>

      <div
        className={`fixed inset-0 z-[100] md:hidden transition-all duration-300 ${
          menuOpen
            ? 'visible bg-black/40 opacity-100 backdrop-blur-md'
            : 'invisible pointer-events-none bg-black/0 opacity-0 backdrop-blur-0'
        }`}
        onClick={closeMenu}
      >
        <div
          className={`ml-auto flex h-full w-[85%] max-w-sm flex-col border-l border-white/10 bg-black/60 backdrop-blur-xl transition-transform duration-300 ${
            menuOpen ? 'translate-x-0' : 'translate-x-full'
          }`}
          onClick={(e) => e.stopPropagation()}
        >
          <div className="flex h-[72px] items-center justify-between border-b border-white/10 px-5">
            <Link
              to="/"
              onClick={closeMenu}
              className="flex items-center gap-2 no-underline"
            >
              <img
                src="/android-chrome-192x192.png"
                alt="CogniFi logo"
                className="h-9 w-9 object-contain"
              />
              <span className="text-xl font-semibold text-white">
                Cogni<span className="text-cyan-400">Fi</span>
              </span>
            </Link>

            <button
              onClick={closeMenu}
              className="rounded-md border border-white/10 bg-white/5 p-2 text-white transition hover:bg-white/10"
              aria-label="Close menu"
            >
              <X size={24} />
            </button>
          </div>

          <div className="flex flex-col px-6 pt-8">
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
              className="border-b border-white/10 py-5 text-lg text-slate-300 no-underline transition hover:text-cyan-400"
            >
              Features
            </a>

            <a
              href="#how-it-works"
              onClick={closeMenu}
              className="border-b border-white/10 py-5 text-lg text-slate-300 no-underline transition hover:text-cyan-400"
            >
              How It Works
            </a>

            {isAuthenticated && (
              <Link
                to="/dashboard"
                onClick={closeMenu}
                className="border-b border-white/10 py-5 text-lg text-slate-300 no-underline transition hover:text-cyan-400"
              >
                Dashboard
              </Link>
            )}
          </div>

          <div className="mt-auto p-6">
            {!isAuthenticated && (
              <Link
                to="/login"
                onClick={closeMenu}
                className="mb-3 flex w-full items-center justify-center rounded-md border border-white/20 bg-white/5 py-3 font-medium text-white no-underline transition hover:border-cyan-400/50 hover:bg-cyan-400/10 hover:text-cyan-400"
              >
                Sign In
              </Link>
            )}

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
    </>
  );
}

export default Navbar;