(()=>{
 const projectSlugs=["starter-kit", "spot-radar", "github-taskflow", "job-process-automation", "webtoon-feedback", "inheritance-guide"];
 const views=[...document.querySelectorAll('[data-view]')];
 const activeProject=document.getElementById('active-project');
 const activePost=document.getElementById('active-post');
 const projectTemplates=Object.fromEntries(projectSlugs.map(slug=>[slug,document.getElementById('tpl-'+slug)]));
 const blogDataNode=document.getElementById('blog-posts-data');
 const posts=blogDataNode?JSON.parse(blogDataNode.textContent):[];
 const postTemplates=Object.fromEntries(posts.filter(p=>p.template).map(p=>[p.slug,document.getElementById(p.template)]));
 const pageNames=['home','about','projects','blog'];
 const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 function addPostCards(){
  const target=document.querySelector('[data-post-list]');
  if(!target)return;
  target.replaceChildren();

  const titleIndex=document.createElement('ol');
  titleIndex.className='diary-title-index';
  const cards=document.createElement('div');
  cards.className='diary-card-grid';

  posts.forEach(post=>{
   const title=post.title||'제목 없는 글';
   const excerpt=post.excerpt||'';

   const indexItem=document.createElement('li');
   const indexLink=document.createElement('a');
   indexLink.href='#post/'+encodeURIComponent(post.slug);
   indexLink.setAttribute('aria-label','글 열기: '+title);
   indexLink.innerHTML='<span class="diary-title-index__title">'+esc(title)+'</span>';
   indexItem.append(indexLink);
   titleIndex.append(indexItem);

   const card=document.createElement('a');
   card.href='#post/'+encodeURIComponent(post.slug);
   card.className='diary-entry';
   card.setAttribute('aria-label','기록 열기: '+title);
   card.innerHTML='<strong class="diary-entry__title">'+esc(title)+'</strong>'+
    '<span class="diary-entry__excerpt">'+esc(excerpt)+'</span>'+
    '<span class="diary-entry__read">READ NOTE <span aria-hidden="true">↗</span></span>';
   cards.append(card);
  });

  target.append(titleIndex,cards);
 }
 function safeUrl(url){
  const value=String(url||'').trim();
  if(/^javascript:/i.test(value)||/^data:/i.test(value)||value.startsWith('//'))return '#';
  return value;
 }
 function inlineMarkdown(source){
  const hold=[];const token=html=>{const i=hold.push(html)-1;return '\u0000'+i+'\u0000'};
  let s=String(source).replace(/`([^`]+)`/g,(_,x)=>token('<code>'+esc(x)+'</code>'));
  s=esc(s);
  s=s.replace(/!\[([^\]]*)\]\(([^)]+)\)/g,(_,alt,url)=>'<img src="'+esc(safeUrl(url))+'" alt="'+esc(alt)+'">');
  s=s.replace(/\[([^\]]+)\]\(([^)]+)\)/g,(_,label,url)=>{const href=safeUrl(url),external=/^https?:\/\//i.test(href);return '<a href="'+esc(href)+'"'+(external?' target="_blank" rel="noopener noreferrer"':'')+'>'+label+'</a>'});
  s=s.replace(/\*\*([^*]+)\*\*/g,'<strong>$1</strong>').replace(/__([^_]+)__/g,'<strong>$1</strong>');
  s=s.replace(/~~([^~]+)~~/g,'<del>$1</del>').replace(/(^|[^*])\*([^*]+)\*(?!\*)/g,'$1<em>$2</em>');
  s=s.replace(/\u0000(\d+)\u0000/g,(_,i)=>hold[Number(i)]);
  return s;
 }
 function headingId(s){return s.toLowerCase().replace(/`/g,'').replace(/[^\p{L}\p{N}\s-]/gu,'').trim().replace(/\s+/g,'-');}
 function cells(line){return line.trim().replace(/^\|/,'').replace(/\|$/,'').split(/(?<!\\)\|/).map(x=>x.trim().replace(/\\\|/g,'|'));}
 function markdownToHtml(markdown,codeBlocks=[]){
  const lines=String(markdown||'').replace(/\r/g,'').split('\n'),out=[];let codeBlockIndex=0,paragraph=[],listType='',listItems=[],quote=[];
  const flushP=()=>{if(paragraph.length){out.push('<p>'+inlineMarkdown(paragraph.join(' '))+'</p>');paragraph=[]}};
  const flushList=()=>{if(listItems.length){out.push('<'+listType+'>'+listItems.map(x=>'<li>'+inlineMarkdown(x)+'</li>').join('')+'</'+listType+'>');listItems=[];listType=''}};
  const flushQuote=()=>{if(quote.length){out.push('<blockquote><p>'+inlineMarkdown(quote.join(' '))+'</p></blockquote>');quote=[]}};
  for(let i=0;i<lines.length;i++){
   const line=lines[i];
   const fence=line.match(/^\s*```([\w+-]*)\s*$/);
   if(fence){flushP();flushList();flushQuote();const lang=fence[1];const code=[];i++;while(i<lines.length&&!/^\s*```\s*$/.test(lines[i])){code.push(lines[i]);i++}const block=codeBlocks[codeBlockIndex++]||null;const shownLang=(block&&block.language)||lang||'text';const highlighted=block&&typeof block.html==='string'?block.html:esc(code.join('\n'));out.push('<figure class="portfolio-code"><figcaption><span class="code-tab">'+esc(shownLang.toUpperCase())+'</span></figcaption><pre><code class="language-'+esc(shownLang)+'">'+highlighted+'</code></pre></figure>');continue}
   if(!line.trim()){flushP();flushList();flushQuote();continue}
   if(/^\s*\|.*\|\s*$/.test(line)&&i+1<lines.length&&/^\s*\|?\s*:?-{3,}/.test(lines[i+1])){
    flushP();flushList();flushQuote();const heads=cells(line);i+=2;const rows=[];while(i<lines.length&&/^\s*\|.*\|\s*$/.test(lines[i])){rows.push(cells(lines[i]));i++}i--;
    out.push('<div class="markdown-table-wrap"><table><thead><tr>'+heads.map(c=>'<th scope="col">'+inlineMarkdown(c)+'</th>').join('')+'</tr></thead><tbody>'+rows.map(row=>'<tr>'+heads.map((_,j)=>'<td>'+inlineMarkdown(row[j]||'')+'</td>').join('')+'</tr>').join('')+'</tbody></table></div>');continue;
   }
   const h=line.match(/^(#{1,6})\s+(.+)$/);if(h){flushP();flushList();flushQuote();const n=h[1].length;out.push('<h'+n+' id="'+esc(headingId(h[2]))+'">'+inlineMarkdown(h[2])+'</h'+n+'>');continue}
   if(/^\s*(---+|___+|\*\*\*+)\s*$/.test(line)){flushP();flushList();flushQuote();out.push('<hr>');continue}
   const q=line.match(/^\s*>\s?(.*)$/);if(q){flushP();flushList();quote.push(q[1]);continue}else flushQuote();
   const li=line.match(/^\s*(?:[-+*])\s+(.+)$/),oi=line.match(/^\s*\d+[.)]\s+(.+)$/);
   if(li||oi){flushP();const type=li?'ul':'ol';if(listType&&type!==listType)flushList();listType=type;listItems.push((li||oi)[1]);continue}else flushList();
   paragraph.push(line.trim());
  }
  flushP();flushList();flushQuote();return out.join('\n');
 }
 function show(name,animate=false){
  views.forEach(v=>{
   v.hidden=v.dataset.view!==name;
   v.removeAttribute('data-entering');
   if(v.dataset.view===name&&animate)v.setAttribute('data-entering','true');
  });
 }
 let lastRenderedRoute=null;
 let keyboardNavigation=false;
 const reducedMotionPreference=window.matchMedia('(prefers-reduced-motion: reduce)');
 document.addEventListener('keydown',event=>{if(event.key==='Tab')keyboardNavigation=true;});
 document.addEventListener('pointerdown',()=>{keyboardNavigation=false;},{passive:true});
 document.addEventListener('animationend',event=>{
  if(event.target.matches('.view[data-entering="true"]')&&event.animationName==='archive-view-arrive')event.target.removeAttribute('data-entering');
 });
 function enhanceCodeFrames(root){
  if(!root)return;
  root.querySelectorAll('pre').forEach(pre=>{
   if(!pre.hasAttribute('tabindex'))pre.tabIndex=0;
   if(pre.closest('.portfolio-code'))return;
   const code=pre.querySelector('code');
   const classes=(pre.className+' '+(code?code.className:''));
   const match=classes.match(/\b(java|python|bash|sql|javascript|json|yaml|xml|text)\b/i);
   const language=match?match[1].toLowerCase():'code';
   const figure=document.createElement('figure');figure.className='portfolio-code';
   const caption=document.createElement('figcaption');
   const label=document.createElement('span');label.className='code-tab';label.textContent=language.toUpperCase();caption.append(label);
   const parent=pre.parentElement;
   if(parent&&parent.classList.contains('sourceCode')&&parent.children.length===1){if(parent.id)figure.id=parent.id;parent.replaceWith(figure)}else{pre.replaceWith(figure)}
   if(code&&!code.classList.contains('language-'+language))code.classList.add('language-'+language);
   figure.append(caption,pre);
  });
 }
 function enhanceRelatedPostLinks(root){
  if(!root)return;
  root.querySelectorAll('.project-resources a[href^="#post/"]').forEach(link=>{
   const slug=decodeURIComponent(link.getAttribute('href').slice(6));
   const post=posts.find(item=>item.slug===slug);
   if(!post)return;
   const details=document.createElement('details');details.className='related-post-preview';
   const summary=document.createElement('summary');summary.textContent=link.textContent.replace(/\s*↗\s*$/,'');
   const excerpt=document.createElement('p');excerpt.textContent=post.excerpt||'';
   const full=link.cloneNode(true);full.className='related-post-full';full.textContent='전체 기록 열기 ↗';
   details.append(summary,excerpt,full);link.replaceWith(details);
  });
 }
 function scrollKey(route){return 'portfolio-scroll:'+location.pathname+route}
 function enhanceResponsiveTables(root){
  if(!root)return;
  root.querySelectorAll('table').forEach(table=>{
   table.querySelectorAll('thead th').forEach(cell=>{if(!cell.hasAttribute('scope'))cell.setAttribute('scope','col')});
   const headers=[...table.querySelectorAll('thead th')].map(cell=>cell.textContent.trim());
   if(headers.length<3||table.dataset.mobileCards==='ready')return;
   table.dataset.mobileCards='ready';
   table.classList.add('mobile-card-source');
   const cards=document.createElement('div');
   cards.className='mobile-table-cards';
   const caption=table.querySelector('caption');
   cards.setAttribute('role','region');
   cards.setAttribute('aria-label',caption?caption.textContent.trim()+' · 모바일 표 요약':'모바일 표 요약');
   table.querySelectorAll('tbody tr').forEach(row=>{
    const cells=[...row.children];
    const card=document.createElement('article');
    card.className='mobile-table-card';
    const list=document.createElement('dl');
    cells.forEach((cell,index)=>{
     const field=document.createElement('div');
     field.className='mobile-table-field';
     const term=document.createElement('dt');
     term.textContent=headers[index]||('항목 '+(index+1));
     const value=document.createElement('dd');
     cell.childNodes.forEach(node=>value.append(node.cloneNode(true)));
     field.append(term,value);
     list.append(field);
    });
    card.append(list);
    cards.append(card);
   });
   table.after(cards);
  });
 }

