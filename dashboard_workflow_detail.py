"""
dashboard_workflow_detail.py — Workflow Detail page (opens as its own page
when a Workflow ID is clicked in the Scraper Abyss Workflow table).
Three blocks: Details+Actions, Stages progress, Logs (search + headers).
"""

from dashboard_ui import html_page, esc, status_icons_json
import json

STATUS_BADGES = {
    'waiting':     ('Waiting', 'badge-waiting'),
    'in_progress': ('In Progress', 'badge-inprogress'),
    'hold':        ('Hold', 'badge-hold'),
    'failed':      ('Failed', 'badge-failed'),
    'cancelled':   ('Cancelled', 'badge-cancelled'),
    'completed':   ('Completed', 'badge-completed'),
}

STAGE_STATUS_ICON = {
    'not_started': 'not_started',
    'in_progress': 'in_progress',
    'completed':   'completed',
    'failed':      'failed',
}


def build_workflow_detail_page(workflow_id):
    body = '''
<div class="header">
  <h1>Workflow Detail — ''' + esc(workflow_id) + '''</h1>
  <a href="/scraper" style="color:white;text-decoration:none;font-size:13px;background:rgba(255,255,255,0.12);padding:8px 16px;border-radius:20px;">&#8592; Back to Scraper Abyss</a>
</div>
<div class="wfd-wrap" id="wfd-wrap" data-wfid="''' + esc(workflow_id) + '''">
  <div class="wfd-top-row">
    <button class="jo-reload-btn" onclick="wfdLoad()">&#8635; Refresh</button>
    <label class="wfd-auto-label">
      <input type="checkbox" id="wfd-autorefresh" checked> Auto refresh
    </label>
  </div>

  <div class="cr-card" id="wfd-details-block"></div>
  <div class="cr-card" id="wfd-stages-block"></div>

  <div class="cr-card" id="wfd-logs-block">
    <h2 class="cr-section-title">Logs <span class="cr-pill" id="wfd-log-count">0</span></h2>
    <input type="text" id="wfd-log-search" placeholder="Search logs&#8230;" oninput="wfdLoadLogs()" style="width:100%;padding:8px 12px;border-radius:8px;border:1.5px solid #d0d3e8;margin-bottom:10px;">
    <div class="wfd-log-headers">
      <span>Timestamp</span><span>Workflow ID</span><span>Message</span>
    </div>
    <div id="wfd-log-list"></div>
  </div>
</div>

<style>
''' + build_wfd_css() + '''
</style>
<script>
''' + build_wfd_js() + '''
</script>
'''
    return html_page('Workflow Detail — ' + workflow_id, body)


