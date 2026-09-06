"""
dashboard_profile.py — Profile Nexus tab (personal data form)
Reads/writes profile.json. Split into sub-tabs (one per section heading)
so a long single-scroll form doesn't force scanning past unrelated
sections to find a field. Sub-nav/sub-page CSS is the shared one already
defined in dashboard_ui.py.
Imported by dashboard_server.py
"""

def build_profile_html(prof_json):
    return '''
<!-- PROFILE -->
<div id="page-profile" class="page active">

  <div class="pf-top-row">
    <button class="cr-tab-btn cr-log-btn" id="pf-log-toggle-btn" onclick="crToggleLogPanel('pf')">&#128220; Logs</button>
  </div>

  <div class="sub-nav">
    <button class="active" onclick="pfSwitchSub('personal',this)">Personal Information</button>
    <button onclick="pfSwitchSub('education',this)">Education</button>
    <button onclick="pfSwitchSub('experience',this)">Experience</button>
    <button onclick="pfSwitchSub('workhistory',this)">Work History</button>
    <button onclick="pfSwitchSub('eeo',this)">EEO Information</button>
    <button onclick="pfSwitchSub('workauth',this)">Work Authorization</button>
    <button onclick="pfSwitchSub('india',this)">India Specific</button>
    <button onclick="pfSwitchSub('social',this)">Social &amp; Links</button>
    <button onclick="pfSwitchSub('skills',this)">Skills &amp; Preferences</button>
  </div>

  <div class="sub-page active" id="pf-sub-personal">
    <div class="section-title">Personal Information</div>
    <div class="form-grid">
      <div class="form-group"><label>First Name</label><input id="firstName" type="text"></div>
      <div class="form-group"><label>Last Name</label><input id="lastName" type="text"></div>
      <div class="form-group"><label>Full Name</label><input id="fullName" type="text"></div>
      <div class="form-group"><label>Legal Name</label><input id="legalName" type="text"></div>
      <div class="form-group"><label>Middle Name</label><input id="middleName" type="text"></div>
      <div class="form-group"><label>Preferred Name</label><input id="preferredName" type="text"></div>
      <div class="form-group"><label>Email</label><input id="email" type="email"></div>
      <div class="form-group"><label>Phone</label><input id="phone" type="text"></div>
      <div class="form-group"><label>Phone Type</label><select id="phoneType"><option>Mobile</option><option>Home</option><option>Work</option></select></div>
      <div class="form-group"><label>Phone Country Code</label><input id="phoneCountry" type="text"></div>
      <div class="form-group"><label>Birthday</label><input id="birthday" type="date"></div>
      <div class="form-group"><label>Location</label><input id="location_p" type="text"></div>
      <div class="form-group"><label>Address</label><input id="address" type="text"></div>
      <div class="form-group"><label>City</label><input id="city" type="text"></div>
      <div class="form-group"><label>State</label><input id="state" type="text"></div>
      <div class="form-group"><label>Country</label><input id="country" type="text"></div>
      <div class="form-group"><label>Postal Code</label><input id="postalCode" type="text"></div>
    </div>
  </div>

  <div class="sub-page" id="pf-sub-education">
    <div class="section-title">Education</div>
    <div class="form-grid">
      <div class="form-group"><label>School / University</label><input id="school" type="text"></div>
      <div class="form-group"><label>Degree</label><input id="degree" type="text"></div>
      <div class="form-group"><label>Highest Degree</label><select id="highestDegree"><option value="">Select</option><option>High School</option><option>Diploma</option><option>Bachelor</option><option>Master</option><option>PhD</option></select></div>
      <div class="form-group"><label>Graduation Year</label><input id="gradYear" type="text"></div>
      <div class="form-group"><label>GPA / CGPA</label><input id="gpa" type="text"></div>
      <div class="form-group"><label>Field of Study</label><input id="fieldOfStudy" type="text"></div>
    </div>
  </div>

  <div class="sub-page" id="pf-sub-experience">
    <div class="section-title">Experience</div>
    <div class="form-grid">
      <div class="form-group"><label>Currently Employed</label><select id="currentlyEmployed"><option>No</option><option>Yes</option></select></div>
      <div class="form-group"><label>Total Experience (Years)</label><input id="totalExperience" type="text"></div>
      <div class="form-group"><label>Relevant Experience (Years)</label><input id="relevantExperience" type="text"></div>
      <div class="form-group"><label>Notice Period</label><select id="noticePeriod"><option value="">Select</option><option>Immediate</option><option>15 Days</option><option>30 Days</option><option>45 Days</option><option>60 Days</option><option>90 Days</option></select></div>
      <div class="form-group"><label>Current CTC</label><input id="currentCTC" type="text"></div>
      <div class="form-group"><label>Expected CTC — Text</label><input id="expectedCTCText" type="text"></div>
      <div class="form-group"><label>Expected CTC — Number</label><input id="expectedCTCNumber" type="number"></div>
      <div class="form-group"><label>Available From</label><input id="availableFrom" type="date"></div>
      <div class="form-group"><label>Night Shift</label><select id="nightShift"><option>No</option><option>Yes</option></select></div>
    </div>
  </div>

  <div class="sub-page" id="pf-sub-workhistory">
    <div class="section-title">Work History <button onclick="addJob()" style="background:#3498db;color:white;border:none;padding:4px 12px;border-radius:6px;cursor:pointer;font-size:12px;margin-left:10px;">+ Add Job</button></div>
    <div id="jobs_container_profile"></div>
  </div>

  <div class="sub-page" id="pf-sub-eeo">
    <div class="section-title">EEO Information</div>
    <div class="form-grid">
      <div class="form-group"><label>Gender</label><select id="gender"><option value="">Prefer not to say</option><option>Male</option><option>Female</option><option>Non-binary</option></select></div>
      <div class="form-group"><label>Ethnicity</label><input id="ethnicity" type="text"></div>
      <div class="form-group"><label>Hispanic</label><select id="hispanic"><option>No</option><option>Yes</option></select></div>
      <div class="form-group"><label>Veteran Status</label><select id="veteran"><option>No</option><option>Yes</option></select></div>
      <div class="form-group"><label>Disability</label><select id="disability"><option>No</option><option>Yes</option></select></div>
      <div class="form-group"><label>LGBT</label><select id="lgbt"><option>Prefer not to say</option><option>Yes</option><option>No</option></select></div>
    </div>
  </div>

  <div class="sub-page" id="pf-sub-workauth">
    <div class="section-title">Work Authorization</div>
    <div class="form-grid">
      <div class="form-group"><label>Work Authorization</label><input id="workAuthorization" type="text"></div>
      <div class="form-group"><label>Work Auth (US)</label><select id="workAuthUS"><option>No</option><option>Yes</option></select></div>
      <div class="form-group"><label>Visa Type</label><input id="visaType" type="text"></div>
      <div class="form-group"><label>Sponsorship Required</label><select id="sponsorship"><option>No</option><option>Yes</option></select></div>
      <div class="form-group"><label>Willing to Relocate</label><select id="relocate"><option>No</option><option>Yes</option></select></div>
      <div class="form-group"><label>Relocate Preference</label><input id="relocatePreference" type="text"></div>
      <div class="form-group"><label>Work Location Preference</label><input id="workLocation" type="text"></div>
    </div>
  </div>

  <div class="sub-page" id="pf-sub-india">
    <div class="section-title">India Specific</div>
    <div class="form-grid">
      <div class="form-group"><label>PAN Number</label><input id="pan" type="text"></div>
      <div class="form-group"><label>Aadhaar Number</label><input id="aadhaar" type="text"></div>
      <div class="form-group"><label>UAN Number</label><input id="uan" type="text"></div>
      <div class="form-group"><label>ESIC Number</label><input id="esic" type="text"></div>
    </div>
  </div>

  <div class="sub-page" id="pf-sub-social">
    <div class="section-title">Social &amp; Links</div>
    <div class="form-grid">
      <div class="form-group"><label>LinkedIn</label><input id="linkedin_p" type="text"></div>
      <div class="form-group"><label>GitHub</label><input id="github" type="text"></div>
      <div class="form-group"><label>Portfolio</label><input id="portfolio" type="text"></div>
      <div class="form-group"><label>Website</label><input id="website" type="text"></div>
      <div class="form-group"><label>Twitter</label><input id="twitter" type="text"></div>
    </div>
  </div>

  <div class="sub-page" id="pf-sub-skills">
    <div class="section-title">Skills &amp; Preferences</div>
    <div class="form-grid">
      <div class="form-group full-width"><label>Skills</label><textarea id="skills"></textarea></div>
      <div class="form-group"><label>Language</label><input id="language" type="text"></div>
      <div class="form-group"><label>Native Language</label><input id="nativeLanguage" type="text"></div>
      <div class="form-group"><label>Employment Type</label><select id="empType"><option>Full Time</option><option>Part Time</option><option>Contract</option><option>Internship</option></select></div>
      <div class="form-group full-width"><label>Professional Summary</label><textarea id="summary"></textarea></div>
    </div>
  </div>

  <button class="btn-save" onclick="saveProfile()">&#128190; Save profile.json</button>
  <span class="save-msg" id="saveMsg"></span>

  <!-- ACTIVITY LOG — shares the same /api/logs feed as the Career tab's panel -->
  <div class="cr-card cr-log-panel" id="pf-log-panel" style="display:none">
    <h2 class="cr-section-title">
      Activity Log <span class="cr-pill" id="pf-log-count">0</span>
      <button class="cr-log-refresh" onclick="crLoadLogs('pf')" title="Refresh">&#8635;</button>
    </h2>
    <div class="cr-log-list" id="pf-log-list"></div>
  </div>

</div>
'''


