let raw = {};               // { section: [questions] } as returned
let filtered = {};          // after search/filter
let dirtySections = new Set();

function el(tag, attrs={}, children=[]) {
  const e = document.createElement(tag);
  for (const k in attrs) {
    if (k === "class") e.className = attrs[k];
    else if (k === "text") e.textContent = attrs[k];
    else e.setAttribute(k, attrs[k]);
  }
  const add = (c) => {
    if (c == null || c === false) return;
    if (Array.isArray(c)) return c.forEach(add);
    e.appendChild(c instanceof Node ? c : document.createTextNode(String(c)));
  };
  add(children);
  return e;
}

const naturalCompareIds = (a, b) => {
  // Splits by ".", compare numeric prefix then alpha suffix, segment by segment
  const seg = s => s.split('.').map(p => {
    const m = /^(\d+)([a-z]*)$/i.exec(p) || [null, p, ""];
    return { n: isNaN(+m[1]) ? null : +m[1], s: isNaN(+m[1]) ? p : m[2] };
  });
  const A = seg(a), B = seg(b);
  const L = Math.max(A.length, B.length);
  for (let i=0;i<L;i++){
    const x=A[i], y=B[i];
    if(!x && y) return -1;
    if(x && !y) return 1;
    if(!x && !y) return 0;
    if(x.n!==null && y.n!==null){
      if(x.n!==y.n) return x.n - y.n;
      if(x.s!==y.s) return x.s.localeCompare(y.s);
    }else{
      const ax = (x.n!==null)? String(x.n)+x.s : x.s;
      const ay = (y.n!==null)? String(y.n)+y.s : y.s;
      if(ax!==ay) return ax.localeCompare(ay);
    }
  }
  return 0;
};

const computeNextIdForSection = (sectionName) => {
  // sectionName starts like "1.1 Identity …" -> take numeric prefix "1.1"
  const m = /^(\d+(?:\.\d+)+)/.exec(sectionName);
  if (!m) return null;
  const base = m[1]; // e.g., "1.1"
  const list = (raw[sectionName] || []).map(q => q.id).filter(id => id.startsWith(base + "."));
  if (list.length === 0) return base + ".1";
  // find max last numeric segment
  let maxNum = 0, suffix = "";
  list.forEach(id => {
    const parts = id.split('.');
    let last = parts[parts.length - 1]; // may be "1", "1f", "1m"
    const mm = /^(\d+)/.exec(last);
    if (mm) {
      const n = +mm[1];
      if (n > maxNum) maxNum = n;
    }
  });
  return `${base}.${maxNum + 1}`;
};

const refreshCreateSectionSelect = () => {
  const sel = document.getElementById("c_section");
  sel.innerHTML = "";
  Object.keys(raw).sort((a,b)=> naturalCompareIds(a,b)).forEach(sec => {
    const opt = document.createElement("option");
    opt.value = sec; opt.textContent = sec;
    sel.appendChild(opt);
  });
  updateNextIdHint();
};

const updateNextIdHint = () => {
  const sec = document.getElementById("c_section").value;
  const id = computeNextIdForSection(sec);
  document.getElementById("c_nextid_hint").textContent = id ? `Next ID will be: ${id}` : "Next ID will be computed…";
};

async function reload(){
  const res = await fetch('/api/admin/intake');
  if(!res.ok){ alert('Failed to load'); return; }
  const json = await res.json();
  raw = json.sections || {};
  applyFilterAndRender();
  // setup create form sections
  refreshCreateSectionSelect();
}

function applyFilterAndRender(){
  const q = document.getElementById('search').value.trim().toLowerCase();
  const secFilter = document.getElementById('sectionFilter').value;
  filtered = {};
  for(const sec of Object.keys(raw)){
    if(secFilter && sec !== secFilter) continue;
    const list = raw[sec].filter(it => {
      if(!q) return true;
      return (it.id||"").toLowerCase().includes(q)
          || (it.variable_name||"").toLowerCase().includes(q)
          || (it.text||"").toLowerCase().includes(q);
    });
    if(list.length) filtered[sec] = list.slice();
  }
  render();
}

function showSaveOrder(section, show){
  const card = document.querySelector(`[data-section="${CSS.escape(section)}"]`);
  if(!card) return;
  if(show) card.classList.add('dirty');
  else card.classList.remove('dirty');
  if(show) dirtySections.add(section);
  else dirtySections.delete(section);
}