def build_wfd_css():
    return '''
.wfd-wrap { padding: 24px; }
.wfd-top-row { display: flex; gap: 16px; align-items: center; margin-bottom: 14px; }
.wfd-auto-label { font-size: 13px; color: #555; display: flex; align-items: center; gap: 6px; }
.cr-card { background: white; border-radius: 12px; box-shadow: 0 2px 5px rgba(0,0,0,0.08); padding: 18px 20px; margin-bottom: 16px; }
.wfd-badge { display: inline-flex; align-items: center; gap: 6px; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 700; background: #f0f0f5; }
.badge-waiting { background: #e3f2fd; color: #1565c0; }
.badge-inprogress { background: #fff8e1; color: #f57f17; }
.badge-hold { background: #fff3e0; color: #e65100; }
.badge-failed { background: #ffebee; color: #c62828; }
.badge-cancelled { background: #eceff1; color: #607d8b; }
.badge-completed { background: #e8f5e9; color: #2e7d32; }
.wfd-meta-grid { display: grid; grid-template-columns: repeat(auto-fit,minmax(140px,1fr)); gap: 10px; margin: 14px 0; }
.wfd-meta-item { background: #f7f8fc; border-radius: 8px; padding: 10px 12px; }
.wfd-meta-item .l { font-size: 11px; color: #888; text-transform: uppercase; }
.wfd-meta-item .v { font-size: 13px; color: #2c3e50; margin-top: 2px; font-weight: 600; }
.wfd-actions { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 10px; }
.wfd-act-btn { padding: 7px 16px; border: none; border-radius: 6px; font-size: 12px; font-weight: 700; cursor: pointer; color: #fff; }
.wfd-act-hold { background: #ff9800; }
.wfd-act-cancel { background: #f44336; }
.wfd-act-revoke { background: #b71c1c; }
.wfd-act-retry { background: #3949ab; }
.wfd-act-reset { background: #607d8b; }
.wfd-act-btn:disabled { background: #ccc; cursor: not-allowed; }
.wfd-stage-row { display: flex; flex-wrap: nowrap; align-items: center; justify-content: flex-start; gap: 0; margin-bottom: 28px; }
.wfd-stage-row.wfd-reversed { justify-content: flex-end; }
.wfd-stage-chip { flex: 0 0 auto; display: flex; align-items: center; gap: 5px; padding: 6px 12px; border-radius: 20px; font-size: 12px; border: 1px solid #e0e0e0; background: #f7f8fc; white-space: nowrap; }
.wfd-stage-chip.completed { background: linear-gradient(180deg, #eafaf0, #e0f5e6); border-color: #a5d6a7; color: #2e7d32; }
.wfd-stage-chip.in_progress { background: linear-gradient(180deg, #fffdf3, #fff3cf); border-color: #ffe082; color: #f57f17; font-weight: 700; }
.wfd-stage-chip.failed { background: linear-gradient(180deg, #fef2f2, #fde0e0); border-color: #ef9a9a; color: #c62828; }
.wfd-connector { flex: 1 1 16px; min-width: 16px; height: 6px; border-radius: 3px; position: relative; overflow: hidden; background: linear-gradient(180deg, #eceef5, #dcdfea); }
.wfd-row-sparse .wfd-connector { flex: 0 0 24px; }
.wfd-connector.completed { background: linear-gradient(180deg, #7bc47f, #4caf50); }
.wfd-connector.in_progress::after { content: ''; position: absolute; left: -30%; top: 0; width: 30%; height: 100%; background: linear-gradient(90deg, #ffca28, #ffa726); animation: wfdFlow 1.6s linear infinite; }
.wfd-connector.in_progress.wfd-flow-rev::after { left: auto; right: -30%; animation: wfdFlowRev 1.6s linear infinite; }
@keyframes wfdFlowRev { 100% { right: 120%; } }
#wfd-stages-block { overflow: hidden; }
#wfd-stage-canvas { position: relative; padding: 0 34px; box-sizing: border-box; }
.wfd-corner-svg { position: absolute; overflow: visible; pointer-events: none; }
.wfd-corner-svg path { stroke: #c3c8d6; fill: none; }
.wfd-corner-svg.completed path { stroke: #4caf50; }
.wfd-corner-svg.in_progress path { stroke: #ffa726; stroke-dasharray: 10 7; animation: wfdDash 0.9s linear infinite; }
@keyframes wfdDash { to { stroke-dashoffset: -34; } }
@keyframes wfdFlow { 100% { left: 120%; } }
@keyframes wfdFlowV { 100% { top: 120%; } }
.wfd-legend { display: flex; gap: 16px; background: #f7f8fc; border-radius: 8px; padding: 8px 14px; margin-top: 10px; font-size: 12px; flex-wrap: wrap; }
.wfd-log-headers { display: grid; grid-template-columns: 150px 180px 1fr; gap: 8px; padding: 6px 0; border-bottom: 1px solid #ddd; font-size: 11px; color: #888; text-transform: uppercase; }
.wfd-log-row { display: grid; grid-template-columns: 150px 180px 1fr; gap: 8px; padding: 7px 0; border-bottom: 1px solid #f0f0f0; font-size: 12px; font-family: monospace; }
'''


