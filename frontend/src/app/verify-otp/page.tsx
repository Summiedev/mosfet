'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { InputOTP, InputOTPGroup, InputOTPSlot } from '@/components/ui/input-otp'
import { ShieldCheck } from 'lucide-react'
import Link from 'next/link'
import { Mail, Phone, Lock, Activity } from 'lucide-react'

export default function VerifyOTPPage() {
    const router = useRouter()
    const [otp, setOtp] = useState('')
    const [loading, setLoading] = useState(false)

    const handleVerify = () => {
        setLoading(true)
        // Handle OTP verification
        setTimeout(() => {
            setLoading(false)
            router.push('/dashboard')
        }, 1000)
    }

    useEffect(() => {
        if (otp.length === 6 && !loading) {
            handleVerify()
        }
    }, [otp])

    return (
        <div className="min-h-screen bg-blue flex items-center justify-center p-4">
            <div className="w-full max-w-md">
                <div className="bg-[#0F172B] backdrop-blur border border-slate-700/50 rounded-2xl p-8 space-y-8">
                    {/* Logo */}
                    <div className="flex items-center justify-center gap-2">
                        <div className="rounded-lg flex items-center justify-center">
                            <div/>
                            <Activity className="w-12 h-12 text-[#615FFF]" />
                        </div>
                        <span className="text-3xl font-bold text-white">RadFlow</span>
                    </div>

                    {/* Shield Icon */}
                    <div className="flex justify-center">
                        <div className="w-12 h-12 bg-green-500/20 rounded-full flex items-center justify-center">
                            <ShieldCheck className="w-6 h-6 text-green-500" />
                        </div>
                    </div>

                    {/* Header */}
                    <div className="space-y-2 text-center">
                        <h1 className="text-2xl font-bold text-white">Enter Verification Code</h1>
                        <p className="text-sm text-slate-400">We&apos;ve sent a 6-digit code to wrety@hospital.ng</p>
                    </div>

                    {/* OTP Input */}
                    <div className="space-y-6">
                        <InputOTP
                            maxLength={6}
                            value={otp}
                            onChange={setOtp}
                        >
                            <InputOTPGroup className="gap-2 justify-center">
                                <InputOTPSlot index={0} className="w-12 h-12 text-xl" />
                                <InputOTPSlot index={1} className="w-12 h-12 text-xl" />
                                <InputOTPSlot index={2} className="w-12 h-12 text-xl" />
                                <InputOTPSlot index={3} className="w-12 h-12 text-xl" />
                                <InputOTPSlot index={4} className="w-12 h-12 text-xl" />
                                <InputOTPSlot index={5} className="w-12 h-12 text-xl" />
                            </InputOTPGroup>
                        </InputOTP>

                        {/* Verify Button */}
                        <Button
                            onClick={handleVerify}
                            disabled={otp.length !== 6 || loading}
                            className="w-full bg-[#4F39F6] text-white font-medium py-2 rounded-lg transition-all disabled:opacity-50"
                        >
                            {loading ? 'Verifying...' : 'Verify & Log In'}
                        </Button>
                    </div>

                    {/* Footer Links */}
                    <div className="space-y-3">
                        <Link href="/login" className="w-full text-center block text-sm text-slate-400 hover:text-slate-300">
                            Back to Login
                        </Link>
                        <button className="w-full text-sm text-blue-400 hover:text-blue-300 font-medium">
                            Resend Code
                        </button>
                    </div>
                </div>
            </div>
        </div>
    )
}
