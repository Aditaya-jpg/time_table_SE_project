/**
 * Main Application Controller for College Timetable Scheduling Demo
 */

window.APP_DATA = null;

// Temporary state for availability picker in modals
let currentFacultyAvailGrid = [];
let currentRoomAvailGrid = [];

document.addEventListener('DOMContentLoaded', () => {
  initNavigation();
  initModals();
  initActionButtons();
  TimetableVisualizer.init();
  refreshAppData();
});

// Toast notification helper
function showToast(message, type = 'success') {
  const toast = document.getElementById('toast');
  if (!toast) return;
  toast.textContent = message;
  toast.className = `toast toast-${type}`;
  toast.classList.remove('hidden');
  setTimeout(() => {
    toast.classList.add('hidden');
  }, 3500);
}

// Navigation Handler
function initNavigation() {
  const navLinks = document.querySelectorAll('.sidebar-nav a[data-section], .feature-card a[data-section]');
  navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const targetSec = link.dataset.section;
      switchSection(targetSec);
    });
  });

  // Handle hash changes
  window.addEventListener('hashchange', () => {
    const sec = window.location.hash.replace('#', '') || 'dashboard';
    switchSection(sec);
  });

  const initialSec = window.location.hash.replace('#', '') || 'dashboard';
  switchSection(initialSec);
}

function switchSection(sectionId) {
  // Update nav links
  document.querySelectorAll('.sidebar-nav .nav-item').forEach(link => {
    if (link.dataset.section === sectionId) {
      link.classList.add('active');
    } else {
      link.classList.remove('active');
    }
  });

  // Update content sections
  document.querySelectorAll('.content-section').forEach(sec => {
    sec.classList.remove('active');
  });

  const activeSection = document.getElementById(`sec-${sectionId}`);
  if (activeSection) {
    activeSection.classList.add('active');
  }

  // Update Title
  const titles = {
    dashboard: 'Dashboard Overview',
    courses: 'Course Offerings',
    sections: 'Student Sections',
    faculty: 'Faculty Directory & Availability',
    rooms: 'Classrooms & Laboratories',
    slots: 'Time Slots & Working Days',
    generate: 'Generate Timetable (CP-SAT)',
    view: 'Timetable Visualizer',
  };
  const titleEl = document.getElementById('pageTitle');
  if (titleEl && titles[sectionId]) {
    titleEl.textContent = titles[sectionId];
  }

  // Update location hash
  if (window.location.hash !== `#${sectionId}`) {
    window.location.hash = `#${sectionId}`;
  }

  if (sectionId === 'view') {
    TimetableVisualizer.populateFilterDropdown();
    TimetableVisualizer.render();
  }
}

// Data Fetch & Dashboard Update
async function refreshAppData() {
  try {
    const data = await API.getData();
    window.APP_DATA = data;
    updateDashboardUI(data);
    renderCoursesTable(data);
    renderSectionsTable(data);
    renderCourseGroupsTable(data);
    renderFacultyTable(data);
    renderRoomsTable(data);
    renderTimeSlotsView(data);
    TimetableVisualizer.render();
  } catch (err) {
    console.error('Error loading data:', err);
    showToast('Failed to connect to backend service', 'error');
  }
}

