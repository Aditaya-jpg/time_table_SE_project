/**
 * Timetable Matrix Renderer & Multi-Perspective Visualizer
 * Supports Section-Wise, Faculty-Wise, Room-Wise, and Master Views.
 */

const TimetableVisualizer = {
  currentView: 'section', // 'section' | 'faculty' | 'room' | 'master'
  currentProgramme: 'ALL', // 'ALL' | 'CSE' | 'AI' | 'DS'
  currentFilterId: null,

  init() {
    this.bindEvents();
  },

  bindEvents() {
    // Programme filter dropdown
    const progSelect = document.getElementById('programmeFilterSelect');
    if (progSelect) {
      progSelect.addEventListener('change', (e) => {
        this.currentProgramme = e.target.value;
        this.currentFilterId = null;
        this.populateFilterDropdown();
        this.render();
      });
    }

    // View tab buttons
    document.querySelectorAll('.view-controls [data-view]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        document.querySelectorAll('.view-controls [data-view]').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        this.currentView = btn.dataset.view;
        this.populateFilterDropdown();
        this.render();
      });
    });

    // Filter dropdown change
    const filterSelect = document.getElementById('viewFilterSelect');
    if (filterSelect) {
      filterSelect.addEventListener('change', (e) => {
        this.currentFilterId = e.target.value;
        this.render();
      });
    }

    // Print button
    const btnPrint = document.getElementById('btnPrintTimetable');
    if (btnPrint) {
      btnPrint.addEventListener('click', () => {
        window.print();
      });
    }
  },

  populateFilterDropdown() {
    const select = document.getElementById('viewFilterSelect');
    if (!select || !window.APP_DATA) return;

    select.innerHTML = '';
    select.style.display = 'inline-block';

    const prog = this.currentProgramme;

    if (this.currentView === 'section') {
      let secs = window.APP_DATA.sections || [];
      if (prog !== 'ALL') {
        secs = secs.filter(s => s.department === prog || s.department.includes(prog));
      }

      secs.forEach((sec, idx) => {
        const opt = document.createElement('option');
        opt.value = sec.id;
        opt.textContent = `${sec.name} (${sec.department} • ${sec.strength} students)`;
        select.appendChild(opt);
        if (idx === 0 && !this.currentFilterId) this.currentFilterId = sec.id;
      });

      // Also add course groups (G1, G2) if CSE or ALL
      if (prog === 'ALL' || prog === 'CSE') {
        (window.APP_DATA.course_groups || []).forEach(g => {
          const opt = document.createElement('option');
          opt.value = g.id;
          const vStr = g.is_verified ? 'Verified' : 'Unverified';
          opt.textContent = `Group ${g.name} [Course Group • ${vStr}]`;
          select.appendChild(opt);
        });
      }

      if (!this.currentFilterId && secs.length) {
        this.currentFilterId = secs[0].id;
      }
    } else if (this.currentView === 'faculty') {
      let facs = window.APP_DATA.faculty || [];
      if (prog !== 'ALL') {
        facs = facs.filter(f => f.department === prog || f.department.includes(prog) || f.is_shared || f.department === 'COMMON');
      }

      facs.forEach((fac, idx) => {
        const opt = document.createElement('option');
        opt.value = fac.id;
        const sharedTag = fac.is_shared ? ' (Shared Across Depts)' : '';
        opt.textContent = `${fac.name}${sharedTag} (${fac.department})`;
        select.appendChild(opt);
        if (idx === 0 && !this.currentFilterId) this.currentFilterId = fac.id;
      });
      if (!this.currentFilterId && facs.length) {
        this.currentFilterId = facs[0].id;
      }
    } else if (this.currentView === 'room') {
      (window.APP_DATA.rooms || []).forEach((rm, idx) => {
        const opt = document.createElement('option');
        opt.value = rm.id;
        const capStr = (rm.capacity === null || rm.capacity === undefined || rm.capacity <= 0) ? 'Unverified' : `${rm.capacity} seats`;
        opt.textContent = `${rm.name} [${rm.room_type} • Cap: ${capStr}]`;
        select.appendChild(opt);
        if (idx === 0 && !this.currentFilterId) this.currentFilterId = rm.id;
      });
      if (!this.currentFilterId && window.APP_DATA.rooms?.length) {
        this.currentFilterId = window.APP_DATA.rooms[0].id;
      }
    } else if (this.currentView === 'master') {
      select.style.display = 'none';
      this.currentFilterId = 'ALL';
    }

    if (this.currentFilterId) {
      select.value = this.currentFilterId;
    }
  },

  render() {
    const emptyState = document.getElementById('emptyTimetablePlaceholder');
    const wrapper = document.getElementById('timetableGridWrapper');
    const valBanner = document.getElementById('timetableValBanner');

    const solution = window.APP_DATA?.last_solution;
    if (!solution || !solution.scheduled_events || solution.scheduled_events.length === 0) {
      if (emptyState) emptyState.classList.remove('hidden');
      if (wrapper) wrapper.classList.add('hidden');
      if (valBanner) valBanner.classList.add('hidden');
      return;
    }

    if (emptyState) emptyState.classList.add('hidden');
    if (wrapper) wrapper.classList.remove('hidden');

    // Update validation banner
    if (valBanner && solution.validation) {
      valBanner.classList.remove('hidden');
      const badge = document.getElementById('bannerValBadge');
      const text = document.getElementById('bannerValText');
      const v = solution.validation;
      if (v.overall_status === 'FULLY VALIDATED') {
        badge.className = 'val-badge badge-success';
        badge.textContent = 'FULLY VALIDATED (100% FEASIBLE)';
        text.textContent = 'All Hard Constraints Satisfied • G1/G2 Cohort Mappings Verified • 0 Clashes';
      } else if (v.overall_status === 'VALIDATED WITH WARNINGS') {
        badge.className = 'val-badge badge-warning';
        badge.textContent = 'VALIDATED WITH WARNINGS';
        const warnStr = (v.unverified_constraints || []).join('; ');
        text.textContent = `Provisional Schedule Feasible • Warnings: ${warnStr || 'Unverified constraints'}`;
      } else {
        badge.className = 'val-badge badge-danger';
        badge.textContent = 'VALIDATION ISSUES / INFEASIBLE';
        text.textContent = `${v.details ? v.details.length : 0} issue(s) detected.`;
      }
    }

    // Filter events according to current perspective and programme
    let allEvents = solution.scheduled_events;
    if (this.currentProgramme !== 'ALL') {
      allEvents = allEvents.filter(e => e.department === this.currentProgramme || e.department.includes(this.currentProgramme));
    }

    let filteredEvents = [];
    if (this.currentView === 'section') {
      filteredEvents = allEvents.filter(e =>
        e.section_ids.includes(this.currentFilterId) ||
        e.group_id === this.currentFilterId
      );
    } else if (this.currentView === 'faculty') {
      filteredEvents = allEvents.filter(e =>
        e.faculty_id === this.currentFilterId ||
        (e.faculty_ids && e.faculty_ids.includes(this.currentFilterId))
      );
    } else if (this.currentView === 'room') {
      filteredEvents = allEvents.filter(e => e.room_ids.includes(this.currentFilterId));
    } else {
      filteredEvents = allEvents; // Master View
    }

    const config = window.APP_DATA.config;
    const days = config.days;
    const periods = config.periods;
    const breaks = config.break_after_period || [];

    // Construct Table Matrix (Days as Rows, Periods as Columns)
    let html = `<table class="timetable-grid">
      <thead>
        <tr>
          <th style="width: 100px;">Day</th>`;

    periods.forEach((p, idx) => {
      html += `<th>
        <div>${p.name}</div>
        <span class="time-slot-header">${p.start_time} - ${p.end_time}</span>
      </th>`;
      if (breaks.includes(idx)) {
        html += `<th style="width: 50px; background-color: rgba(255,255,255,0.03);">
          <div>Break</div>
          <span class="time-slot-header">Lunch</span>
        </th>`;
      }
    });

    html += `</tr></thead><tbody>`;

    // Populate rows for each day
    days.forEach((dayName, dayIdx) => {
      html += `<tr>
        <th class="day-header">${dayName}</th>`;

      let periodIdx = 0;
      while (periodIdx < periods.length) {
        // Find events starting at (dayIdx, periodIdx)
        const eventsHere = filteredEvents.filter(
          e => e.day_index === dayIdx && e.start_period === periodIdx
        );

        // Check if there is an event spanning multiple periods from this start
        let colSpan = 1;
        if (eventsHere.length > 0) {
          const maxDur = Math.max(...eventsHere.map(e => e.duration));
          colSpan = maxDur;
        }

        html += `<td colspan="${colSpan}">`;

        if (eventsHere.length === 0) {
          // Empty slot
          html += `<div style="height: 100%; min-height: 48px;"></div>`;
        } else {
          eventsHere.forEach(ev => {
            const typeClass = `type-${ev.session_type.toLowerCase()}`;
            const isBundle = ev.allocation_mode === 'SIMULTANEOUS_BUNDLE' || ev.room_names.length > 1;
            const roomDisplay = isBundle
              ? `Bundle: ${ev.room_names.join(' + ')}`
              : (ev.room_names[0] || 'Room TBA');

            const facultyDisplay = (ev.faculty_names && ev.faculty_names.length > 0)
              ? ev.faculty_names.join(', ')
              : (ev.faculty_name || 'Faculty TBA');

            const cohortDisplay = ev.group_name
              ? `Group ${ev.group_name} [Cohort Group]`
              : `${ev.section_names.join(', ')} (${ev.total_student_strength} students)`;

            const reviewPill = ev.needs_review
              ? `<span class="badge badge-warning text-xs" title="${ev.review_reason || 'Incomplete source data'}">⚠️ Review</span>`
              : '';

            html += `
              <div class="event-tile ${typeClass}">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 4px;">
                  <span class="tile-code">${ev.course_code}</span>
                  <div style="display: flex; gap: 4px; align-items: center;">
                    ${reviewPill}
                    <span class="badge ${ev.session_type === 'Lecture' ? 'badge-info' : 'badge-purple'} text-xs">
                      ${ev.session_type} ${ev.duration > 1 ? `(${ev.duration} Periods)` : ''}
                    </span>
                  </div>
                </div>
                <div class="tile-name" title="${ev.course_name}">${ev.course_name}</div>
                <div class="tile-meta">
                  <span class="tile-badge tile-badge-faculty" title="Faculty / Co-Instructors">
                    👤 ${facultyDisplay}
                  </span>
                  <span class="tile-badge tile-badge-room" title="Allocated Venue">
                    🏛️ ${roomDisplay} ${isBundle ? '(Simultaneous)' : ''}
                  </span>
                  <span class="tile-badge" title="Student Cohort">
                    👥 ${cohortDisplay}
                  </span>
                </div>
              </div>
            `;
          });
        }

        html += `</td>`;

        // Check if a lunch break follows this period
        for (let s = 0; s < colSpan; s++) {
          const p = periodIdx + s;
          if (breaks.includes(p) && s === colSpan - 1) {
            html += `<td class="break-slot" title="Lunch Break">Lunch</td>`;
          }
        }

        periodIdx += colSpan;
      }

      html += `</tr>`;
    });

    html += `</tbody></table>`;
    wrapper.innerHTML = html;
  },
};