function render(){
  const root = document.getElementById('sections');
  root.innerHTML = '';
  // fill filter dropdown
  const filterSel = document.getElementById('sectionFilter');
  const existing = new Set(Array.from(filterSel.options).map(o=>o.value));
  Object.keys(raw).forEach(sec=>{
    if(!existing.has(sec)){
      const o = document.createElement('option');
      o.value = sec; o.textContent = sec;
      filterSel.appendChild(o);
    }
  });

  const secs = Object.keys(filtered).sort((a,b)=> naturalCompareIds(a,b));
  for(const sec of secs){
    // sort by sort_index (if present), else natural id
    filtered[sec].sort((a,b)=>{
      const ai = (typeof a.sort_index === 'number') ? a.sort_index : null;
      const bi = (typeof b.sort_index === 'number') ? b.sort_index : null;
      if(ai!=null && bi!=null) return ai - bi;
      if(ai!=null && bi==null) return -1;
      if(ai==null && bi!=null) return 1;
      return naturalCompareIds(a.id, b.id);
    });

    const scard = el('div', {class:'card section-card', 'data-section':sec});
    const head = el('div', {class:'head'});
    head.appendChild(el('h2', {text:sec, style:"margin:0; font-size:18px;"}));
    head.appendChild(el('span', {class:'tag', text:`${filtered[sec].length} questions`}));
    scard.appendChild(head);

    const list = el('div', {'data-list':sec});
    // Drop hint
    const dh = el('div', {class:'drop-hint', text:'Drag cards to reorder'});
    list.appendChild(dh);

    // Cards
    filtered[sec].forEach(q => list.appendChild(qCard(sec, q)));

    // Save/Revert order bar
    const bar = el('div', {class:'save-order-bar'});
    const save = el('button', {class:'btn small'}, 'Save order');
    const revert = el('button', {class:'btn ghost small'}, 'Revert');
    save.onclick = ()=> saveOrder(sec);
    revert.onclick = ()=> { applyFilterAndRender(); showSaveOrder(sec, false); };
    bar.appendChild(revert); bar.appendChild(save);

    scard.appendChild(list);
    scard.appendChild(bar);
    root.appendChild(scard);

    // DnD events on container
    list.addEventListener('dragover', e => { e.preventDefault(); dh.style.display = 'block'; });
    list.addEventListener('dragleave', () => { dh.style.display = 'none'; });
    list.addEventListener('drop', e => {
      e.preventDefault(); dh.style.display = 'none';
      const dragId = e.dataTransfer.getData('text/plain');
      const after = e.target.closest('.qcard');
      const container = list;
      const card = container.querySelector(`.qcard[data-id="${CSS.escape(dragId)}"]`);
      if(!card) return;
      if(after && after !== card){
        const rect = after.getBoundingClientRect();
        const mid = rect.top + rect.height/2;
        if(e.clientY > mid) after.after(card);
        else after.before(card);
      }else{
        container.appendChild(card);
      }
      // mark dirty by syncing filtered[sec] to current DOM order
      const ids = Array.from(container.querySelectorAll('.qcard')).map(n => n.getAttribute('data-id'));
      filtered[sec].sort((a,b)=> ids.indexOf(a.id) - ids.indexOf(b.id));
      showSaveOrder(sec, true);
    });
  }
}