function updateDashboardUI(data) {
  // Update KPI counters
  document.getElementById('kpiCourses').textContent = data.courses.length;
  document.getElementById('kpiFaculty').textContent = data.faculty.length;
  document.getElementById('kpiSections').textContent = data.sections.length;
  document.getElementById('kpiRooms').textContent = data.rooms.length;

  const totalSessions = data.courses.reduce((sum, c) => sum + (c.sessions_per_week || 1), 0);
  document.getElementById('kpiSessions').textContent = totalSessions;

  // Update Import Summary Card if present
  if (data.import_summary) {
    const sum = data.import_summary;
    const sumCourses = document.getElementById('sumCourseCodes');
    if (sumCourses) sumCourses.textContent = `${sum.unique_course_codes} Codes (${sum.total_offerings} Offerings)`;
    const sumFac = document.getElementById('sumFaculty');
    if (sumFac) sumFac.textContent = `${sum.total_faculty} Instructors`;
    const sumSec = document.getElementById('sumSections');
    if (sumSec) sumSec.textContent = `${sum.total_sections} Sections + 2 Groups`;
    const sumVen = document.getElementById('sumVenues');
    if (sumVen) sumVen.textContent = `${sum.total_venues} Venues (Cap Unverified)`;
  }

  // Solver Status
  const statusBadge = document.getElementById('solverStatusTag');
  const quickBadge = document.getElementById('solverQuickBadge');
  const quickText = document.getElementById('quickStatusText');
  const timeVal = document.getElementById('statusSolveTime');
  const validVal = document.getElementById('statusValidation');
  const schedVal = document.getElementById('statusScheduleCount');
  const ribbon = document.getElementById('validationRibbon');

  if (data.last_solution) {
    const sol = data.last_solution;
    if (sol.status === 'OPTIMAL' || sol.status === 'FEASIBLE') {
      timeVal.textContent = `${sol.solve_time_seconds}s`;
      schedVal.textContent = `${sol.scheduled_events.length} sessions active`;

      const v = sol.validation;
      if (v) {
        ribbon.classList.remove('hidden');
        if (v.overall_status === 'FULLY VALIDATED') {
          statusBadge.className = 'badge badge-success';
          statusBadge.textContent = 'Status: Fully Validated';
          quickBadge.className = 'status-pill status-ready';
          quickText.textContent = 'Fully Validated';
          validVal.innerHTML = '<span style="color: #34d399; font-weight: 600;">PASSED (100% Verified)</span>';
        } else if (v.overall_status === 'VALIDATED WITH WARNINGS') {
          statusBadge.className = 'badge badge-warning';
          statusBadge.textContent = 'Status: Validated (With Warnings)';
          quickBadge.className = 'status-pill';
          quickText.textContent = 'Validated (Warnings)';
          const warnTitle = (v.unverified_constraints || []).join('; ');
          validVal.innerHTML = `<span style="color: #fbbf24; font-weight: 600;" title="${warnTitle}">VALIDATED (Warnings)</span>`;
        } else {
          statusBadge.className = 'badge badge-danger';
          statusBadge.textContent = 'Status: Infeasible Violations';
          validVal.innerHTML = '<span style="color: #f87171; font-weight: 600;">FAILED</span>';
        }

        document.getElementById('valFaculty').textContent = `Faculty Clashes: ${v.faculty_conflicts} (${v.faculty_status || 'Passed'})`;
        document.getElementById('valSection').textContent = `Section Clashes: ${v.section_conflicts} (${v.section_status || 'Passed'})`;
        document.getElementById('valRoom').textContent = `Room Clashes: ${v.room_conflicts} (${v.room_status || 'Passed'})`;
        document.getElementById('valCapacity').textContent = `Capacity: ${v.capacity_violations} (${v.capacity_status || 'Unverified'})`;
        document.getElementById('valDuration').textContent = `Duration: ${v.duration_violations} (${v.duration_status || 'Passed'})`;
      } else {
        statusBadge.className = 'badge badge-success';
        statusBadge.textContent = `Status: ${sol.status}`;
        quickBadge.className = 'status-pill status-ready';
        quickText.textContent = `CP-SAT ${sol.status}`;
        validVal.innerHTML = '<span style="color: #34d399; font-weight: 600;">FEASIBLE</span>';
      }
    } else {
      statusBadge.className = 'badge badge-danger';
      statusBadge.textContent = `Status: ${sol.status}`;
      quickBadge.className = 'status-pill';
      quickText.textContent = sol.status;
      timeVal.textContent = `${sol.solve_time_seconds}s`;
      schedVal.textContent = '0 sessions';
      validVal.textContent = 'Infeasible';
      ribbon.classList.add('hidden');
    }
  } else {
    statusBadge.className = 'badge badge-info';
    statusBadge.textContent = 'Status: Ready to Solve';
    quickBadge.className = 'status-pill status-ready';
    quickText.textContent = 'CP-SAT Ready';
    timeVal.textContent = '—';
    validVal.textContent = 'Not yet generated';
    schedVal.textContent = '0 sessions scheduled';
    ribbon.classList.add('hidden');
  }
}

