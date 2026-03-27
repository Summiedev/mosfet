import { Image as ImageIcon } from 'lucide-react'

export function CapturedEvidence() {
  return (
    <div className="bg-[#0F172B] border border-[#1D293D] rounded-lg p-5 flex flex-col h-full min-h-[200px]">
      <h3 className="font-semibold text-white flex items-center gap-2 text-sm mb-4">
        <ImageIcon className="w-4 h-4 text-[#7C86FF]" />
        Captured Evidence (0)
      </h3>
      
      <div className="flex-1 flex flex-col items-center justify-center text-center">
        <div className="w-12 h-12 rounded-xl bg-[#1A2235] flex items-center justify-center mb-3">
            <ImageIcon className="w-6 h-6 text-[#3E4C69]" />
        </div>
        <p className="text-sm text-[#6B7280]">No images captured.</p>
      </div>
    </div>
  )
}
