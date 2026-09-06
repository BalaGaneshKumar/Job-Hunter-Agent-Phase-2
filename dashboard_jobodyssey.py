"""
dashboard_jobodyssey.py — Job Odyssey tab
Filter bar + stats breakdown + split view (job card list / detail panel)
over jobs collected by Scraper Abyss. Actions (Eligible/Hold/Ineligible/
Applied) update status in jobodyssey.db with an undo toast.
"""

def build_jobodyssey_html():
    return '''
<style>
''' + build_jobodyssey_css() + '''
</style>
<div id="page-jobodyssey" class="page">
  <div class="jo-wrap">

    <!-- UNDO TOAST -->
    <div class="jo-undo-bar" id="jo-undo-bar">
      <span id="jo-undo-text"></span>
      <button onclick="joUndo()">Undo</button>
    </div>

    <div class="jo-top-row">
      <button class="cr-tab-btn cr-log-btn" id="jo-log-toggle-btn" onclick="crToggleLogPanel('jo')">&#128220; Logs</button>
    </div>

    <!-- FILTER BAR -->
    <div class="jo-filter-bar">
      <div class="jo-status-filter" id="jo-status-filter">
        <button type="button" class="jo-status-btn" id="jo-status-btn" onclick="joToggleStatusPanel(event)">Status: All &#9662;</button>
        <div class="jo-status-panel" id="jo-status-panel" style="display:none" onclick="event.stopPropagation()">
          <label><input type="checkbox" value="scraped" onchange="joPage=1;joOnStatusChange()"> Scraped</label>
          <label><input type="checkbox" value="eligible" onchange="joPage=1;joOnStatusChange()"> Eligible</label>
          <label><input type="checkbox" value="hold" onchange="joPage=1;joOnStatusChange()"> Hold</label>
          <label><input type="checkbox" value="ineligible" onchange="joPage=1;joOnStatusChange()"> Ineligible</label>
          <label><input type="checkbox" value="blacklist" onchange="joPage=1;joOnStatusChange()"> Blacklist</label>
          <label><input type="checkbox" value="applied" onchange="joPage=1;joOnStatusChange()"> Applied</label>
          <div class="jo-status-op">
            <label><input type="radio" name="jo-status-op" value="or" checked onchange="joPage=1;joOnStatusChange()"> Any of these (OR)</label>
            <label><input type="radio" name="jo-status-op" value="not" onchange="joPage=1;joOnStatusChange()"> None of these (NOT)</label>
          </div>
          <button type="button" class="jo-status-clear" onclick="joClearStatusFilter()">Clear</button>
        </div>
      </div>
      <select id="jo-filter-portal" onchange="joPage=1;joLoad()">
        <option value="">Portals: All</option>
      </select>
      <select id="jo-filter-location" onchange="joPage=1;joLoad()">
        <option value="">Location: All</option>
      </select>
      <select id="jo-filter-validation" onchange="joPage=1;joLoad()">
        <option value="">Validation: All</option>
        <option value="valid">Valid</option>
        <option value="defect">Defect</option>
      </select>
      <select id="jo-filter-linktype" onchange="joPage=1;joLoad()">
        <option value="">Type: All</option>
        <option value="internal">Internal</option>
        <option value="external">External</option>
        <option value="others">Others</option>
      </select>
      <input type="text" id="jo-search" placeholder="Search title or company&#8230;" oninput="joPage=1;joDebouncedLoad()">
      <select id="jo-sort" onchange="joPage=1;joLoad()">
        <option value="date_desc">Newest first</option>
        <option value="date_asc">Oldest first</option>
        <option value="title_asc">Title A&#8594;Z</option>
        <option value="title_desc">Title Z&#8594;A</option>
        <option value="company_asc">Company A&#8594;Z</option>
        <option value="company_desc">Company Z&#8594;A</option>
      </select>
      <button class="jo-reload-btn" onclick="joLoad()" title="Reload">&#8635; Reload</button>
      <button class="jo-reload-btn" onclick="joOpenExport()" title="Download" style="background:#00838f;">&#8595; Download</button>
    </div>

    <!-- STATS BREAKDOWN -->
    <div class="jo-stats-row" id="jo-stats-row"></div>

    <!-- SPLIT VIEW -->
    <div class="jobs-split" id="jo-split">
      <div class="jobs-list-col">
        <div class="jobs-list" id="jo-list"></div>
        <div class="pagination" id="jo-pagination"></div>
        <div class="jo-page-count" id="jo-page-count"></div>
      </div>
      <div class="job-detail-panel" id="jo-detail">
        <div class="job-detail-empty">Select a job to see details.</div>
      </div>
    </div>

    <!-- ACTIVITY LOG -->
    <div class="cr-card cr-log-panel" id="jo-log-panel" style="display:none">
      <h2 class="cr-section-title">
        Activity Log <span class="cr-pill" id="jo-log-count">0</span>
        <button class="cr-log-refresh" onclick="crLoadLogs('jo')" title="Refresh">&#8635;</button>
      </h2>
      <div class="cr-log-list" id="jo-log-list"></div>
    </div>
  </div>
</div>

<!-- SHARED EXPORT WIZARD — used by Job Odyssey, Applications, and Job
     Sites. Placed as a sibling of the .page divs (not nested inside any
     one of them) so it works regardless of which tab is active, matching
     the pattern already used for Career's own modals. -->
<div class="exp-overlay-bg" id="exp-overlay-bg" style="display:none" onclick="expClose()"></div>
<div class="exp-modal-overlay" id="exp-modal">
  <div class="exp-modal" onclick="event.stopPropagation()">
    <button class="exp-modal-x" onclick="expClose()">&times;</button>

    <div id="exp-step-choice" class="exp-step">
      <h3>Download <span id="exp-source-label"></span></h3>
      <div class="exp-choice-row">
        <button class="exp-choice-btn" onclick="expChooseCurrent()">
          <div class="exp-choice-title">Current</div>
          <div class="exp-choice-sub">Export everything matching the filters, search &amp; sort already applied on screen</div>
        </button>
        <button class="exp-choice-btn" onclick="expChooseNew()">
          <div class="exp-choice-title">New</div>
          <div class="exp-choice-sub">Choose fresh filters and a sort order for this export</div>
        </button>
      </div>
    </div>

    <div id="exp-step-filters" class="exp-step" style="display:none">
      <h3>Filters</h3>
      <div id="exp-filters-body"></div>
      <div class="exp-nav-row">
        <button class="exp-btn-secondary" onclick="expBackToChoice()">&#8592; Back</button>
        <button class="exp-btn-primary" onclick="expGoToColumns()">Next: Columns &#8594;</button>
      </div>
    </div>

    <div id="exp-step-columns" class="exp-step" style="display:none">
      <h3>Columns</h3>
      <label class="exp-col-all"><input type="checkbox" id="exp-col-all-cb" onchange="expToggleAllColumns(this)" checked> All columns</label>
      <div id="exp-columns-body" class="exp-columns-grid"></div>
      <div class="exp-nav-row">
        <button class="exp-btn-secondary" onclick="expBackFromColumns()">&#8592; Back</button>
        <button class="exp-btn-primary" onclick="expGoToFileType()">Next: File Type &#8594;</button>
      </div>
    </div>

    <div id="exp-step-filetype" class="exp-step" style="display:none">
      <h3>File Type</h3>
      <div class="exp-choice-row">
        <button class="exp-choice-btn" onclick="expDownload('csv')">
          <div class="exp-choice-title">CSV</div>
          <div class="exp-choice-sub">Plain comma-separated file, opens in any spreadsheet app</div>
        </button>
        <button class="exp-choice-btn" onclick="expDownload('xlsx')">
          <div class="exp-choice-title">XLSX</div>
          <div class="exp-choice-sub">Excel format with a frozen header row and color-coded status/stage rows</div>
        </button>
      </div>
      <div class="exp-nav-row">
        <button class="exp-btn-secondary" onclick="expBackFromFileType()">&#8592; Back</button>
        <span></span>
      </div>
    </div>

    <div id="exp-step-loading" class="exp-step" style="display:none">
      <div class="exp-loading">Preparing your file&#8230;</div>
    </div>
  </div>
</div>
'''


