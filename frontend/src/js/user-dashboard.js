/* ============ SIDEBAR / VIEW NAVIGATION ============ */
document.addEventListener('DOMContentLoaded', () => {
  const sideLinks   = document.querySelectorAll('.side-link[data-view]');
  const views       = document.querySelectorAll('.view');
  const pageTitle   = document.getElementById('pageTitle');
  const sidebar     = document.getElementById('sidebar');
  const menuBtn     = document.getElementById('menuBtn');
  const scrim       = document.getElementById('scrim');

  function activateView(name) {
    views.forEach(v => { v.style.display = (v.id === 'view-' + name) ? '' : 'none'; });
    sideLinks.forEach(l => l.classList.toggle('active', l.dataset.view === name));
    if (pageTitle) {
      const label = document.querySelector('.side-link[data-view="' + name + '"]')?.textContent.trim();
      pageTitle.textContent = label || name;
    }
    closeSidebar();
  }

  sideLinks.forEach(link => {
    link.addEventListener('click', () => {
      activateView(link.dataset.view);
      closeSidebar();
    });
  });

  document.querySelectorAll('[data-view-link]').forEach(el => {
    el.addEventListener('click', (e) => {
      e.preventDefault();
      activateView(el.dataset.viewLink);
    });
  });

  function openSidebar() { sidebar.classList.add('open'); scrim.classList.add('show'); }
  function closeSidebar() { sidebar.classList.remove('open'); scrim.classList.remove('show'); }

  menuBtn.addEventListener('click', openSidebar);
  scrim.addEventListener('click', closeSidebar);

  try {
    const email = sessionStorage.getItem('wg_email');
    if (email) {
      const nameEl = document.getElementById('sideUserName');
      const avatarEl = document.getElementById('avatarInitials');
      const displayName = email.split('@')[0];
      if (nameEl) nameEl.textContent = displayName;
      if (avatarEl) avatarEl.textContent = displayName.charAt(0).toUpperCase();
    }
  } catch (err) { /* sessionStorage unavailable — non-blocking */ }
});

/* ============ PILL TABS / SETTINGS SWITCHES ============ */
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.pill-tabs').forEach(group => {
    group.querySelectorAll('.pill-tab').forEach(tab => {
      tab.addEventListener('click', () => {
        group.querySelectorAll('.pill-tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
      });
    });
  });

  document.querySelectorAll('.switch input').forEach(input => {
    input.addEventListener('change', () => {
      console.log(`Setting "${input.closest('.settings-row').querySelector('h4').textContent}" -> ${input.checked}`);
    });
  });
});

