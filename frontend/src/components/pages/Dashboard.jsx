import React from 'react';

function Dashboard() {
  return React.createElement(
    'div',
    { className: 'container py-5 text-center text-muted' },
    React.createElement('h3', null, 'Dashboard — coming soon'),
    React.createElement(
      'p',
      null,
      '(Placeholder — Member 4 to implement: RiskScore, AlertsList, ActivityChart, NetworkTable)'
    )
  );
}

export default Dashboard;