function qCard(section, q){
  const card = el('div', {class:'qcard', draggable:'true', 'data-id':q.id});
  card.addEventListener('dragstart', e => {
    e.dataTransfer.setData('text/plain', q.id);
  });

  const head = el('div', {class:'qhead'});
  const left = el('div', {class:'qtitle grow'});
  const drag = el('span', {class:'drag', title:'Drag to reorder'}, '⋮⋮');
  const idpill = el('span', {class:'idpill'}, q.id);
  const name = el('div', {class:'grow', text:`${q.variable_name || '(no variable)'}`});
  left.appendChild(drag); left.appendChild(idpill); left.appendChild(name);

  const right = el('div', {class:'handle-col'});
  const typ = el('span', {class:'pill'}, q.type);
  const expandBtn = el('button', {class:'collapse-btn', title:'Expand/collapse'}, '▸');
  right.appendChild(typ);
  // up/down fallback (mobile)
  const updown = el('div', {class:'updown'});
  const up = el('button', {class:'btn ghost small'}, '↑');
  const down = el('button', {class:'btn ghost small'}, '↓');
  up.onclick = () => nudge(section, q.id, -1);
  down.onclick = () => nudge(section, q.id, +1);
  right.appendChild(updown); updown.appendChild(up); updown.appendChild(down);
  right.appendChild(expandBtn);

  head.appendChild(left); head.appendChild(right);

  const body = el('div', {class:'qbody'});
  const text = el('textarea', {rows:'3'}); text.value = q.text || '';

  // editable meta
  const row1 = el('div', {class:'row'});
  const varInput = el('input', {type:'text', value: q.variable_name || ''});
  const typeSel = el('select');
  ["single-select","multi-select","number","time","time_24h","boolean"].forEach(t=>{
    const o = document.createElement('option'); o.value=t; o.textContent=t;
    if(t===q.type) o.selected=true; typeSel.appendChild(o);
  });
  const optionalSel = el('select');
  optionalSel.innerHTML = `<option value="">optional: no</option><option value="true">optional: yes</option>`;
  if(q.optional) optionalSel.value = "true";
  row1.appendChild(el('div',[el('label',{text:'variable_name'}), varInput]));
  row1.appendChild(el('div',[el('label',{text:'type'}), typeSel]));
  row1.appendChild(el('div',[el('label',{text:'optional'}), optionalSel]));

  const row2 = el('div', {class:'row'});
  const maxSel = el('input', {type:'number', min:'1', value: q.max_selections ?? ''});
  const rmin = el('input', {type:'number', value: (q.range && q.range.min!=null) ? q.range.min : ''});
  const rmax = el('input', {type:'number', value: (q.range && q.range.max!=null) ? q.range.max : ''});
  row2.appendChild(el('div',[el('label',{text:'max_selections (multi-select only)'}), maxSel]));
  row2.appendChild(el('div',[el('label',{text:'range.min (number type)'}), rmin]));
  row2.appendChild(el('div',[el('label',{text:'range.max (number type)'}), rmax]));

  const row3 = el('div', {class:'row'});
  const cvar = el('input', {type:'text', value: (q.conditional_on && q.conditional_on.variable_name) || ''});
  const cval = el('input', {type:'text', value: (q.conditional_on && q.conditional_on.value) || ''});
  row3.appendChild(el('div',[el('label',{text:'conditional var (variable_name)'}), cvar]));
  row3.appendChild(el('div',[el('label',{text:'conditional value'}), cval]));

  // options editor
  const optsWrap = el('div', {});
  const optsHead = el('div', {class:'opts-head'});
  optsHead.appendChild(el('strong', {text: 'Options'}));
  const addBtn = el('button', {class:'btn ghost small', type:'button'}, 'Add');
  optsHead.appendChild(addBtn);
  const opts = el('div');
  (q.options || []).forEach(op => opts.appendChild(optRow(op)));
  addBtn.onclick = ()=> opts.appendChild(optRow({id:'', text:'', value:''}));
  optsWrap.appendChild(optsHead); optsWrap.appendChild(opts);

  const actions = el('div', {class:'row'});
  const save = el('button', {class:'btn'}, 'Save');
  const del  = el('button', {class:'btn danger'}, 'Delete');
  actions.appendChild(save); actions.appendChild(del);

  body.appendChild(el('div',[el('label',{text:'text'}), text]));
  body.appendChild(row1);
  body.appendChild(row2);
  body.appendChild(row3);
  body.appendChild(optsWrap);
  body.appendChild(actions);

  // type-aware visibility
  const applyTypeVisibility = () => {
    const t = typeSel.value;
    // show options for single/multi
    optsWrap.style.display = (t === 'single-select' || t === 'multi-select') ? '' : 'none';
    // show max selections only for multi
    maxSel.parentElement.parentElement.style.display = (t === 'multi-select') ? '' : 'none';
    // show range only for number
    rmin.parentElement.parentElement.style.display = (t === 'number') ? '' : 'none';
    rmax.parentElement.parentElement.style.display = (t === 'number') ? '' : 'none';
  };
  typeSel.addEventListener('change', applyTypeVisibility);
  applyTypeVisibility();

  // collapse
  const expandBtn = right.querySelector('.collapse-btn');
  expandBtn.onclick = () => {
    const open = body.style.display === 'block';
    body.style.display = open ? 'none' : 'block';
    expandBtn.textContent = open ? '▸' : '▾';
  };

  // save/delete
  save.onclick = async () => {
    const payload = {
      id: q.id,
      section: q.section,
      variable_name: varInput.value.trim(),
      text: text.value.trim(),
      type: typeSel.value,
      options: [...opts.querySelectorAll('.opt')].map(row=>{
        const oi=row.querySelector('.oid').value.trim();
        const ot=row.querySelector('.otext').value.trim();
        const ov=row.querySelector('.oval').value.trim();
        const o={id:oi,text:ot}; if(ov) o.value=ov; return o;
      }).filter(o=>o.id && o.text),
      range: (rmin.value || rmax.value) ? {
        min: rmin.value ? Number(rmin.value) : null,
        max: rmax.value ? Number(rmax.value) : null
      } : null,
      optional: optionalSel.value === "true" ? true : null,
      conditional_on: (cvar.value && cval.value) ? { variable_name:cvar.value, value:cval.value } : null
    };
    if (typeSel.value === 'multi-select' && maxSel.value) payload.max_selections = Number(maxSel.value);

    // cleanups
    if (!payload.options.length) delete payload.options;
    if (!payload.range || (payload.range.min==null && payload.range.max==null)) delete payload.range;
    if (payload.optional == null) delete payload.optional;
    if (!payload.conditional_on) delete payload.conditional_on;
    if (payload.max_selections == null || isNaN(payload.max_selections)) delete payload.max_selections;

    const res = await fetch(`/api/admin/intake/${encodeURIComponent(q.id)}`, {
      method:'PUT', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)
    });
    if(res.ok){ reload(); } else { alert('Save failed'); }
  };
  del.onclick = async () => {
    if(!confirm(`Delete ${q.id}?`)) return;
    const res = await fetch(`/api/admin/intake/${encodeURIComponent(q.id)}`, { method:'DELETE' });
    if(res.ok){ reload(); } else { alert('Delete failed'); }
  };

  card.appendChild(head);
  card.appendChild(body);
  return card;
}

