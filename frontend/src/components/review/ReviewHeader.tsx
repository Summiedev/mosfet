import { ArrowLeft } from 'lucide-react'
import Link from 'next/link'

export function ReviewHeader() {
  return (
    <div className="w-full mb-8">
      <div className="flex items-start gap-4 mb-6">
        <Link href="/scan-view" className="text-[#A5B4D3] hover:text-white transition-colors mt-1">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Review Capture</h1>
          <p className="text-sm text-[#6B7280] mt-1">fffffff • Lower Outer Quadrant</p>
        </div>
      </div>
      <div className="h-px bg-[#1D293D] w-full"></div>
    </div>
  )
}
