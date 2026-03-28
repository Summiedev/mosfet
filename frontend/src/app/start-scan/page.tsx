'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card } from '@/components/ui/card'
import { ArrowLeft, Activity, Contact } from 'lucide-react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { Sidebar } from '@/components/sidebar'
import { patientsApi, scansApi } from '@/utils/endpoints'

const QUICK_REASONS = [
  "There's a lump",
  'Routine screening',
  'Follow-up on previous mass',
]

const SCAN_TYPES = [
  'Fetal Ultrasound',
  'Breast Ultrasound',
  'Abdominal Ultrasound',
  'Thyroid Ultrasound',
]

export default function StartScanPage() {
  const router = useRouter()
  const [patientName, setPatientName] = useState('')
  const [patientPhone, setPatientPhone] = useState('')
  const [scanType, setScanType] = useState('')
  const [selectedReasons, setSelectedReasons] = useState<string[]>([])
  const [customReason, setCustomReason] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const toggleReason = (r: string) => {
    setSelectedReasons((prev) =>
      prev.includes(r) ? prev.filter((x) => x !== r) : [...prev, r]
    )
  }

  const handleStartScan = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!patientName.trim() || !scanType.trim()) {
      setError('Patient name and scan type are required.')
      return
    }

    setError('')
    setLoading(true)

    try {
      const patient = await patientsApi.create({
        name: patientName.trim(),
        phone: patientPhone.trim() || undefined,
      })

      const indication =
        [...selectedReasons, customReason.trim()].filter(Boolean).join('; ') ||
        'Not specified'

      const scan = await scansApi.create({
        patient_id: patient.id,
        scan_type: scanType,
        clinical_indication: indication,
      })

      router.push(`/scan-view?id=${scan.id}`)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to start scan')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#020618] flex">
      <Sidebar />

      <div className="flex-1 ml-64 p-8">
        <div className="flex items-center gap-4 mb-8 pb-6 border-b border-[#1E2433]">
          <Link href="/dashboard">
            <Button variant="ghost" size="icon" className="text-[#9CA3AF] hover:text-white">
              <ArrowLeft className="w-5 h-5" />
            </Button>
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-white">Start New Scan</h1>
            <p className="text-sm text-[#9CA3AF]">
              Enter minimal details to anchor the scan in clinical context.
            </p>
          </div>
        </div>

        <Card className="bg-[#0F172B] border-[#1D293D] border-t-2 border-b-2 p-8 max-w-2xl mx-auto mt-10">
          <form className="space-y-6" onSubmit={handleStartScan}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-200 flex items-center gap-2">
                  <Contact className="w-5 h-5 text-[#7C86FF]" />
                  Patient Name
                </label>
                <Input
                  placeholder="e.g. Joy Okafor"
                  value={patientName}
                  onChange={(e) => setPatientName(e.target.value)}
                  className="bg-[#020618] border-slate-700/50 text-white placeholder:text-slate-500"
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-200 flex items-center gap-2">
                  <Activity className="w-5 h-5 text-[#7C86FF]" />
                  Scan Type
                </label>
                <Input
                  placeholder="e.g. Breast Ultrasound"
                  value={scanType}
                  onChange={(e) => setScanType(e.target.value)}
                  className="bg-[#020618] border-slate-700/50 text-white placeholder:text-slate-500"
                />
              </div>
            </div>

            {error && (
              <p className="text-sm text-red-400 bg-red-400/10 border border-red-400/20 rounded-lg px-4 py-2">
                {error}
              </p>
            )}

            <div className="space-y-2">
              <label className="text-sm font-medium text-[#CAD5E2]">Patient Phone (optional)</label>
              <Input
                placeholder="+234 XXX XXX XXXX"
                value={patientPhone}
                onChange={(e) => setPatientPhone(e.target.value)}
                className="bg-[#020618] border-[#314158] text-white placeholder-slate-500"
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-[#CAD5E2]">Scan Type *</label>
              <div className="grid grid-cols-2 gap-2">
                {SCAN_TYPES.map((t) => (
                  <button
                    key={t}
                    type="button"
                    onClick={() => setScanType(t)}
                    className={`text-sm px-4 py-2 rounded-lg border transition-colors ${
                      scanType === t
                        ? 'bg-[#4F39F6] border-[#4F39F6] text-white'
                        : 'bg-[#020618] border-[#314158] text-[#90A1B9] hover:border-[#615FFF]'
                    }`}
                  >
                    {t}
                  </button>
                ))}
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-[#CAD5E2]">Clinical Indication</label>
              <div className="flex flex-wrap gap-2 mb-2">
                {QUICK_REASONS.map((r) => (
                  <button
                    key={r}
                    type="button"
                    onClick={() => toggleReason(r)}
                    className={`text-xs px-3 py-1.5 rounded-full border transition-colors ${
                      selectedReasons.includes(r)
                        ? 'bg-[#4F39F6] border-[#4F39F6] text-white'
                        : 'bg-transparent border-[#314158] text-[#90A1B9] hover:border-[#615FFF]'
                    }`}
                  >
                    {r}
                  </button>
                ))}
              </div>
              <Input
                placeholder="Or type a custom reason…"
                value={customReason}
                onChange={(e) => setCustomReason(e.target.value)}
                className="bg-[#020618] border-[#314158] text-white placeholder-slate-500"
              />
            </div>

            <Button
              type="submit"
              disabled={loading}
              className="w-full bg-[#4F39F6] hover:opacity-90 text-white font-medium py-2 rounded-lg"
            >
              {loading ? 'Starting…' : 'Start Scan →'}
            </Button>
          </form>
        </Card>
      </div>
    </div>
  )
}
