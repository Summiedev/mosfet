'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { InputOTP, InputOTPGroup, InputOTPSlot } from '@/components/ui/input-otp'
import { Activity, ShieldCheck } from 'lucide-react'
import { authApi } from '@/utils/endpoints'

export default function VerifyOTPPage() {
    const router = useRouter()
    const [otp, setOtp] = useState('')
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')
    const [phone, setPhone] = useState('')

    useEffect(() => {
        // The phone was saved when we logged in
        const stored = localStorage.getItem('user')
        if (stored) {
            const user = JSON.parse(stored)
            setPhone(user.phone)
        } else {
            router.push('/login')
        }
    }, [router])

    const handleVerify = async () => {
        if (otp.length !== 6 || loading) return
        setError('')
        setLoading(true)

        try {
            await authApi.verifyOtp(phone, otp)
            router.push('/dashboard')
        } catch (err: unknown) {
            setError(err instanceof Error ? err.message : 'Verification failed')
            setOtp('')
        } finally {
            setLoading(false)
        }
    }

    const handleResend = async () => {
        if (!phone) return
        try {
            await authApi.sendOtp(phone)
            setError('')
        } catch (err: unknown) {
            setError(err instanceof Error ? err.message : 'Could not resend OTP')
        }
    }

    // Auto-submit when all 6 digits filled
    useEffect(() => {
        if (otp.length === 6) handleVerify()
    }, [otp])

    return (
        <div className="min-h-screen bg-[#020618] flex items-center justify-center p-4">
            <div className="w-full max-w-md">
                <div className="bg-[#0F172B] backdrop-blur border border-slate-700/50 rounded-2xl p-8 space-y-8">
                    <div className="flex items-center justify-center gap-2">
                        <Activity className="w-12 h-12 text-[#615FFF]" />
                        <span className="text-3xl font-bold text-white">RadFlow</span>
                    </div>

                    <div className="space-y-2 text-center">
                        <ShieldCheck className="w-10 h-10 text-[#615FFF] mx-auto" />
                        <h1 className="text-2xl font-bold text-white">Verify your phone</h1>
                        <p className="text-sm text-[#90A1B9]">
                            We sent a 6-digit code to{' '}
                            <span className="text-white font-medium">{phone}</span>
                        </p>
                    </div>

                    {error && (
                        <p className="text-sm text-red-400 text-center bg-red-400/10 border border-red-400/20 rounded-lg px-4 py-2">
                            {error}
                        </p>
                    )}

                    <div className="flex justify-center">
                        <InputOTP maxLength={6} value={otp} onChange={setOtp}>
                            <InputOTPGroup>
                                {[0, 1, 2, 3, 4, 5].map((i) => (
                                    <InputOTPSlot key={i} index={i} />
                                ))}
                            </InputOTPGroup>
                        </InputOTP>
                    </div>

                    <Button
                        onClick={handleVerify}
                        disabled={otp.length !== 6 || loading}
                        className="w-full bg-[#4F39F6] hover:opacity-90 text-white font-medium py-2 rounded-lg"
                    >
                        {loading ? 'Verifying…' : 'Verify →'}
                    </Button>

                    <p className="text-center text-sm text-slate-400">
                        Didn&apos;t get a code?{' '}
                        <button
                            onClick={handleResend}
                            className="text-blue-400 hover:text-blue-300 font-medium"
                        >
                            Resend
                        </button>
                    </p>
                </div>
            </div>
        </div>
    )
}
