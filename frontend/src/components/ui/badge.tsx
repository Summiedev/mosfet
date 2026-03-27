import * as React from "react"

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: "default" | "secondary" | "success" | "warning" | "outline"
}

export function Badge({
  children,
  variant = "default",
  className = "",
  ...props
}: BadgeProps) {
  const base =
    "inline-flex items-center px-2 py-1 rounded-md text-xs font-medium"

  const variants = {
    default: "bg-primary text-white",
    secondary: "bg-gray-200 text-gray-800",
    success: "bg-green-500 text-white",
    warning: "bg-yellow-500 text-black",
    outline: "border border-slate-600 bg-transparent text-slate-300",
  }

  return (
    <span
      className={`${base} ${variants[variant]} ${className}`}
      {...props}
    >
      {children}
    </span>
  )
}