import React from 'react'

export type ButtonVariant = 'primary' | 'secondary' | 'tertiary' | 'danger' | 'success'
export type ButtonSize = 'sm' | 'md' | 'lg'

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant
  size?: ButtonSize
  isLoading?: boolean
  children: React.ReactNode
}

const variantStyles: Record<ButtonVariant, string> = {
  primary:
    'bg-[#8B5A3C] text-white hover:bg-[#6B4423] border-2 border-[#8B5A3C] hover:border-[#6B4423]',
  secondary:
    'bg-white text-[#8B5A3C] hover:bg-[#FFF8F0] border-2 border-[#8B5A3C] hover:border-[#6B4423]',
  tertiary:
    'bg-transparent text-[#8B5A3C] hover:bg-[#FFF8F0] border-0 underline hover:no-underline',
  danger: 'bg-red-600 text-white hover:bg-red-700 border-2 border-red-600 hover:border-red-700',
  success:
    'bg-green-600 text-white hover:bg-green-700 border-2 border-green-600 hover:border-green-700',
}

const sizeStyles: Record<ButtonSize, string> = {
  sm: 'px-3 py-2 text-sm',
  md: 'px-4 py-2 text-base',
  lg: 'px-6 py-3 text-lg',
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = 'primary',
      size = 'md',
      isLoading = false,
      disabled = false,
      className = '',
      children,
      ...props
    },
    ref
  ) => {
    return (
      <button
        ref={ref}
        disabled={disabled || isLoading}
        className={`
          font-medium rounded-lg transition
          disabled:opacity-60 disabled:cursor-not-allowed
          focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#8B5A3C]
          ${variantStyles[variant]}
          ${sizeStyles[size]}
          ${className}
        `}
        {...props}
      >
        {isLoading ? (
          <span className="flex items-center gap-2">
            <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-current border-r-transparent"></span>
            Loading...
          </span>
        ) : (
          children
        )}
      </button>
    )
  }
)

Button.displayName = 'Button'