// Action Buttons Handler
function initActionButtons() {
  // Load Sample Data
  const btnLoadSample = document.getElementById('btnLoadSample');
  if (btnLoadSample) {
    btnLoadSample.addEventListener('click', async () => {
      try {
        btnLoadSample.disabled = true;
        const data = await API.loadSampleData();
        window.APP_DATA = data;
        await refreshAppData();
        showToast('Sample college dataset successfully loaded!');
      } catch (err) {
        showToast('Error loading sample dataset: ' + err.message, 'error');
      } finally {
        btnLoadSample.disabled = false;
      }
    });
  }

  // Reset Data
  const btnResetData = document.getElementById('btnResetData');
  if (btnResetData) {
    btnResetData.addEventListener('click', async () => {
      if (!confirm('Are you sure you want to reset all scheduling data to empty?')) return;
      try {
        await API.resetData();
        await refreshAppData();
        showToast('All scheduling data reset.');
      } catch (err) {
        showToast('Error resetting data: ' + err.message, 'error');
      }
    });
  }

  // Trigger Solver
  const triggerSolver = async () => {
    const loader = document.getElementById('solverLoader');
    const outputBox = document.getElementById('solverOutput');
    const outputTitle = document.getElementById('outputTitle');
    const outputBadge = document.getElementById('outputBadge');
    const outputContent = document.getElementById('outputContent');

    try {
      if (loader) loader.classList.remove('hidden');
      if (outputBox) outputBox.classList.add('hidden');

      const sol = await API.generateTimetable();
      await refreshAppData();

      if (loader) loader.classList.add('hidden');
      if (outputBox) outputBox.classList.remove('hidden');

      if (sol.status === 'OPTIMAL' || sol.status === 'FEASIBLE') {
        outputBadge.className = 'badge badge-success';
        outputBadge.textContent = sol.status;
        outputTitle.textContent = `CP-SAT Timetable Solved (${sol.solve_time_seconds}s)`;
        outputContent.innerHTML = `
          <div style="color: #34d399; font-weight: 600; margin-bottom: 8px;">
            ✓ Successfully generated feasible timetable schedule!
          </div>
          <div>Total Events Solved: ${sol.total_events}</div>
          <div>Independent Validation: ${sol.validation.is_valid ? 'PASSED (0 Violations)' : 'FAILED'}</div>
          <div>Diagnostics: ${sol.diagnostics.join('<br>')}</div>
          <div style="margin-top: 12px;">
            <button class="btn btn-primary btn-sm" onclick="switchSection('view')">View Generated Timetable Matrix &rarr;</button>
          </div>
        `;
        showToast(`Feasible timetable generated in ${sol.solve_time_seconds}s!`);
      } else {
        outputBadge.className = 'badge badge-danger';
        outputBadge.textContent = sol.status;
        outputTitle.textContent = `CP-SAT Result: ${sol.status}`;
        outputContent.innerHTML = `
          <div style="color: #f87171; font-weight: 600; margin-bottom: 8px;">
            ✕ No feasible timetable found for current inputs.
          </div>
          <div style="margin-bottom: 8px;"><strong>Diagnostic Analysis:</strong></div>
          <ul style="padding-left: 20px;">
            ${sol.diagnostics.map(d => `<li>${d}</li>`).join('')}
          </ul>
        `;
        showToast('Timetable is infeasible. Inspect diagnostics for bottlenecks.', 'error');
      }
    } catch (err) {
      if (loader) loader.classList.add('hidden');
      showToast('Solver error: ' + err.message, 'error');
    }
  };

  const btnTopGen = document.getElementById('btnTopGenerate');
  if (btnTopGen) btnTopGen.addEventListener('click', triggerSolver);

  const btnDashGen = document.getElementById('btnDashboardGenerate');
  if (btnDashGen) btnDashGen.addEventListener('click', () => { switchSection('generate'); triggerSolver(); });

  const btnExecSolver = document.getElementById('btnExecSolver');
  if (btnExecSolver) btnExecSolver.addEventListener('click', triggerSolver);

  const btnEmptyGen = document.getElementById('btnEmptyGenerate');
  if (btnEmptyGen) btnEmptyGen.addEventListener('click', () => { switchSection('generate'); triggerSolver(); });

  const btnDashView = document.getElementById('btnDashboardView');
  if (btnDashView) btnDashView.addEventListener('click', () => switchSection('view'));
}

// --- TABLE RENDERERS ---

