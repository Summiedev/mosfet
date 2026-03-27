'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { ArrowLeft, AlertCircle } from 'lucide-react'
import Link from 'next/link'
import { Sidebar } from '@/components/sidebar'

const QUICK_REASONS = [
    "There's a lump",
    'Routine screening',
    'Follow-up on previous mass'
]

export default function StartScanPage() {
    const [patientName, setPatientName] = useState('')
    const [scanType, setScanType] = useState('')
    const [reason, setReason] = useState('')
    const [selectedReasons, setSelectedReasons] = useState<string[]>([])

    const toggleReason = (r: string) => {
        setSelectedReasons(prev =>
            prev.includes(r) ? prev.filter(x => x !== r) : [...prev, r]
        )
    }

    const handleStartScan = () => {
        // Handle scan start
    }

    return (
        <div className="min-h-screen bg-[#020618] flex">
            <Sidebar />

            {/* Main Content */}
            <div className="flex-1 ml-64 p-8">
                {/* Header */}
                <div className="flex items-center gap-4 mb-8">
                    <Link href="/dashboard">
                        <Button variant="ghost" size="icon" className="text-slate-400 hover:text-slate-300">
                            <ArrowLeft className="w-5 h-5" />
                        </Button>
                    </Link>
                    <div>
                        <h1 className="text-3xl font-bold text-white">Start New Scan</h1>
                        <p className="text-sm text-slate-400">Enter minimal details to anchor the scan in clinical context.</p>
                    </div>
                </div>

                {/* Form Card */}
                <Card className="bg-[#0F172B] border-[#1D293D] border-t-2 border-b-2 p-8 max-w-2xl">
                    <form className="space-y-6">
                        {/* Patient Info Row */}
                        <div className="grid grid-cols-2 gap-6">
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-slate-200 flex items-center gap-2">
                                    <div className="w-4 h-4 rounded-full border border-blue-400" />
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
                                    <div className="w-4 h-4 rounded-full border border-blue-400" />
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

                        {/* Why is this scan being done */}
                        <div className="space-y-3">
                            <div className="flex items-center gap-2 text-amber-400">
                                <AlertCircle className="w-4 h-4" />
                                <label className="font-semibold">Why is this scan being done?</label>
                            </div>
                            <p className="text-sm text-slate-400">
                                Provide brief clinical context. E.g. &quot;Patient reports a palpable lump in the upper outer quadrant.&quot;
                            </p>
                            <textarea
                                placeholder="Enter reason or clinical indication..."
                                value={reason}
                                onChange={(e) => setReason(e.target.value)}
                                className="w-full bg-[#020618] border border-slate-700/50 rounded-lg p-3 text-white placeholder:text-slate-500 text-sm"
                                rows={4}
                            />
                            <div className="flex gap-2 flex-wrap">
                                {QUICK_REASONS.map((r) => (
                                    <Badge
                                        key={r}
                                        onClick={() => toggleReason(r)}
                                        className={`cursor-pointer transition-colors ${selectedReasons.includes(r)
                                                ? 'bg-[slate-600] text-white'
                                                : 'bg-slate-700/50 text-slate-300 hover:bg-slate-600'
                                            }`}
                                    >
                                        {r}
                                    </Badge>
                                ))}
                            </div>
                        </div>

                        {/* Note */}
                        <div className="bg-slate-700/30 border border-slate-600/50 rounded-lg p-4">
                            <p className="text-xs text-slate-300">
                                <strong>Note:</strong> Date of arrival is automatically recorded. Clinical context is critical for accurate scanning and reporting.
                            </p>
                        </div>

                        {/* Start Button */}
                        <Button
                            type="button"
                            onClick={handleStartScan}
                            className="w-full bg-[#4F39F6] hover:to-purple-700 text-white font-medium py-3 rounded-lg transition-all"
                        >
                            Start Scan
                        </Button>
                    </form>
                </Card>
            </div>
        </div>
    )
}
