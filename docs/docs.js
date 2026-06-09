(function () {
  const root = document.body.dataset.root || '';
  const index = window.DOCS_INDEX || [];
  const byHref = new Map(index.map((entry) => [entry.href, entry]));

  function matchesQuery(entry, query) {
    return entry.title.toLowerCase().includes(query) || entry.text.includes(query);
  }

  const sidebar = document.querySelector('.docs-sidebar');
  const sidebarSearch = sidebar.querySelector('.docs-search');
  const empty = sidebar.querySelector('.docs-empty');

  sidebarSearch.addEventListener('input', () => {
    const query = sidebarSearch.value.trim().toLowerCase();
    let visible = 0;
    sidebar.classList.toggle('searching', query.length > 0);
    sidebar.querySelectorAll('[data-doc-link]').forEach((link) => {
      const entry = byHref.get(link.dataset.href);
      const match = !query || (entry && matchesQuery(entry, query));
      link.parentElement.style.display = match ? '' : 'none';
      if (match) visible += 1;
    });
    sidebar.querySelectorAll('.docs-nav-section').forEach((section) => {
      const hasVisible = Array.from(section.querySelectorAll('li')).some(
        (item) => item.style.display !== 'none'
      );
      section.style.display = hasVisible ? '' : 'none';
    });
    empty.style.display = visible ? 'none' : 'block';
  });

  const menuToggle = document.querySelector('.docs-menu-toggle');
  menuToggle.addEventListener('click', () => {
    const open = sidebar.classList.toggle('open');
    menuToggle.setAttribute('aria-expanded', String(open));
    menuToggle.textContent = open ? 'Close' : 'Menu';
  });

  const homeSearch = document.querySelector('.docs-home-search');
  if (homeSearch) {
    const results = document.querySelector('.docs-home-results');
    homeSearch.addEventListener('input', () => {
      const query = homeSearch.value.trim().toLowerCase();
      results.innerHTML = '';
      if (!query) {
        results.style.display = 'none';
        return;
      }
      const titleHits = index.filter((entry) => entry.title.toLowerCase().includes(query));
      const textHits = index.filter(
        (entry) => !titleHits.includes(entry) && entry.text.includes(query)
      );
      const hits = titleHits.concat(textHits).slice(0, 8);
      if (hits.length === 0) {
        const item = document.createElement('li');
        item.className = 'docs-home-noresults';
        item.textContent = 'No matching docs.';
        results.appendChild(item);
      }
      hits.forEach((entry) => {
        const item = document.createElement('li');
        const link = document.createElement('a');
        link.href = root + entry.href;
        link.textContent = entry.title;
        const section = document.createElement('span');
        section.textContent = entry.section;
        link.appendChild(section);
        item.appendChild(link);
        results.appendChild(item);
      });
      results.style.display = 'block';
    });
  }
})();
