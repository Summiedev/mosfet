import { Pause, Camera, PlayCircle, Ruler } from 'lucide-react'
import { Button } from '@/components/ui/button'

export function BottomToolbar() {
  return (
    <div className="flex gap-3">
      <Button
        className="bg-[#020618] hover:bg-[#4a321d] text-amber-500 border border-[#1D293D] px-6 gap-2"
      >
        <span className="w-2 h-4 bg-amber-500 rounded-sm inline-block mr-1"></span> {/* Freeze icon mock */}
        Freeze
      </Button>

      <Button
        className="flex-1 bg-[#1A2235] hover:bg-[#2A3042] text-[#A5B4D3] border border-[#2A3042] gap-2"
      >
        <Camera className="w-4 h-4" />
        Capture
      </Button>

      <Button
        className="flex-1 bg-[#1A2235] hover:bg-[#2A3042] text-[#A5B4D3] border border-[#2A3042] gap-2"
      >
        <PlayCircle className="w-4 h-4" />
        Cine Loop
      </Button>

      <Button
        className="flex-1 bg-[#5B8DEF] hover:bg-[#4a7bdd] text-white gap-2"
      >
        <Ruler className="w-4 h-4" />
        Measure
      </Button>
    </div>
  )
}
