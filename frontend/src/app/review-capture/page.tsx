'use client'

import { ReviewHeader } from '@/components/review/ReviewHeader'
import { CapturePreview } from '@/components/review/CapturePreview'
import { AIDetectionWarning } from '@/components/review/AIDetectionWarning'
import { X, Check } from 'lucide-react'
import { Button } from '@/components/ui/button'

export default function ReviewCapturePage() {
    return (
        <div className="min-h-screen bg-[#020618] flex flex-col p-6 lg:p-10 lg:pt-12 items-center">
            <div className="w-full max-w-5xl flex flex-col">
                <ReviewHeader />
                
                <div className="flex flex-col flex-1 w-full mt-2">
                    {/* Main Card */}
                    <div className="bg-[#020618] border border-[#1D293D] rounded-xl lg:rounded-2xl p-6 md:p-10 w-full shadow-2xl flex flex-col items-center">
                        <CapturePreview />
                        <AIDetectionWarning />
                    </div>

                    {/* Actions */}
                    <div className="flex flex-wrap items-center justify-center gap-4 mt-10 mb-8">
                        <Button 
                            variant="outline" 
                            className="bg-[#1A0A10] hover:bg-[#2A1118] text-[#F43F5E] border border-[#3D1621] hover:border-[#F43F5E]/40 hover:text-[#F43F5E] transition-colors rounded-xl px-6 lg:px-8 h-12 text-sm font-medium"
                        >
                            <X className="w-4 h-4 mr-2" strokeWidth={2.5} />
                            Reject & Delete
                        </Button>

                        <Button 
                            className="bg-[#00C17E] hover:bg-[#00A96B] text-white border-0 transition-all rounded-xl px-6 lg:px-8 h-12 text-sm font-medium shadow-[0_0_20px_rgba(0,193,126,0.3)] hover:shadow-[0_0_25px_rgba(0,193,126,0.5)]"
                        >
                            <Check className="w-4 h-4 mr-2" strokeWidth={2.5} />
                            Accept Capture
                        </Button>
                    </div>
                </div>
            </div>
        </div>
    )
}
