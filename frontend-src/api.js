const BASE = '/api';

async function req(method, path, body) {
  const res = await fetch(BASE + path, {
    method,
    credentials: 'include',
    headers: body ? { 'Content-Type': 'application/json' } : {},
    body: body ? JSON.stringify(body) : undefined,
  });
  if (res.status === 204) return null;
  const data = await res.json();
  if (!res.ok) throw new Error(data.error ?? 'Request failed');
  return data;
}

export const api = {
  // Auth
  getMe:   ()               => req('GET',  '/auth/me'),
  login:   (username, password) => req('POST', '/auth/login', { username, password }),
  logout:  ()               => req('POST', '/auth/logout'),

  // Boxes
  getBoxes:      ()                => req('GET',    '/boxes'),
  getBox:        (id)              => req('GET',    `/boxes/${id}`),
  createBox:     (body)            => req('POST',   '/boxes', body),
  updateBox:     (id, body)        => req('PUT',    `/boxes/${id}`, body),
  deleteBox:     (id)              => req('DELETE', `/boxes/${id}`),
  getBoxHistory: (id)              => req('GET',    `/boxes/${id}/history`),
  revertBox:     (id, versionId)   => req('POST',   `/boxes/${id}/revert/${versionId}`),
  emptyBox:      (id)              => req('POST',   `/boxes/${id}/empty`),

  // Tubes
  getTubes:           ()                    => req('GET',    '/tubes'),
  bulkAssignTubes:    (tubeIds, boxId)     => req('POST',   '/tubes/bulk-assign', { tube_ids: tubeIds, box_id: boxId }),
  getTube:        (id)             => req('GET',    `/tubes/${id}`),
  createTube:     (body)           => req('POST',   '/tubes', body),
  updateTube:     (id, body)       => req('PUT',    `/tubes/${id}`, body),
  deleteTube:     (id)             => req('DELETE', `/tubes/${id}`),
  getTubeHistory: (id)             => req('GET',    `/tubes/${id}/history`),
  revertTube:     (id, versionId)  => req('POST',   `/tubes/${id}/revert/${versionId}`),

  // Utilities
  scan:    (barcode) => req('GET', `/scan/${encodeURIComponent(barcode)}`),
  search:  (q)       => req('GET', `/search?q=${encodeURIComponent(q)}`),
  version: ()        => req('GET', '/version'),
};
