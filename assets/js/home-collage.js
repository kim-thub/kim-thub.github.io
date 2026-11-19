(()=>{
 const home=document.querySelector('[data-view="home"]');
 const maker=home?.querySelector('[data-maker-world]');
 const replay=home?.querySelector('[data-home-replay]');
 const artwork=home?.querySelector('.labyrinth-being');
 if(!home||!maker||!artwork)return;
 const reduced=window.matchMedia('(prefers-reduced-motion: reduce)');
 const reveal=()=>maker.classList.add('is-revealed');
 maker.addEventListener('animationend',event=>{
  if(event.animationName==='maker-paper-reverse')reveal();
 });
 if(reduced.matches)reveal();
 replay?.addEventListener('click',()=>{
  if(reduced.matches){reveal();return;}
  maker.classList.remove('is-revealed');
  document.body.removeAttribute('data-archive-art-played');
  requestAnimationFrame(()=>requestAnimationFrame(()=>{
   document.body.dataset.archiveArtPlayed='true';
  }));
 });
})();
