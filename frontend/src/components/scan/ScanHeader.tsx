import Link from 'next/link'
import { ArrowLeft, ArrowRight } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface ScanHeaderProps {
  patientName?: string
  patientId?: string
  scanType?: string
  clinicalContext?: string
}

export function ScanHeader({
  patientName = 'Amaka Johnson',
  patientId = 'PT-2024-001',
  scanType = 'Breast Ultrasound',
  clinicalContext = 'Palpable lump in left breast',
}: ScanHeaderProps) {
  return (
    <div className="flex items-center justify-between mb-6 px-2">
      <div className="flex items-center gap-4">
        <Link href="/dashboard">
          <Button variant="ghost" size="icon" className="text-[#9CA3AF] hover:text-white">
            <ArrowLeft className="w-5 h-5" />
          </Button>
        </Link>
        <div>
          <h1 className="text-xl font-bold text-white mb-0.5">{patientName}</h1>
          <p className="text-xs text-[#6B7280]">
            {patientId} - {scanType}
          </p>
        </div>
      </div>
      <div className="flex items-center gap-3">
        <div className="px-4 py-2 bg-[#1A2235] border border-[#2A3042] rounded-lg text-xs text-[#A5B4D3]">
          Context: {clinicalContext}
        </div>
        <Link href="/dashboard">
            <Button className="bg-[#00D978] hover:bg-[#00D978]/90 text-white font-medium rounded-lg px-6 flex items-center gap-2">
              Complete Scan
              <ArrowRight className="w-4 h-4" />
            </Button>
        </Link>
      </div>
    </div>
  )
}
