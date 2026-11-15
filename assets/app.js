/* A buildless, source-linked timeline. Data is authored separately. */
(() => {
  'use strict';
  const data = window.CAREER_DATA;
  if (!data || !Array.isArray(data.milestones)) return;
  const milestones = data.milestones.filter(item => item && item.id && item.date && item.title);
  const byId = new Map(milestones.map(item => [item.id, item]));
  const el = id => document.getElementById(id);
  const escape = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const humanize = value => String(value ?? '').replace(/[_-]/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
  const labels = {
    research:'Research', science:'Research', systems:'Systems & products', technology:'Systems & products',
    teaching:'Teaching', education:'Teaching', leadership:'Leadership', partnerships:'Partnerships',
    community:'Community', communities:'Community', fieldwork:'Fieldwork', field:'Fieldwork',
    publication:'Publication', award:'Award', product:'Product', grant:'Award', appointment:'Appointment',
    milestone:'Milestone', service:'Service', collaboration:'Collaboration', data:'Data & methods'
  };
  const label = value => labels[value] || humanize(value);
  const accents = {research:'#6853a2',science:'#6853a2',teaching:'#087fab',education:'#087fab',community:'#ac4e34',communities:'#ac4e34',fieldwork:'#28734b',field:'#28734b',leadership:'#775b2b',partnerships:'#775b2b','Population & data':'#006575','Climate & coasts':'#6853a2','Teaching':'#087fab','Open science':'#775b2b','Field methods':'#28734b','Leadership':'#ac4e34'};
  const themes = [...new Set(milestones.flatMap(item => item.themes || []))].sort((a,b) => label(a).localeCompare(label(b)));
  const years = [...new Set(milestones.map(item => item.date.slice(0,4)))].sort().reverse();
  const hasFeatured = milestones.some(item => item.featured);
  const hasMedia = milestones.some(item => (item.media || []).length);
  const defaultView = hasFeatured ? 'featured' : 'all';
  if (hasMedia) {
    const mediaButton = document.createElement('button');
    mediaButton.type = 'button';
    mediaButton.dataset.view = 'media';
    mediaButton.setAttribute('aria-pressed', 'false');
    mediaButton.textContent = 'With media';
    document.querySelector('.view-switch').append(mediaButton);
  }
  // Seasons position year-level records relative to other work in that year.
  // The inferred ordering month is never presented as an event date.
  function chronologicalKey(item) {
    const seasonOrder = {spring:'03',summer:'06',fall:'09',autumn:'09',winter:'12'};
    return item.date.length === 4 && seasonOrder[item.season] ? `${item.date}-${seasonOrder[item.season]}` : item.date;
  }
  const themeGroup = el('theme-filters');
  themeGroup.innerHTML = `<button type="button" class="theme-filter" data-theme="all" aria-pressed="true">All themes</button>` + themes.map(theme => `<button type="button" class="theme-filter" data-theme="${escape(theme)}" aria-pressed="false">${escape(label(theme))}</button>`).join('');
  el('year-filter').innerHTML = '<option value="all">All years</option>' + years.map(year => `<option value="${escape(year)}">${escape(year)}</option>`).join('');
  el('milestone-total').textContent = String(milestones.length);
  el('year-span').textContent = years.length ? `${years.at(-1)}–${years[0]}` : 'An evolving record';
  if (data.updated) {
    const updated = new Date(`${data.updated}T12:00:00`);
    if (!Number.isNaN(updated.getTime())) {
      el('updated-date').textContent = updated.toLocaleDateString('en-US',{month:'long',day:'numeric',year:'numeric'});
      el('updated-date').dateTime = data.updated;
    }
  }
  el('explore-tools').hidden = false;
  if (!hasFeatured) document.querySelector('[data-view="featured"]').disabled = true;
  let state;
  function readState() {
    const params = new URLSearchParams(location.search);
    return {
      q: params.get('q') || '',
      theme: themes.includes(params.get('theme')) ? params.get('theme') : 'all',
      year: years.includes(params.get('year')) ? params.get('year') : 'all',
      view: ['featured','all','media'].includes(params.get('view')) ? params.get('view') : defaultView,
      sort: params.get('sort') === 'newest' ? 'newest' : 'oldest'
    };
  }
  function updateUrl() {
    const url = new URL(location.href);
    for (const key of ['q','theme','year','view','sort']) url.searchParams.delete(key);
    if (state.q.trim()) url.searchParams.set('q',state.q.trim());
    if (state.theme !== 'all') url.searchParams.set('theme',state.theme);
    if (state.year !== 'all') url.searchParams.set('year',state.year);
    if (state.view !== defaultView) url.searchParams.set('view',state.view);
    if (state.sort !== 'oldest') url.searchParams.set('sort',state.sort);
    history.replaceState(null,'',url);
  }
  function safeUrl(value) {
    if (typeof value !== 'string' || !value.trim()) return null;
    try {
      const url = new URL(value,location.href);
      return ['https:','http:'].includes(url.protocol) ? url.href : null;
    } catch { return null; }
  }
  function safeImage(value) {
    return typeof value === 'string' && /^assets\/media\/[a-z0-9][a-z0-9._-]*\.(webp|jpg|jpeg|png)$/i.test(value) ? value : null;
  }
  function renderCredit(media) {
    const license = safeUrl(media.licenseUrl);
    const rights = license ? ` · <a href="${escape(license)}" rel="noopener">${escape(media.rightsLabel || 'Reuse license')}</a>` : media.rightsLabel ? ` · ${escape(media.rightsLabel)}` : '';
    return `<span class="media-credit">${escape(media.credit)}${rights}</span>`;
  }
  function renderMedia(item) {
    const figures = (item.media || []).map((media, index) => {
      if (media.kind === 'image' && safeImage(media.src)) {
        const source = safeUrl(media.sourceUrl);
        return `<figure class="milestone-image"><a class="media-preview" href="${escape(media.src)}" data-image-open data-milestone-id="${escape(item.id)}" data-media-index="${index}" aria-label="Enlarge image: ${escape(media.alt)}"><img src="${escape(media.src)}" alt="${escape(media.alt)}" width="${Number(media.width)}" height="${Number(media.height)}" loading="lazy" decoding="async"><span class="media-enlarge" aria-hidden="true">Enlarge ↗</span></a><figcaption><span class="media-caption">${escape(media.caption)}</span>${renderCredit(media)}${source ? `<a class="media-source" href="${escape(source)}" rel="noopener">${escape(media.sourceTitle || 'Image source')} ↗</a>` : ''}</figcaption></figure>`;
      }
      const destination = safeUrl(media.url);
      if (!destination || !['video','interactive','slides','article'].includes(media.kind)) return '';
      const kindLabel = {video:'Watch video',interactive:'Explore interactive',slides:'View slides',article:'Read the story'}[media.kind];
      return `<div class="milestone-media-link"><span class="media-kind">${kindLabel}</span><a href="${escape(destination)}" rel="noopener">${escape(media.title)} <span aria-hidden="true">↗</span></a>${media.caption ? `<p>${escape(media.caption)}</p>` : ''}</div>`;
    }).join('');
    return figures ? `<div class="milestone-media">${figures}</div>` : '';
  }
  function renderItem(item) {
    const itemThemes = item.themes || [];
    const accent = itemThemes.map(theme => accents[theme]).find(Boolean) || '#006575';
    const sources = (item.sources || []).filter(source => safeUrl(source.url));
    const sourceList = sources.length ? `<p class="milestone-source-label">Explore this work</p><ul class="milestone-sources">${sources.map(source => `<li><a href="${escape(safeUrl(source.url))}" rel="noopener">${escape(source.title || 'Read the source')} <span aria-hidden="true">↗</span></a></li>`).join('')}</ul>` : '<p class="milestone-context">More about this work will be added here.</p>';
    return `<li class="timeline-item" id="${escape(item.id)}" style="--card-accent:${accent}"><article class="milestone" aria-labelledby="title-${escape(item.id)}"><div class="milestone-date-line"><time class="milestone-date" datetime="${escape(item.date)}">${escape(item.dateLabel || item.date.slice(0,4))}</time><span class="milestone-kind">${escape(label(item.type || 'milestone'))}</span></div><h3 id="title-${escape(item.id)}"><a href="#${escape(item.id)}">${escape(item.title)}</a></h3>${renderMedia(item)}<p class="milestone-summary">${escape(item.summary)}</p><div class="milestone-themes">${itemThemes.map(theme => `<span class="theme-label">${escape(label(theme))}</span>`).join('')}${item.status && item.status !== 'completed' ? `<span class="status-label">${escape(label(item.status))}</span>` : ''}</div><details><summary>Contribution &amp; sources<span class="sr-only">: ${escape(item.title)}</span></summary>${item.role ? `<p class="milestone-role"><strong>Kytt’s contribution</strong>${escape(item.role)}</p>` : ''}${item.detail ? `<p class="milestone-context">${escape(item.detail)}</p>` : ''}${sourceList}<a class="permalink" href="#${escape(item.id)}">Link to this milestone <span aria-hidden="true">↗</span></a></details></article></li>`;
  }
  function render(syncUrl = true) {
    el('timeline-search').value = state.q;
    el('year-filter').value = state.year;
    el('sort-order').value = state.sort;
    document.querySelectorAll('[data-view]').forEach(button => button.setAttribute('aria-pressed',String(button.dataset.view === state.view)));
    document.querySelectorAll('[data-theme]').forEach(button => button.setAttribute('aria-pressed',String(button.dataset.theme === state.theme)));
    const query = state.q.trim().toLocaleLowerCase();
    const filtered = milestones.filter(item => {
      if (state.view === 'featured' && !item.featured) return false;
      if (state.view === 'media' && !(item.media || []).length) return false;
      if (state.theme !== 'all' && !(item.themes || []).includes(state.theme)) return false;
      if (state.year !== 'all' && !item.date.startsWith(state.year)) return false;
      if (!query) return true;
      return [item.title,item.summary,item.role,item.detail,item.dateLabel,item.type,...(item.themes || []).map(label),...(item.sources || []).map(source => source.title),...(item.media || []).flatMap(media => [media.title,media.alt,media.caption,media.credit])].filter(Boolean).join(' ').toLocaleLowerCase().includes(query);
    }).sort((a,b) => {
      const order = chronologicalKey(a).localeCompare(chronologicalKey(b)) || a.title.localeCompare(b.title);
      return state.sort === 'newest' ? -order : order;
    });
    el('timeline-list').innerHTML = filtered.map(renderItem).join('');
    el('timeline-list').hidden = filtered.length === 0;
    el('empty-state').hidden = filtered.length !== 0;
    const descriptor = state.view === 'featured' ? 'selected milestones' : state.view === 'media' ? 'milestones with media' : 'milestones';
    el('result-count').textContent = `Showing ${filtered.length} ${descriptor}${state.year !== 'all' ? ` · ${state.year}` : ''}${state.theme !== 'all' ? ` · ${label(state.theme)}` : ''}${query ? ` · matching “${state.q.trim()}”` : ''}`;
    if (syncUrl) updateUrl();
  }
  function showHash() {
    let id;
    try { id = decodeURIComponent(location.hash.slice(1)); } catch { return; }
    if (!byId.has(id)) return;
    if (!el(id)) {
      state = {q:'',theme:'all',year:'all',view:'all',sort:state.sort};
      render();
    }
    const target = el(id);
    if (target) {
      target.querySelector('details').open = true;
      requestAnimationFrame(() => target.scrollIntoView({block:'start',behavior:'instant'}));
    }
  }
  function reset(full = false) {
    state = {q:'',theme:'all',year:'all',view:full ? 'all' : defaultView,sort:'oldest'};
    render();
  }
  const imageDialog = document.createElement('dialog');
  imageDialog.className = 'media-dialog';
  imageDialog.setAttribute('aria-labelledby', 'media-dialog-title');
  imageDialog.innerHTML = '<div class="media-dialog-inner"><div class="media-dialog-top"><h2 id="media-dialog-title">Photo and context</h2><button class="media-dialog-close" type="button" autofocus aria-label="Close enlarged image">Close ×</button></div><figure><img alt=""><figcaption></figcaption></figure></div>';
  document.body.append(imageDialog);
  let imageOpener = null;
  imageDialog.querySelector('.media-dialog-close').addEventListener('click', () => imageDialog.close());
  imageDialog.addEventListener('click', event => { if (event.target === imageDialog) imageDialog.close(); });
  imageDialog.addEventListener('close', () => {
    imageDialog.querySelector('img').removeAttribute('src');
    if (imageOpener && imageOpener.isConnected) imageOpener.focus({preventScroll:true});
  });
  el('timeline-list').addEventListener('click', event => {
    const opener = event.target.closest('[data-image-open]');
    if (!opener || typeof imageDialog.showModal !== 'function') return;
    const item = byId.get(opener.dataset.milestoneId);
    const media = item && (item.media || [])[Number(opener.dataset.mediaIndex)];
    if (!media || media.kind !== 'image' || !safeImage(media.src)) return;
    event.preventDefault();
    imageOpener = opener;
    const image = imageDialog.querySelector('img');
    image.src = media.src;
    image.alt = media.alt;
    el('media-dialog-title').textContent = item.title;
    const source = safeUrl(media.sourceUrl);
    imageDialog.querySelector('figcaption').innerHTML = `<span class="media-caption">${escape(media.caption)}</span>${renderCredit(media)}${source ? `<a href="${escape(source)}" rel="noopener">${escape(media.sourceTitle || 'Image source')} ↗</a>` : ''}`;
    imageDialog.showModal();
  });
  document.querySelectorAll('[data-view]').forEach(button => button.addEventListener('click',() => {state.view=button.dataset.view; render();}));
  themeGroup.addEventListener('click',event => {const button=event.target.closest('[data-theme]');if(button){state.theme=button.dataset.theme;render();}});
  let debounce;
  el('timeline-search').addEventListener('input',event => {state.q=event.target.value;clearTimeout(debounce);debounce=setTimeout(render,120);});
  el('timeline-search').addEventListener('search',event => {state.q=event.target.value;clearTimeout(debounce);render();});
  el('year-filter').addEventListener('change',event => {state.year=event.target.value;render();});
  el('sort-order').addEventListener('change',event => {state.sort=event.target.value;render();});
  el('reset-filters').addEventListener('click',() => reset());
  el('empty-reset').addEventListener('click',() => reset(true));
  addEventListener('popstate',() => {state=readState();render(false);showHash();});
  addEventListener('hashchange',showHash);
  state=readState();
  render(false);
  showHash();
})();
