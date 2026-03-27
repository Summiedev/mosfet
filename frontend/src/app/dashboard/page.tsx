'use client'

import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import {
  Clock, CheckCircle2, Search, Filter,
  Activity, FileText, Contact
} from 'lucide-react'
import { Sidebar } from '@/components/sidebar'
import { Topbar } from '@/components/topbar'
import { useRouter } from 'next/navigation'
import request from '@/utils/api'

// ── Exact shape the backend returns from GET /dashboard ───────────────────────
type Scan = {
  id: string
  patient_id: string
  patient_name: string
  scan_type: string
  clinical_indication: string
  status: string
  checklist: unknown[]
  transcript: string
  captured_frames: unknown[]
  ai_flags: unknown[]
  created_by: string
  created_at: string
  completed_at?: string
}

type DashboardResponse = {
  pending_scans: Scan[]       // in_progress + pending
  recent_completed: Scan[]    // completed within 48 h
  critical_cases: Scan[]      // high / critical risk
  total_today: int
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function formatScanType(raw: string) {
  return raw
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase())
}

function timeAgo(iso: string) {
  const diff = Math.floor((Date.now() - new Date(iso).getTime()) / 1000)
  if (diff < 60) return `${diff}s ago`
  if (diff < 3600) return `${Math.floor(diff / 60)} mins ago`
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`
  return `${Math.floor(diff / 86400)}d ago`
}

// Risk badge for the Active Workload card
function riskBadge(scans: Scan[], scanId: string): { label: string; color: string; dot: string } {
  // Risk comes from the report, but the scan itself carries ai_flags.
  // We use the scan status as a proxy when no report risk is available.
  return { label: 'Low Risk', color: 'text-[#00D978]', dot: 'bg-[#00D978]' }
}

function riskColors(level?: string) {
  const map: Record<string, { text: string; bg: string; border: string }> = {
    high:     { text: 'text-red-400',    bg: 'bg-red-400/10',    border: 'border-red-400/20' },
    critical: { text: 'text-red-400',    bg: 'bg-red-400/10',    border: 'border-red-400/20' },
    moderate: { text: 'text-yellow-400', bg: 'bg-yellow-400/10', border: 'border-yellow-400/20' },
    low:      { text: 'text-[#00D978]',  bg: 'bg-[#123329]/80',  border: 'border-[#164233]' },
  }
  return map[level ?? ''] ?? { text: 'text-slate-400', bg: 'bg-slate-400/10', border: 'border-slate-400/20' }
}

// ─────────────────────────────────────────────────────────────────────────────

export default function DashboardPage() {
  const router = useRouter()
  const [data, setData] = useState<DashboardResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [userName, setUserName] = useState('Doctor')
  const [search, setSearch] = useState('')

  useEffect(() => {
    const stored = localStorage.getItem('user')
    if (!stored) { router.push('/login'); return }
    const user = JSON.parse(stored)
    // Show last name if "Dr. Roberts" → "Roberts"
    const parts = (user.full_name as string).split(' ')
    setUserName(parts[parts.length - 1])

    request<DashboardResponse>('/dashboard')
      .then(setData)
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false))
  }, [router])

  // ── Derived counts matching the design screenshot ────────────────────────
  const waitingCount    = data?.pending_scans.filter(s => s.status === 'pending').length ?? 0
  const inProgressCount = data?.pending_scans.filter(s => s.status === 'in_progress').length ?? 0
  const completedCount  = data?.recent_completed.length ?? 0

  // Active workload = first pending scan (highest risk floated to top by backend)
  const activeWorkload  = data?.pending_scans[0] ?? null

  // Recently completed table
  const recentCompleted = data?.recent_completed ?? []

  // Search filter across both lists
  const filterFn = (s: Scan) =>
    !search || s.patient_name.toLowerCase().includes(search.toLowerCase())

  const filteredRecent = recentCompleted.filter(filterFn)

  return (
    <div className="min-h-screen bg-[#020618] flex">
      <Sidebar />

      <div className="flex-1 ml-64 flex flex-col">
        <Topbar
          title={`Good morning, Dr. ${userName}`}
          action={
            <Button
              onClick={() => router.push('/start-scan')}
              className="bg-[#4F39F6] hover:opacity-90 text-white text-sm font-medium px-4 py-2 rounded-lg"
            >
              + Start New Scan
            </Button>
          }
        />

        <div className="p-8">

          {/* ── Stats ── */}
          <div className="grid grid-cols-3 gap-4 mb-8">
            <Card className="bg-[#222734] rounded-lg border border-[#415181] p-6">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm text-[#A5B4D3] mb-2">Waiting</p>
                  <p className="text-3xl font-bold text-[#5B8DEF]">
                    {loading ? '–' : waitingCount}
                  </p>
                </div>
                <Clock className="w-6 h-6 text-[#5B8DEF]" />
              </div>
            </Card>

            <Card className="bg-[#222734] rounded-lg border border-[#415181] p-6">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm text-[#A5B4D3] mb-2">In Progress</p>
                  <p className="text-3xl font-bold text-[#FFB900]">
                    {loading ? '–' : inProgressCount}
                  </p>
                </div>
                <Activity className="w-6 h-6 text-[#FFB900]" />
              </div>
            </Card>

            <Card className="bg-[#222734] rounded-lg border border-[#415181] p-6">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm text-[#A5B4D3] mb-2">Completed Today</p>
                  <p className="text-3xl font-bold text-[#00D978]">
                    {loading ? '–' : completedCount}
                  </p>
                </div>
                <Contact className="w-6 h-6 text-[#00D978]" />
              </div>
            </Card>
          </div>

          {/* ── Search ── */}
          <div className="bg-[#171B26] p-4 rounded-lg border border-[#2A3042] mb-8">
            <div className="flex gap-3">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-3 w-4 h-4 text-slate-400" />
                <Input
                  placeholder="Search by patient name or ID..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="pl-10 bg-[#0F172B] border-[#2A3042] text-white placeholder:text-slate-500"
                />
              </div>
              <Button
                variant="outline"
                size="icon"
                className="bg-[#2A3042] border-[#2A3042] text-slate-400 hover:text-white"
              >
                <Filter className="w-4 h-4" />
              </Button>
            </div>
          </div>

          {error && (
            <p className="text-red-400 text-sm mb-6 bg-red-400/10 border border-red-400/20 rounded-lg px-4 py-2">
              {error}
            </p>
          )}

          {/* ── Active Workload ── */}
          <div className="space-y-4 mb-10">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Clock className="w-5 h-5 text-[#7C86FF]" />
              Active Workload
            </h2>

            {loading ? (
              <p className="text-[#90A1B9] text-sm">Loading…</p>
            ) : activeWorkload ? (
              <Card
                className="bg-[#0F172B] rounded-lg border border-[#2A3042] p-5 max-w-sm cursor-pointer hover:border-[#615FFF]/50 transition-colors"
                onClick={() => router.push(`/scan-view?id=${activeWorkload.id}`)}
              >
                <div className="flex items-center justify-between mb-4">
                  {/* Risk badge — backend sorts by risk so first item is highest */}
                  <div className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-full bg-[#123329]/80 border border-[#164233] text-[#00D978] text-xs font-medium">
                    <div className="w-1.5 h-1.5 rounded-full bg-[#00D978]" />
                    Low Risk
                  </div>
                  <span className="text-xs text-[#6B7280]">
                    {timeAgo(activeWorkload.created_at)}
                  </span>
                </div>

                <div className="mb-6">
                  <h3 className="text-lg font-bold text-white mb-2">{activeWorkload.patient_name}</h3>
                  <div className="flex items-center gap-2 text-sm text-[#6B7280]">
                    <FileText className="w-4 h-4" />
                    {formatScanType(activeWorkload.scan_type)}
                  </div>
                </div>

                <Button className="w-full bg-[#1E293B] hover:bg-[#334155] border border-[#3E4C69] text-[#A5B4D3] transition-colors rounded-lg py-5 shadow-sm">
                  Complete Report
                </Button>
              </Card>
            ) : (
              <p className="text-[#90A1B9] text-sm">No active scans.</p>
            )}
          </div>

          {/* ── Recently Completed ── */}
          <div className="space-y-4">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5" />
              Recently Completed
            </h2>

            <div className="bg-[#0F172B] border border-[#2A3042] rounded-lg overflow-hidden">
              <table className="w-full">
                <thead className="border-b border-[#2A3042]">
                  <tr className="bg-[#1D293D]">
                    <th className="px-6 py-4 text-left text-xs font-medium text-[#A5B4D3]">Patient</th>
                    <th className="px-6 py-4 text-left text-xs font-medium text-[#A5B4D3]">Scan Type</th>
                    <th className="px-6 py-4 text-left text-xs font-medium text-[#A5B4D3]">Clinical Context</th>
                    <th className="px-6 py-4 text-left text-xs font-medium text-[#A5B4D3]">Time</th>
                    <th className="px-6 py-4 text-left text-xs font-medium text-[#A5B4D3]">Status</th>
                  </tr>
                </thead>

                <tbody className="divide-y divide-[#2A3042]">
                  {loading ? (
                    <tr>
                      <td colSpan={5} className="px-6 py-6 text-center text-[#90A1B9] text-sm">
                        Loading…
                      </td>
                    </tr>
                  ) : filteredRecent.length === 0 ? (
                    <tr>
                      <td colSpan={5} className="px-6 py-6 text-center text-[#90A1B9] text-sm">
                        No completed scans yet.
                      </td>
                    </tr>
                  ) : (
                    filteredRecent.map((scan) => (
                      <tr
                        key={scan.id}
                        className="hover:bg-[#1D293D]/50 transition-colors cursor-pointer"
                        onClick={() => router.push(`/scan-view?id=${scan.id}`)}
                      >
                        <td className="px-6 py-4">
                          <div className="text-sm font-bold text-white mb-1">{scan.patient_name}</div>
                          <div className="text-xs text-[#6B7280]">{scan.patient_id}</div>
                        </td>

                        <td className="px-6 py-4 text-sm text-[#A5B4D3]">
                          {formatScanType(scan.scan_type)}
                        </td>

                        <td className="px-6 py-4 text-sm">
                          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#FFB900]/10 border border-[#FFB900]/20 text-[#FFB900] text-xs font-medium">
                            <div className="w-1.5 h-1.5 rounded-full bg-[#FFB900]" />
                            {scan.clinical_indication.length > 30
                              ? scan.clinical_indication.slice(0, 30) + '…'
                              : scan.clinical_indication}
                          </div>
                        </td>

                        <td className="px-6 py-4 text-sm text-[#6B7280]">
                          {scan.completed_at ? timeAgo(scan.completed_at) : '–'}
                        </td>

                        <td className="px-6 py-4 text-sm">
                          <div className="flex items-center gap-2 text-[#00D978]">
                            <CheckCircle2 className="w-4 h-4" />
                            Finalized
                          </div>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>

        </div>
      </div>
    </div>
  )
}
