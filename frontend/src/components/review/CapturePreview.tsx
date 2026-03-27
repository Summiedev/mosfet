import { ImageIcon } from 'lucide-react'

export function CapturePreview() {
  return (
      <div className="relative aspect-video w-full max-w-4xl mx-auto bg-[#070A11] rounded-xl border border-[#1D293D]/60 flex items-center justify-center overflow-hidden mb-6 shadow-inner">
          <ImageIcon className="w-14 h-14 text-[#2B354D] opacity-60 flex-shrink-0" strokeWidth={1.5} />
          
          <div className="absolute bottom-4 left-4 right-4 flex justify-between items-center bg-[#020618]/80 backdrop-blur-md border border-[#1D293D]/80 px-4 py-2.5 rounded-lg font-mono text-[11px] text-[#8B98B4]">
              <span>Lower Outer Quadrant</span>
              <span>5:37:58 AM</span>
          </div>
      </div>
  )
}
