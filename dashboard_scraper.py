"""
dashboard_scraper.py — Scraper Abyss tab
Request sub-tab: portal -> keyword -> location cascading selection with
select-all, editable tag lists, and submit gated on all three having at
least one selection. Workflow sub-tab is still a placeholder (next build
pass).
"""

from dashboard_ui import status_icons_json
import json

DEFAULT_KEYWORDS = [
    'Technical Support Engineer', 'Associate Cloud Engineer', 'Junior DevOps Engineer',
    'Cloud Operations Engineer', 'Cloud Administrator', 'L1 Support Engineer',
    'L2 Support Engineer', 'Cloud Support Engineer', 'Junior Cloud Support Engineer',
    'Service Desk Engineer'
]

DEFAULT_LOCATIONS = ['Chennai', 'Coimbatore', 'Bangalore']

DEFAULT_BLACKLIST = ['Senior', 'Lead', 'Principal', 'Staff', 'Manager', 'Walk In']


def build_scraper_html():
    return '''
<style>
''' + build_scraper_css() + '''
</style>
<div id="page-scraper" class="page">
  <div class="sa-wrap">
    <div class="cr-tab-bar">
      <button class="cr-tab-btn sa-active" onclick="saSwitchTab('request', this)">&#128301; Request</button>
      <button class="cr-tab-btn" onclick="saSwitchTab('workflow', this)">&#9881; Workflow</button>
      <button class="cr-tab-btn cr-log-btn" id="sa-log-toggle-btn" onclick="crToggleLogPanel('sa')">&#128220; Logs</button>
    </div>

    <div id="sa-tab-request" class="cr-tab-panel cr-panel-active">

      <div class="req-section">
        <h3>Engine <button class="sa-selectall-btn" onclick="saSelectAll('engine')">Select all</button></h3>
        <div class="scraper-options" id="sa-engine-options">
          <div class="scraper-option" data-engine="Scraper" onclick="saToggleEngine('Scraper')">&#128301; Scraper</div>
          <div class="scraper-option" data-engine="Descriptor" onclick="saToggleEngine('Descriptor')">&#128220; Descriptor</div>
        </div>
      </div>

      <div class="req-section">
        <h3>Portal <button class="sa-selectall-btn" onclick="saSelectAll('portal')">Select all</button></h3>
        <div class="scraper-options" id="sa-portal-options">
          <div class="scraper-option" data-portal="Adzuna" onclick="saTogglePortal('Adzuna')">&#127760; Adzuna</div>
          <div class="scraper-option" data-portal="JSearch" onclick="saTogglePortal('JSearch')">&#128269; JSearch</div>
          <div class="scraper-option" data-portal="JobsPipe" onclick="saTogglePortal('JobsPipe')">&#128225; JobsPipe</div>
        </div>
      </div>

      <div class="req-section" id="sa-keyword-section" style="display:none">
        <h3>Keywords <button class="sa-selectall-btn" onclick="saSelectAll('keyword')">Select all</button></h3>
        <div class="tag-list" id="sa-keyword-tags"></div>
        <div class="extra-input">
          <input type="text" id="sa-keyword-new" placeholder="Add a keyword&#8230;" onkeydown="if(event.key==='Enter')saAddKeyword()">
          <button onclick="saAddKeyword()">Add</button>
        </div>
      </div>

      <div class="req-section" id="sa-location-section" style="display:none">
        <h3>Location <button class="sa-selectall-btn" onclick="saSelectAll('location')">Select all</button></h3>
        <div class="tag-list" id="sa-location-tags"></div>
        <div class="extra-input">
          <input type="text" id="sa-location-new" placeholder="Add a location&#8230;" onkeydown="if(event.key==='Enter')saAddLocation()">
          <button onclick="saAddLocation()">Add</button>
        </div>
      </div>

      <div class="req-section" id="sa-blacklist-section" style="display:none">
        <h3>Blacklist <button class="sa-selectall-btn" onclick="saSelectAll('blacklist')">Select all</button></h3>
        <div class="tag-list" id="sa-blacklist-tags"></div>
        <div class="extra-input">
          <input type="text" id="sa-blacklist-new" placeholder="Add a blacklist keyword&#8230;" onkeydown="if(event.key==='Enter')saAddBlacklist()">
          <button onclick="saAddBlacklist()">Add</button>
        </div>
      </div>

      <div class="sa-request-actions">
        <button class="btn-submit" id="sa-submit-btn" disabled onclick="saSubmit()">Submit</button>
        <button class="sa-reset-btn" onclick="saReset()">Reset</button>
      </div>
    </div>

    <div id="sa-tab-workflow" class="cr-tab-panel">
      <div class="sa-wf-top-row">
        <div class="sa-wf-legend" id="sa-wf-legend"></div>
        <div class="sa-wf-controls">
          <button class="jo-reload-btn" onclick="saLoadWorkflows()">&#8635; Refresh</button>
          <label class="sa-auto-label"><input type="checkbox" id="sa-autorefresh" checked> Auto refresh</label>
        </div>
      </div>
      <div class="wf-table-wrap">
        <table>
          <thead><tr>
            <th>Status</th><th>Workflow ID</th><th>Portal</th><th>Type</th><th>Stage</th><th>Started</th><th>Updated</th>
          </tr></thead>
          <tbody id="sa-workflow-tbody"></tbody>
        </table>
      </div>
    </div>

    <!-- ACTIVITY LOG — shared by Request and Workflow sub-tabs -->
    <div class="cr-card cr-log-panel" id="sa-log-panel" style="display:none">
      <h2 class="cr-section-title">
        Activity Log <span class="cr-pill" id="sa-log-count">0</span>
        <button class="cr-log-refresh" onclick="crLoadLogs('sa')" title="Refresh">&#8635;</button>
      </h2>
      <div class="cr-log-list" id="sa-log-list"></div>
    </div>
  </div>
</div>
'''