def build_jobodyssey_css():
    return '''
.jo-page-count { text-align: center; font-size: 12px; color: #888; margin-top: 6px; }
.jo-wrap { padding: 24px; max-width: 1500px; margin: 0 auto; }
.jo-top-row { display: flex; justify-content: flex-end; margin-bottom: 10px; }
.jo-filter-bar { display: flex; gap: 10px; flex-wrap: wrap; align-items: center; margin-bottom: 14px; }
.jo-filter-bar select, .jo-filter-bar input {
  padding: 8px 12px; border-radius: 8px; border: 1.5px solid #d0d3e8;
  font-size: 13px; background: #f5f6fa; outline: none;
}
.jo-filter-bar input[type="text"] { flex: 1; min-width: 200px; }
.jo-filter-bar select:focus, .jo-filter-bar input:focus { border-color: #3949ab; background: #fff; }
.jo-reload-btn {
  padding: 8px 16px; background: #3949ab; color: #fff; border: none;
  border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer;
}
.jo-reload-btn:hover { background: #283593; }

.jo-status-filter { position: relative; }
.jo-status-btn {
  padding: 8px 12px; border-radius: 8px; border: 1.5px solid #d0d3e8;
  font-size: 13px; background: #f5f6fa; cursor: pointer; white-space: nowrap;
}
.jo-status-btn:hover { border-color: #3949ab; }
.jo-status-panel {
  position: absolute; top: calc(100% + 6px); left: 0; z-index: 50;
  background: #fff; border: 1.5px solid #d0d3e8; border-radius: 10px;
  padding: 10px 14px; min-width: 190px; box-shadow: 0 6px 18px rgba(0,0,0,0.12);
}
.jo-status-panel label {
  display: flex; align-items: center; gap: 6px; font-size: 13px;
  padding: 4px 0; cursor: pointer; white-space: nowrap;
}
.jo-status-op {
  margin-top: 6px; padding-top: 8px; border-top: 1px solid #eceff1;
}
.jo-status-op label { font-size: 12px; color: #555; }
.jo-status-clear {
  margin-top: 8px; width: 100%; padding: 5px 0; background: #eceff1; color: #444;
  border: none; border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer;
}
.jo-status-clear:hover { background: #dfe3e8; }

.jo-stats-row {
  display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 16px;
  background: #fff; border-radius: 12px; border: 1px solid #e4e6f0; padding: 14px 18px;
}
.jo-stat { text-align: center; min-width: 90px; flex: 1; }
.jo-stat .sv { font-size: 20px; font-weight: 700; color: #2c3e50; }
.jo-stat .sl { font-size: 10px; color: #888; margin-top: 2px; text-transform: uppercase; letter-spacing: 0.03em; }
.jo-stat.total .sv { color: #3949ab; }
.jo-stat.scraped .sv { color: #607d8b; }
.jo-stat.applied .sv { color: #6a1b9a; }
.jo-stat.ineligible .sv { color: #c62828; }
.jo-stat.blacklist .sv { color: #4e342e; }
.jo-stat.eligible .sv { color: #2e7d32; }
.jo-stat.hold .sv { color: #f57f17; }

.jo-card-title { font-size: 14px; font-weight: bold; color: #2c3e50; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.jo-card-sub { font-size: 12px; color: #777; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-top: 2px; }
.jo-card-badges { display: flex; gap: 4px; margin-top: 6px; flex-wrap: wrap; }
.jo-badge { display: inline-block; padding: 2px 8px; border-radius: 20px; font-size: 10px; font-weight: 700; }
.jo-badge-portal { background: #fff3e0; color: #e65100; }
.jo-badge-valid { background: #e8f5e9; color: #2e7d32; }
.jo-badge-internal { background: #e3f2fd; color: #1565c0; }
.jo-badge-external { background: #fce4ec; color: #ad1457; }
.jo-badge-others { background: #eceff1; color: #607d8b; }
.jo-badge-duplicate { background: #fff8e1; color: #f57f17; border: 1px dashed #ffca28; }
.jo-badge-defect { background: #ffebee; color: #c62828; }
.jo-badge-status-scraped { background: #eceff1; color: #607d8b; }
.jo-badge-status-applied { background: #f3e5f5; color: #6a1b9a; }
.jo-badge-status-ineligible { background: #ffebee; color: #c62828; }
.jo-badge-status-blacklist { background: #efebe9; color: #4e342e; }
.jo-badge-status-eligible { background: #e8f5e9; color: #2e7d32; }
.jo-badge-status-hold { background: #fff3e0; color: #f57f17; }

.jo-detail-badges { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 12px; }
.jo-act-btn {
  padding: 6px 14px; border: none; border-radius: 6px; cursor: pointer;
  font-size: 12px; font-weight: 600; margin-right: 6px; margin-bottom: 6px;
}
.jo-act-view { background: #2196f3; color: #fff; text-decoration: none; display: inline-block; }
.jo-act-eligible { background: #4caf50; color: #fff; }
.jo-act-hold { background: #ff9800; color: #fff; }
.jo-act-ineligible { background: #f44336; color: #fff; }
.jo-act-applied { background: #9b59b6; color: #fff; }

.jo-undo-bar {
  display: none; position: sticky; top: 0; z-index: 999; background: #2c3e50; color: white;
  padding: 10px 20px; align-items: center; gap: 14px; font-size: 13px; border-radius: 10px; margin-bottom: 12px;
}
.jo-undo-bar button { padding: 5px 16px; background: #3949ab; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 12px; font-weight: bold; }

/* ── Shared Export Wizard (Job Odyssey, Applications, Job Sites) ── */
.exp-overlay-bg { position: fixed; inset: 0; background: rgba(0,0,0,0.35); z-index: 1200; }
.exp-modal-overlay {
  position: fixed; inset: 0; z-index: 1201; display: none;
  align-items: center; justify-content: center;
}
.exp-modal-overlay.exp-open { display: flex; }
.exp-modal {
  background: #fff; border-radius: 14px; padding: 24px 28px; width: 480px;
  max-width: 92vw; max-height: 85vh; overflow-y: auto; position: relative;
  box-shadow: 0 12px 40px rgba(0,0,0,0.25);
}
.exp-modal-x {
  position: absolute; top: 12px; right: 14px; background: none; border: none;
  font-size: 22px; line-height: 1; cursor: pointer; color: #888;
}
.exp-modal-x:hover { color: #333; }
.exp-modal h3 { margin: 0 0 16px; font-size: 17px; color: #222; }
.exp-choice-row { display: flex; gap: 12px; }
.exp-choice-btn {
  flex: 1; padding: 16px; border: 1.5px solid #d0d3e8; border-radius: 10px;
  background: #f5f6fa; cursor: pointer; text-align: left; transition: all 0.15s;
}
.exp-choice-btn:hover { border-color: #3949ab; background: #eef0fb; }
.exp-choice-title { font-weight: 700; font-size: 14px; color: #3949ab; margin-bottom: 4px; }
.exp-choice-sub { font-size: 12px; color: #666; line-height: 1.4; }
.exp-filter-group { margin-bottom: 16px; }
.exp-filter-label { display: block; font-size: 12px; font-weight: 700; color: #555; margin-bottom: 6px; }
.exp-filter-group select {
  width: 100%; padding: 7px 10px; border-radius: 8px; border: 1.5px solid #d0d3e8;
  font-size: 13px; background: #f5f6fa;
}
.exp-status-checks { display: flex; flex-wrap: wrap; gap: 5px 14px; }
.exp-status-checks label { font-size: 13px; display: flex; align-items: center; gap: 5px; white-space: nowrap; }
.exp-status-op { margin-top: 8px; display: flex; gap: 16px; }
.exp-status-op label { font-size: 12px; color: #555; }
.exp-col-all { display: block; font-size: 13px; font-weight: 700; margin-bottom: 10px; padding-bottom: 10px; border-bottom: 1px solid #eceff1; }
.exp-columns-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 6px 12px; max-height: 260px; overflow-y: auto; }
.exp-col-item { font-size: 13px; display: flex; align-items: center; gap: 6px; }
.exp-nav-row { display: flex; justify-content: space-between; margin-top: 20px; }
.exp-btn-primary {
  padding: 8px 18px; background: #3949ab; color: #fff; border: none;
  border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer;
}
.exp-btn-primary:hover { background: #283593; }
.exp-btn-secondary {
  padding: 8px 18px; background: #eceff1; color: #444; border: none;
  border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer;
}
.exp-btn-secondary:hover { background: #dfe3e8; }
.exp-loading { text-align: center; padding: 30px 0; color: #555; font-size: 14px; }
'''


