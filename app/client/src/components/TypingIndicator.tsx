export const TypingIndicator = () => {
    return (
        <div
            className="inline-flex max-w-[80%] items-center gap-2 rounded-full border border-slate-200 bg-slate-50 px-4 py-2 text-slate-700"
            role="status"
            aria-live="polite"
            aria-label="El asistente esta escribiendo"
        >
            <span className="sr-only">El asistente esta escribiendo</span>
            <span className="size-2 animate-bounce rounded-full bg-slate-700 [animation-delay:-0.2s]" />
            <span className="size-2 animate-bounce rounded-full bg-slate-700" />
            <span className="size-2 animate-bounce rounded-full bg-slate-700 [animation-delay:0.2s]" />
        </div>
    )
}