def build_scraper_css():
    return '''
.sa-wrap { padding: 24px; max-width: 1200px; margin: 0 auto; }
.sa-selectall-btn {
  float: right; padding: 4px 12px; background: #eef0fb; border: 1px solid #d0d3e8;
  border-radius: 16px; font-size: 11px; font-weight: 600; color: #3949ab; cursor: pointer;
}
.sa-selectall-btn:hover { background: #3949ab; color: #fff; }
.sa-request-actions { display: flex; gap: 12px; align-items: center; margin-top: 6px; }
.sa-reset-btn {
  padding: 12px 28px; background: #fff; color: #555; border: 1.5px solid #d0d3e8;
  border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer;
}
.sa-reset-btn:hover { background: #f5f6fa; }
.sa-wf-top-row { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; margin-bottom: 14px; }
.sa-wf-legend { display: flex; gap: 14px; flex-wrap: wrap; font-size: 12px; background: #fff; border: 1px solid #e4e6f0; border-radius: 8px; padding: 8px 14px; }
.sa-wf-controls { display: flex; gap: 12px; align-items: center; }
.sa-auto-label { font-size: 13px; color: #555; display: flex; align-items: center; gap: 6px; }
.sa-desc-hint { font-size: 12px; color: #888; margin-top: 6px; }
.sa-status-badge { display: inline-flex; align-items: center; gap: 5px; padding: 3px 10px; border-radius: 20px; font-size: 12px; font-weight: 700; }
.badge-waiting { background: #e3f2fd; color: #1565c0; }
.badge-inprogress { background: #fff8e1; color: #f57f17; }
.badge-hold { background: #fff3e0; color: #e65100; }
.badge-failed { background: #ffebee; color: #c62828; }
.badge-cancelled { background: #eceff1; color: #607d8b; }
.badge-completed { background: #e8f5e9; color: #2e7d32; }
'''


