// Khokhar TV site script: mobile nav + live download links.
//
// Builds are published by the app's CI into a public Supabase Storage bucket,
// alongside a manifest.json describing the newest file for each platform.
// Download buttons carry data-dl="<platform key>" and get their href, version
// and size filled in from that manifest. If the manifest can't be read, the
// buttons keep the fallback href written in the HTML, so nothing is ever dead.
(function () {
  var MANIFEST =
    'https://mchwhfdfpovaxbyeijjr.supabase.co/storage/v1/object/public/releases/manifest.json';

  var btn = document.querySelector('.menu-btn');
  var links = document.querySelector('.nav-links');
  if (btn && links) {
    btn.addEventListener('click', function () {
      var open = links.classList.toggle('open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  var y = document.getElementById('year');
  if (y) y.textContent = new Date().getFullYear();

  function fmtSize(bytes) {
    if (!bytes) return '';
    return (bytes / 1048576).toFixed(bytes > 104857600 ? 0 : 1) + ' MB';
  }

  function detect() {
    var ua = navigator.userAgent || '';
    if (/AFT|Android TV|GoogleTV|BRAVIA|SMART-TV|AndroidTV/i.test(ua)) return 'android-tv';
    if (/Android/i.test(ua)) return 'android-phone';
    if (/Windows/i.test(ua)) return 'windows';
    if (/Linux/i.test(ua) && !/CrOS/i.test(ua)) return 'linux';
    return null;
  }

  var labels = {
    'android-tv': 'Download for Android TV',
    'android-phone': 'Download for Android',
    windows: 'Download for Windows',
    linux: 'Download for Linux'
  };

  // Highlight the card that matches this device, and point the hero button at it.
  var mine = detect();
  if (mine) {
    var card = document.querySelector('[data-platform="' + mine + '"]');
    if (card) card.classList.add('recommended');
    document.querySelectorAll('[data-hero-dl]').forEach(function (a) {
      a.setAttribute('data-dl', mine);
      var t = a.querySelector('span');
      if (t) t.textContent = labels[mine];
    });
  }

  if (!document.querySelector('[data-dl],[data-redirect]')) return;

  fetch(MANIFEST, { cache: 'no-cache' })
    .then(function (r) {
      if (!r.ok) throw new Error(r.status);
      return r.json();
    })
    .then(function (m) {
      var p = (m && m.platforms) || {};
      document.querySelectorAll('[data-dl]').forEach(function (a) {
        var b = p[a.getAttribute('data-dl')];
        if (!b || !b.url) return;
        a.href = b.url;
        a.removeAttribute('aria-disabled');
        var meta = a.closest('.dl-card') && a.closest('.dl-card').querySelector('.meta');
        if (meta) {
          meta.textContent = ['Version ' + b.version, fmtSize(b.size), b.date ? b.date.slice(0, 10) : '']
            .filter(Boolean)
            .join(' · ');
        }
      });
      var redirect = document.querySelector('[data-redirect]');
      if (redirect) {
        var target = p[redirect.getAttribute('data-redirect')];
        if (target && target.url) location.replace(target.url);
        else location.replace(redirect.getAttribute('href'));
      }
    })
    .catch(function () {
      var redirect = document.querySelector('[data-redirect]');
      if (redirect) location.replace(redirect.getAttribute('href'));
    });
})();
