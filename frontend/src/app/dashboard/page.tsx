'use client'

import { useEffect, useState } from 'react'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Clock, CheckCircle2, Activity } from 'lucide-react'
import { Sidebar } from '@/components/sidebar'
import { Topbar } from '@/components/topbar'
import { scansApi, type DashboardData, type Scan } from '@/utils/endpoints'
import { useRouter } from 'next/navigation'

export default function DashboardPage() {
    const router = useRouter()
    const [data, setData] = useState<DashboardData | null>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')
    const [userName, setUserName] = useState('Doctor')

    useEffect(() => {
        const stored = localStorage.getItem('user')
        if (!stored) { router.push('/login'); return }
        const user = JSON.parse(stored)
        setUserName(user.full_name?.split(' ')[1] || user.full_name)

        scansApi.getDashboard()
            .then(setData)
            .catch((err) => setError(err.message))
            .finally(() => setLoading(false))
    }, [router])

    const statusBadge = (status: string) => {
        const map: Record<string, string> = {
            waiting: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
            in_progress: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
            completed: 'bg-green-500/20 text-green-400 border-green-500/30',
            finalized: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
        }
        return map[status.toLowerCase()] ?? 'bg-slate-500/20 text-slate-400'
    }

    return (
        <div className="min-h-screen bg-[#020618] flex">
            <Sidebar />
            <div className="flex-1 ml-64 flex flex-col">
                <Topbar title={`Good morning, Dr. ${userName}`} />
                <div className="p-8">

                    {/* Stats */}
                    <div className="grid grid-cols-3 gap-4 mb-8">
                        <Card className="bg-[#222734] rounded-lg border border-[#415181] p-6">
                            <div className="flex items-start justify-between">
                                <div>
                                    <p className="text-sm text-[#A5B4D3] mb-2">Waiting</p>
                                    <p className="text-3xl font-bold text-[#5B8DEF]">
                                        {loading ? '–' : data?.waiting ?? 0}
                                    </p>
                                </div>
                                <Clock className="w-6 h-6 text-[#5B8DEF]" />
                            </div>
                        </Card>

                        <Card className="bg-[#222734] rounded-lg border border-[#415181] p-6">
                            <div className="flex items-start justify-between">
                                <div>
                                    <p className="text-sm text-[#A5B4D3] mb-2">Completed</p>
                                    <p className="text-3xl font-bold text-[#34D399]">
                                        {loading ? '–' : data?.completed ?? 0}
                                    </p>
                                </div>
                                <CheckCircle2 className="w-6 h-6 text-[#34D399]" />
                            </div>
                        </Card>

                        <Card className="bg-[#222734] rounded-lg border border-[#415181] p-6">
                            <div className="flex items-start justify-between">
                                <div>
                                    <p className="text-sm text-[#A5B4D3] mb-2">Total Scans</p>
                                    <p className="text-3xl font-bold text-white">
                                        {loading ? '–' : data?.total ?? 0}
                                    </p>
                                </div>
                                <Activity className="w-6 h-6 text-white" />
                            </div>
                        </Card>
                    </div>

                    {/* Recent Scans */}
                    <div>
                        <h2 className="text-lg font-semibold text-white mb-4">Recent Scans</h2>
                        {error && (
                            <p className="text-red-400 text-sm mb-4">{error}</p>
                        )}
                        {loading ? (
                            <p className="text-[#90A1B9] text-sm">Loading scans…</p>
                        ) : (
                            <div className="space-y-3">
                                {(data?.recent_scans ?? []).map((scan: Scan) => (
                                    <Card
                                        key={scan.id}
                                        className="bg-[#222734] border border-[#415181] p-4 flex items-center justify-between cursor-pointer hover:border-[#615FFF]/50 transition-colors"
                                        onClick={() => router.push(`/scan-view?id=${scan.id}`)}
                                    >
                                        <div>
                                            <p className="text-white font-medium">{scan.patient_name}</p>
                                            <p className="text-[#90A1B9] text-sm">{scan.scan_type} · {scan.clinical_indication}</p>
                                        </div>
                                        <Badge className={`text-xs border ${statusBadge(scan.status)}`}>
                                            {scan.status}
                                        </Badge>
                                    </Card>
                                ))}
                                {(data?.recent_scans?.length ?? 0) === 0 && (
                                    <p className="text-[#90A1B9] text-sm">No scans yet.</p>
                                )}
                            </div>
                        )}
                    </div>

                </div>
            </div>
        </div>
    )
}