def build_scraper_js():
    return '''
// ── Scraper Abyss — Request sub-tab state ──
var saEngines = ['Scraper', 'Descriptor'];
var saSelectedEngines = new Set();
var saPortals   = ['Adzuna', 'JSearch', 'JobsPipe'];
var saSelectedPortals   = new Set();
var saKeywords          = ''' + json.dumps(DEFAULT_KEYWORDS) + ''';
var saSelectedKeywords  = new Set();
var saLocations         = ''' + json.dumps(DEFAULT_LOCATIONS) + ''';
var saSelectedLocations = new Set();
var saBlacklist          = ''' + json.dumps(DEFAULT_BLACKLIST) + ''';
var saSelectedBlacklist  = new Set();

function saSwitchTab(id, btn) {
  document.querySelectorAll('#page-scraper .cr-tab-panel').forEach(function(p){ p.classList.remove('cr-panel-active'); });
  document.querySelectorAll('#page-scraper .cr-tab-btn:not(.cr-log-btn)').forEach(function(b){ b.classList.remove('sa-active'); });
  var panel = document.getElementById('sa-tab-'+id);
  if (panel) panel.classList.add('cr-panel-active');
  if (btn) btn.classList.add('sa-active');
  if (id === 'workflow') saLoadWorkflows();
}

// ── Workflow table ──
var SA_STATUS_BADGES = ''' + json.dumps({
    'waiting': ('Waiting', 'badge-waiting'), 'in_progress': ('In Progress', 'badge-inprogress'),
    'hold': ('Hold', 'badge-hold'), 'failed': ('Failed', 'badge-failed'),
    'cancelled': ('Cancelled', 'badge-cancelled'), 'completed': ('Completed', 'badge-completed')
}) + ''';
var SA_STATUS_ICON_SVG = ''' + status_icons_json() + ''';

function saRenderWfLegend() {
  var el = document.getElementById('sa-wf-legend');
  if (!el) return;
  var colors = {waiting:'#1565c0', in_progress:'#f57f17', hold:'#e65100', failed:'#c62828', cancelled:'#607d8b', completed:'#2e7d32'};
  var order = ['waiting','in_progress','hold','failed','cancelled','completed'];
  el.innerHTML = order.map(function(k){
    return '<span style="color:'+colors[k]+'">'+(SA_STATUS_ICON_SVG[k]||'')+' '+SA_STATUS_BADGES[k][0]+'</span>';
  }).join('');
}
saRenderWfLegend();
var saWfAutoTimer = null;

function saLoadWorkflows() {
  fetch('/api/workflow-list').then(function(r){ return r.json(); }).then(function(d){
    var tbody = document.getElementById('sa-workflow-tbody');
    var rows = d.workflows || [];
    if (!rows.length) {
      tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;color:#999;padding:20px;">No workflows yet.</td></tr>';
    } else {
      tbody.innerHTML = rows.map(function(w){
        var b = SA_STATUS_BADGES[w.status] || [w.status, ''];
        var icon = SA_STATUS_ICON_SVG[w.status] || '';
        return '<tr>'+
          '<td><span class="sa-status-badge '+b[1]+'">'+icon+' '+b[0]+'</span></td>'+
          '<td><a class="wf-id-link" href="/workflow-detail?id='+encodeURIComponent(w.workflow_id)+'">'+crEsc(w.workflow_id)+'</a></td>'+
          '<td>'+crEsc(w.portal)+'</td><td>'+crEsc(w.type)+'</td><td>'+crEsc(w.stage)+'</td>'+
          '<td>'+crEsc(w.started_at||'--')+'</td><td>'+crEsc(w.updated_at||'--')+'</td>'+
        '</tr>';
      }).join('');
    }
    var anyNonTerminal = rows.some(function(w){ return w.status !== 'completed' && w.status !== 'cancelled'; });
    clearTimeout(saWfAutoTimer);
    if (document.getElementById('sa-autorefresh').checked && anyNonTerminal) {
      saWfAutoTimer = setTimeout(saLoadWorkflows, 5000);
    }
  }).catch(function(){});
}

function saToggleEngine(name) {
  if (saSelectedEngines.has(name)) saSelectedEngines.delete(name);
  else saSelectedEngines.add(name);
  saRenderEngines();
  saUpdateSectionVisibility();
  saCheckSubmit();
}
function saRenderEngines() {
  document.querySelectorAll('#sa-engine-options .scraper-option').forEach(function(el){
    el.classList.toggle('selected', saSelectedEngines.has(el.dataset.engine));
  });
}

function saUpdateSectionVisibility() {
  var scraperOn = saSelectedEngines.has('Scraper');
  var descriptorOn = saSelectedEngines.has('Descriptor');
  var portalPicked = saSelectedPortals.size > 0;

  // Keyword only matters for Scraper.
  var needsKeyword = portalPicked && scraperOn;
  document.getElementById('sa-keyword-section').style.display = needsKeyword ? 'block' : 'none';
  if (needsKeyword) saRenderKeywords();

  // Location is shared by both engines now. Descriptor doesn't need a
  // keyword picked first — Scraper still does, since it chains keyword->location.
  var needsLocation = portalPicked && (descriptorOn || (scraperOn && saSelectedKeywords.size > 0));
  document.getElementById('sa-location-section').style.display = needsLocation ? 'block' : 'none';
  if (needsLocation) saRenderLocations();

  // Blacklist is Scraper-only and optional — shown once Location appears,
  // never required for Submit.
  document.getElementById('sa-blacklist-section').style.display = (needsLocation && scraperOn) ? 'block' : 'none';
  if (needsLocation && scraperOn) saRenderBlacklist();
}

function saTogglePortal(name) {
  if (saSelectedPortals.has(name)) saSelectedPortals.delete(name);
  else saSelectedPortals.add(name);
  saRenderPortals();
  saUpdateSectionVisibility();
  saCheckSubmit();
}
function saRenderPortals() {
  document.querySelectorAll('#sa-portal-options .scraper-option').forEach(function(el){
    el.classList.toggle('selected', saSelectedPortals.has(el.dataset.portal));
  });
}

function saRenderKeywords() {
  var wrap = document.getElementById('sa-keyword-tags');
  wrap.innerHTML = saKeywords.map(function(k){
    var sel = saSelectedKeywords.has(k) ? ' selected' : '';
    return '<span class="tag'+sel+'" onclick="saToggleKeyword(\\''+k.replace(/'/g,"\\\\'")+'\\')">'+crEsc(k)+
      '<button class="remove-btn" onclick="event.stopPropagation();saRemoveKeyword(\\''+k.replace(/'/g,"\\\\'")+'\\')">&times;</button></span>';
  }).join('');
}
function saToggleKeyword(k) {
  if (saSelectedKeywords.has(k)) saSelectedKeywords.delete(k);
  else saSelectedKeywords.add(k);
  saRenderKeywords();
  saUpdateSectionVisibility();
  saCheckSubmit();
}
function saRemoveKeyword(k) {
  saKeywords = saKeywords.filter(function(x){ return x !== k; });
  saSelectedKeywords.delete(k);
  saRenderKeywords();
  saCheckSubmit();
}
function saAddKeyword() {
  var input = document.getElementById('sa-keyword-new');
  var v = input.value.trim();
  if (!v || saKeywords.includes(v)) { input.value=''; return; }
  saKeywords.push(v);
  saSelectedKeywords.add(v);
  input.value = '';
  saRenderKeywords();
  saUpdateSectionVisibility();
  saCheckSubmit();
}

function saRenderLocations() {
  var wrap = document.getElementById('sa-location-tags');
  wrap.innerHTML = saLocations.map(function(l){
    var sel = saSelectedLocations.has(l) ? ' selected' : '';
    return '<span class="tag'+sel+'" onclick="saToggleLocation(\\''+l.replace(/'/g,"\\\\'")+'\\')">'+crEsc(l)+
      '<button class="remove-btn" onclick="event.stopPropagation();saRemoveLocation(\\''+l.replace(/'/g,"\\\\'")+'\\')">&times;</button></span>';
  }).join('');
}
function saToggleLocation(l) {
  if (saSelectedLocations.has(l)) saSelectedLocations.delete(l);
  else saSelectedLocations.add(l);
  saRenderLocations();
  saCheckSubmit();
}
function saRemoveLocation(l) {
  saLocations = saLocations.filter(function(x){ return x !== l; });
  saSelectedLocations.delete(l);
  saRenderLocations();
  saCheckSubmit();
}

function saRenderBlacklist() {
  var wrap = document.getElementById('sa-blacklist-tags');
  wrap.innerHTML = saBlacklist.map(function(l){
    var sel = saSelectedBlacklist.has(l) ? ' selected' : '';
    return '<span class="tag'+sel+'" onclick="saToggleBlacklist(\\''+l.replace(/'/g,"\\\\'")+'\\')">'+crEsc(l)+
      '<button class="remove-btn" onclick="event.stopPropagation();saRemoveBlacklist(\\''+l.replace(/'/g,"\\\\'")+'\\')">&times;</button></span>';
  }).join('');
}
function saToggleBlacklist(l) {
  if (saSelectedBlacklist.has(l)) saSelectedBlacklist.delete(l);
  else saSelectedBlacklist.add(l);
  saRenderBlacklist();
  saCheckSubmit();
}
function saRemoveBlacklist(l) {
  saBlacklist = saBlacklist.filter(function(x){ return x !== l; });
  saSelectedBlacklist.delete(l);
  saRenderBlacklist();
  saCheckSubmit();
}
function saAddBlacklist() {
  var input = document.getElementById('sa-blacklist-new');
  var v = input.value.trim();
  if (!v || saBlacklist.includes(v)) { input.value=''; return; }
  saBlacklist.push(v);
  saSelectedBlacklist.add(v);
  input.value = '';
  saRenderBlacklist();
  saCheckSubmit();
}
function saAddLocation() {
  var input = document.getElementById('sa-location-new');
  var v = input.value.trim();
  if (!v || saLocations.includes(v)) { input.value=''; return; }
  saLocations.push(v);
  saSelectedLocations.add(v);
  input.value = '';
  saRenderLocations();
  saCheckSubmit();
}

function saSelectAll(kind) {
  if (kind === 'engine') { saEngines.forEach(function(e){ saSelectedEngines.add(e); }); saRenderEngines(); saUpdateSectionVisibility(); }
  if (kind === 'portal') { saPortals.forEach(function(p){ saSelectedPortals.add(p); }); saRenderPortals(); saUpdateSectionVisibility(); }
  if (kind === 'keyword') { saKeywords.forEach(function(k){ saSelectedKeywords.add(k); }); saRenderKeywords(); saUpdateSectionVisibility(); }
  if (kind === 'location') { saLocations.forEach(function(l){ saSelectedLocations.add(l); }); saRenderLocations(); }
  if (kind === 'blacklist') { saBlacklist.forEach(function(l){ saSelectedBlacklist.add(l); }); saRenderBlacklist(); }
  saCheckSubmit();
}

function saCheckSubmit() {
  var scraperOn = saSelectedEngines.has('Scraper');
  var descriptorOn = saSelectedEngines.has('Descriptor');
  var ok = saSelectedEngines.size > 0 && saSelectedPortals.size > 0 &&
    (!scraperOn || saSelectedKeywords.size > 0) &&
    ((scraperOn || descriptorOn) ? saSelectedLocations.size > 0 : true);
  document.getElementById('sa-submit-btn').disabled = !ok;
}

function saReset() {
  saSelectedEngines.clear();
  saSelectedPortals.clear();
  saSelectedKeywords.clear();
  saSelectedLocations.clear();
  saSelectedBlacklist.clear();
  saRenderEngines();
  saRenderPortals();
  document.getElementById('sa-keyword-section').style.display = 'none';
  document.getElementById('sa-location-section').style.display = 'none';
  document.getElementById('sa-blacklist-section').style.display = 'none';
  saRenderKeywords();
  saRenderLocations();
  saRenderBlacklist();
  saCheckSubmit();
}

function saSubmit() {
  var payload = {
    engines: Array.from(saSelectedEngines),
    portals: saPortals.filter(function(p){ return saSelectedPortals.has(p); }),
    keywords: Array.from(saSelectedKeywords),
    locations: Array.from(saSelectedLocations),
    blacklist: Array.from(saSelectedBlacklist)
  };
  fetch('/api/scraper-submit', {
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify(payload)
  }).then(function(r){ return r.json(); }).then(function(d){
    crSendLog('sa', 'ScraperAbyss', 'Request submitted: '+payload.engines.join(',')+' engine(s) | '+
      payload.portals.join(',')+' | '+payload.keywords.length+' keywords | '+payload.locations.length+' locations | '+
      payload.blacklist.length+' blacklist keyword(s)');
    saReset();
  }).catch(function(){});
}

// initial render
saRenderEngines();
saRenderPortals();
'''
