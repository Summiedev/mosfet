import { CheckSquare } from 'lucide-react'

export function ProtocolChecklist() {
  const CHECKLIST_ITEMS = [
    { title: 'Relevant anatomical regions', checked: false },
    { title: 'Margins (Circumscribed, etc.)', checked: false },
    { title: 'Review all anatomical planes', checked: false },
    { title: 'Size of lesion', checked: false }
  ];

  return (
    <div className="bg-[#0F172B] border border-[#1D293D] rounded-lg p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-white flex items-center gap-2 text-sm">
          <CheckSquare className="w-4 h-4 text-[#7C86FF]" />
          Protocol Checklist
        </h3>
        <div className="bg-[#1A2235] text-[#9CA3AF] text-xs px-2 py-0.5 rounded-md">
          2 / 4
        </div>
      </div>
      
      <div className="space-y-2.5">
        {CHECKLIST_ITEMS.map((item, index) => (
          <div 
            key={index} 
            className="flex items-center gap-3 bg-[#13192B] border border-[#1E2433] p-3 rounded-lg hover:border-[#2A3042] transition-colors cursor-pointer"
          >
            <div className={`w-4 h-4 rounded-sm border ${item.checked ? 'bg-[#5B8DEF] border-[#5B8DEF]' : 'border-[#3E4C69] bg-[#0A0E17]'}`}></div>
            <label className="text-sm text-[#A5B4D3] cursor-pointer flex-1 user-select-none">
              {item.title}
            </label>
          </div>
        ))}
      </div>
    </div>
  )
}
