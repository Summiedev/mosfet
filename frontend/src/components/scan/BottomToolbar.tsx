import { Pause, Camera, Film, Ruler } from 'lucide-react'
import { Button } from '@/components/ui/button'

export function BottomToolbar() {
  return (
    <div className="flex gap-3">
      <Button
        className="bg-[#3A1F0D] hover:bg-[#4A2D1A] text-[#F59E0B] border border-[#4A2D1A] px-6 gap-2"
      >
        <Pause className="w-4 h-4 fill-current" />
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
        <Film className="w-4 h-4" />
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