function renderCoursesTable(data) {
  const tbody = document.querySelector('#coursesTable tbody');
  if (!tbody) return;
  tbody.innerHTML = '';

  const facultyMap = Object.fromEntries(data.faculty.map(f => [f.id, f.name]));
  const sectionMap = Object.fromEntries(data.sections.map(s => [s.id, s.name]));
  const groupMap = Object.fromEntries((data.course_groups || []).map(g => [g.id, g.name]));

  if (data.courses.length === 0) {
    tbody.innerHTML = '<tr><td colspan="10" class="text-muted" style="text-align:center;">No courses defined. Click "Add Course" or load sample data.</td></tr>';
    return;
  }

  data.courses.forEach(c => {
    const tr = document.createElement('tr');

    // Multi-faculty display
    let facStr = '';
    if (c.faculty_ids && c.faculty_ids.length > 0) {
      facStr = c.faculty_ids.map(fid => facultyMap[fid] || fid).join(', ');
    } else {
      facStr = facultyMap[c.faculty_id] || c.faculty_id || 'TBA';
    }

    // Target display (Group vs Sections)
    let targetStr = '';
    if (c.group_id) {
      const gName = groupMap[c.group_id] || c.group_id;
      targetStr = `<span class="badge badge-warning" title="Cohort Group ${gName}">Group ${gName}</span>`;
    } else {
      const secNames = c.section_ids.map(sid => sectionMap[sid] || sid).join(', ');
      const isShared = c.section_ids.length > 1;
      targetStr = `${secNames} ${isShared ? '<span class="badge badge-purple text-xs">Shared</span>' : ''}`;
    }

    const reviewPill = c.needs_review
      ? `<span class="badge badge-warning text-xs" title="${c.review_reason || 'Incomplete source data'}">⚠️ Review</span>`
      : '';

    // Room Allocation Mode & Venues display
    let allocStr = '';
    if (c.allocation_mode === 'SIMULTANEOUS_BUNDLE') {
      const bundle = (c.required_room_bundle_ids && c.required_room_bundle_ids.length > 0)
        ? c.required_room_bundle_ids.join(' + ')
        : (c.designated_rooms || []).join(' + ');
      allocStr = `<div style="font-weight: 600; color: #a855f7;">Simultaneous Bundle</div><div class="text-xs text-muted" style="font-family: monospace;">${bundle}</div>`;
    } else if (c.allocation_mode === 'SINGLE_FROM_ELIGIBLE' && c.eligible_room_ids && c.eligible_room_ids.length > 0) {
      allocStr = `<div style="font-weight: 600; color: #38bdf8;">1 Room from Eligible</div><div class="text-xs text-muted" style="font-family: monospace;">${c.eligible_room_ids.join(', ')}</div>`;
    } else if (c.designated_rooms && c.designated_rooms.length > 0) {
      allocStr = `<div style="font-weight: 600;">Fixed: ${c.designated_rooms.join(', ')}</div>`;
    } else {
      allocStr = `<div>${c.required_room_type} (${c.rooms_required} room)</div>`;
    }

    tr.innerHTML = `
      <td><strong>${c.code}</strong> ${reviewPill}</td>
      <td>${c.name}</td>
      <td><span class="badge badge-subtle">${c.department}</span></td>
      <td><strong>${facStr}</strong></td>
      <td>${targetStr}</td>
      <td><span class="badge ${c.session_type === 'Lecture' ? 'badge-info' : 'badge-purple'}">${c.session_type}</span></td>
      <td>${c.sessions_per_week} / wk</td>
      <td>${c.duration} period(s)</td>
      <td>${allocStr}</td>
      <td>
        <button class="btn btn-secondary btn-sm" onclick="editCourse('${c.id}')">Edit</button>
        <button class="btn btn-danger btn-sm" onclick="deleteCourse('${c.id}')">Delete</button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function renderSectionsTable(data) {
  const tbody = document.querySelector('#sectionsTable tbody');
  if (!tbody) return;
  tbody.innerHTML = '';

  if (data.sections.length === 0) {
    tbody.innerHTML = '<tr><td colspan="6" class="text-muted" style="text-align:center;">No student sections defined.</td></tr>';
    return;
  }

  data.sections.forEach(s => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><code>${s.id}</code></td>
      <td><strong>${s.name}</strong></td>
      <td><span class="badge badge-subtle">${s.department}</span></td>
      <td>${s.semester_year}</td>
      <td><span class="badge badge-info">${s.strength} Students</span></td>
      <td>
        <button class="btn btn-secondary btn-sm" onclick="editSection('${s.id}')">Edit</button>
        <button class="btn btn-danger btn-sm" onclick="deleteSection('${s.id}')">Delete</button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function renderCourseGroupsTable(data) {
  const tbody = document.querySelector('#groupsTable tbody');
  if (!tbody) return;
  tbody.innerHTML = '';

  const groups = data.course_groups || [];
  const sectionMap = Object.fromEntries(data.sections.map(s => [s.id, s.name]));

  const statusBadge = document.getElementById('groupStatusBadge');
  const allVerified = groups.length > 0 && groups.every(g => g.is_verified);
  if (statusBadge) {
    if (allVerified) {
      statusBadge.className = 'badge badge-success';
      statusBadge.textContent = 'All Groups Verified';
    } else {
      statusBadge.className = 'badge badge-warning';
      statusBadge.textContent = 'Mapping Pending / Unverified';
    }
  }

  if (groups.length === 0) {
    tbody.innerHTML = '<tr><td colspan="6" class="text-muted" style="text-align:center;">No Course Groups defined.</td></tr>';
    return;
  }

  groups.forEach(g => {
    const tr = document.createElement('tr');
    const mappedSecNames = (g.section_ids && g.section_ids.length > 0)
      ? g.section_ids.map(sid => `<span class="badge badge-subtle" style="margin-right: 4px;">${sectionMap[sid] || sid}</span>`).join('')
      : '<span class="text-muted text-xs" style="color: #f59e0b;">⚠️ Unmapped (No sections assigned)</span>';

    const verifyBadge = g.is_verified
      ? '<span class="badge badge-success">Verified</span>'
      : '<span class="badge badge-warning">Unverified</span>';

    tr.innerHTML = `
      <td><code>${g.id}</code></td>
      <td><strong>Group ${g.name}</strong></td>
      <td><span class="badge badge-subtle">${g.department}</span></td>
      <td>${mappedSecNames}</td>
      <td>${verifyBadge}</td>
      <td>
        <button class="btn btn-secondary btn-sm" onclick="openGroupMappingModal('${g.id}')">Configure Mapping</button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

window.openGroupMappingModal = (groupId) => {
  const group = (window.APP_DATA?.course_groups || []).find(g => g.id === groupId);
  if (!group) return;

  const modal = document.getElementById('groupMappingModal');
  const title = document.getElementById('groupMappingTitle');
  const groupIdInput = document.getElementById('mappingGroupId');
  const grid = document.getElementById('groupSectionsCheckboxGrid');
  const desc = document.getElementById('mappingGroupDesc');

  if (title) title.textContent = `Map Student Sections for Group ${group.name} (${group.department})`;
  if (groupIdInput) groupIdInput.value = group.id;
  if (desc) desc.textContent = `Select which student sections belong to cohort Group ${group.name}. When mapped, any G${group.name} lecture will reserve these student sections, preventing overlap with their section practicals or tutorials.`;

  if (grid) {
    grid.innerHTML = '';
    const cseSections = (window.APP_DATA?.sections || []).filter(s => s.department === group.department || s.department === 'CSE');
    const mappedSet = new Set(group.section_ids || []);

    cseSections.forEach(s => {
      const isChecked = mappedSet.has(s.id) ? 'checked' : '';
      const label = document.createElement('label');
      label.style.display = 'flex';
      label.style.alignItems = 'center';
      label.style.gap = '8px';
      label.style.cursor = 'pointer';
      label.style.fontSize = '13px';
      label.style.padding = '6px';
      label.style.borderRadius = '4px';
      label.style.background = 'rgba(255,255,255,0.02)';
      label.innerHTML = `
        <input type="checkbox" name="groupSectionCheckbox" value="${s.id}" ${isChecked} />
        <span><strong>${s.name}</strong> (${s.strength} st.)</span>
      `;
      grid.appendChild(label);
    });
  }

  if (modal) modal.classList.remove('hidden');
};

async function handleGroupMappingSubmit(e) {
  e.preventDefault();
  const groupId = document.getElementById('mappingGroupId').value;
  const checkboxes = document.querySelectorAll('input[name="groupSectionCheckbox"]:checked');
  const selectedIds = Array.from(checkboxes).map(cb => cb.value);

  try {
    await API.updateGroupMapping(groupId, selectedIds);
    document.getElementById('groupMappingModal')?.classList.add('hidden');
    await refreshAppData();
    showToast(`Group mapping updated successfully!`);
  } catch (err) {
    showToast('Error updating group mapping: ' + err.message, 'error');
  }
}

function renderFacultyTable(data) {
  const tbody = document.querySelector('#facultyTable tbody');
  if (!tbody) return;
  tbody.innerHTML = '';

  if (data.faculty.length === 0) {
    tbody.innerHTML = '<tr><td colspan="6" class="text-muted" style="text-align:center;">No faculty members defined.</td></tr>';
    return;
  }

  data.faculty.forEach(f => {
    const tr = document.createElement('tr');
    let unavailCount = 0;
    if (f.availability) {
      f.availability.forEach(daySlots => {
        daySlots.forEach(avail => { if (!avail) unavailCount++; });
      });
    }

    const sharedTag = f.is_shared ? '<span class="badge badge-purple text-xs" style="margin-left: 6px;">Shared (CSE/AI)</span>' : '';
    const noteStr = f.notes ? `<div class="text-muted text-xs" style="color: #fbbf24;">ℹ️ ${f.notes}</div>` : '';

    tr.innerHTML = `
      <td><code>${f.id}</code></td>
      <td><strong>${f.name}</strong> ${sharedTag} ${noteStr}</td>
      <td><span class="badge badge-subtle">${f.department}</span></td>
      <td>${f.designation}</td>
      <td>
        ${unavailCount > 0
          ? `<span class="badge badge-warning">${unavailCount} Restricted Period(s)</span>`
          : '<span class="badge badge-success">Full Availability</span>'}
      </td>
      <td>
        <button class="btn btn-secondary btn-sm" onclick="editFaculty('${f.id}')">Edit &amp; Availability</button>
        <button class="btn btn-danger btn-sm" onclick="deleteFaculty('${f.id}')">Delete</button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function renderRoomsTable(data) {
  const tbody = document.querySelector('#roomsTable tbody');
  if (!tbody) return;
  tbody.innerHTML = '';

  if (data.rooms.length === 0) {
    tbody.innerHTML = '<tr><td colspan="6" class="text-muted" style="text-align:center;">No rooms or labs defined.</td></tr>';
    return;
  }

  data.rooms.forEach(r => {
    const tr = document.createElement('tr');
    const capStr = (r.capacity === null || r.capacity === undefined || r.capacity <= 0)
      ? `<span class="badge badge-warning" style="cursor: pointer;" onclick="editRoom('${r.id}')" title="Capacity unverified in source timetable. Click Edit to set.">Unverified</span>`
      : `<strong>${r.capacity} seats</strong>`;

    tr.innerHTML = `
      <td><code>${r.id}</code></td>
      <td><strong>${r.name}</strong></td>
      <td><span class="badge ${r.room_type === 'Classroom' ? 'badge-info' : 'badge-purple'}">${r.room_type}</span></td>
      <td>${capStr}</td>
      <td><span class="badge badge-success">Available</span></td>
      <td>
        <button class="btn btn-secondary btn-sm" onclick="editRoom('${r.id}')">Edit</button>
        <button class="btn btn-danger btn-sm" onclick="deleteRoom('${r.id}')">Delete</button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function renderTimeSlotsView(data) {
  const daysList = document.getElementById('daysList');
  if (daysList) {
    daysList.innerHTML = data.config.days.map(d => `<span class="badge badge-info">${d}</span>`).join(' ');
  }

  const breaksList = document.getElementById('breaksList');
  if (breaksList) {
    breaksList.innerHTML = (data.config.break_after_period || []).map(b =>
      `<span class="badge badge-warning">Lunch Break after ${data.config.periods[b]?.name || 'Period ' + (b+1)}</span>`
    ).join(' ');
  }

  const periodsTbody = document.querySelector('#periodsTable tbody');
  if (periodsTbody) {
    periodsTbody.innerHTML = '';
    data.config.periods.forEach(p => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td><strong>Period ${p.index + 1}</strong></td>
        <td>${p.name}</td>
        <td><code>${p.start_time}</code></td>
        <td><code>${p.end_time}</code></td>
        <td>60 mins</td>
      `;
      periodsTbody.appendChild(tr);
    });
  }
}

// --- MODAL CONTROLLER & FORMS ---

function initModals() {
  // Close modals on [data-close]
  document.querySelectorAll('[data-close]').forEach(btn => {
    btn.addEventListener('click', () => {
      const modalId = btn.dataset.close;
      document.getElementById(modalId)?.classList.add('hidden');
    });
  });

  // Open modals
  document.getElementById('btnAddCourse')?.addEventListener('click', () => openCourseModal());
  document.getElementById('btnAddSection')?.addEventListener('click', () => openSectionModal());
  document.getElementById('btnAddFaculty')?.addEventListener('click', () => openFacultyModal());
  document.getElementById('btnAddRoom')?.addEventListener('click', () => openRoomModal());

  // Form Submissions
  document.getElementById('courseForm')?.addEventListener('submit', handleCourseSubmit);
  document.getElementById('sectionForm')?.addEventListener('submit', handleSectionSubmit);
  document.getElementById('facultyForm')?.addEventListener('submit', handleFacultySubmit);
  document.getElementById('roomForm')?.addEventListener('submit', handleRoomSubmit);
  document.getElementById('groupMappingForm')?.addEventListener('submit', handleGroupMappingSubmit);
}

// Course Modal
function openCourseModal(course = null) {
  const modal = document.getElementById('courseModal');
  const title = document.getElementById('courseModalTitle');
  const facultySel = document.getElementById('cFaculty');
  const sectionSel = document.getElementById('cSections');

  // Populate faculty select
  facultySel.innerHTML = (window.APP_DATA?.faculty || []).map(f =>
    `<option value="${f.id}">${f.name} (${f.department})</option>`
  ).join('');

  // Populate sections select
  sectionSel.innerHTML = (window.APP_DATA?.sections || []).map(s =>
    `<option value="${s.id}">${s.name} [${s.department} • ${s.strength} students]</option>`
  ).join('');

  if (course) {
    title.textContent = 'Edit Course Offering';
    document.getElementById('courseFormMode').value = course.id;
    document.getElementById('cCode').value = course.code;
    document.getElementById('cName').value = course.name;
    document.getElementById('cDept').value = course.department;
    document.getElementById('cFaculty').value = course.faculty_id;
    document.getElementById('cType').value = course.session_type;
    document.getElementById('cSessions').value = course.sessions_per_week;
    document.getElementById('cDuration').value = course.duration;
    document.getElementById('cRoomType').value = course.required_room_type;
    document.getElementById('cRoomsReq').value = course.rooms_required;

    // Multi-select sections
    Array.from(sectionSel.options).forEach(opt => {
      opt.selected = course.section_ids.includes(opt.value);
    });
  } else {
    title.textContent = 'Add Course Offering';
    document.getElementById('courseFormMode').value = 'add';
    document.getElementById('courseForm').reset();
    document.getElementById('cSessions').value = '3';
    document.getElementById('cDuration').value = '1';
    document.getElementById('cRoomsReq').value = '1';
  }

  modal.classList.remove('hidden');
}

async function handleCourseSubmit(e) {
  e.preventDefault();
  const mode = document.getElementById('courseFormMode').value;
  const sectionSel = document.getElementById('cSections');
  const selectedSections = Array.from(sectionSel.selectedOptions).map(opt => opt.value);

  if (selectedSections.length === 0) {
    alert('Please select at least one student section.');
    return;
  }

  const courseData = {
    id: mode === 'add' ? `CRS_${document.getElementById('cCode').value.replace(/[^A-Za-z0-9]/g, '')}` : mode,
    code: document.getElementById('cCode').value.trim(),
    name: document.getElementById('cName').value.trim(),
    department: document.getElementById('cDept').value,
    faculty_id: document.getElementById('cFaculty').value,
    section_ids: selectedSections,
    session_type: document.getElementById('cType').value,
    sessions_per_week: parseInt(document.getElementById('cSessions').value, 10),
    duration: parseInt(document.getElementById('cDuration').value, 10),
    required_room_type: document.getElementById('cRoomType').value,
    rooms_required: parseInt(document.getElementById('cRoomsReq').value, 10),
  };

  try {
    if (mode === 'add') {
      await API.addCourse(courseData);
      showToast('Course added successfully.');
    } else {
      await API.updateCourse(mode, courseData);
      showToast('Course updated successfully.');
    }
    document.getElementById('courseModal').classList.add('hidden');
    refreshAppData();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

window.editCourse = (id) => {
  const course = window.APP_DATA?.courses.find(c => c.id === id);
  if (course) openCourseModal(course);
};

window.deleteCourse = async (id) => {
  if (!confirm('Are you sure you want to delete this course?')) return;
  try {
    await API.deleteCourse(id);
    showToast('Course deleted.');
    refreshAppData();
  } catch (err) {
    showToast(err.message, 'error');
  }
};

// Section Modal
function openSectionModal(section = null) {
  const modal = document.getElementById('sectionModal');
  const title = document.getElementById('sectionModalTitle');

  if (section) {
    title.textContent = 'Edit Student Section';
    document.getElementById('sectionFormMode').value = section.id;
    document.getElementById('secId').value = section.id;
    document.getElementById('secId').disabled = true;
    document.getElementById('secName').value = section.name;
    document.getElementById('secDept').value = section.department;
    document.getElementById('secSem').value = section.semester_year;
    document.getElementById('secStrength').value = section.strength;
  } else {
    title.textContent = 'Add Student Section';
    document.getElementById('sectionFormMode').value = 'add';
    document.getElementById('sectionForm').reset();
    document.getElementById('secId').disabled = false;
    document.getElementById('secStrength').value = '60';
  }

  modal.classList.remove('hidden');
}

async function handleSectionSubmit(e) {
  e.preventDefault();
  const mode = document.getElementById('sectionFormMode').value;
  const sectionData = {
    id: mode === 'add' ? document.getElementById('secId').value.trim() : mode,
    name: document.getElementById('secName').value.trim(),
    department: document.getElementById('secDept').value,
    semester_year: document.getElementById('secSem').value.trim(),
    strength: parseInt(document.getElementById('secStrength').value, 10),
  };

  try {
    if (mode === 'add') {
      await API.addSection(sectionData);
      showToast('Section added.');
    } else {
      await API.updateSection(mode, sectionData);
      showToast('Section updated.');
    }
    document.getElementById('sectionModal').classList.add('hidden');
    refreshAppData();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

window.editSection = (id) => {
  const section = window.APP_DATA?.sections.find(s => s.id === id);
  if (section) openSectionModal(section);
};

window.deleteSection = async (id) => {
  if (!confirm('Are you sure you want to delete this section?')) return;
  try {
    await API.deleteSection(id);
    showToast('Section deleted.');
    refreshAppData();
  } catch (err) {
    showToast(err.message, 'error');
  }
};

// Faculty Modal & Interactive Availability Picker
function openFacultyModal(faculty = null) {
  const modal = document.getElementById('facultyModal');
  const title = document.getElementById('facultyModalTitle');
  const numDays = window.APP_DATA?.config.days.length || 5;
  const numPeriods = window.APP_DATA?.config.periods.length || 6;

  if (faculty) {
    title.textContent = 'Edit Faculty & Availability';
    document.getElementById('facultyFormMode').value = faculty.id;
    document.getElementById('fId').value = faculty.id;
    document.getElementById('fId').disabled = true;
    document.getElementById('fName').value = faculty.name;
    document.getElementById('fDept').value = faculty.department;
    document.getElementById('fDesig').value = faculty.designation;

    // Deep copy availability grid
    currentFacultyAvailGrid = (faculty.availability && faculty.availability.length)
      ? JSON.parse(JSON.stringify(faculty.availability))
      : Array.from({ length: numDays }, () => Array(numPeriods).fill(true));
  } else {
    title.textContent = 'Add Faculty & Availability';
    document.getElementById('facultyFormMode').value = 'add';
    document.getElementById('facultyForm').reset();
    document.getElementById('fId').disabled = false;
    currentFacultyAvailGrid = Array.from({ length: numDays }, () => Array(numPeriods).fill(true));
  }

  renderAvailabilityGrid(
    'facultyAvailGrid',
    currentFacultyAvailGrid,
    (d, p) => {
      currentFacultyAvailGrid[d][p] = !currentFacultyAvailGrid[d][p];
      renderAvailabilityGrid('facultyAvailGrid', currentFacultyAvailGrid, arguments.callee);
    }
  );

  modal.classList.remove('hidden');
}

function renderAvailabilityGrid(containerId, grid, onToggle) {
  const container = document.getElementById(containerId);
  if (!container || !window.APP_DATA) return;

  const days = window.APP_DATA.config.days;
  const periods = window.APP_DATA.config.periods;

  let html = '';
  days.forEach((dayName, d) => {
    html += `<div class="avail-row">
      <div class="avail-day-label">${dayName.substring(0, 3)}</div>`;

    periods.forEach((p, pIdx) => {
      const isAvail = grid[d] ? grid[d][pIdx] : true;
      const cellClass = isAvail ? 'cell-available' : 'cell-unavailable';
      const cellText = isAvail ? 'Avail' : 'Off';
      html += `<div class="avail-cell ${cellClass}" data-day="${d}" data-period="${pIdx}" title="${dayName} ${p.name}: Click to toggle">
        ${cellText}
      </div>`;
    });

    html += `</div>`;
  });

  container.innerHTML = html;

  container.querySelectorAll('.avail-cell').forEach(cell => {
    cell.addEventListener('click', () => {
      const d = parseInt(cell.dataset.day, 10);
      const p = parseInt(cell.dataset.period, 10);
      grid[d][p] = !grid[d][p];
      renderAvailabilityGrid(containerId, grid, onToggle);
    });
  });
}

async function handleFacultySubmit(e) {
  e.preventDefault();
  const mode = document.getElementById('facultyFormMode').value;
  const facultyData = {
    id: mode === 'add' ? document.getElementById('fId').value.trim() : mode,
    name: document.getElementById('fName').value.trim(),
    department: document.getElementById('fDept').value,
    designation: document.getElementById('fDesig').value.trim(),
    availability: currentFacultyAvailGrid,
  };

  try {
    if (mode === 'add') {
      await API.addFaculty(facultyData);
      showToast('Faculty added successfully.');
    } else {
      await API.updateFaculty(mode, facultyData);
      showToast('Faculty & availability updated.');
    }
    document.getElementById('facultyModal').classList.add('hidden');
    refreshAppData();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

window.editFaculty = (id) => {
  const fac = window.APP_DATA?.faculty.find(f => f.id === id);
  if (fac) openFacultyModal(fac);
};

window.deleteFaculty = async (id) => {
  if (!confirm('Are you sure you want to delete this faculty member?')) return;
  try {
    await API.deleteFaculty(id);
    showToast('Faculty member deleted.');
    refreshAppData();
  } catch (err) {
    showToast(err.message, 'error');
  }
};

// Room Modal
function openRoomModal(room = null) {
  const modal = document.getElementById('roomModal');
  const title = document.getElementById('roomModalTitle');
  const numDays = window.APP_DATA?.config.days.length || 5;
  const numPeriods = window.APP_DATA?.config.periods.length || 6;

  if (room) {
    title.textContent = 'Edit Room / Lab';
    document.getElementById('roomFormMode').value = room.id;
    document.getElementById('rId').value = room.id;
    document.getElementById('rId').disabled = true;
    document.getElementById('rName').value = room.name;
    document.getElementById('rType').value = room.room_type;
    document.getElementById('rCap').value = room.capacity;
    currentRoomAvailGrid = (room.availability && room.availability.length)
      ? JSON.parse(JSON.stringify(room.availability))
      : Array.from({ length: numDays }, () => Array(numPeriods).fill(true));
  } else {
    title.textContent = 'Add Room / Lab';
    document.getElementById('roomFormMode').value = 'add';
    document.getElementById('roomForm').reset();
    document.getElementById('rId').disabled = false;
    document.getElementById('rCap').value = '65';
    currentRoomAvailGrid = Array.from({ length: numDays }, () => Array(numPeriods).fill(true));
  }

  renderAvailabilityGrid('roomAvailGrid', currentRoomAvailGrid, null);
  modal.classList.remove('hidden');
}

async function handleRoomSubmit(e) {
  e.preventDefault();
  const mode = document.getElementById('roomFormMode').value;
  const roomData = {
    id: mode === 'add' ? document.getElementById('rId').value.trim() : mode,
    name: document.getElementById('rName').value.trim(),
    room_type: document.getElementById('rType').value,
    capacity: parseInt(document.getElementById('rCap').value, 10),
    availability: currentRoomAvailGrid,
  };

  try {
    if (mode === 'add') {
      await API.addRoom(roomData);
      showToast('Room added.');
    } else {
      await API.updateRoom(mode, roomData);
      showToast('Room updated.');
    }
    document.getElementById('roomModal').classList.add('hidden');
    refreshAppData();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

window.editRoom = (id) => {
  const rm = window.APP_DATA?.rooms.find(r => r.id === id);
  if (rm) openRoomModal(rm);
};

window.deleteRoom = async (id) => {
  if (!confirm('Are you sure you want to delete this room?')) return;
  try {
    await API.deleteRoom(id);
    showToast('Room deleted.');
    refreshAppData();
  } catch (err) {
    showToast(err.message, 'error');
  }
};
