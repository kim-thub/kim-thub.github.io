(() => {
  const toggle = document.querySelector('.sound-toggle');
  const key = 'portfolio-sound-enabled';
  let enabled = false;
  let audio;

  try { enabled = localStorage.getItem(key) === 'true'; } catch (_) { /* private mode */ }

  function label() {
    toggle.setAttribute('aria-pressed', String(enabled));
    const soundLabel = document.documentElement.lang === 'en'
      ? (enabled ? 'Sound on' : 'Sound off')
      : '소리 ' + (enabled ? '켜짐' : '꺼짐');
    toggle.innerHTML = '<span aria-hidden="true">' + (enabled ? '◖))' : '◖)') + '</span><span>' + soundLabel + '</span>';
  }

  function chime() {
    if (!enabled) return;
    const Context = window.AudioContext || window.webkitAudioContext;
    if (!Context) return;
    try {
      audio ||= new Context();
      if (audio.state === 'suspended') audio.resume();
      const start = audio.currentTime;
      [[392, 0], [523.25, .055]].forEach(([frequency, delay]) => {
        const oscillator = audio.createOscillator();
        const gain = audio.createGain();
        oscillator.type = 'sine';
        oscillator.frequency.value = frequency;
        gain.gain.setValueAtTime(.0001, start + delay);
        gain.gain.exponentialRampToValueAtTime(.012, start + delay + .018);
        gain.gain.exponentialRampToValueAtTime(.0001, start + delay + .19);
        oscillator.connect(gain).connect(audio.destination);
        oscillator.start(start + delay);
        oscillator.stop(start + delay + .2);
      });
    } catch (_) { /* sound is optional */ }
  }

  if (toggle) {
    label();
    document.addEventListener('portfolio:language-changed', label);
    toggle.addEventListener('click', () => {
      enabled = !enabled;
      try { localStorage.setItem(key, String(enabled)); } catch (_) { /* private mode */ }
      label();
      chime();
    });
    document.querySelectorAll('.site-nav a, .project-card .text-link, .next-case, .experiment-row, .button').forEach(link => {
      link.addEventListener('pointerdown', chime);
      link.addEventListener('keydown', event => { if (event.key === 'Enter') chime(); });
    });
  }

  if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches && 'IntersectionObserver' in window) {
    const targets = [...document.querySelectorAll('.project-card, .principle, .case-body section, .case-visual, .experiment-row')];
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: .07, rootMargin: '0px 0px 40px 0px' });
    targets.forEach(target => { target.classList.add('reveal'); observer.observe(target); });
    document.documentElement.classList.add('motion-ready');
  }
})();
