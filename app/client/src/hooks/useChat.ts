import { useEffect, useRef, useState } from 'react'
import type { KeyboardEvent, SyntheticEvent } from 'react'

import { useAuthStore } from '../storage/authStore'

export type ChatMessage = {
    id: number
    role: 'user' | 'assistant'
    content: string
    table?: {
        columns: string[]
        rows: Array<Record<string, unknown>>
    }
}


export const useChat = () => {
    const [messages, setMessages] = useState<ChatMessage[]>([])
    const [inputValue, setInputValue] = useState('')
    const [isLoading, setIsLoading] = useState(false)
    const listEndRef = useRef<HTMLDivElement | null>(null)
    const inputRef = useRef<HTMLTextAreaElement | null>(null)
    const nextIdRef = useRef(1)
    const incrementMessagesChat = useAuthStore((state) => state.incrementMessagesChat)

    const hasMessages = messages.length > 0 || isLoading
    const canSubmit = !isLoading && inputValue.trim().length > 0

    useEffect(() => {
        listEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' })
    }, [messages, isLoading])

    useEffect(() => {
        inputRef.current?.focus()
    }, [])

    const sendMessage = async () => {
        const trimmed = inputValue.trim()
        if (!trimmed || isLoading) {
            return
        }

        const userMessage: ChatMessage = {
            id: nextIdRef.current,
            role: 'user',
            content: trimmed,
        }
        nextIdRef.current += 1

        setMessages((prev) => [...prev, userMessage])
        setInputValue('')
        setIsLoading(true)

        //llamando a la pide chat /api/chat/message/
        try {
            const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/chat/message/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
                body: JSON.stringify({ message: trimmed }),
            })

            if (!response.ok) {
                let errorMessage = 'Error al procesar la solicitud.'
                if (response.status === 403) {
                    errorMessage = 'Chat quota reached'
                }

                //Seteamos un mensaje de error en el chat
                setMessages((prev) => [
                    ...prev,
                    {
                        id: nextIdRef.current,
                        role: 'assistant',
                        content: errorMessage,
                    }
                ])

                throw new Error(`Error en la respuesta del servidor: ${response.statusText}`)
            }

            //manejo de error asgi aplication error
            if (response.status === 500) {
                setMessages((prev) => [
                    ...prev,
                    {
                        id: nextIdRef.current,
                        role: 'assistant',
                        content: 'Error interno del servidor.'
                    }
                ])
                throw new Error('Error interno del servidor')
            }

            const reader = response.body?.getReader()
            if (!reader) {
                throw new Error('No se pudo obtener el lector de la respuesta')
            }

            const decoder = new TextDecoder()
            let assistantResponse = ''

            while (true) {
                
                const { done, value } = await reader.read()
                if (done) break

                const chunk = decoder.decode(value, { stream: true })
                assistantResponse += chunk
                setMessages((prev) => {
                    const lastMessage = prev[prev.length - 1]
                    if (lastMessage && lastMessage.role === 'assistant') {
                        // Actualizar el último mensaje del asistente con el nuevo contenido
                        const updatedMessage = {
                            ...lastMessage,
                            content: lastMessage.content + chunk,
                        }
                        return [...prev.slice(0, -1), updatedMessage]
                    } else {
                        // Agregar un nuevo mensaje del asistente
                        const newMessage: ChatMessage = {
                            id: nextIdRef.current,
                            role: 'assistant',
                            content: chunk,
                        }
                        nextIdRef.current += 1
                        return [...prev, newMessage]
                    }
                })
            }

            if (assistantResponse.trim().length > 0) {
                incrementMessagesChat()
            }


        } catch (error) {
            console.error('Error al enviar el mensaje:', error)
            setIsLoading(false)
        } finally {
            setIsLoading(false)
        }
    }

    const handleSubmit = (event: SyntheticEvent<HTMLFormElement>) => {
        event.preventDefault()
        sendMessage()
    }

    const handleInputKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault()
            sendMessage()
        }
    }

    return {
        messages,
        inputValue,
        isLoading,
        hasMessages,
        canSubmit,
        listEndRef,
        inputRef,
        setInputValue,
        handleSubmit,
        handleInputKeyDown,
    }
}