/* ============ NETWORK TRAFFIC CHART ============ */
document.addEventListener('DOMContentLoaded', () => {
  const svg = document.getElementById('trafficChart');
  if (!svg) return;

  const axisEl     = document.getElementById('trafficAxis');
  const currentEl  = document.getElementById('trafficCurrent');
  const peakEl     = document.getElementById('trafficPeak');
  const avgEl      = document.getElementById('trafficAvg');

  const POINTS     = 20;
  const TICK_MS    = 2000;
  const SCALE_MAX  = 320;
  const W = 600, H = 180, PAD_TOP = 14, PAD_BOTTOM = 26;

  const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));

  let down = 150, up = 35;
  let history = [];
  function seedHistory() {
    down = 120 + Math.random() * 60;
    up = 20 + Math.random() * 30;
    history = [];
    for (let i = 0; i < POINTS; i++) {
      down = clamp(down + (Math.random() - 0.5) * 36, 40, SCALE_MAX - 20);
      up   = clamp(up   + (Math.random() - 0.5) * 14, 10, SCALE_MAX - 60);
      history.push({ down, up });
    }
  }
  seedHistory();

  function toY(v) {
    const usable = H - PAD_TOP - PAD_BOTTOM;
    return PAD_TOP + usable - (clamp(v, 0, SCALE_MAX) / SCALE_MAX) * usable;
  }
  function buildPath(series) {
    const stepX = W / (series.length - 1);
    return series.map((v, i) => `${i === 0 ? 'M' : 'L'} ${(i * stepX).toFixed(1)} ${toY(v).toFixed(1)}`).join(' ');
  }
  function buildArea(series) {
    const stepX = W / (series.length - 1);
    const baseline = H - PAD_BOTTOM;
    const top = buildPath(series);
    const lastX = ((series.length - 1) * stepX).toFixed(1);
    return `${top} L ${lastX} ${baseline} L 0 ${baseline} Z`;
  }

  function render() {
    const downs = history.map(p => p.down);
    const ups   = history.map(p => p.up);
    const baseline = H - PAD_BOTTOM;

    let gridlines = '';
    for (let i = 1; i <= 3; i++) {
      const y = PAD_TOP + ((H - PAD_TOP - PAD_BOTTOM) / 4) * i;
      gridlines += `<line x1="0" y1="${y.toFixed(1)}" x2="${W}" y2="${y.toFixed(1)}" stroke="rgba(148,163,184,0.14)" stroke-width="1"/>`;
    }

    const lastDownY = toY(downs[downs.length - 1]);
    const lastUpY   = toY(ups[ups.length - 1]);

    svg.innerHTML = `
      <defs>
        <linearGradient id="downFill" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#3B82F6" stop-opacity="0.35"/>
          <stop offset="100%" stop-color="#3B82F6" stop-opacity="0"/>
        </linearGradient>
        <linearGradient id="upFill" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#22C55E" stop-opacity="0.30"/>
          <stop offset="100%" stop-color="#22C55E" stop-opacity="0"/>
        </linearGradient>
      </defs>
      <line x1="0" y1="${baseline}" x2="${W}" y2="${baseline}" stroke="rgba(148,163,184,0.25)" stroke-width="1"/>
      ${gridlines}
      <path d="${buildArea(downs)}" fill="url(#downFill)" stroke="none"/>
      <path d="${buildArea(ups)}" fill="url(#upFill)" stroke="none"/>
      <path d="${buildPath(downs)}" fill="none" stroke="#3B82F6" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>
      <path d="${buildPath(ups)}" fill="none" stroke="#22C55E" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>
      <circle class="traffic-pulse" cx="${W}" cy="${lastDownY.toFixed(1)}" r="4" fill="#3B82F6"/>
      <circle class="traffic-pulse" cx="${W}" cy="${lastUpY.toFixed(1)}" r="4" fill="#22C55E"/>
    `;

    if (currentEl) currentEl.textContent = `${Math.round(downs[downs.length - 1])} ↓ / ${Math.round(ups[ups.length - 1])} ↑ KB/s`;
    if (peakEl) peakEl.textContent = `${Math.round(Math.max(...downs))} KB/s`;
    if (avgEl) avgEl.textContent = `${Math.round(downs.reduce((a, b) => a + b, 0) / downs.length)} KB/s`;

    if (axisEl) {
      const stepSeconds = TICK_MS / 1000;
      const labels = [4, 3, 2, 1, 0].map(n => n === 0 ? 'now' : `-${n * stepSeconds}s`);
      axisEl.innerHTML = labels.map(l => `<span>${l}</span>`).join('');
    }
  }

  function tick() {
    const last = history[history.length - 1];
    const nextDown = clamp(last.down + (Math.random() - 0.5) * 40, 20, SCALE_MAX - 10);
    const nextUp   = clamp(last.up   + (Math.random() - 0.5) * 16, 5, SCALE_MAX - 40);
    history.push({ down: nextDown, up: nextUp });
    if (history.length > POINTS) history.shift();
    render();
  }

  render();
  setInterval(tick, TICK_MS);

  // Exposed so the network-scan flow can reseed traffic per-network
  window.__wgReseedTraffic = () => { seedHistory(); render(); };
});

