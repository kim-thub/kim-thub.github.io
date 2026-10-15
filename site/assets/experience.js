(() => {
  const toggle = document.querySelector('.sound-toggle');
  const key = 'portfolio-sound-enabled';
  let enabled = false;
  let audio;

  try { enabled = localStorage.getItem(key) === 'true'; } catch (_) { /* private mode */ }

  function label() {
    toggle.setAttribute('aria-pressed', String(enabled));
    toggle.innerHTML = `<span aria-hidden="true">${enabled ? '◖))' : '◖)'}</span><span>소리 ${enabled ? '켜짐' : '꺼짐'}</span>`;
  }

  function tick() {
    if (!enabled) return;
    const Context = window.AudioContext || window.webkitAudioContext;
    if (!Context) return;
    try {
      audio ||= new Context();
      if (audio.state === 'suspended') audio.resume();
      const oscillator = audio.createOscillator();
      const gain = audio.createGain();
      oscillator.type = 'sine';
      oscillator.frequency.setValueAtTime(550, audio.currentTime);
      oscillator.frequency.exponentialRampToValueAtTime(740, audio.currentTime + .065);
      gain.gain.setValueAtTime(.0001, audio.currentTime);
      gain.gain.exponentialRampToValueAtTime(.025, audio.currentTime + .01);
      gain.gain.exponentialRampToValueAtTime(.0001, audio.currentTime + .12);
      oscillator.connect(gain).connect(audio.destination);
      oscillator.start();
      oscillator.stop(audio.currentTime + .13);
    } catch (_) { /* sound is optional */ }
  }

  if (toggle) {
    label();
    toggle.addEventListener('click', () => {
      enabled = !enabled;
      try { localStorage.setItem(key, String(enabled)); } catch (_) { /* private mode */ }
      label();
      tick();
    });
    document.querySelectorAll('.project-card a, .next-case, .experiment-row, .button').forEach(link => {
      link.addEventListener('pointerdown', tick);
      link.addEventListener('keydown', event => { if (event.key === 'Enter') tick(); });
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