function optRow(op){
  const row = el('div', {class:'opt'});
  const oid = el('input', {class:'oid', placeholder:'id', value: op.id || ''});
  const otext = el('input', {class:'otext', placeholder:'text', value: op.text || ''});
  const oval = el('input', {class:'oval', placeholder:'value (optional)', value: op.value || ''});
  const rm = el('button', {class:'btn ghost small', type:'button'}, '−');
  rm.onclick = ()=> row.remove();
  row.appendChild(oid); row.appendChild(otext); row.appendChild(oval); row.appendChild(rm);
  return row;
}

function nudge(section, id, delta){
  const container = document.querySelector(`[data-list="${CSS.escape(section)}"]`);
  const cards = Array.from(container.querySelectorAll('.qcard'));
  const idx = cards.findIndex(c=> c.getAttribute('data-id')===id);
  if(idx < 0) return;
  const newIdx = Math.max(0, Math.min(cards.length-1, idx + delta));
  if(newIdx === idx) return;
  const card = cards[idx];
  if(delta < 0) cards[newIdx].before(card); else cards[newIdx].after(card);
  // mark dirty
  const ids = Array.from(container.querySelectorAll('.qcard')).map(n => n.getAttribute('data-id'));
  filtered[section].sort((a,b)=> ids.indexOf(a.id) - ids.indexOf(b.id));
  showSaveOrder(section, true);
}

async function saveOrder(section){
  const container = document.querySelector(`[data-list="${CSS.escape(section)}"]`);
  const ids = Array.from(container.querySelectorAll('.qcard')).map(n => n.getAttribute('data-id'));
  const order = ids.map((id, i)=> ({ id, sort_index: i }));
  const res = await fetch('/api/admin/intake/reorder', {
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({ section: section, order })
  });
  if(res.ok){
    // update raw with sort_index values
    (raw[section]||[]).forEach(q => {
      const idx = order.find(o=>o.id===q.id);
      if(idx) q.sort_index = idx.sort_index;
    });
    applyFilterAndRender();
    showSaveOrder(section, false);
  }else{
    alert('Failed to save order');
  }
}

/* ---------- Create flow ---------- */
function toggleCreate(){
  const f = document.getElementById('createForm');
  const on = (f.style.display !== 'block');
  f.style.display = on ? 'block' : 'none';
  if(on){
    // default type show/hide
    applyCreateTypeVisibility();
  }
}
function addCOpt(){ document.getElementById('c_opts').appendChild(optRow({id:'', text:'', value:''})); }

function applyCreateTypeVisibility(){
  const t = document.getElementById('c_type').value;
  document.getElementById('c_opts_wrap').classList.toggle('hidden', !(t==='single-select'||t==='multi-select'));
  document.getElementById('c_multisel_wrap').classList.toggle('hidden', t!=='multi-select');
  document.getElementById('c_numwrap').classList.toggle('hidden', t!=='number');
}
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('c_type').addEventListener('change', applyCreateTypeVisibility);
  document.getElementById('c_section').addEventListener('change', updateNextIdHint);

  /* ---------- UI wires ---------- */
  document.getElementById('reloadBtn').onclick = reload;
  document.getElementById('toggleCreate').onclick = toggleCreate;
  document.getElementById('search').addEventListener('input', applyFilterAndRender);
  document.getElementById('sectionFilter').addEventListener('change', applyFilterAndRender);
  document.getElementById('expandAll').onclick = () => {
    document.querySelectorAll('.qbody').forEach(b=>{ b.style.display='block'; });
    document.querySelectorAll('.collapse-btn').forEach(b=> b.textContent='▾');
  };
  document.getElementById('collapseAll').onclick = () => {
    document.querySelectorAll('.qbody').forEach(b=>{ b.style.display='none'; });
    document.querySelectorAll('.collapse-btn').forEach(b=> b.textContent='▸');
  };

  /* ---------- Go ---------- */
  reload();
});