/* ============ AVAILABLE NETWORKS / SCAN / DASHBOARD FLOW ============ */
document.addEventListener('DOMContentLoaded', () => {
  const networksGrid      = document.getElementById('networksGrid');
  if (!networksGrid) return; // not on this page

  const networksScreen    = document.getElementById('networksScreen');
  const dashboardScreen    = document.getElementById('dashboardScreen');
  const recentScansPanel  = document.getElementById('recentScansPanel');
  const recentScansRow    = document.getElementById('recentScansRow');
  const backToNetworksBtn = document.getElementById('backToNetworksBtn');

  const scanOverlay       = document.getElementById('scanOverlay');
  const scanSSIDEl        = document.getElementById('scanSSID');
  const scanStepsEl       = document.getElementById('scanSteps');
  const scanProgressFill  = document.getElementById('scanProgressFill');

  const wifiIconPath = '<path d="M5 12.55a11 11 0 0 1 14 0"/><path d="M1.4 9a16 16 0 0 1 21.2 0"/><path d="M8.5 16.3a6 6 0 0 1 7 0"/><path d="M12 20h.01"/>';

  const NETWORKS = [
    {
      id: 'cafe', ssid: 'Cafe_Free_WiFi', bars: 3, freq: '2.4 GHz', enc: 'Open Network', open: true,
      encFull: 'WPA2 (Open Guest Portal)', bssid: '3C:5A:B4:9E:11:02', dbm: '-58 dBm', channel: '6 · 2.4GHz',
      trust: 64, risk: 'Medium', status: 'Caution', badge: 'warn', icon: 'amber',
      features: { signal: 82, dns: 58, bssid: 74, reconnect: 66, traffic: 41 },
      flags: [
        { icon: 'amber', title: 'Inconsistent DNS responses detected', time: '2 min ago' },
        { icon: 'blue', title: 'Open captive portal — no traffic encryption', time: '5 min ago' },
        { icon: 'green', title: 'No evil-twin BSSID match found nearby', time: '6 min ago' },
      ],
      rec: { danger: true, title: 'Avoid sensitive activity on this network', text: 'DNS integrity is low and this SSID has no encryption on its captive portal. Avoid logging into banking or personal accounts until trust score improves.' },
    },
    {
      id: 'home', ssid: 'Home_Router_2.4G', bars: 4, freq: '2.4 GHz', enc: 'WPA2', open: false,
      encFull: 'WPA2-PSK (AES)', bssid: 'A4:2B:8C:11:6F:03', dbm: '-42 dBm', channel: '11 · 2.4GHz',
      trust: 94, risk: 'Low', status: 'Safe', badge: 'safe', icon: 'green',
      features: { signal: 96, dns: 93, bssid: 98, reconnect: 91, traffic: 12 },
      flags: [
        { icon: 'green', title: 'BSSID matches known trusted router', time: 'Just now' },
        { icon: 'green', title: 'DNS responses consistent across checks', time: '1 min ago' },
        { icon: 'green', title: 'No anomalous traffic patterns found', time: '2 min ago' },
      ],
      rec: { danger: false, title: 'Safe for normal use', text: 'This network shows strong signal integrity and consistent behavior. No unusual activity detected — safe for everyday browsing and sensitive logins.' },
    },
    {
      id: 'library', ssid: 'Campus_Library_5G', bars: 5, freq: '5 GHz', enc: 'WPA3', open: false,
      encFull: 'WPA3-Personal', bssid: 'D8:3C:11:AA:02:5E', dbm: '-38 dBm', channel: '44 · 5GHz',
      trust: 89, risk: 'Low', status: 'Safe', badge: 'safe', icon: 'green',
      features: { signal: 94, dns: 90, bssid: 95, reconnect: 88, traffic: 15 },
      flags: [
        { icon: 'green', title: 'WPA3 encryption verified', time: 'Just now' },
        { icon: 'green', title: 'BSSID consistent with campus network map', time: '1 min ago' },
        { icon: 'blue', title: 'High device density detected on this AP', time: '3 min ago' },
      ],
      rec: { danger: false, title: 'Safe for normal use', text: 'Strong WPA3 encryption and a verified BSSID make this network safe for coursework, email, and general browsing.' },
    },
    {
      id: 'airport', ssid: 'Airport_Free_WiFi', bars: 2, freq: '2.4 GHz', enc: 'Open', open: true,
      encFull: 'None (Open Network)', bssid: '00:1A:2B:CE:99:07', dbm: '-71 dBm', channel: '1 · 2.4GHz',
      trust: 12, risk: 'Critical', status: 'Evil Twin', badge: 'danger', icon: 'red',
      features: { signal: 35, dns: 18, bssid: 9, reconnect: 22, traffic: 88 },
      flags: [
        { icon: 'red', title: 'Evil Twin BSSID match detected nearby', time: 'Just now' },
        { icon: 'red', title: 'No encryption — all traffic is plaintext', time: '1 min ago' },
        { icon: 'amber', title: 'Abnormal reconnect / deauth pattern observed', time: '2 min ago' },
      ],
      rec: { danger: true, title: 'Do not connect to this network', text: 'This SSID is being impersonated by a nearby rogue access point. Connecting risks credential theft and traffic interception — auto-connect has been blocked.' },
    },
    {
      id: 'neighbor', ssid: 'Neighbor_Home_5G', bars: 3, freq: '5 GHz', enc: 'WPA2', open: false,
      encFull: 'WPA2-PSK (AES)', bssid: '6C:71:D9:44:2A:10', dbm: '-64 dBm', channel: '36 · 5GHz',
      trust: 78, risk: 'Low', status: 'Safe', badge: 'safe', icon: 'green',
      features: { signal: 70, dns: 82, bssid: 85, reconnect: 76, traffic: 20 },
      flags: [
        { icon: 'green', title: 'Consistent BSSID across scan window', time: 'Just now' },
        { icon: 'blue', title: 'Weaker signal — expect intermittent drops', time: '2 min ago' },
        { icon: 'green', title: 'No suspicious DNS behavior found', time: '4 min ago' },
      ],
      rec: { danger: false, title: 'Generally safe, signal is weak', text: 'No threats detected, though the weaker signal outside your control may cause occasional drops. Fine for casual browsing.' },
    },
    {
      id: 'mall', ssid: 'Mall_Guest_WiFi', bars: 3, freq: '2.4 GHz', enc: 'WPA2', open: false,
      encFull: 'WPA2 (Shared Guest Portal)', bssid: 'F0:9E:4A:7C:31:88', dbm: '-60 dBm', channel: '9 · 2.4GHz',
      trust: 57, risk: 'Medium', status: 'Caution', badge: 'warn', icon: 'amber',
      features: { signal: 68, dns: 54, bssid: 62, reconnect: 59, traffic: 47 },
      flags: [
        { icon: 'amber', title: 'Shared guest credentials detected', time: '1 min ago' },
        { icon: 'blue', title: 'High number of connected clients on AP', time: '3 min ago' },
        { icon: 'green', title: 'No evil-twin BSSID match found', time: '5 min ago' },
      ],
      rec: { danger: true, title: 'Use with caution', text: 'This is a shared guest network with many simultaneous users. Avoid entering passwords or payment details while connected.' },
    },
    {
      id: 'office', ssid: 'Office_Secure_5G', bars: 5, freq: '5 GHz', enc: 'WPA3', open: false,
      encFull: 'WPA3-Enterprise (802.1X)', bssid: 'B4:2E:99:10:5C:47', dbm: '-35 dBm', channel: '149 · 5GHz',
      trust: 96, risk: 'Low', status: 'Safe', badge: 'safe', icon: 'green',
      features: { signal: 98, dns: 97, bssid: 99, reconnect: 95, traffic: 8 },
      flags: [
        { icon: 'green', title: 'Enterprise authentication verified', time: 'Just now' },
        { icon: 'green', title: 'BSSID matches corporate infrastructure', time: '1 min ago' },
        { icon: 'green', title: 'No anomalies in traffic behavior', time: '2 min ago' },
      ],
      rec: { danger: false, title: 'Safe for all activity', text: 'Enterprise-grade WPA3 authentication and verified infrastructure make this network safe for sensitive work, including logins and file transfers.' },
    },
    {
      id: 'hotel', ssid: 'Hotel_Guest_WiFi', bars: 2, freq: '2.4 GHz', enc: 'Open', open: true,
      encFull: 'None (Room Number Login)', bssid: '7A:1F:C2:88:0B:3D', dbm: '-68 dBm', channel: '3 · 2.4GHz',
      trust: 33, risk: 'High', status: 'Danger', badge: 'danger', icon: 'red',
      features: { signal: 55, dns: 37, bssid: 44, reconnect: 40, traffic: 63 },
      flags: [
        { icon: 'red', title: 'No encryption on guest portal', time: 'Just now' },
        { icon: 'amber', title: 'DNS responses inconsistent across checks', time: '2 min ago' },
        { icon: 'amber', title: 'Multiple SSIDs broadcasting similar names', time: '4 min ago' },
      ],
      rec: { danger: true, title: 'Avoid sensitive activity', text: 'This network is unencrypted and shows signs of nearby SSID spoofing. Avoid logging into accounts or making payments while connected.' },
    },
  ];

  const SCAN_STEP_LABELS_COUNT = 7;
  const STEP_DURATION_MS = 500; // 7 steps * 500ms = 3.5s total

  let recentScans = []; // [{id, time}] most-recent-first
  try {
    recentScans = JSON.parse(sessionStorage.getItem('wg_recent_scans') || '[]');
  } catch (err) { recentScans = []; }

  function findNetwork(id) { return NETWORKS.find(n => n.id === id); }

  /* ---------- RENDER: NETWORKS GRID ---------- */
  function renderNetworksGrid() {
    networksGrid.innerHTML = NETWORKS.map(n => `
      <div class="network-card">
        <div class="network-card-top">
          <div class="feature-icon icon-blue" style="width:38px;height:38px;margin:0;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="17" height="17">${wifiIconPath}</svg></div>
          <div class="signal-bars bars-${n.bars}"><span></span><span></span><span></span><span></span><span></span></div>
        </div>
        <div class="network-card-name mono">${n.ssid}</div>
        <div class="network-card-meta">
          <span class="chip">${n.freq}</span>
          <span class="chip ${n.open ? 'chip-open' : 'chip-secure'}">${n.enc}</span>
        </div>
        <button class="btn btn-outline btn-sm btn-block scan-btn" data-network="${n.id}">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg>
          Scan
        </button>
      </div>
    `).join('');

    networksGrid.querySelectorAll('.scan-btn').forEach(btn => {
      btn.addEventListener('click', () => startScan(btn.dataset.network));
    });
  }

  /* ---------- RENDER: RECENT SCANS ---------- */
  function renderRecentScans() {
    if (!recentScans.length) { recentScansPanel.style.display = 'none'; return; }
    recentScansPanel.style.display = '';
    recentScansRow.innerHTML = recentScans.map(entry => {
      const n = findNetwork(entry.id);
      if (!n) return '';
      const color = n.badge === 'safe' ? 'var(--green-bright)' : n.badge === 'warn' ? 'var(--amber)' : 'var(--red)';
      return `
        <div class="recent-scan-card" data-network="${n.id}">
          <span class="sig sig-${n.badge === 'safe' ? 'safe' : n.badge === 'warn' ? 'warn' : 'danger'}"></span>
          <div>
            <div class="recent-scan-name">${n.ssid}</div>
            <div class="recent-scan-meta">
              <span class="recent-scan-score" style="color:${color};">${n.trust}</span>
              <span>${n.risk}</span>
            </div>
          </div>
        </div>
      `;
    }).join('');

    recentScansRow.querySelectorAll('.recent-scan-card').forEach(card => {
      card.addEventListener('click', () => showDashboard(card.dataset.network, { fromCache: true }));
    });
  }

  function pushRecentScan(id) {
    recentScans = recentScans.filter(e => e.id !== id);
    recentScans.unshift({ id, time: Date.now() });
    recentScans = recentScans.slice(0, 6);
    try { sessionStorage.setItem('wg_recent_scans', JSON.stringify(recentScans)); } catch (err) { /* non-blocking */ }
    renderRecentScans();
  }

  /* ---------- SCANNING OVERLAY ---------- */
  function startScan(id) {
    const n = findNetwork(id);
    if (!n) return;

    scanSSIDEl.textContent = n.ssid;
    scanProgressFill.style.width = '0%';
    scanStepsEl.querySelectorAll('li').forEach(li => li.classList.remove('active', 'done'));
    scanOverlay.classList.add('show');

    const steps = Array.from(scanStepsEl.querySelectorAll('li'));
    steps.forEach((li, i) => {
      setTimeout(() => {
        li.classList.add('active');
        scanProgressFill.style.width = `${Math.round(((i + 0.5) / SCAN_STEP_LABELS_COUNT) * 100)}%`;
      }, i * STEP_DURATION_MS);
      setTimeout(() => {
        li.classList.remove('active');
        li.classList.add('done');
        scanProgressFill.style.width = `${Math.round(((i + 1) / SCAN_STEP_LABELS_COUNT) * 100)}%`;
      }, i * STEP_DURATION_MS + STEP_DURATION_MS - 120);
    });

    const totalDuration = steps.length * STEP_DURATION_MS + 300;
    setTimeout(() => {
      scanOverlay.classList.remove('show');
      showDashboard(id, { fromCache: false });
    }, totalDuration);
  }

  /* ---------- POPULATE + SHOW DASHBOARD ---------- */
  function showDashboard(id, opts) {
    opts = opts || {};
    const n = findNetwork(id);
    if (!n) return;

    document.getElementById('dashSSID').textContent = n.ssid;
    document.getElementById('dashTrust').textContent = n.trust;
    document.getElementById('dashStatus').textContent = n.status;
    document.getElementById('dashRisk').textContent = n.risk;

    const statusColor = n.badge === 'safe' ? 'var(--green-bright)' : n.badge === 'warn' ? 'var(--amber)' : 'var(--red)';
    document.getElementById('dashStatus').style.color = statusColor;
    document.getElementById('dashRisk').style.color = statusColor;
    document.getElementById('dashTrustIcon').className = `feature-icon icon-${n.icon}`;
    document.getElementById('dashStatusIcon').className = `feature-icon icon-${n.icon}`;
    document.getElementById('dashRiskIcon').className = `feature-icon icon-${n.icon}`;

    document.getElementById('detSSID').textContent = n.ssid;
    document.getElementById('detBSSID').textContent = n.bssid;
    document.getElementById('detEncryption').textContent = n.encFull;
    document.getElementById('detSignal').textContent = n.dbm;
    document.getElementById('detChannel').textContent = n.channel;
    document.getElementById('detConnectedSince').textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    const detBadge = document.getElementById('detBadge');
    detBadge.textContent = n.open ? 'Unverified SSID' : 'Verified SSID';
    detBadge.className = `badge badge-${n.badge}`;

    const featMap = [
      ['featSignalFill', 'featSignalPct', n.features.signal, false],
      ['featDnsFill', 'featDnsPct', n.features.dns, true],
      ['featBssidFill', 'featBssidPct', n.features.bssid, false],
      ['featReconnectFill', 'featReconnectPct', n.features.reconnect, false],
      ['featTrafficFill', 'featTrafficPct', n.features.traffic, true],
    ];
    featMap.forEach(([fillId, pctId, val, warnGradient]) => {
      const fill = document.getElementById(fillId);
      fill.style.width = val + '%';
      fill.style.background = (warnGradient && val < 60) ? 'linear-gradient(90deg,#FBBF24,#F87171)' : '';
      document.getElementById(pctId).textContent = val + '%';
    });

    const iconPaths = {
      amber: '<path d="M12 9v4M12 17h.01"/><path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z"/>',
      blue: '<circle cx="12" cy="12" r="9"/><path d="M12 8v4l3 3"/>',
      green: '<path d="M20 6 9 17l-5-5"/>',
      red: '<path d="M12 9v4M12 17h.01"/><circle cx="12" cy="12" r="9"/>',
    };
    document.getElementById('threatList').innerHTML = n.flags.map(f => `
      <div class="activity-item">
        <div class="activity-dot icon-${f.icon}"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">${iconPaths[f.icon]}</svg></div>
        <div><p class="title">${f.title}</p><span class="time">${f.time}</span></div>
      </div>
    `).join('');

    const recBox = document.getElementById('recBox');
    recBox.classList.toggle('danger', n.rec.danger);
    document.getElementById('recTitle').textContent = n.rec.title;
    document.getElementById('recText').textContent = n.rec.text;

    if (!opts.fromCache) {
      const activityList = document.getElementById('recentActivityList');
      const item = document.createElement('div');
      item.className = 'activity-item';
      const iconClass = n.badge === 'safe' ? 'icon-green' : n.badge === 'warn' ? 'icon-amber' : 'icon-red';
      const iconSvg = n.badge === 'safe' ? iconPaths.green : n.badge === 'warn' ? iconPaths.amber : iconPaths.red;
      item.innerHTML = `
        <div class="activity-dot ${iconClass}"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">${iconSvg}</svg></div>
        <div><p class="title">Scan completed — <span class="mono">${n.ssid}</span> rated ${n.status} (${n.trust})</p><span class="time">Just now</span></div>
      `;
      activityList.insertBefore(item, activityList.firstChild);
      pushRecentScan(id);
    }

    if (window.__wgReseedTraffic) window.__wgReseedTraffic();

    networksScreen.style.display = 'none';
    dashboardScreen.style.display = '';
  }

  backToNetworksBtn.addEventListener('click', () => {
    dashboardScreen.style.display = 'none';
    networksScreen.style.display = '';
  });

  renderNetworksGrid();
  renderRecentScans();
});