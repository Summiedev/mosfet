"use client"

import * as React from "react"

interface InputOTPProps {
  maxLength: number
  value: string
  onChange: (value: string) => void
  children: React.ReactNode
}

const OTPContext = React.createContext<{
  value: string
  onChange: (val: string) => void
  maxLength: number
  focusIndex: number
  setFocusIndex: (index: number) => void
} | null>(null)

export function InputOTP({ maxLength, value, onChange, children }: InputOTPProps) {
  const [focusIndex, setFocusIndex] = React.useState(0)
  
  return (
    <OTPContext.Provider value={{ value, onChange, maxLength, focusIndex, setFocusIndex }}>
      <div className="flex justify-center gap-2">
        {children}
      </div>
    </OTPContext.Provider>
  )
}

export function InputOTPGroup({ children, className = "" }: { children: React.ReactNode, className?: string }) {
  return <div className={`flex gap-2 ${className}`}>{children}</div>
}

export function InputOTPSlot({ index, className = "" }: { index: number; className?: string }) {
  const context = React.useContext(OTPContext)
  if (!context) throw new Error("InputOTPSlot must be used within InputOTP")
  
  const { value, onChange, focusIndex, setFocusIndex, maxLength } = context
  const inputRef = React.useRef<HTMLInputElement>(null)

  React.useEffect(() => {
    if (focusIndex === index && inputRef.current) {
      inputRef.current.focus()
    }
  }, [focusIndex, index])

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    let char = e.target.value
    if (char.length > 1) char = char.slice(-1) // handle paste or fast typing

    if (!/^\d*$/.test(char)) return // allow only digits
    
    // Replace character at current index or append
    const charArray = Array.from({ length: maxLength }, (_, i) => value[i] || " ")
    charArray[index] = char || " "
    
    onChange(charArray.join("").trimEnd()) // remove trailing spaces
    
    if (char && index < maxLength - 1) {
      setFocusIndex(index + 1) // move to next input
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Backspace') {
      e.preventDefault()
      const charArray = Array.from({ length: maxLength }, (_, i) => value[i] || " ")
      if (!value[index] && index > 0) {
        // If empty, delete previous and move back
        charArray[index - 1] = " "
        onChange(charArray.join("").trimEnd())
        setFocusIndex(index - 1)
      } else {
        // Delete current
        charArray[index] = " "
        onChange(charArray.join("").trimEnd())
      }
    } else if (e.key === 'ArrowLeft' && index > 0) {
      setFocusIndex(index - 1)
    } else if (e.key === 'ArrowRight' && index < maxLength - 1) {
      setFocusIndex(index + 1)
    }
  }

  return (
    <input
      ref={inputRef}
      type="text"
      inputMode="numeric"
      maxLength={2} // Allow 2 to trap fast typing, we handle slicing in handleChange
      value={value[index] || ''}
      onChange={handleChange}
      onKeyDown={handleKeyDown}
      onFocus={() => setFocusIndex(index)}
      className={`w-12 h-12 text-center border rounded-md text-xl bg-slate-900 border-slate-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all ${className}`}
    />
  )
}