let projectTocObserver=null;
 function buildProjectTOC(root){
  const toc=document.querySelector('[data-project-toc]'),globalNav=document.getElementById('ed-global-nav');
  if(!toc)return;
  if(projectTocObserver){projectTocObserver.disconnect();projectTocObserver=null}
  toc.replaceChildren();
  const headings=[...root.querySelectorAll('.case-copy h3')];
  headings.forEach((heading,index)=>{
   const label=heading.textContent.trim().replace(/\s+/g,' ');
   if(!heading.id){const base=label.toLowerCase().replace(/[^\p{L}\p{N}]+/gu,'-').replace(/^-|-$/g,'')||'section';heading.id='project-section-'+base+'-'+(index+1)}
   heading.tabIndex=-1;
   const button=document.createElement('button');button.type='button';button.className='project-toc-link';button.dataset.tocTarget=heading.id;button.textContent=label;toc.append(button);
  });
  toc.hidden=headings.length===0;
  if(globalNav)globalNav.hidden=headings.length>0;
  if(!headings.length||!('IntersectionObserver' in window))return;
  projectTocObserver=new IntersectionObserver(entries=>{
   const active=entries.filter(entry=>entry.isIntersecting).sort((a,b)=>a.boundingClientRect.top-b.boundingClientRect.top)[0];
   if(!active)return;
   let activeButton=null;
   toc.querySelectorAll('button').forEach(button=>{
    if(button.dataset.tocTarget===active.target.id){
     if(!button.hasAttribute('aria-current'))activeButton=button;
     button.setAttribute('aria-current','location');
    }else button.removeAttribute('aria-current');
   });
   if(activeButton){const containerRect=toc.getBoundingClientRect(),itemRect=activeButton.getBoundingClientRect();if(itemRect.left<containerRect.left)toc.scrollLeft-=containerRect.left-itemRect.left;else if(itemRect.right>containerRect.right)toc.scrollLeft+=itemRect.right-containerRect.right;if(itemRect.top<containerRect.top)toc.scrollTop-=containerRect.top-itemRect.top;else if(itemRect.bottom>containerRect.bottom)toc.scrollTop+=itemRect.bottom-containerRect.bottom;}
  },{rootMargin:'-18% 0px -72% 0px',threshold:0});
  headings.forEach(heading=>projectTocObserver.observe(heading));
 }
 function clearProjectTOC(){
  if(projectTocObserver){projectTocObserver.disconnect();projectTocObserver=null}
  const toc=document.querySelector('[data-project-toc]'),globalNav=document.getElementById('ed-global-nav');
  if(toc){toc.replaceChildren();toc.hidden=true}
  if(globalNav)globalNav.hidden=false;
 }
 document.addEventListener('click',event=>{
  const button=event.target.closest('[data-toc-target]');if(!button)return;
  const target=document.getElementById(button.dataset.tocTarget);if(!target)return;
  target.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'start'});
  target.focus({preventScroll:true});
 });
 function current(){return(location.hash||'#home').slice(1)}
 function render(){
  const route=current();
  const routeChanged=lastRenderedRoute!==null&&lastRenderedRoute!==route;
  const animateRoute=routeChanged&&!reducedMotionPreference.matches;
  if(route.startsWith('project/')){
   const slug=decodeURIComponent(route.slice(8)),template=projectTemplates[slug];
   if(!template){location.hash='#projects';return}
   activeProject.replaceChildren(template.content.cloneNode(true));const projectSourceTitle=activeProject.querySelector('.case-copy h2');const projectHeading=document.querySelector('[data-project-title]');if(projectSourceTitle&&projectHeading){projectHeading.textContent=projectSourceTitle.textContent.trim();projectSourceTitle.remove();}enhanceResponsiveTables(activeProject);enhanceCodeFrames(activeProject);enhanceRelatedPostLinks(activeProject);show('detail',animateRoute);
  }else if(route.startsWith('post/')){
   const slug=decodeURIComponent(route.slice(5)),post=posts.find(p=>p.slug===slug);
   if(!post){location.hash='#blog';return}
   const template=postTemplates[slug];
   if(template)activePost.replaceChildren(template.content.cloneNode(true));
   else activePost.innerHTML='<article class="blog-body markdown-body">'+markdownToHtml(post.markdown||'',post.codeBlocks||[])+'</article>';
   const postHeading=activePost.querySelector('.blog-body h1,.markdown-body h1');const postTitle=postHeading?.textContent.trim()||post.title||'FIELD NOTE';if(postHeading)postHeading.remove();const readerHead=document.createElement('header');readerHead.className='diary-reader-head';const eyebrow=document.createElement('small');eyebrow.textContent='FIELD NOTE / ARCHIVE';const visibleTitle=document.createElement('h1');visibleTitle.setAttribute('data-post-title','');visibleTitle.textContent=postTitle;visibleTitle.tabIndex=-1;readerHead.append(eyebrow,visibleTitle);activePost.prepend(readerHead);enhanceResponsiveTables(activePost);enhanceCodeFrames(activePost);show('post-detail',animateRoute);
  }else if(pageNames.includes(route)){
   show(route,animateRoute);
  }else{location.hash='#home';return}
  document.querySelectorAll('[data-route-link]').forEach(a=>{
   const href=(a.getAttribute('href')||'').slice(1),match=route===href||((route.startsWith('project/')&&href==='projects')||(route.startsWith('post/')&&href==='blog'));
   if(match)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current');
  });
  document.body.dataset.route=route.startsWith('project/')?'detail':route.startsWith('post/')?'post-detail':route;
  if(route.startsWith('project/'))buildProjectTOC(activeProject);else clearProjectTOC();
  let restoreY=0;if(route==='home'&&document.body.dataset.archiveArtPlayed!=='true')document.body.dataset.archiveArtPlayed='true';try{const saved=sessionStorage.getItem(scrollKey(route));if(saved!==null){restoreY=Math.max(0,Number(saved)||0);sessionStorage.removeItem(scrollKey(route));}}catch{}requestAnimationFrame(()=>window.scrollTo({top:restoreY,behavior:'auto'}));
  if(routeChanged&&keyboardNavigation){
   const activeView=document.querySelector('.view:not([hidden])');
   let focusTarget=null;
   if(route.startsWith('project/'))focusTarget=activeView?.querySelector('.ed-reader-head h1,[data-project-title]');
   else if(route.startsWith('post/'))focusTarget=activeView?.querySelector('.diary-reader-head h1');
   else if(route==='home')focusTarget=activeView?.querySelector('.ed-home-title');
   else focusTarget=activeView?.querySelector('.ed-section-label h1,.ed-blog-head h1');
   if(focusTarget){focusTarget.setAttribute('data-route-focus','');focusTarget.tabIndex=-1;focusTarget.focus({preventScroll:true});}
  }
  keyboardNavigation=false;
  lastRenderedRoute=route;
 }
 const paperPointerQuery=window.matchMedia('(hover: hover) and (pointer: fine)');
 document.addEventListener('pointermove',event=>{
  if(!paperPointerQuery.matches||event.pointerType!=='mouse')return;
  const card=event.target.closest('.project-specimen,.diary-entry,.ed-home-link,.profile-archive-sheet .ed-profile-columns>section');
  if(!card)return;
  const rect=card.getBoundingClientRect();
  const x=Math.max(0,Math.min(100,((event.clientX-rect.left)/rect.width)*100));
  const y=Math.max(0,Math.min(100,((event.clientY-rect.top)/rect.height)*100));
  card.style.setProperty('--paper-pointer-x',x.toFixed(1)+'%');
  card.style.setProperty('--paper-pointer-y',y.toFixed(1)+'%');
 },{passive:true});
 window.history.scrollRestoration='manual';let scrollSaveFrame=0;window.addEventListener('scroll',()=>{if(scrollSaveFrame)return;scrollSaveFrame=requestAnimationFrame(()=>{scrollSaveFrame=0;try{sessionStorage.setItem(scrollKey(current()),String(window.scrollY))}catch{}})},{passive:true});
 document.addEventListener('click',e=>{const a=e.target.closest('a[href^="#"]');if(!a)return;const target=(a.getAttribute('href')||'').slice(1),from=current();if(target===from){e.preventDefault();return}try{if(target.startsWith('project/')||target.startsWith('post/'))sessionStorage.removeItem(scrollKey(target))}catch{}});
 window.addEventListener('hashchange',render);addPostCards();render();
})();
