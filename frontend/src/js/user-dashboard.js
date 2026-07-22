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
    link.addEventListener("click", () => {
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

  function openSidebar() {
    sidebar.classList.add("open");
    scrim.classList.add("show");
}

function closeSidebar() {
    sidebar.classList.remove("open");
    scrim.classList.remove("show");
}

menuBtn.addEventListener("click", openSidebar);

scrim.addEventListener("click", closeSidebar);

  try {
    const email = sessionStorage.getItem('wg_email');
    const role  = sessionStorage.getItem('wg_role');
    if (email) {
      const nameEl = document.getElementById('sideUserName');
      const avatarEl = document.getElementById('avatarInitials');
      const displayName = email.split('@')[0];
      if (nameEl) nameEl.textContent = displayName;
      if (avatarEl) avatarEl.textContent = displayName.charAt(0).toUpperCase();
    }
  } catch (err) { /* sessionStorage unavailable — non-blocking */ }
});

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
      // In a Flask app: fetch('/api/settings', { method:'PATCH', body: JSON.stringify({...}) })
      console.log(`Setting "${input.closest('.settings-row').querySelector('h4').textContent}" -> ${input.checked}`);
    });
  });
});