def build_profile_js(prof_json):
    return '''
// ── Profile ────────────────────────────────────────────────────────────────────
const PROFILE_DATA = ''' + prof_json + ''';
function escHtml(s){return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}
const PF=['firstName','lastName','fullName','legalName','middleName','preferredName','email','phone',
  'phoneType','phoneCountry','birthday','location_p','address','city','state','country','postalCode',
  'school','degree','highestDegree','gradYear','gpa','fieldOfStudy','currentlyEmployed','totalExperience',
  'relevantExperience','noticePeriod','currentCTC','expectedCTCText','expectedCTCNumber','availableFrom',
  'nightShift','gender','ethnicity','hispanic','veteran','disability','lgbt','workAuthorization','workAuthUS',
  'visaType','sponsorship','relocate','relocatePreference','workLocation','pan','aadhaar','uan','esic',
  'linkedin_p','github','portfolio','website','twitter','skills','language','nativeLanguage','empType','summary'];
function fillProfileForm(data){
  PF.forEach(id=>{const el=document.getElementById(id);if(el&&data[id]!==undefined)el.value=data[id];});
  const c=document.getElementById('jobs_container_profile');c.innerHTML='';
  if(data.jobs&&data.jobs.length)data.jobs.forEach((j,i)=>renderJobEntry(j,i));else renderJobEntry({},0);
}
function collectProfile(){
  const p={};PF.forEach(id=>{const el=document.getElementById(id);if(el)p[id]=el.value;});
  const c=document.getElementById('jobs_container_profile');const jj=[];
  for(let i=0;i<c.children.length;i++){
    jj.push({title:document.getElementById('job_title_'+i)?.value||'',
      company:document.getElementById('job_company_'+i)?.value||'',
      startDate:document.getElementById('job_startDate_'+i)?.value||'',
      endDate:document.getElementById('job_endDate_'+i)?.value||'',
      currentlyWorking:document.getElementById('job_cw_'+i)?.value||'No',
      description:document.getElementById('job_desc_'+i)?.value||''});
  }
  p.jobs=jj;return p;
}
function renderJobEntry(job,idx){
  const c=document.getElementById('jobs_container_profile');const d=document.createElement('div');
  d.id='job_'+idx;d.style.cssText='background:white;padding:15px;border-radius:8px;margin-bottom:10px;box-shadow:0 2px 5px rgba(0,0,0,0.08);';
  d.innerHTML=`<div style="display:flex;justify-content:space-between;margin-bottom:10px;"><b>Job #${idx+1}</b>
    <button onclick="removeJob(${idx})" style="background:#e74c3c;color:white;border:none;padding:3px 10px;border-radius:5px;cursor:pointer;font-size:12px;">Remove</button></div>
    <div class="form-grid">
      <div class="form-group"><label>Job Title</label><input id="job_title_${idx}" type="text" value="${escHtml(job.title||'')}"></div>
      <div class="form-group"><label>Company</label><input id="job_company_${idx}" type="text" value="${escHtml(job.company||'')}"></div>
      <div class="form-group"><label>Start Date</label><input id="job_startDate_${idx}" type="month" value="${job.startDate||''}"></div>
      <div class="form-group"><label>End Date</label><input id="job_endDate_${idx}" type="month" value="${job.endDate||''}"></div>
      <div class="form-group"><label>Currently Working</label>
        <select id="job_cw_${idx}"><option value="No" ${job.currentlyWorking!=='Yes'?'selected':''}>No</option><option value="Yes" ${job.currentlyWorking==='Yes'?'selected':''}>Yes</option></select></div>
      <div class="form-group full-width"><label>Description</label><textarea id="job_desc_${idx}">${escHtml(job.description||'')}</textarea></div>
    </div>`;
  c.appendChild(d);
}
function addJob(){const c=document.getElementById('jobs_container_profile');renderJobEntry({},c.children.length);}
function removeJob(idx){const el=document.getElementById('job_'+idx);if(el)el.remove();}

// ── Sub-tab switch (Profile Nexus) ──
function pfSwitchSub(id, btn) {
  const root = document.getElementById('page-profile');
  root.querySelectorAll('.sub-page').forEach(function(p){ p.classList.remove('active'); });
  root.querySelectorAll('.sub-nav button').forEach(function(b){ b.classList.remove('active'); });
  const panel = document.getElementById('pf-sub-'+id);
  if (panel) panel.classList.add('active');
  if (btn) btn.classList.add('active');
}

async function saveProfile(){
  try {
    const r=await fetch('/api/save-profile',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(collectProfile())});
    const d=await r.json();
    const msg=document.getElementById('saveMsg');
    msg.textContent=d.ok?'&#10003; Saved!':'&#10007; '+d.error;
    setTimeout(()=>msg.textContent='',3000);
    if (typeof crSendLog === 'function') {
      crSendLog('pf', 'Profile', d.ok ? 'Saved profile.json' : ('Failed to save profile.json: '+(d.error||'unknown error')));
    }
  } catch(e) { alert('Browser is busy, please try again in a moment.'); }
}
'''
