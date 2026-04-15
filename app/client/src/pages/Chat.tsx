import { TypingIndicator } from '../components/TypingIndicator'
import { Callout } from '../components/ui/Callout'
import { ChatButton } from '../components/ui/ChatButton'
import { ChatTextarea } from '../components/ui/ChatTextarea'
import { useChat } from '../hooks/useChat'
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm'
import { useAuthStore } from '../storage/authStore'

const playgroundTables = [
    'actor',
    'address',
    'category',
    'city',
    'country',
    'customer',
    'film',
    'film_actor',
    'film_category',
    'inventory',
    'language',
    'payment',
    'rental',
    'staff',
    'store',
]

export const Chat = () => {
    const {
        messages,
        inputValue,
        isLoading,
        canSubmit,
        listEndRef,
        inputRef,
        setInputValue,
        handleSubmit,
        handleInputKeyDown,
    } = useChat()

    const { user } = useAuthStore()

    if (!user) {
        return (
            <main className="text-slate-800 flex h-full min-h-0 justify-center bg-transparent">
                <div className="m-auto min-h-0 w-full max-w-4xl flex-col py-10">
                    <li className="flex items-center justify-center py-8">
                        <p className="font-serif text-4xl tracking-tight text-emerald-800/80 sm:text-5xl">NaturalSQL</p>
                    </li>
                    <h2 className="text-2xl text-slate-800 text-center">Please log in to access the chat.</h2>
                </div>
            </main>
        )
    }

    if (user.messagesChat >= 10) {
        return (
            <main className="text-slate-800 flex h-full min-h-0 justify-center bg-transparent">
                <div className="m-auto min-h-0 w-full max-w-4xl flex-col py-10">
                    <li className="flex items-center justify-center py-8">
                        <p className="font-serif text-4xl tracking-tight text-emerald-800/80 sm:text-5xl">NaturalSQL</p>
                    </li>
                    <h2 className="text-2xl text-slate-800 text-center">
                        All chat messages have been used. Please wait for reset.
                    </h2>
                </div>
            </main>
        )
    }

    if (!messages.length && !isLoading) {
        return (
            <main className="text-slate-800 flex h-full min-h-0 justify-center bg-transparent">
                <div className="m-auto min-h-0 w-full max-w-4xl flex-col py-10">
                    <li className="flex items-center justify-center py-8">
                        <p className="font-serif text-4xl tracking-tight text-emerald-800/80 sm:text-5xl">NaturalSQL</p>
                    </li>
                    <form onSubmit={handleSubmit} className="shrink-0 px-4 py-4 sm:px-6 sm:py-5">
                        <label htmlFor="chat-input" className="sr-only">
                            Escribe tu mensaje
                        </label>
                        <div className="flex items-end gap-3 rounded-full border border-emerald-200 bg-white/90 p-2 shadow-sm">
                            <ChatTextarea
                                id="chat-input"
                                ref={inputRef}
                                value={inputValue}
                                onChange={(event) => setInputValue(event.target.value)}
                                onKeyDown={handleInputKeyDown}
                                rows={1}
                                placeholder="Escribe tu mensaje..."
                            />
                            <ChatButton
                                type="submit"
                                disabled={!canSubmit}
                            >
                                {isLoading ? 'Enviando...' : 'Enviar'}
                            </ChatButton>
                        </div>
                    </form>

                    <div className="px-4 sm:px-6">
                        <Callout title="Playground database tables">
                            <p className="mb-3">
                                This environment is controlled. You can ask questions using the following sample tables:
                            </p>
                            <ul className="grid grid-cols-2 gap-x-6 gap-y-1 text-sm sm:grid-cols-3">
                                {playgroundTables.map((table) => (
                                    <li key={table} className="font-medium text-emerald-900/90">
                                        {table}
                                    </li>
                                ))}
                            </ul>
                        </Callout>
                    </div>
                </div>
            </main>
        )
    }
    return (
        <main className="text-slate-800 flex h-full min-h-0 justify-center bg-transparent">
            <div className="flex h-full min-h-0 w-full max-w-4xl flex-col py-10">
                
                <section
                    className="flex-1 min-h-0 overflow-y-auto px-4 sm:px-8"
                    aria-live="polite"
                    aria-label="Mensajes del chat"
                >
                    <ul className="flex min-h-full flex-col justify-end gap-4" role="list">
                        {messages.map((message) => {
                            const isUser = message.role === 'user'
                            return (
                                <li
                                    key={message.id}
                                    className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}
                                >
                                    <div className={` rounded-2xl px-4 py-3 sm:max-w-[75%] ${isUser ? 'bg-emerald-800 text-white' : 'border border-emerald-200 bg-white/90 text-slate-800'}`}>
                                        <ReactMarkdown
                                            remarkPlugins={[remarkGfm]}>
                                            {message.content}
                                        </ReactMarkdown>
                                    </div>
                                </li>
                            )
                        })}

                        {isLoading ? (
                            <li className="flex justify-start">
                                <TypingIndicator />
                            </li>
                        ) : null}
                    </ul>
                    <div ref={listEndRef} aria-hidden="true" />
                </section>

                <form onSubmit={handleSubmit} className="shrink-0 px-4 py-4 sm:px-6 sm:py-5">
                    <label htmlFor="chat-input" className="sr-only">
                        Escribe tu mensaje
                    </label>
                    <div className="flex items-end gap-3 rounded-full border border-emerald-200 bg-white/90 p-2 shadow-sm">
                        <ChatTextarea
                            id="chat-input"
                            ref={inputRef}
                            value={inputValue}
                            onChange={(event) => setInputValue(event.target.value)}
                            onKeyDown={handleInputKeyDown}
                            rows={1}
                            placeholder="Escribe tu mensaje..."
                        />
                        <ChatButton
                            type="submit"
                            disabled={!canSubmit}
                        >
                            {isLoading ? 'Enviando...' : 'Enviar'}
                        </ChatButton>
                    </div>
                </form>
            </div>
        </main>
    )
}

//  {messages.length === 0 ? (
//                             <li className="flex items-center justify-center py-8">
//                                 <p className="font-serif text-4xl tracking-tight text-slate-300 sm:text-5xl">NaturalSQL</p>
//                             </li>
//                         ) : null}