def build_wfd_js():
    return '''
var wfdId = document.getElementById('wfd-wrap').dataset.wfid;
var wfdAutoTimer = null;

var STATUS_BADGES = ''' + json.dumps(STATUS_BADGES) + ''';
var STAGE_ICON = ''' + json.dumps(STAGE_STATUS_ICON) + ''';
var STATUS_ICON_SVG = ''' + status_icons_json() + ''';

function esc(s){return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}

function wfdLoad() {
  fetch('/api/workflow-detail?id='+encodeURIComponent(wfdId))
    .then(function(r){ return r.json(); })
    .then(function(d){
      if (!d.ok) { document.getElementById('wfd-details-block').innerHTML = '<p>Workflow not found.</p>'; return; }
      wfdRenderDetails(d.workflow);
      wfdRenderStages(d.workflow);
      wfdScheduleAuto(d.workflow.status);
    }).catch(function(){});
  wfdLoadLogs();
}

function wfdRenderDetails(w) {
  var badge = STATUS_BADGES[w.status] || [w.status, ''];
  var icon = STATUS_ICON_SVG[w.status] || '';
  var el = document.getElementById('wfd-details-block');
  el.innerHTML =
    '<div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:10px;">'+
      '<div><div style="font-size:18px;font-weight:700;font-family:monospace;">'+esc(w.workflow_id)+'</div>'+
      '<div style="font-size:13px;color:#777;margin-top:2px;">'+esc(w.portal)+' &middot; '+(w.kind==='descriptor'?'Descriptor':'Scraping')+'</div></div>'+
      '<span class="wfd-badge '+badge[1]+'">'+icon+' '+badge[0]+'</span>'+
    '</div>'+
    '<div class="wfd-meta-grid">'+
      '<div class="wfd-meta-item"><div class="l">Started</div><div class="v">'+esc(w.started_at||'--')+'</div></div>'+
      '<div class="wfd-meta-item"><div class="l">Updated</div><div class="v">'+esc(w.updated_at||'--')+'</div></div>'+
      (w.kind==='descriptor'
        ? '<div class="wfd-meta-item"><div class="l">Depends On</div><div class="v">'+esc(w.depends_on||'None')+'</div></div>'
        : '<div class="wfd-meta-item"><div class="l">Keywords</div><div class="v">'+(w.keywords||[]).length+' selected</div></div>')+
      '<div class="wfd-meta-item"><div class="l">Locations</div><div class="v">'+(w.locations||[]).length+' selected</div></div>'+
    '</div>'+
    wfdRenderActions(w);
}

function wfdRenderActions(w) {
  var s = w.status;
  var buttons = '';
  if (s === 'waiting') {
    buttons = wfdBtn('cancel','Cancel');
  } else if (s === 'in_progress') {
    buttons = wfdBtn('hold','Hold') + wfdBtn('cancel','Cancel') + wfdBtn('revoke','Revoke');
  } else if (s === 'hold' || s === 'failed') {
    buttons = wfdBtn('retry','Retry') + wfdBtn('cancel','Cancel') + wfdBtn('revoke','Revoke') + wfdBtn('reset','Reset');
  } else {
    buttons = '<span style="color:#999;font-size:12px;">No actions available.</span>';
  }
  return '<div class="wfd-actions">'+buttons+'</div>';
}

function wfdBtn(action, label) {
  return '<button class="wfd-act-btn wfd-act-'+action+'" onclick="wfdConfirmAction(\\''+action+'\\')">'+label+'</button>';
}

var CONFIRM_TEXT = {
  hold:   'Hold this workflow? Scraper will finish the current cycle, save its position, and then stop.',
  retry:  'Retry this workflow from the last saved point?',
  cancel: 'Cancel this workflow? The process will stop immediately.',
  revoke: 'Force kill this workflow immediately? This will fail the workflow and lose the current stage\\'s progress (emergency stop).',
  reset:  'Reset this workflow? This clears all progress and moves it to Hold — press Retry afterward to start over.'
};

function wfdConfirmAction(action) {
  if (!confirm(CONFIRM_TEXT[action])) return;
  fetch('/api/workflow-action', {
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({workflow_id: wfdId, action: action})
  }).then(function(){ setTimeout(wfdLoad, 300); }).catch(function(){});
}

var wfdLastWorkflow = null;
var wfdRowSizeCache = {}; // workflow_id -> { containerWidth, sizes: [n, n, ...] }
var WFD_CONNECTOR_SPAN = 36; // connector width + gaps, used in width-packing math

function wfdChunk(arr, size) {
  var out = [];
  for (var i = 0; i < arr.length; i += size) out.push(arr.slice(i, i + size));
  return out;
}

// A pill's width depends on its status and (for fetch stages) its cycle
// progress text — e.g. gaining " (1/3)" the moment it starts running.
// This signature changes whenever any of that changes, so the row-packing
// cache below gets invalidated at exactly the moments a pill could have
// grown or shrunk — not just when the browser window resizes.
function wfdStagesSignature(stages) {
  return stages.map(function(s) {
    var extra = (s.type === 'fetch' && s.cycles_total) ? (s.cycles_done + '/' + s.cycles_total) : '';
    return s.status + ':' + extra;
  }).join('|');
}

// Packs stages into rows based on actually-measured chip widths so each
// row fills the available width instead of a guessed fixed count.
function wfdChunkByWidth(stages, containerWidth) {
  var measure = document.createElement('div');
  measure.style.cssText = 'position:absolute;visibility:hidden;white-space:nowrap;top:-9999px;left:-9999px;';
  measure.className = 'wfd-stage-row';
  document.body.appendChild(measure);

  var widths = stages.map(function(s, i) {
    var span = document.createElement('span');
    span.className = 'wfd-stage-chip ' + s.status;
    span.style.fontWeight = '400'; // never let in-progress bold skew the packing measurement
    var iconKey = STAGE_ICON[s.status] || 'not_started';
    var label = (s.type === 'fetch') ? s.stage_code : esc(s.name);
    var extra = (s.type === 'fetch' && s.cycles_total) ? ' ('+s.cycles_done+'/'+s.cycles_total+')' : '';
    span.innerHTML = (STATUS_ICON_SVG[iconKey]||'') + ' ' + label + extra;
    measure.appendChild(span);
    return span.offsetWidth;
  });
  document.body.removeChild(measure);

  var usable = Math.max(containerWidth - 68, 160); // minus canvas side padding

  var rows = [];
  var current = [];
  var currentWidth = 0;

  for (var i = 0; i < stages.length; i++) {
    var w = widths[i] + (current.length ? WFD_CONNECTOR_SPAN : 0);
    if (current.length && currentWidth + w > usable) {
      rows.push({ items: current, width: currentWidth });
      current = [];
      currentWidth = 0;
      w = widths[i];
    }
    current.push(stages[i]);
    currentWidth += w;
  }
  if (current.length) rows.push({ items: current, width: currentWidth });

  // Greedy left-to-right packing above wraps to a new row the moment one
  // chip doesn't fit — but that says nothing about whether the NEXT row's
  // first chip would still fit in the space left behind. Pull chips
  // backward whenever they do, so a row doesn't end early with visible
  // leftover space just because a later, wider chip happened to be next.
  for (var r = 0; r < rows.length - 1; r++) {
    while (rows[r + 1].items.length) {
      var nextStage = rows[r + 1].items[0];
      var nextIdx = stages.indexOf(nextStage);
      var nextW = widths[nextIdx] + WFD_CONNECTOR_SPAN;
      if (rows[r].width + nextW <= usable) {
        rows[r].items.push(rows[r + 1].items.shift());
        rows[r].width += nextW;
      } else {
        break;
      }
    }
  }

  return rows.filter(function(row) { return row.items.length > 0; })
             .map(function(row) { return row.items; });
}

function wfdConnStatus(stage) {
  if (stage.status === 'completed') return 'completed';
  if (stage.status === 'in_progress') return 'in_progress';
  return 'pending';
}

function wfdChip(s, globalIdx) {
  var iconKey = STAGE_ICON[s.status] || 'not_started';
  var icon = STATUS_ICON_SVG[iconKey] || '';
  var label = (s.type === 'fetch') ? s.stage_code : esc(s.name);
  var extra = (s.type === 'fetch' && s.cycles_total) ? ' ('+s.cycles_done+'/'+s.cycles_total+')' : '';
  return '<span id="wfd-chip-'+globalIdx+'" class="wfd-stage-chip '+s.status+'">'+icon+' '+label+extra+'</span>';
}

function wfdSliceBySizes(stages, sizes) {
  var rows = [];
  var idx = 0;
  sizes.forEach(function(n) { rows.push(stages.slice(idx, idx + n)); idx += n; });
  return rows;
}

function wfdRenderStages(w) {
  wfdLastWorkflow = w;
  var el = document.getElementById('wfd-stages-block');
  var stages = w.stages || [];
  var containerWidth = el.clientWidth || 1000;

  var cache = wfdRowSizeCache[w.workflow_id];
  var sig = wfdStagesSignature(stages);
  var rows;
  if (cache && cache.containerWidth === containerWidth && cache.sig === sig) {
    rows = wfdSliceBySizes(stages, cache.sizes);
  } else {
    rows = wfdChunkByWidth(stages, containerWidth);
    wfdRowSizeCache[w.workflow_id] = { containerWidth: containerWidth, sig: sig, sizes: rows.map(function(r){ return r.length; }) };
  }

  var rowsHtml = rows.map(function(rowStages, rowIdx) {
    var reversed = rowIdx % 2 === 1;
    var display = reversed ? rowStages.slice().reverse() : rowStages;
    var rowClass = 'wfd-stage-row' + (reversed ? ' wfd-reversed' : '') + (display.length <= 2 ? ' wfd-row-sparse' : '');
    return '<div class="' + rowClass + '">' + display.map(function(s, i) {
      var globalIdx = stages.indexOf(s);
      var chip = wfdChip(s, globalIdx);
      if (i === display.length - 1) return chip;
      var laterStage = reversed ? display[i] : display[i + 1];
      var connClass = wfdConnStatus(laterStage);
      return chip + '<span class="wfd-connector '+connClass+(reversed?' wfd-flow-rev':'')+'"></span>';
    }).join('') + '</div>';
  }).join('');

  el.innerHTML = '<div id="wfd-stage-canvas">' + rowsHtml + '</div>' +
    '<div class="wfd-legend">'+
      '<span style="color:#2e7d32">'+STATUS_ICON_SVG.completed+' Completed</span>'+
      '<span style="color:#f57f17">'+STATUS_ICON_SVG.in_progress+' In Progress</span>'+
      '<span style="color:#9e9e9e">'+STATUS_ICON_SVG.not_started+' Not Started</span>'+
      '<span style="color:#c62828">'+STATUS_ICON_SVG.failed+' Failed</span>'+
    '</div>';

  requestAnimationFrame(function(){ wfdDrawCorners(stages, rows); });
}

function wfdDrawCorners(stages, rows) {
  var canvas = document.getElementById('wfd-stage-canvas');
  if (!canvas) return;
  canvas.querySelectorAll('.wfd-corner-svg').forEach(function(e){ e.remove(); });
  var canvasRect = canvas.getBoundingClientRect();

  for (var r = 0; r < rows.length - 1; r++) {
    var lastStageOfRow = rows[r][rows[r].length - 1];
    var firstStageOfNextRow = rows[r + 1][0];
    var lastIdxOfRow = stages.indexOf(lastStageOfRow);
    var firstIdxOfNextRow = stages.indexOf(firstStageOfNextRow);
    var elA = document.getElementById('wfd-chip-' + lastIdxOfRow);
    var elB = document.getElementById('wfd-chip-' + firstIdxOfNextRow);
    if (!elA || !elB) continue;

    var rectA = elA.getBoundingClientRect();
    var rectB = elB.getBoundingClientRect();
    var side = (r % 2 === 0) ? 'right' : 'left';
    var xA = (side === 'right' ? rectA.right : rectA.left) - canvasRect.left;
    var xB = (side === 'right' ? rectB.right : rectB.left) - canvasRect.left;
    var xShared = (xA + xB) / 2; // avoids asymmetric curves from sub-pixel row-width rounding
    xA = xShared;
    xB = xShared;
    var yA = rectA.top + rectA.height / 2 - canvasRect.top;
    var yB = rectB.top + rectB.height / 2 - canvasRect.top;
    var bulge = (side === 'right') ? 40 : -40;

    var cls = wfdConnStatus(firstStageOfNextRow);

    var d = 'M ' + xA + ' ' + yA +
            ' C ' + (xA + bulge) + ' ' + yA +
            ', ' + (xB + bulge) + ' ' + yB +
            ', ' + xB + ' ' + yB;

    var svgNS = 'http://www.w3.org/2000/svg';
    var svg = document.createElementNS(svgNS, 'svg');
    svg.setAttribute('class', 'wfd-corner-svg ' + cls);
    svg.setAttribute('style', 'left:0;top:0;width:' + canvasRect.width + 'px;height:' + canvasRect.height + 'px;');
    var path = document.createElementNS(svgNS, 'path');
    path.setAttribute('d', d);
    path.setAttribute('stroke-width', '6');
    path.setAttribute('stroke-linecap', 'round');
    svg.appendChild(path);
    canvas.appendChild(svg);
  }
}

window.addEventListener('resize', function() {
  if (wfdLastWorkflow) requestAnimationFrame(function(){ wfdRenderStages(wfdLastWorkflow); });
});

function wfdLoadLogs() {
  var search = document.getElementById('wfd-log-search').value;
  fetch('/api/workflow-logs?id='+encodeURIComponent(wfdId)+'&search='+encodeURIComponent(search))
    .then(function(r){ return r.json(); })
    .then(function(d){
      var el = document.getElementById('wfd-log-list');
      var logs = (d.logs||[]).slice().reverse();
      document.getElementById('wfd-log-count').textContent = logs.length;
      if (!logs.length) { el.innerHTML = '<p style="color:#999;font-size:13px;padding:10px 0;">No logs yet.</p>'; return; }
      el.innerHTML = logs.map(function(l){
        return '<div class="wfd-log-row"><span>'+esc(l.ts)+'</span><span>'+esc(l.workflow_id)+'</span><span>'+esc(l.message)+'</span></div>';
      }).join('');
    }).catch(function(){});
}

function wfdScheduleAuto(status) {
  clearTimeout(wfdAutoTimer);
  var auto = document.getElementById('wfd-autorefresh').checked;
  if (auto && status !== 'completed' && status !== 'cancelled') {
    wfdAutoTimer = setTimeout(wfdLoad, 5000);
  }
}

wfdLoad();
'''
