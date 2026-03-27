/**
 * RadFlow API endpoints
 * Every backend route is mapped here. Import what you need in each page.
 *
 * Usage:
 *   import { authApi } from '@/utils/endpoints'
 *   const { access_token, user } = await authApi.login({ email, password })
 */

import request from './api'

// ─── Types (mirror your backend schemas) ──────────────────────────────────────

export type User = {
  id: string
  full_name: string
  email: string
  phone: string
  role: string
  otp_verified: boolean
  created_at: string
}

export type AuthResponse = {
  access_token: string
  user: User
}

export type Patient = {
  id: string
  name: string
  age?: number
  sex?: string
  phone?: string
  created_by: string
  created_at: string
}

export type Scan = {
  id: string
  patient_id: string
  patient_name: string
  scan_type: string
  clinical_indication: string
  status: string
  checklist: unknown[]
  transcript: string
  captured_frames: string[]
  ai_flags: unknown[]
  created_by: string
  created_at: string
  completed_at?: string
}

export type DashboardData = {
  pending_scans: Scan[]      // in_progress + pending, risk-sorted
  recent_completed: Scan[]   // completed within 48 h
  critical_cases: Scan[]     // high / critical risk
  total_today: number
}

export type Report = {
  id: string
  scan_id: string
  risk?: string
  findings?: string
  is_finalized: boolean
  created_at: string
}

export type MediaUpload = {
  id: string
  url: string
  public_id: string
}

// ─── Auth ──────────────────────────────────────────────────────────────────────

export const authApi = {
  /** POST /auth/register */
  register: (data: { full_name: string; email: string; phone: string; password: string; role: string }) =>
    request<AuthResponse>('/auth/register', { method: 'POST', body: data, auth: false }),

  /** POST /auth/login */
  login: (data: { email: string; password: string }) =>
    request<AuthResponse>('/auth/login', { method: 'POST', body: data, auth: false }),

  /** GET /auth/me */
  me: () => request<User>('/auth/me'),

  /** POST /auth/logout */
  logout: () => request<{ message: string }>('/auth/logout', { method: 'POST' }),

  /** POST /auth/otp/send */
  sendOtp: (phone: string) =>
    request<{ message: string }>('/auth/otp/send', { method: 'POST', body: { phone } }),

  /** POST /auth/otp/verify */
  verifyOtp: (phone: string, code: string) =>
    request<{ message: string; otp_verified: boolean }>('/auth/otp/verify', {
      method: 'POST',
      body: { phone, code },
    }),
}

// ─── Patients ─────────────────────────────────────────────────────────────────

export const patientsApi = {
  /** POST /patients */
  create: (data: { name: string; age?: number; sex?: string; phone?: string }) =>
    request<Patient>('/patients', { method: 'POST', body: data }),

  /** GET /patients/:id */
  getById: (patientId: string) => request<Patient>(`/patients/${patientId}`),
}

// ─── Scans ────────────────────────────────────────────────────────────────────

export const scansApi = {
  /** GET /dashboard */
  getDashboard: () => request<DashboardData>('/dashboard'),

  /** POST /scans */
  create: (data: { patient_id: string; scan_type: string; clinical_indication: string }) =>
    request<Scan>('/scans', { method: 'POST', body: data }),

  /** GET /scans/:id */
  getById: (scanId: string) => request<Scan>(`/scans/${scanId}`),

  /** PATCH /scans/:id */
  update: (scanId: string, data: Partial<Scan>) =>
    request<Scan>(`/scans/${scanId}`, { method: 'PATCH', body: data }),

  /** POST /scans/:id/validate */
  validate: (scanId: string) => request(`/scans/${scanId}/validate`, { method: 'POST' }),

  /** POST /scans/:id/complete */
  complete: (scanId: string) => request<Scan>(`/scans/${scanId}/complete`, { method: 'POST' }),

  /** GET /scans/:id/ai-events */
  getAiEvents: (scanId: string) => request(`/scans/${scanId}/ai-events`),
}

// ─── Reports ──────────────────────────────────────────────────────────────────

export const reportsApi = {
  /** GET /reports/:id */
  getById: (reportId: string) => request<Report>(`/reports/${reportId}`),

  /** GET /reports/by-scan/:scanId */
  getByScan: (scanId: string) => request<Report>(`/reports/by-scan/${scanId}`),

  /** PATCH /reports/:id */
  update: (reportId: string, data: Partial<Report>) =>
    request<Report>(`/reports/${reportId}`, { method: 'PATCH', body: data }),

  /** PATCH /reports/:id/risk */
  updateRisk: (reportId: string, risk: string) =>
    request<Report>(`/reports/${reportId}/risk`, { method: 'PATCH', body: { risk } }),

  /** POST /reports/:id/apply-template/:templateId */
  applyTemplate: (reportId: string, templateId: string) =>
    request<Report>(`/reports/${reportId}/apply-template/${templateId}`, { method: 'POST' }),

  /** POST /reports/:id/finalize */
  finalize: (reportId: string) =>
    request<Report>(`/reports/${reportId}/finalize`, { method: 'POST' }),
}

// ─── Media ────────────────────────────────────────────────────────────────────

export const mediaApi = {
  /** POST /media/upload (multipart) */
  upload: async (file: File): Promise<MediaUpload> => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null
    const formData = new FormData()
    formData.append('file', file)

    const res = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/media/upload`,
      {
        method: 'POST',
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        body: formData,
      }
    )
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Upload failed' }))
      throw new Error(err.detail)
    }
    return res.json()
  },

  /** POST /media/upload-base64 */
  uploadBase64: (data: { base64: string; filename: string }) =>
    request<MediaUpload>('/media/upload-base64', { method: 'POST', body: data }),

  /** GET /media */
  list: () => request<MediaUpload[]>('/media'),

  /** DELETE /media/:id */
  delete: (mediaId: string) => request<void>(`/media/${mediaId}`, { method: 'DELETE' }),
}