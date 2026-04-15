import { forwardRef } from 'react'
import type { TextareaHTMLAttributes } from 'react'

type ChatTextareaProps = TextareaHTMLAttributes<HTMLTextAreaElement>

export const ChatTextarea = forwardRef<HTMLTextAreaElement, ChatTextareaProps>(
    ({ className = '', ...props }, ref) => {
        return (
            <textarea
                ref={ref}
                className={`max-h-40 min-h-11 flex-1 resize-none rounded-full bg-transparent px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-slate-300 ${className}`}
                {...props}
            />
        )
    },
)

ChatTextarea.displayName = 'ChatTextarea'
