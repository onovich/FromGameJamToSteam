(() => {
  const search = document.getElementById('search');
  const status = document.getElementById('status-filter');
  const categories = [...document.querySelectorAll('[data-category-filter]')];
  const rows = [...document.querySelectorAll('.game-row')];
  const count = document.getElementById('result-count');
  const empty = document.getElementById('empty-state');
  const clear = document.getElementById('clear-filters');
  const languageLinks = [...document.querySelectorAll('[data-lang]')];
  let category = '';

  const normalize = value => value.normalize('NFKC').toLocaleLowerCase().trim();

  function apply() {
    const query = normalize(search.value);
    let visible = 0;
    for (const row of rows) {
      const matches = (!query || normalize(row.dataset.search).includes(query)) &&
        (!category || row.dataset.category === category) &&
        (!status.value || row.dataset.status === status.value);
      row.hidden = !matches;
      if (matches) visible++;
    }
    count.textContent = count.dataset.template
      .replace('{visible}', visible)
      .replace('{total}', rows.length);
    empty.hidden = visible !== 0;
  }

  search.addEventListener('input', apply);
  status.addEventListener('change', apply);
  categories.forEach(button => button.addEventListener('click', () => {
    category = button.dataset.categoryFilter;
    categories.forEach(item => item.setAttribute('aria-pressed', String(item === button)));
    apply();
  }));
  clear.addEventListener('click', () => {
    search.value = '';
    status.value = '';
    category = '';
    categories.forEach(item => item.setAttribute('aria-pressed', String(item.dataset.categoryFilter === '')));
    apply();
    search.focus();
  });
  languageLinks.forEach(link => link.addEventListener('click', () => {
    try { localStorage.setItem('jam-to-steam-language', link.dataset.lang); } catch {}
  }));
  apply();
})();
