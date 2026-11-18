/**
 * API Client for College Timetable Scheduling Demo
 */

const API = {
  async getData() {
    const res = await fetch('/api/data');
    if (!res.ok) throw new Error('Failed to fetch timetable data');
    return await res.json();
  },

  async loadSampleData() {
    const res = await fetch('/api/sample-data', { method: 'POST' });
    if (!res.ok) throw new Error('Failed to load sample dataset');
    return await res.json();
  },

  async resetData() {
    const res = await fetch('/api/reset-data', { method: 'POST' });
    if (!res.ok) throw new Error('Failed to reset dataset');
    return await res.json();
  },

  async generateTimetable() {
    const res = await fetch('/api/generate', { method: 'POST' });
    if (!res.ok) throw new Error('Failed to generate timetable');
    return await res.json();
  },

  async getSolution() {
    const res = await fetch('/api/solution');
    if (!res.ok) throw new Error('Failed to fetch active solution');
    return await res.json();
  },

  // Sections
  async addSection(data) {
    const res = await fetch('/api/sections', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to add section');
    return await res.json();
  },

  async updateSection(id, data) {
    const res = await fetch(`/api/sections/${encodeURIComponent(id)}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to update section');
    return await res.json();
  },

  async deleteSection(id) {
    const res = await fetch(`/api/sections/${encodeURIComponent(id)}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Failed to delete section');
    return await res.json();
  },

  // Faculty
  async addFaculty(data) {
    const res = await fetch('/api/faculty', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to add faculty');
    return await res.json();
  },

  async updateFaculty(id, data) {
    const res = await fetch(`/api/faculty/${encodeURIComponent(id)}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to update faculty');
    return await res.json();
  },

  async deleteFaculty(id) {
    const res = await fetch(`/api/faculty/${encodeURIComponent(id)}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Failed to delete faculty');
    return await res.json();
  },

  // Rooms
  async addRoom(data) {
    const res = await fetch('/api/rooms', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to add room');
    return await res.json();
  },

  async updateRoom(id, data) {
    const res = await fetch(`/api/rooms/${encodeURIComponent(id)}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to update room');
    return await res.json();
  },

  async deleteRoom(id) {
    const res = await fetch(`/api/rooms/${encodeURIComponent(id)}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Failed to delete room');
    return await res.json();
  },

  // Courses
  async addCourse(data) {
    const res = await fetch('/api/courses', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to add course');
    return await res.json();
  },

  async updateCourse(id, data) {
    const res = await fetch(`/api/courses/${encodeURIComponent(id)}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to update course');
    return await res.json();
  },

  async deleteCourse(id) {
    const res = await fetch(`/api/courses/${encodeURIComponent(id)}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Failed to delete course');
    return await res.json();
  },

  // Course Groups (G1 / G2)
  async getGroups() {
    const res = await fetch('/api/groups');
    if (!res.ok) throw new Error('Failed to fetch course groups');
    return await res.json();
  },

  async updateGroupMapping(groupId, sectionIds) {
    const res = await fetch(`/api/groups/${encodeURIComponent(groupId)}/mapping`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ section_ids: sectionIds }),
    });
    if (!res.ok) throw new Error('Failed to update group mapping');
    return await res.json();
  },
};
