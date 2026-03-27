import { MousePointer2 } from 'lucide-react'

export function AnatomicalMap() {
  return (
    <div className="bg-[#0F172B] border border-[#1D293D] rounded-lg p-5">
      <div className="flex items-center justify-between mb-8">
        <h3 className="font-semibold text-white flex items-center gap-2 text-sm">
          <MousePointer2 className="w-4 h-4 text-[#7C86FF] rotate-90" />
          Anatomical Capture Map
        </h3>
        <div className="bg-[#5B8DEF] text-white text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-wider">
          Right Breast
        </div>
      </div>
      
      <div className="relative w-full aspect-square max-w-[280px] mx-auto mb-6 flex items-center justify-center">
        {/* Labels */}
        <div className="absolute top-0 w-full text-center text-[10px] text-[#6B7280] font-medium tracking-widest">SUPERIOR<br/>12</div>
        <div className="absolute bottom-0 w-full text-center text-[10px] text-[#6B7280] font-medium tracking-widest">6<br/>INFERIOR</div>
        <div className="absolute left-0 h-full flex items-center text-[10px] text-[#6B7280] font-medium tracking-widest -rotate-90 origin-center -translate-x-8">LATERAL</div>
        <div className="absolute right-0 h-full flex items-center text-[10px] text-[#6B7280] font-medium tracking-widest rotate-90 origin-center translate-x-8">MEDIAL</div>
        
        {/* SVG Diagram */}
        <svg viewBox="0 0 200 200" className="w-[85%] h-[85%] mx-auto overflow-visible">
          {/* Main concentric circles (Breast outline) */}
          <circle cx="100" cy="100" r="90" fill="none" stroke="#2A3042" strokeWidth="1" strokeDasharray="4 4" />
          <circle cx="100" cy="100" r="60" fill="none" stroke="#2A3042" strokeWidth="1" />
          <circle cx="100" cy="100" r="15" fill="none" stroke="#3E4C69" strokeWidth="1.5" />
          
          {/* Crosshairs */}
          <line x1="10" y1="100" x2="190" y2="100" stroke="#2A3042" strokeWidth="1" strokeDasharray="4 4" />
          <line x1="100" y1="10" x2="100" y2="190" stroke="#2A3042" strokeWidth="1" strokeDasharray="4 4" />
          
          {/* UOQ (Upper Outer) - Amber Finding */}
          <g className="translate-x-[-35px] translate-y-[-35px]">
            <circle cx="100" cy="100" r="22" fill="#FFB900" fillOpacity="0.05" stroke="#FFB900" strokeWidth="1" strokeDasharray="3 3"/>
            <circle cx="100" cy="100" r="4" fill="#FFB900" />
            <circle cx="100" cy="100" r="8" fill="none" stroke="#FFB900" strokeWidth="1" opacity="0.5"/>
            <text x="100" y="115" fill="#FFB900" fontSize="10" fontWeight="bold" textAnchor="middle">UOQ</text>
            <text x="100" y="125" fill="#FFB900" fontSize="7" opacity="0.8" textAnchor="middle">Upper Outer</text>
            {/* Finding marker */}
            <line x1="85" y1="85" x2="92" y2="92" stroke="#FF4D4D" strokeWidth="1.5" />
            <line x1="92" y1="85" x2="85" y2="92" stroke="#FF4D4D" strokeWidth="1.5" />
            <text x="88" y="80" fill="#FF4D4D" fontSize="6" textAnchor="middle" className="uppercase">Finding</text>
          </g>

          {/* UIQ (Upper Inner) - Amber */}
          <g className="translate-x-[35px] translate-y-[-35px]">
            <circle cx="100" cy="100" r="22" fill="#FFB900" fillOpacity="0.05" stroke="#FFB900" strokeWidth="1" strokeDasharray="3 3"/>
            <circle cx="100" cy="100" r="4" fill="#FFB900" />
            <text x="100" y="115" fill="#FFB900" fontSize="10" fontWeight="bold" textAnchor="middle">UIQ</text>
            <text x="100" y="125" fill="#FFB900" fontSize="7" opacity="0.8" textAnchor="middle">Upper Inner</text>
          </g>

          {/* LOQ (Lower Outer) - Amber */}
          <g className="translate-x-[-35px] translate-y-[35px]">
            <circle cx="100" cy="100" r="22" fill="#FFB900" fillOpacity="0.05" stroke="#FFB900" strokeWidth="1" strokeDasharray="3 3"/>
            <circle cx="100" cy="100" r="4" fill="#FFB900" />
            <text x="100" y="115" fill="#FFB900" fontSize="10" fontWeight="bold" textAnchor="middle">LOQ</text>
            <text x="100" y="125" fill="#FFB900" fontSize="7" opacity="0.8" textAnchor="middle">Lower Outer</text>
          </g>

          {/* LIQ (Lower Inner) - Green Clear */}
          <g className="translate-x-[35px] translate-y-[35px]">
            <circle cx="100" cy="100" r="22" fill="#00D978" fillOpacity="0.05" stroke="#00D978" strokeWidth="1" />
            {/* Checkmark instead of dot */}
            <circle cx="100" cy="100" r="6" fill="#00D978" />
            <path d="M97 100 l2 2 l4 -4" fill="none" stroke="#111625" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
            <text x="100" y="115" fill="#00D978" fontSize="10" fontWeight="bold" textAnchor="middle">LIQ</text>
            <text x="100" y="125" fill="#00D978" fontSize="7" opacity="0.8" textAnchor="middle">Lower Inner</text>
            
            {/* 1/5 fraction indicator floating nearby */}
            <g className="translate-x-[25px] translate-y-[25px]">
              <circle cx="100" cy="100" r="8" fill="#1A2235" stroke="#00D978" strokeWidth="1"/>
              <text x="100" y="103" fill="#00D978" fontSize="7" fontWeight="bold" textAnchor="middle">1/5</text>
            </g>
          </g>
          
          {/* Axilla */}
          <g className="translate-x-[-70px] translate-y-[-20px]">
            <circle cx="100" cy="100" r="10" fill="none" stroke="#FFB900" strokeWidth="1" strokeDasharray="2 2"/>
            <circle cx="100" cy="100" r="2" fill="#FFB900" />
            <text x="100" y="112" fill="#FFB900" fontSize="6" opacity="0.8" textAnchor="middle" className="uppercase">Axilla</text>
          </g>
        </svg>
      </div>

      <div className="text-center font-medium mt-4">
        <span className="text-[#6B7280] text-sm mr-2">Selected:</span>
        <span className="text-[#7C86FF] text-sm">Upper Outer</span>
      </div>
    </div>
  )
}
