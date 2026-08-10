import React from 'react';

function Footer() {
  return (
    <footer className="bg-light text-center text-muted py-3 mt-5 border-top">
      <small>
        &copy; {new Date().getFullYear()} CogniFi  — CEC/CSE/2025-2026/P-09
      </small>
    </footer>
  );
}

export default Footer;
