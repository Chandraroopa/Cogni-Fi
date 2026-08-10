import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext'; // Member 2 (Ashwini) builds this hook

function Home() {
  const { isAuthenticated } = useAuth();

  return (
    <div>
      {/* Hero Section */}
      <section className="text-center py-5 bg-primary text-white">
        <h1 className="display-4 fw-bold">
          The Future of Smart Cyber-Solutions
        </h1>
        <p className="lead">
          Intelligent Behavioral Analysis of Public Networks — real-time
          detection of Wi-Fi threats like DNS spoofing and Evil Twin attacks.
        </p>
        <Link
          to={isAuthenticated ? '/dashboard' : '/login'}
          className="btn btn-light btn-lg mt-3"
        >
          {isAuthenticated ? 'Go to Dashboard' : 'Get Started'}
        </Link>
      </section>

      {/* Key Features Section */}
      <section className="container py-5">
        <h2 className="text-center mb-4">Key Features</h2>
        <div className="row g-4">
          <div className="col-md-4">
            <div className="card h-100 p-3 text-center shadow-sm">
              <h5>⚡ Real-time Detection</h5>
              <p className="text-muted">
                Continuously monitors network behavior to flag anomalies
                as they happen.
              </p>
            </div>
          </div>
          <div className="col-md-4">
            <div className="card h-100 p-3 text-center shadow-sm">
              <h5>🔒 Privacy-Preserving</h5>
              <p className="text-muted">
                Analyzes network metadata without exposing personal
                browsing data.
              </p>
            </div>
          </div>
          <div className="col-md-4">
            <div className="card h-100 p-3 text-center shadow-sm">
              <h5>📊 Trust Score</h5>
              <p className="text-muted">
                Gives every network a simple, color-coded safety rating.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

export default Home;
