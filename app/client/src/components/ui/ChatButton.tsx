import type { ButtonHTMLAttributes } from 'react'

type ChatButtonProps = ButtonHTMLAttributes<HTMLButtonElement>

export const ChatButton = ({ className = '', ...props }: ChatButtonProps) => {
    return (
        <button
            className={`inline-flex h-11 items-center justify-center rounded-full bg-black px-6 text-sm font-medium tracking-wide text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-300 ${className}`}
            {...props}
        />
    )
}
