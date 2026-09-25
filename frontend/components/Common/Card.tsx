import React from 'react'

interface CardProps {
  children: React.ReactNode
  className?: string
  variant?: 'default' | 'outlined' | 'elevated'
}

interface CardHeaderProps {
  children: React.ReactNode
  className?: string
}

interface CardBodyProps {
  children: React.ReactNode
  className?: string
}

interface CardFooterProps {
  children: React.ReactNode
  className?: string
}

const variantStyles: Record<string, string> = {
  default: 'bg-white border-2 border-[#D2B48C] rounded-lg shadow-sm',
  outlined: 'bg-[#FFF8F0] border-2 border-[#D2B48C] rounded-lg',
  elevated: 'bg-white border-0 rounded-lg shadow-md',
}

export const Card: React.FC<CardProps> & {
  Header: React.FC<CardHeaderProps>
  Body: React.FC<CardBodyProps>
  Footer: React.FC<CardFooterProps>
} = ({ children, className = '', variant = 'default' }) => (
  <div className={`${variantStyles[variant]} ${className}`}>{children}</div>
)

Card.Header = ({ children, className = '' }) => (
  <div className={`px-6 py-4 border-b border-[#D2B48C] ${className}`}>{children}</div>
)

Card.Body = ({ children, className = '' }) => (
  <div className={`px-6 py-4 ${className}`}>{children}</div>
)

Card.Footer = ({ children, className = '' }) => (
  <div className={`px-6 py-4 border-t border-[#D2B48C] bg-[#FFF8F0] rounded-b-lg ${className}`}>
    {children}
  </div>
)

Card.displayName = 'Card'
Card.Header.displayName = 'Card.Header'
Card.Body.displayName = 'Card.Body'
Card.Footer.displayName = 'Card.Footer'
