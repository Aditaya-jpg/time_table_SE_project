<%@ page language="java" pageEncoding="utf-8" contentType="text/html;charset=utf-8"%>
<%--
 * Licensed to The Apereo Foundation under one or more contributor license
 * agreements. See the NOTICE file distributed with this work for
 * additional information regarding copyright ownership.
--%>
<%@ page import="org.unitime.timetable.util.Constants" %>
<%@ taglib prefix="s" uri="/struts-tags" %>
<%@ taglib prefix="tt" uri="http://www.unitime.org/tags-custom" %>
<%@ taglib prefix="loc" uri="http://www.unitime.org/tags-localization" %>
<loc:bundle name="CourseMessages">

<style>
	#unitime-Header, .unitime-PageHeader {
		display: none !important;
	}
</style>

<s:if test="message != null && !message.isEmpty()">
	<div class='messages' style="margin-bottom: 24px;">
		<div class='WelcomeRowHead'><loc:message name="sectSystemMessages"/></div>
		<div class='message'><s:property value="message" escapeHtml="false"/></div>
	</div>
</s:if>

<div class="apple-dashboard">
	<!-- Hero Section: Apple Keynote Minimalism -->
	<section class="apple-hero">
		<div class="apple-hero-eyebrow">
			<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
				<circle cx="12" cy="12" r="10"></circle>
				<polyline points="12 6 12 12 16 14"></polyline>
			</svg>
			<span>UniTime <%=Constants.getVersion()%> &bull; Enterprise Timetabling</span>
		</div>
		<h1>Intelligent scheduling.<br>At campus scale.</h1>
		<p>
			Coordinate complex university operations with mathematical precision. Orchestrate course offerings,
			student sectioning, examination periods, and campus facilities in real time.
		</p>
		<div class="apple-hero-cta">
			<a href="classSearch.action" class="apple-btn-primary">
				<span>Open Class Search</span>
				<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
					<polyline points="9 18 15 12 9 6"></polyline>
				</svg>
			</a>
			<a href="timetableGrid.action" class="apple-btn-link">
				<span>View Timetable Matrix</span>
				<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
					<polyline points="9 18 15 12 9 6"></polyline>
				</svg>
			</a>
		</div>
	</section>

	<!-- Software Preview Canvas (macOS Window Presentation) -->
	<div class="apple-showcase-canvas">
		<div class="apple-canvas-header">
			<div class="apple-window-dot apple-dot-red"></div>
			<div class="apple-window-dot apple-dot-yellow"></div>
			<div class="apple-window-dot apple-dot-green"></div>
			<div class="apple-canvas-title">UniTime Control Center &mdash; Operations Live</div>
		</div>
		<div class="apple-canvas-body">
			<div class="apple-stats-ribbon">
				<div class="apple-stat-item">
					<div class="apple-stat-number">2</div>
					<div class="apple-stat-label">Active Academic Sessions</div>
				</div>
				<div class="apple-stat-item">
					<div class="apple-stat-number">5</div>
					<div class="apple-stat-label">CPSolver Engines Online</div>
				</div>
				<div class="apple-stat-item">
					<div class="apple-stat-number">Superuser</div>
					<div class="apple-stat-label">Full Administrative Access</div>
				</div>
				<div class="apple-stat-item">
					<div class="apple-stat-number">100%</div>
					<div class="apple-stat-label">Features &amp; Modules Unlocked</div>
				</div>
			</div>

			<!-- Quick Context Bar -->
			<div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 16px;">
				<div style="display: flex; align-items: center; gap: 12px;">
					<div style="width: 32px; height: 32px; border-radius: 8px; background: var(--surface-tertiary); display: flex; align-items: center; justify-content: center; color: var(--apple-blue);">
						<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
							<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
							<circle cx="12" cy="7" r="4"></circle>
						</svg>
					</div>
					<div>
						<div style="font-size: 13px; font-weight: 600; color: var(--text-primary);">Logged in as Abraham Root (Administrator)</div>
						<div style="font-size: 12px; color: var(--text-secondary);">Superuser privileges granted across all academic departments and terms.</div>
					</div>
				</div>
				<a href="selectPrimaryRole.action" class="apple-pill-btn">Change Session / Role</a>
			</div>
		</div>
	</div>

	<!-- Section Header -->
	<div class="apple-section-header">
		<div class="apple-section-eyebrow">Academic Operations</div>
		<h2 class="apple-section-title">Designed for every facet of campus scheduling.</h2>
	</div>

	<!-- Story Deck 1: Asymmetric 2-Column Bento Deck -->
	<div class="apple-feature-deck-2">
		<!-- Card 1: Course Timetabling Studio (Wide Hero Bento) -->
		<div class="apple-bento-card">
			<div>
				<div class="apple-bento-header">
					<span class="apple-section-eyebrow">Timetabling Studio</span>
					<span style="font-size: 11px; font-weight: 600; color: var(--apple-green); background: var(--apple-green-subtle); padding: 3px 8px; border-radius: 12px;">ACTIVE</span>
				</div>
				<h3 class="apple-bento-title">Course Timetabling</h3>
				<p class="apple-bento-desc">
					Formulate optimal schedules for lectures, recitations, and laboratories. Satisfy instructor availability,
					space limits, and student curriculum requirements simultaneously with constraint optimization.
				</p>
			</div>
			<div class="apple-pill-group">
				<a href="classSearch.action" class="apple-pill-btn-prominent">Class Search</a>
				<a href="timetableGrid.action" class="apple-pill-btn">Timetable Matrix</a>
				<a href="gwt.jsp?page=offerings" class="apple-pill-btn">Instructional Offerings</a>
				<a href="gwt.jsp?page=solver" class="apple-pill-btn">Course Solver</a>
				<a href="gwt.jsp?page=curricula" class="apple-pill-btn">Curricula</a>
			</div>
		</div>

		<!-- Card 2: Student Online Sectioning -->
		<div class="apple-bento-card">
			<div>
				<div class="apple-bento-header">
					<span class="apple-section-eyebrow">Student Sectioning</span>
					<span style="font-size: 11px; font-weight: 600; color: var(--apple-green); background: var(--apple-green-subtle); padding: 3px 8px; border-radius: 12px;">ACTIVE</span>
				</div>
				<h3 class="apple-bento-title">Student Scheduling</h3>
				<p class="apple-bento-desc">
					Intelligent conflict-free section assignments, real-time waitlists, advisor schedule approvals,
					and student course demand projections.
				</p>
			</div>
			<div class="apple-pill-group">
				<a href="gwt.jsp?page=sectioning" class="apple-pill-btn-prominent">Scheduling Assistant</a>
				<a href="sectioning.action" class="apple-pill-btn">Dashboard</a>
				<a href="gwt.jsp?page=courseDemands" class="apple-pill-btn">Course Demands</a>
			</div>
		</div>
	</div>

	<!-- Story Deck 2: 3-Column Bento Deck -->
	<div class="apple-feature-deck-3">
		<!-- Card 3: Examination Operations -->
		<div class="apple-bento-card">
			<div>
				<div class="apple-bento-header">
					<span class="apple-section-eyebrow">Assessments</span>
					<span style="font-size: 11px; font-weight: 600; color: var(--apple-green); background: var(--apple-green-subtle); padding: 3px 8px; border-radius: 12px;">ACTIVE</span>
				</div>
				<h3 class="apple-bento-title">Examinations</h3>
				<p class="apple-bento-desc">
					Automated midterm and final exam scheduling with individual student seating layouts and strict conflict verification.
				</p>
			</div>
			<div class="apple-pill-group">
				<a href="examSolver.action" class="apple-pill-btn-prominent">Exam Solver</a>
				<a href="gwt.jsp?page=assignedExams" class="apple-pill-btn">Assigned Exams</a>
				<a href="gwt.jsp?page=exams" class="apple-pill-btn">Exams Directory</a>
			</div>
		</div>

		<!-- Card 4: Campus Spaces & Events -->
		<div class="apple-bento-card">
			<div>
				<div class="apple-bento-header">
					<span class="apple-section-eyebrow">Facilities</span>
					<span style="font-size: 11px; font-weight: 600; color: var(--apple-green); background: var(--apple-green-subtle); padding: 3px 8px; border-radius: 12px;">ACTIVE</span>
				</div>
				<h3 class="apple-bento-title">Events &amp; Spaces</h3>
				<p class="apple-bento-desc">
					Comprehensive campus room directories, real-time space booking requests, event approval workflows, and room utilization.
				</p>
			</div>
			<div class="apple-pill-group">
				<a href="gwt.jsp?page=rooms" class="apple-pill-btn-prominent">Room Availability</a>
				<a href="gwt.jsp?page=events" class="apple-pill-btn">Events Portal</a>
				<a href="events.action" class="apple-pill-btn">Add Event</a>
			</div>
		</div>

		<!-- Card 5: Instructors & Faculty -->
		<div class="apple-bento-card">
			<div>
				<div class="apple-bento-header">
					<span class="apple-section-eyebrow">Faculty</span>
					<span style="font-size: 11px; font-weight: 600; color: var(--apple-green); background: var(--apple-green-subtle); padding: 3px 8px; border-radius: 12px;">ACTIVE</span>
				</div>
				<h3 class="apple-bento-title">Instructors</h3>
				<p class="apple-bento-desc">
					Manage faculty assignments, workload policies, scheduling preferences, instructor attributes, and preference surveys.
				</p>
			</div>
			<div class="apple-pill-group">
				<a href="gwt.jsp?page=instructors" class="apple-pill-btn-prominent">Instructors</a>
				<a href="gwt.jsp?page=instructorattributes" class="apple-pill-btn">Attributes</a>
				<a href="gwt.jsp?page=instructorSurvey" class="apple-pill-btn">Faculty Survey</a>
			</div>
		</div>
	</div>

	<!-- Administrative Control Strip -->
	<div class="apple-admin-strip">
		<div class="apple-admin-info">
			<div class="apple-admin-icon">
				<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
					<circle cx="12" cy="12" r="3"></circle>
					<path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
				</svg>
			</div>
			<div>
				<div style="font-size: 15px; font-weight: 600; color: var(--text-primary); margin-bottom: 2px;">Campus Administration &amp; Configuration</div>
				<div style="font-size: 13px; color: var(--text-secondary);">Manage academic terms, department mappings, user roles, solver profiles, and data integrations.</div>
			</div>
		</div>
		<div class="apple-pill-group">
			<a href="gwt.jsp?page=sessions" class="apple-pill-btn-prominent">Academic Sessions</a>
			<a href="gwt.jsp?page=departments" class="apple-pill-btn">Departments</a>
			<a href="gwt.jsp?page=roles" class="apple-pill-btn">Roles &amp; Permissions</a>
			<a href="gwt.jsp?page=users" class="apple-pill-btn">User Accounts</a>
		</div>
	</div>
</div>

<script type="text/javascript">
	// Clean up legacy classes
	var pageEl = document.getElementById('unitime-Page');
	if (pageEl) { 
		pageEl.className = 'body unitime-MainContent-rework'; 
		pageEl.style.width = '100%';
		pageEl.style.maxWidth = '100%';
		pageEl.style.border = 'none';
	}
	var contentEl = document.getElementById('UniTimeGWT:Content');
	if (contentEl) { 
		contentEl.className = 'unitime-MainContent-rework'; 
		contentEl.style.width = '100%';
		contentEl.style.height = 'auto';
	}
	
	// Hide registration notification elements
	var regEl = document.getElementById('UniTimeGWT:Registration');
	if (regEl) { regEl.style.display = 'none'; }
	var rightCells = document.querySelectorAll('.unitime-Footer .right, .unitime-Footer .cell.right');
	rightCells.forEach(function(el) { el.style.display = 'none'; });

	if (parent && parent.hideGwtDialog && parent.refreshPage) {
		parent.hideGwtDialog();
		parent.refreshPage();
	}
</script>
</loc:bundle>