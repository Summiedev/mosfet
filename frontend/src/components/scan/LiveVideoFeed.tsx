import { ShieldAlert, Eye, Settings2 } from 'lucide-react'
import { BottomToolbar } from './BottomToolbar'

export function LiveVideoFeed() {
  return (
    <div className="w-full h-full min-h-[500px] bg-[#0F172B] border border-[#1D293D] rounded-lg overflow-hidden relative flex flex-col justify-between p-4">
      {/* Top HUD */}
      <div className="flex items-center justify-between z-10">
        <div className="flex items-center gap-4 text-xs font-mono">
          <div className="flex items-center gap-2 text-[#FF4D4D]">
            <div className="w-2 h-2 rounded-full bg-[#FF4D4D] animate-pulse shadow-[0_0_8px_rgba(255,77,77,0.8)]" />
            LIVE
          </div>
          <span className="text-[#6B7280]">|</span>
          <span className="text-[#A5B4D3]">03:57</span>
          <span className="text-[#6B7280]">|</span>
          <span className="text-[#6B7280]">1 captures</span>
        </div>
        
        <div className="flex items-center gap-3">
          <div className="flex items-center bg-[#1A2235]/80 border border-[#2A3042] rounded px-3 py-1.5 gap-3 text-xs">
            <span className="text-[#6B7280]">GAIN</span>
            <span className="text-[#A5B4D3] font-mono">65%</span>
          </div>
          <div className="flex items-center bg-[#1A2235]/80 border border-[#2A3042] rounded px-3 py-1.5 gap-3 text-xs">
            <span className="text-[#6B7280]">DEPTH</span>
            <span className="text-[#A5B4D3] font-mono">4.5cm</span>
          </div>
        </div>

        <div className="flex items-center bg-[#1A2235]/80 border border-[#2A3042] rounded-full px-3 py-1.5 gap-3">
          <Settings2 className="w-3.5 h-3.5 text-[#A5B4D3]" />
          <span className="text-[#A5B4D3] text-xs font-medium">AI Assist</span>
          <div className="w-7 h-4 rounded-full bg-[#5B8DEF] relative cursor-pointer">
            <div className="absolute right-0.5 top-0.5 w-3 h-3 rounded-full bg-white"></div>
          </div>
        </div>
      </div>

      {/* Main Video Overlay Area */}
      <div className="absolute inset-0 z-0 overflow-hidden pointer-events-none">
        
        {/* Floating AI Alerts */}
        <div className="absolute top-24 left-4 flex flex-col gap-3">
          <div className="bg-[#FFB900]/10 border border-[#FFB900]/30 rounded-lg px-4 py-2 flex items-center gap-2 shadow-lg backdrop-blur-sm shadow-[#FFB900]/5 max-w-sm">
            <ShieldAlert className="w-4 h-4 text-[#FFB900]" />
            <span className="text-[#FFB900] text-sm font-medium drop-shadow-md">Possible hypoechoic area detected</span>
          </div>
          <div className="bg-[#7C86FF]/10 border border-[#7C86FF]/30 rounded-lg px-4 py-2 flex items-center gap-2 shadow-lg backdrop-blur-sm shadow-[#7C86FF]/5 max-w-sm">
            <Eye className="w-4 h-4 text-[#7C86FF]" />
            <span className="text-[#7C86FF] text-sm font-medium drop-shadow-md">Consider capturing this frame</span>
          </div>
        </div>

        {/* Bounding Box / Detection Area */}
        <div className="absolute top-1/2 left-1/3 w-32 h-32 border border-[#4F39F6] border-dashed rounded-lg bg-[#4F39F6]/5 translate-y-4 translate-x-12 flex flex-col">
          <div className="absolute -top-6 left-0 bg-[#4F39F6]/20 border border-[#4F39F6]/40 px-2 py-0.5 rounded text-[10px] text-[#A5B4D3] font-mono">
            Mass 78%
          </div>
        </div>
      </div>

      {/* Bottom Controls */}
      <div className="z-10 mt-auto pt-8">
         <BottomToolbar />
      </div>
    </div>
  )
}
