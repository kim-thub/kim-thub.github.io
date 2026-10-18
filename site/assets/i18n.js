(() => {
  const languageKey = 'portfolio-language';
  const root = document.documentElement;
  const pageName = root.dataset.page;
  const scriptUrl = document.currentScript && document.currentScript.src;
  const originalText = new WeakMap();
  const originalAttributes = new WeakMap();
  const originalHtml = new WeakMap();
  const originalTitle = document.title;
  const description = document.querySelector('meta[name="description"]');
  const originalDescription = description && description.content;
  const normalize = value => value.replace(/\s+/g, ' ').trim();
  function keepWhitespace(source, translated) {
    return source.match(/^\s*/)[0] + translated + source.match(/\s*$/)[0];
  }
  function translateTextNodes(language, translations) {
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    let node;
    while ((node = walker.nextNode())) {
      if (node.parentElement.closest('script, style, [data-i18n-title]')) continue;
      if (!originalText.has(node)) originalText.set(node, node.nodeValue);
      const source = originalText.get(node);
      if (language === 'ko') { node.nodeValue = source; continue; }
      const translated = translations.text[normalize(source)];
      if (translated !== undefined) node.nodeValue = keepWhitespace(source, translated);
    }
  }
  function translateAttributes(language, translations) {
    const names = ['aria-label', 'alt', 'title'];
    document.querySelectorAll('*').forEach(element => {
      for (const name of names) {
        if (!element.hasAttribute(name)) continue;
        let saved = originalAttributes.get(element);
        if (!saved) { saved = new Map(); originalAttributes.set(element, saved); }
        if (!saved.has(name)) saved.set(name, element.getAttribute(name));
        const source = saved.get(name);
        if (language === 'ko') { element.setAttribute(name, source); continue; }
        const translated = translations.attributes[normalize(source)];
        if (translated !== undefined) element.setAttribute(name, translated);
      }
    });
  }
  function applyLanguage(language, translations, persist = false) {
    const page = translations.pages[pageName];
    if (!page) return;
    root.lang = language;
    const titleHeading = document.querySelector('[data-i18n-title]');
    if (titleHeading) {
      if (!originalHtml.has(titleHeading)) originalHtml.set(titleHeading, titleHeading.innerHTML);
      titleHeading.innerHTML = language === 'en' && page.titleHtml ? page.titleHtml : originalHtml.get(titleHeading);
    }
    translateTextNodes(language, translations);
    translateAttributes(language, translations);
    document.title = language === 'en' ? page.title : originalTitle;
    if (description) description.content = language === 'en' ? page.description : originalDescription;
    document.querySelectorAll('[data-language]').forEach(button => {
      button.setAttribute('aria-pressed', String(button.dataset.language === language));
    });
    if (persist) { try { localStorage.setItem(languageKey, language); } catch (_) { /* storage may be unavailable */ } }
    document.dispatchEvent(new CustomEvent('portfolio:language-changed', { detail: { language } }));
  }
  let selectedLanguage = 'ko';
  try { if (localStorage.getItem(languageKey) === 'en') selectedLanguage = 'en'; } catch (_) { /* storage may be unavailable */ }
  let translations;
  document.querySelectorAll('[data-language]').forEach(button => {
    button.addEventListener('click', () => {
      const language = button.dataset.language;
      if (language !== 'ko' && language !== 'en') return;
      selectedLanguage = language;
      if (translations) applyLanguage(language, translations, true);
      else { try { localStorage.setItem(languageKey, language); } catch (_) { /* storage may be unavailable */ } }
    });
  });
  window.portfolioI18nReady = fetch(new URL('i18n.json', scriptUrl))
    .then(response => { if (!response.ok) throw new Error('Could not load translations (' + response.status + ')'); return response.json(); })
    .then(async payload => {
      if (payload.encoding !== 'gzip-base64') return payload;
      if (!('DecompressionStream' in window)) throw new Error('This browser cannot decompress the translation data.');
      const binary = atob(payload.payload);
      const bytes = Uint8Array.from(binary, character => character.charCodeAt(0));
      const stream = new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'));
      return JSON.parse(await new Response(stream).text());
    })
    .then(loadedTranslations => {
      translations = loadedTranslations;
      applyLanguage(selectedLanguage, translations);
      document.dispatchEvent(new CustomEvent('portfolio:i18n-ready'));
    })
    .catch(error => console.error('Portfolio translations could not be loaded.', error));
})();