def build_jobodyssey_js():
    return '''
// ── Job Odyssey state ──
var joJobs = [];

function joStatusLabel(status) {
  var labels = {scraped:'Scraped', applied:'Applied', ineligible:'Ineligible', blacklist:'Blacklist', eligible:'Eligible', hold:'Hold'};
  return labels[status] || status;
}
function joLinkTypeInfo(linkType) {
  if (linkType === 'internal') return ['Internal', 'jo-badge-internal'];
  if (linkType === 'external') return ['External', 'jo-badge-external'];
  return ['Others', 'jo-badge-others'];
}
var joSelectedId = null;
var joPage = 1;
var joTotalJobs = 0;
var JO_PAGE_SIZE = 20;
var joDebounceTimer = null;
var joLastAction = null; // {jobId, prevStatus, label} — for undo
var joStatusValues = []; // selected status checkboxes
var joStatusOp = 'or';   // 'or' = any of these, 'not' = none of these

function joDebouncedLoad() {
  clearTimeout(joDebounceTimer);
  joDebounceTimer = setTimeout(joLoad, 300);
}

function joToggleStatusPanel(e) {
  if (e) e.stopPropagation();
  var panel = document.getElementById('jo-status-panel');
  panel.style.display = (panel.style.display === 'none') ? 'block' : 'none';
}
document.addEventListener('click', function(e){
  var wrap = document.getElementById('jo-status-filter');
  if (wrap && !wrap.contains(e.target)) {
    document.getElementById('jo-status-panel').style.display = 'none';
  }
});

function joOnStatusChange() {
  var panel = document.getElementById('jo-status-panel');
  joStatusValues = Array.prototype.slice.call(panel.querySelectorAll('input[type=checkbox]:checked')).map(function(c){ return c.value; });
  var opEl = panel.querySelector('input[name="jo-status-op"]:checked');
  joStatusOp = opEl ? opEl.value : 'or';
  joUpdateStatusLabel();
  joLoad();
}

function joClearStatusFilter() {
  var panel = document.getElementById('jo-status-panel');
  panel.querySelectorAll('input[type=checkbox]').forEach(function(c){ c.checked = false; });
  panel.querySelector('input[name="jo-status-op"][value="or"]').checked = true;
  joStatusValues = [];
  joStatusOp = 'or';
  joUpdateStatusLabel();
  joPage = 1;
  joLoad();
}

function joUpdateStatusLabel() {
  var btn = document.getElementById('jo-status-btn');
  if (!joStatusValues.length) { btn.textContent = 'Status: All \u25be'; return; }
  var names = joStatusValues.map(joStatusLabel).join(', ');
  var opLabel = (joStatusOp === 'not') ? 'NOT' : 'OR';
  btn.textContent = 'Status: ' + names + ' (' + opLabel + ') \u25be';
}

function joLoad() {
  var portal      = document.getElementById('jo-filter-portal').value;
  var location    = document.getElementById('jo-filter-location').value;
  var search      = document.getElementById('jo-search').value;
  var sort        = document.getElementById('jo-sort').value;
  var validation  = document.getElementById('jo-filter-validation').value;
  var linkType    = document.getElementById('jo-filter-linktype').value;

  var qs = new URLSearchParams({status:joStatusValues.join(','), statusOp:joStatusOp, portal:portal, location:location, search:search, sort:sort, validation:validation, linkType:linkType, page:joPage, pageSize:JO_PAGE_SIZE});
  fetch('/api/jobodyssey-load?'+qs.toString())
    .then(function(r){ return r.json(); })
    .then(function(d){
      joJobs = d.jobs || [];
      joTotalJobs = d.total || 0;
      joRenderStats(d.stats || {});
      joRenderFilterOptions(d.filterOptions || {portals:[], locations:[]});
      joRenderList();
    })
    .catch(function(){});
}

function joRenderStats(s) {
  var el = document.getElementById('jo-stats-row');
  if (!el) return;
  el.innerHTML =
    '<div class="jo-stat total"><div class="sv">'+(s.total||0)+'</div><div class="sl">Total Jobs</div></div>'+
    '<div class="jo-stat scraped"><div class="sv">'+(s.scraped||0)+'</div><div class="sl">Scraped</div></div>'+
    '<div class="jo-stat applied"><div class="sv">'+(s.applied||0)+'</div><div class="sl">Applied</div></div>'+
    '<div class="jo-stat ineligible"><div class="sv">'+(s.ineligible||0)+'</div><div class="sl">Ineligible</div></div>'+
    '<div class="jo-stat blacklist"><div class="sv">'+(s.blacklist||0)+'</div><div class="sl">Blacklist</div></div>'+
    '<div class="jo-stat eligible"><div class="sv">'+(s.eligible||0)+'</div><div class="sl">Eligible</div></div>'+
    '<div class="jo-stat hold"><div class="sv">'+(s.hold||0)+'</div><div class="sl">Hold</div></div>';
}

function joRenderFilterOptions(opts) {
  var portalSel = document.getElementById('jo-filter-portal');
  var locSel    = document.getElementById('jo-filter-location');
  var curPortal = portalSel.value, curLoc = locSel.value;
  portalSel.innerHTML = '<option value="">Portals: All</option>' +
    (opts.portals||[]).map(function(p){ return '<option value="'+crEsc(p)+'">'+crEsc(p)+'</option>'; }).join('');
  locSel.innerHTML = '<option value="">Location: All</option>' +
    (opts.locations||[]).map(function(l){ return '<option value="'+crEsc(l)+'">'+crEsc(l)+'</option>'; }).join('');
  portalSel.value = curPortal; locSel.value = curLoc;
}

function shortId(id) {
  if (!id) return '';
  return id.length > 10 ? id.slice(0, 10) + '..' : id;
}

function joRenderList() {
  var listEl = document.getElementById('jo-list');
  var pagerEl = document.getElementById('jo-pagination');
  if (!joJobs.length) {
    listEl.innerHTML = '<div class="cr-empty"><div class="cr-empty-icon">&#128203;</div>No jobs found.</div>';
    pagerEl.innerHTML = '';
    document.getElementById('jo-page-count').textContent = '';
    joRenderDetail(null);
    return;
  }
  var totalPages = Math.max(1, Math.ceil(joTotalJobs / JO_PAGE_SIZE));
  if (joPage > totalPages) joPage = totalPages;
  if (joPage < 1) joPage = 1;
  var pageJobs = joJobs; // server already returns exactly this page's rows

  listEl.innerHTML = pageJobs.map(function(j){
    var sel = (j.id === joSelectedId) ? ' selected' : '';
    return '<div class="job-row'+sel+'" onclick="joSelect('+j.id+')">'+
      '<div class="jo-card-title">'+crEsc(j.title)+'</div>'+
      '<div class="jo-card-sub">'+crEsc(j.company)+' &middot; '+crEsc(j.location)+'</div>'+
      '<div class="jo-card-badges">'+
        '<span class="jo-badge jo-badge-portal">'+crEsc(j.portal)+'</span>'+
        '<span class="jo-badge '+(j.validation==='defect'?'jo-badge-defect':'jo-badge-valid')+'">'+crEsc(j.validation)+'</span>'+
        '<span class="jo-badge jo-badge-status-'+j.status+'">'+joStatusLabel(j.status)+'</span>'+
        (function(){ var lt=joLinkTypeInfo(j.link_type); return '<span class="jo-badge '+lt[1]+'">'+lt[0]+'</span>'; })()+
        (j.is_duplicate ? '<span class="jo-badge jo-badge-duplicate">Duplicate</span>' : '')+
      '</div></div>';
  }).join('');

  renderPagination('jo-pagination', joPage, totalPages, function(p){ joPage = p; joLoad(); });

  var startIdx = (joPage - 1) * JO_PAGE_SIZE + 1;
  var endIdx = Math.min(joPage * JO_PAGE_SIZE, joTotalJobs);
  document.getElementById('jo-page-count').textContent =
    'Showing ' + startIdx + '\u2013' + endIdx + ' of ' + joTotalJobs + ' jobs';

  // auto-select first card if nothing selected or previous selection no longer visible
  var stillVisible = pageJobs.some(function(j){ return j.id === joSelectedId; });
  if (!stillVisible) {
    joSelectedId = pageJobs.length ? pageJobs[0].id : null;
    // re-mark selected row — the HTML above was rendered before this
    // auto-select decision, so the previously-written 'selected' class
    // may now be on the wrong row (or no row at all)
    var rows = listEl.querySelectorAll('.job-row');
    rows.forEach(function(r, i){ r.classList.toggle('selected', pageJobs[i] && pageJobs[i].id === joSelectedId); });
  }
  if (joSelectedId !== null) {
    joFetchAndRenderDetail(joSelectedId);
  } else {
    joRenderDetail(null);
  }
}

function joFetchAndRenderDetail(id) {
  // description isn't included in the list payload anymore (kept out to
  // shrink list-load size), so the detail panel fetches the full row
  // on demand for just the one job currently selected.
  fetch('/api/jobodyssey-job-detail?id='+id)
    .then(function(r){ return r.json(); })
    .then(function(d){
      if (d.ok && joSelectedId === id) joRenderDetail(d.job);
    })
    .catch(function(){});
}

function joSelect(id) {
  joSelectedId = id;
  document.querySelectorAll('#jo-list .job-row').forEach(function(r){ r.classList.remove('selected'); });
  var idx = joJobs.findIndex(function(j){ return j.id===id; });
  var rows = document.querySelectorAll('#jo-list .job-row');
  if (rows[idx]) rows[idx].classList.add('selected');
  joFetchAndRenderDetail(id);
}

function joRenderDetail(j) {
  var panel = document.getElementById('jo-detail');
  if (!j) { panel.innerHTML = '<div class="job-detail-empty">Select a job to see details.</div>'; return; }
  panel.innerHTML =
    '<div class="job-detail-title">'+crEsc(j.title)+'</div>'+
    '<div class="job-detail-meta">&#127970; '+crEsc(j.company)+
      ' &nbsp;|&nbsp; &#128205; '+crEsc(j.location)+' &nbsp;|&nbsp; ID: '+crEsc(shortId(j.raw_id))+'</div>'+
    '<div class="jo-detail-badges">'+
      '<span class="jo-badge jo-badge-portal">'+crEsc(j.portal)+'</span>'+
      '<span class="jo-badge '+(j.validation==='defect'?'jo-badge-defect':'jo-badge-valid')+'">'+crEsc(j.validation)+'</span>'+
      '<span class="jo-badge jo-badge-status-'+j.status+'">'+joStatusLabel(j.status)+'</span>'+
      (function(){ var lt=joLinkTypeInfo(j.link_type); return '<span class="jo-badge '+lt[1]+'">'+lt[0]+'</span>'; })()+
      (j.is_duplicate ? '<span class="jo-badge jo-badge-duplicate">Duplicate</span>' : '')+
    '</div>'+
    '<div class="actions">'+
      '<a class="jo-act-btn jo-act-view" href="'+crEsc(j.link)+'" target="_blank">&#128065; View</a>'+
      '<button class="jo-act-btn jo-act-eligible" onclick="joSetStatus('+j.id+',\\'eligible\\')">&#10003; Eligible</button>'+
      '<button class="jo-act-btn jo-act-hold" onclick="joSetStatus('+j.id+',\\'hold\\')">&#9208; Hold</button>'+
      '<button class="jo-act-btn jo-act-ineligible" onclick="joSetStatus('+j.id+',\\'ineligible\\')">&#10007; Ineligible</button>'+
      '<button class="jo-act-btn jo-act-applied" onclick="joMarkApplied('+j.id+')">&#128188; Applied</button>'+
    '</div>'+
    '<div class="job-detail-desc-label">Description</div>'+
    '<div class="job-detail-desc">'+crEsc(j.description)+'</div>';
}

function joSetStatus(id, status) {
  var job = joJobs.find(function(j){ return j.id === id; });
  if (!job) return;
  var prevStatus = job.status;
  fetch('/api/jobodyssey-status', {
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({id:id, status:status})
  }).then(function(){
    job.status = status;
    joLastAction = {jobId:id, prevStatus:prevStatus, label: crEsc(job.company)+' — '+crEsc(job.title)+' moved to '+status};
    joShowUndo(joLastAction.label);
    crSendLog('jo', 'JobOdyssey', crEsc(job.company)+' — '+crEsc(job.title)+' marked '+status);
    joLoad();
  }).catch(function(){});
}

function joMarkApplied(id) {
  var job = joJobs.find(function(j){ return j.id === id; });
  if (!job) return;
  joSetStatus(id, 'applied');

  var today = new Date().toISOString().slice(0, 10);

  crOpenAppModalPrefill({
    company:  job.company,
    role:     job.title,
    location: job.location,
    date:     today
  });
}

function joShowUndo(text) {
  var bar = document.getElementById('jo-undo-bar');
  document.getElementById('jo-undo-text').textContent = text;
  bar.style.display = 'flex';
  clearTimeout(window.joUndoTimer);
  window.joUndoTimer = setTimeout(function(){ bar.style.display = 'none'; joLastAction = null; }, 6000);
}

function joUndo() {
  if (!joLastAction) return;
  fetch('/api/jobodyssey-status', {
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({id:joLastAction.jobId, status:joLastAction.prevStatus})
  }).then(function(){
    crSendLog('jo', 'JobOdyssey', 'Undo: reverted job '+joLastAction.jobId+' to '+joLastAction.prevStatus);
    document.getElementById('jo-undo-bar').style.display = 'none';
    joLastAction = null;
    joLoad();
  }).catch(function(){});
}

// ─────────────────────────────────────────────────────────────────────────
// SHARED EXPORT WIZARD — generic core, reused by Job Odyssey, Applications,
// and Job Sites. Defined here (loaded first in the concatenated <script>
// block) so build_career_js()'s adapter functions can call it too; plain
// function declarations are hoisted within the same script, so load order
// between the two files doesn't actually matter, but this keeps the
// generic core and its first consumer (Job Odyssey) next to each other.
//
// A "source" registers itself via one of the openXxxExport() calls below,
// passing an EXP config object:
//   title            - shown in the modal header
//   columns          - [{key, label}, ...] in the locked, confirmed order
//   filename         - base filename (no extension) for the download
//   getCurrentRows() - returns a Promise<rows> for whatever is on screen
//                      right now (filters + search + sort), ALL matching
//                      rows, ignoring pagination
//   renderNewFilters(containerEl) - renders the "New" filter+sort UI for
//                      this source into containerEl
//   getNewRows()     - reads whatever renderNewFilters() built and returns
//                      a Promise<rows> for that fresh filter selection
// Rows are plain objects keyed by each column's `key`.
// ─────────────────────────────────────────────────────────────────────────
var EXP = null;

function expOpen(cfg) {
  EXP = cfg;
  EXP.mode = cfg.skipChoice ? 'new' : null;
  EXP.selectedColumns = cfg.columns.map(function(c){ return c.key; });
  document.getElementById('exp-source-label').textContent = cfg.title;
  document.getElementById('exp-overlay-bg').style.display = 'block';
  document.getElementById('exp-modal').classList.add('exp-open');
  if (cfg.skipChoice) {
    // No real filters exist for this source — skip the Current/New screen
    // entirely and go straight to whatever renderNewFilters() offers
    // (e.g. just a sort choice for Job Sites).
    var body = document.getElementById('exp-filters-body');
    body.innerHTML = '';
    cfg.renderNewFilters(body);
    expShowStep('filters');
  } else {
    expShowStep('choice');
  }
}

function expClose() {
  document.getElementById('exp-modal').classList.remove('exp-open');
  document.getElementById('exp-overlay-bg').style.display = 'none';
}

function expShowStep(name) {
  ['choice','filters','columns','filetype','loading'].forEach(function(s){
    document.getElementById('exp-step-'+s).style.display = (s===name) ? 'block' : 'none';
  });
}

function expChooseCurrent() {
  EXP.mode = 'current';
  expShowStep('columns');
  expRenderColumns();
}

function expChooseNew() {
  EXP.mode = 'new';
  var body = document.getElementById('exp-filters-body');
  body.innerHTML = '';
  EXP.renderNewFilters(body);
  expShowStep('filters');
}

function expBackToChoice() {
  // Sources with no real filters (skipChoice) never had a Choice step to
  // return to — Back from their filters screen just closes the wizard.
  if (EXP.skipChoice) { expClose(); return; }
  expShowStep('choice');
}

function expGoToColumns() {
  expShowStep('columns');
  expRenderColumns();
}

function expBackFromColumns() {
  expShowStep(EXP.mode === 'current' ? 'choice' : 'filters');
}

function expGoToFileType() {
  if (!EXP.selectedColumns.length) { alert('Pick at least one column to export.'); return; }
  expShowStep('filetype');
}

function expBackFromFileType() { expShowStep('columns'); }

function expRenderColumns() {
  var body = document.getElementById('exp-columns-body');
  body.innerHTML = EXP.columns.map(function(c){
    var checked = EXP.selectedColumns.indexOf(c.key) !== -1 ? 'checked' : '';
    return '<label class="exp-col-item"><input type="checkbox" value="'+c.key+'" '+checked+' onchange="expOnColToggle()"> '+c.label+'</label>';
  }).join('');
  document.getElementById('exp-col-all-cb').checked = (EXP.selectedColumns.length === EXP.columns.length);
}

function expOnColToggle() {
  var boxes = Array.prototype.slice.call(document.querySelectorAll('#exp-columns-body input[type=checkbox]'));
  EXP.selectedColumns = boxes.filter(function(b){ return b.checked; }).map(function(b){ return b.value; });
  document.getElementById('exp-col-all-cb').checked = (EXP.selectedColumns.length === EXP.columns.length);
}

function expToggleAllColumns(cb) {
  var boxes = document.querySelectorAll('#exp-columns-body input[type=checkbox]');
  boxes.forEach(function(b){ b.checked = cb.checked; });
  EXP.selectedColumns = cb.checked ? EXP.columns.map(function(c){ return c.key; }) : [];
}

function expDownload(fmt) {
  if (!EXP.selectedColumns.length) { alert('Pick at least one column to export.'); return; }
  expShowStep('loading');
  var rowsPromise = (EXP.mode === 'current') ? EXP.getCurrentRows() : EXP.getNewRows();
  var colsMeta = EXP.selectedColumns.map(function(key){
    var col = EXP.columns.find(function(c){ return c.key === key; });
    return {key: key, label: col ? col.label : key};
  });
  var filename = EXP.filename;
  rowsPromise.then(function(rows){
    return fetch('/api/export-file', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({rows: rows, columns: colsMeta, filename: filename, format: fmt})
    });
  }).then(function(r){
    if (!r.ok) throw new Error('export failed');
    return r.blob();
  }).then(function(blob){
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url; a.download = filename + '.' + fmt;
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
    URL.revokeObjectURL(url);
    expClose();
  }).catch(function(){
    alert('Export failed — please try again.');
    expShowStep('filetype');
  });
}

// ── Job Odyssey export adapter ──
var JO_EXPORT_COLUMNS = [
  {key:'title',           label:'Title'},
  {key:'company',         label:'Company'},
  {key:'location',        label:'Location'},
  {key:'status',          label:'Status'},
  {key:'portal',          label:'Portal'},
  {key:'link',            label:'Link'},
  {key:'posted_date',     label:'Posted Date'},
  {key:'keyword',         label:'Keyword'},
  {key:'search_location', label:'Search Location'},
  {key:'validation',      label:'Validation'},
  {key:'is_duplicate',    label:'Duplicate'},
  {key:'link_type',       label:'Link Type'}
];

function joOpenExport() {
  expOpen({
    title: 'Job Odyssey',
    columns: JO_EXPORT_COLUMNS,
    filename: 'job_odyssey_export',
    getCurrentRows: joExpGetCurrentRows,
    renderNewFilters: joExpRenderFilters,
    getNewRows: joExpGetNewRows
  });
}

function joFetchExportRows(statusVals, statusOp, portal, location, search, sort, validation, linkType) {
  var qs = new URLSearchParams({
    status: statusVals.join(','), statusOp: statusOp, portal: portal, location: location,
    search: search, sort: sort, validation: validation, linkType: linkType
  });
  return fetch('/api/jobodyssey-export?'+qs.toString())
    .then(function(r){ return r.json(); })
    .then(function(d){ return d.jobs || []; });
}

function joExpGetCurrentRows() {
  return joFetchExportRows(
    joStatusValues, joStatusOp,
    document.getElementById('jo-filter-portal').value,
    document.getElementById('jo-filter-location').value,
    document.getElementById('jo-search').value,
    document.getElementById('jo-sort').value,
    document.getElementById('jo-filter-validation').value,
    document.getElementById('jo-filter-linktype').value
  );
}

function joExpRenderFilters(container) {
  var portalOpts = document.getElementById('jo-filter-portal').innerHTML;
  var locOpts    = document.getElementById('jo-filter-location').innerHTML;
  container.innerHTML =
    '<div class="exp-filter-group">' +
      '<label class="exp-filter-label">Status</label>' +
      '<div class="exp-status-checks">' +
        ['scraped','eligible','hold','ineligible','blacklist','applied'].map(function(s){
          return '<label><input type="checkbox" class="exp-jo-status" value="'+s+'"> '+joStatusLabel(s)+'</label>';
        }).join('') +
      '</div>' +
      '<div class="exp-status-op">' +
        '<label><input type="radio" name="exp-jo-status-op" value="or" checked> Any of these (OR)</label>' +
        '<label><input type="radio" name="exp-jo-status-op" value="not"> None of these (NOT)</label>' +
      '</div>' +
    '</div>' +
    '<div class="exp-filter-group"><label class="exp-filter-label">Portal</label><select id="exp-jo-portal">'+portalOpts+'</select></div>' +
    '<div class="exp-filter-group"><label class="exp-filter-label">Location</label><select id="exp-jo-location">'+locOpts+'</select></div>' +
    '<div class="exp-filter-group"><label class="exp-filter-label">Validation</label><select id="exp-jo-validation">' +
      '<option value="">All</option><option value="valid">Valid</option><option value="defect">Defect</option>' +
    '</select></div>' +
    '<div class="exp-filter-group"><label class="exp-filter-label">Type</label><select id="exp-jo-linktype">' +
      '<option value="">All</option><option value="internal">Internal</option><option value="external">External</option><option value="others">Others</option>' +
    '</select></div>' +
    '<div class="exp-filter-group"><label class="exp-filter-label">Sort</label><select id="exp-jo-sort">' +
      '<option value="date_desc">Newest first</option><option value="date_asc">Oldest first</option>' +
      '<option value="title_asc">Title A&#8594;Z</option><option value="title_desc">Title Z&#8594;A</option>' +
      '<option value="company_asc">Company A&#8594;Z</option><option value="company_desc">Company Z&#8594;A</option>' +
    '</select></div>';
}

function joExpGetNewRows() {
  var statusVals = Array.prototype.slice.call(document.querySelectorAll('.exp-jo-status:checked')).map(function(c){ return c.value; });
  var opEl = document.querySelector('input[name="exp-jo-status-op"]:checked');
  var statusOp = opEl ? opEl.value : 'or';
  return joFetchExportRows(
    statusVals, statusOp,
    document.getElementById('exp-jo-portal').value,
    document.getElementById('exp-jo-location').value,
    '',
    document.getElementById('exp-jo-sort').value,
    document.getElementById('exp-jo-validation').value,
    document.getElementById('exp-jo-linktype').value
  );
}
'''
