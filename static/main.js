// ── Tab switcher (Text / PDF) ──────────────────────────────────────
document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');

    const tab = btn.dataset.tab;
    document.getElementById('input_type').value = tab;
    document.getElementById('panel-text').classList.toggle('hidden', tab !== 'text');
    document.getElementById('panel-pdf').classList.toggle('hidden',  tab !== 'pdf');
  });
});

// ── PDF file name display ──────────────────────────────────────────
const pdfInput = document.getElementById('pdf_file');
if (pdfInput) {
  pdfInput.addEventListener('change', () => {
    const name = pdfInput.files[0]?.name || '';
    document.getElementById('file-name').textContent = name ? `נבחר: ${name}` : '';
  });
}

// ── Drag-and-drop on drop zone ────────────────────────────────────
const dropZone = document.getElementById('drop-zone');
if (dropZone) {
  dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('drag-over'); });
  dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
  dropZone.addEventListener('drop', e => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
    const file = e.dataTransfer.files[0];
    if (file && file.name.endsWith('.pdf')) {
      const dt = new DataTransfer();
      dt.items.add(file);
      pdfInput.files = dt.files;
      document.getElementById('file-name').textContent = `נבחר: ${file.name}`;
    }
  });
}

// ── Submit spinner ────────────────────────────────────────────────
const form = document.getElementById('summarize-form');
if (form) {
  form.addEventListener('submit', () => {
    const btn     = document.getElementById('submit-btn');
    const btnText = document.getElementById('btn-text');
    const spinner = document.getElementById('btn-spinner');
    btn.disabled      = true;
    btnText.textContent = 'מייצר סיכום...';
    spinner.classList.remove('hidden');
  });
}

// ── Render colored summary sections ──────────────────────────────
function renderSummary(container, rawText) {
  const sections = rawText.split(/(?=🟥|🟧|🟩)/);
  container.innerHTML = sections.map(section => {
    const trimmed = section.trim();
    if (!trimmed) return '';

    // Remove lines that are only "אין מידע", then remove now-empty category headers
    const lines = trimmed.split('\n');
    const filtered = [];
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      if (/^\s*-\s*אין מידע\s*$/.test(line)) continue;
      // Skip a category header if the next non-empty line is another header or end-of-section
      if (/^\s*-\s*.+:\s*$/.test(line)) {
        const next = lines.slice(i + 1).find(l => l.trim() !== '');
        if (!next || /^\s*-\s*.+:\s*$/.test(next) || /^[🟥🟧🟩]/.test(next)) continue;
      }
      filtered.push(line);
    }

    const cleaned = filtered.join('\n').replace(/\n{3,}/g, '\n\n').trim();
    if (!cleaned) return '';

    let cls = '';
    if (trimmed.startsWith('🟥')) cls = 'section-red';
    else if (trimmed.startsWith('🟧')) cls = 'section-orange';
    else if (trimmed.startsWith('🟩')) cls = 'section-green';
    return `<div class="summary-section ${cls}">${escapeHtml(cleaned)}</div>`;
  }).join('');
}

function escapeHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

document.querySelectorAll('.summary-body').forEach(el => {
  const raw = el.dataset.summary;
  if (raw) renderSummary(el, raw);
});

// ── Bulk select & delete ──────────────────────────────────────────
const bulkBar      = document.getElementById('bulk-bar');
const bulkCount    = document.getElementById('bulk-count');
const selectAllBtn = document.getElementById('select-all-btn');
const bulkDeleteBtn= document.getElementById('bulk-delete-btn');

function getChecked() {
  return [...document.querySelectorAll('.card-checkbox:checked')];
}

function getAll() {
  return [...document.querySelectorAll('.card-checkbox')];
}

function updateBulkBar() {
  const checked = getChecked();
  if (!bulkBar) return;
  if (checked.length > 0) {
    bulkBar.classList.remove('hidden');
    bulkCount.textContent = `${checked.length} נבחרו`;
    const allSelected = checked.length === getAll().length;
    selectAllBtn.textContent = allSelected ? 'בטל בחירה' : 'בחר הכל';
  } else {
    bulkBar.classList.add('hidden');
  }
}

document.querySelectorAll('.card-checkbox').forEach(cb => {
  cb.addEventListener('change', updateBulkBar);
});

if (selectAllBtn) {
  selectAllBtn.addEventListener('click', () => {
    const all = getAll();
    const shouldSelectAll = getChecked().length < all.length;
    all.forEach(cb => { cb.checked = shouldSelectAll; });
    updateBulkBar();
  });
}

if (bulkDeleteBtn) {
  bulkDeleteBtn.addEventListener('click', () => {
    const checked = getChecked();
    if (!checked.length) return;
    if (!confirm(`למחוק ${checked.length} סיכומים?`)) return;
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '/summaries/delete-bulk';
    checked.forEach(cb => {
      const input = document.createElement('input');
      input.type  = 'hidden';
      input.name  = 'ids';
      input.value = cb.value;
      form.appendChild(input);
    });
    document.body.appendChild(form);
    form.submit();
  });
}
