import React from 'react';

function Footer() {
  return (
    <footer className="bg-black/20 px-6 py-10 backdrop-blur-md md:px-12 lg:px-20">
      <div className="border-t border-white/10 pt-6 text-xs text-slate-500">
        <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
          <p>
            © {new Date().getFullYear()} CogniFi. All rights reserved.
          </p>
          <p>CEC/CSE/2025-2026/P-09</p>
        </div>
      </div>
    </footer>
  );
}

export default Footer;