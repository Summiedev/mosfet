'use client'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Clock, CheckCircle2, Search, Filter, Contact, Activity, FileText } from 'lucide-react'
import { Sidebar } from '@/components/sidebar'
import { Topbar } from '@/components/topbar'

const mockScans = [
  {
    id: 1,
    patient: 'Grace Okafor, 29',
    patientId: 'PT-2024-001',
    scanType: 'Fetal Ultrasound',
    clinicalContext: 'Suspicious',
    risk: 'Suspicious',
    riskLevel: 'high',
    time: '45 mins ago',
    status: 'Finalized'
  }
]

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-[#020618] flex">
      <Sidebar />

      {/* Main Content */}
      <div className="flex-1 ml-64 flex flex-col">
        <Topbar title="Good morning, Dr. Roberts" />

        <div className="p-8">

          {/* Stats */}
          <div className="grid grid-cols-3 gap-4 mb-8">

            <Card className="bg-[#222734] rounded-lg border border-[#415181] p-6">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm text-[#A5B4D3] mb-2">Waiting</p>
                  <p className="text-3xl font-bold text-[#5B8DEF]">3</p>
                </div>
                <Clock className="w-6 h-6 text-[#5B8DEF]" />
              </div>
            </Card>

            <Card className="bg-[#222734] rounded-lg border border-[#415181] p-6">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm text-[#A5B4D3] mb-2">In Progress</p>
                  <p className="text-3xl font-bold text-[#FFB900]">1</p>
                </div>
                <Activity className="w-6 h-6 text-[#FFB900]" />
              </div>
            </Card>

            <Card className="bg-[#222734] rounded-lg border border-[#415181] p-6">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm text-[#A5B4D3] mb-2">Completed Today</p>
                  <p className="text-3xl font-bold text-[#00D978]">1</p>
                </div>
                <Contact className="w-6 h-6 text-[#00D978]" />
              </div>
            </Card>

          </div>

          {/* Search */}
          <div className='bg-[#171B26] p-4 rounded-lg border border-[#2A3042] mb-8' >
            <div className="flex gap-3">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-3 w-4 h-4 text-slate-400" />
                <Input
                  placeholder="Search by patient name or ID..."
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
          
          {/* Active Workload */}
          <div className="space-y-4 mb-10">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Clock className="w-5 h-5 text-[#7C86FF]" />
              Active Workload
            </h2>
            <Card className="bg-[#0F172B] rounded-lg border border-[#2A3042] p-5 max-w-sm">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-full bg-[#123329]/80 border border-[#164233] text-[#00D978] text-xs font-medium">
                  <div className="w-1.5 h-1.5 rounded-full bg-[#00D978]"></div>
                  Low Risk
                </div>
                <span className="text-xs text-[#6B7280]">10 mins ago</span>
              </div>
              
              <div className="mb-6">
                <h3 className="text-lg font-bold text-white mb-2">Sarah Jenkins, 42</h3>
                <div className="flex items-center gap-2 text-sm text-[#6B7280]">
                  <FileText className="w-4 h-4" />
                  Breast Ultrasound
                </div>
              </div>

              <Button className="w-full bg-[#1E293B] hover:bg-[#334155] border border-[#3E4C69] text-[#A5B4D3] transition-colors rounded-lg py-5 shadow-sm">
                Complete Report
              </Button>
            </Card>
          </div>

          {/* Recently Completed */}
          <div className="space-y-4">

            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5" />
              Recently Completed
            </h2>

            <div className="bg-[#0F172B] border border-[#2A3042] rounded-lg overflow-hidden">

              <table className="w-full">

                <thead className="border-b border-[#2A3042]">
                  <tr className="bg-[#1D293D]">

                    <th className="px-6 py-4 text-left text-xs font-medium text-[#A5B4D3]">
                      Patient
                    </th>

                    <th className="px-6 py-4 text-left text-xs font-medium text-[#A5B4D3]">
                      Scan Type
                    </th>

                    <th className="px-6 py-4 text-left text-xs font-medium text-[#A5B4D3]">
                      Clinical Context
                    </th>

                    <th className="px-6 py-4 text-left text-xs font-medium text-[#A5B4D3]">
                      Risk
                    </th>

                    <th className="px-6 py-4 text-left text-xs font-medium text-[#A5B4D3]">
                      Time
                    </th>

                    <th className="px-6 py-4 text-left text-xs font-medium text-[#A5B4D3]">
                      Status
                    </th>

                  </tr>
                </thead>

                <tbody className="divide-y divide-[#2A3042]">

                  {mockScans.map((scan) => (

                    <tr
                      key={scan.id}
                      className="hover:bg-[#1D293D]/50 transition-colors"
                    >

                      <td className="px-6 py-4">
                        <div className="text-sm font-bold text-white mb-1">{scan.patient}</div>
                        <div className="text-xs text-[#6B7280]">{scan.patientId}</div>
                      </td>

                      <td className="px-6 py-4 text-sm text-[#A5B4D3]">
                        {scan.scanType}
                      </td>

                      <td className="px-6 py-4 text-sm">
                        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#FFB900]/10 border border-[#FFB900]/20 text-[#FFB900] text-xs font-medium">
                          <div className="w-1.5 h-1.5 rounded-full bg-[#FFB900]"></div>
                          {scan.clinicalContext}
                        </div>
                      </td>

                      <td className="px-6 py-4 text-sm">
                        <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-[#123329]/50 border border-[#164233] text-[#00D978] text-xs font-medium">
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          High
                          <span className="text-[#00D978]/60 ml-1 font-normal opacity-75">Physician-provided</span>
                        </div>
                      </td>

                      <td className="px-6 py-4 text-sm text-[#6B7280]">
                        {scan.time}
                      </td>

                      <td className="px-6 py-4 text-sm">
                        <div className="flex items-center gap-2 text-[#00D978] text-sm">
                          <CheckCircle2 className="w-4 h-4" />
                          {scan.status}
                        </div>
                      </td>

                    </tr>

                  ))}

                </tbody>

              </table>

            </div>

          </div>

        </div>

      </div>

    </div>
  )
}