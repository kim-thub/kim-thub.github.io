(() => {
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
