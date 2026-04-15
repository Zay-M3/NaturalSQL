import { useState } from 'react'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { dracula } from 'react-syntax-highlighter/dist/esm/styles/prism';

type CodeBlockProps = {
  code: string
  language?: string
  title?: string
}

export const CodeBlock = ({ code, language = 'bash', title }: CodeBlockProps) => {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(code)
      setCopied(true)
      setTimeout(() => setCopied(false), 1500)
    } catch {
      setCopied(false)
    }
  }

  return (
    <div className="overflow-hidden rounded-xl border border-slate-200 bg-slate-950 text-slate-100">
      <div className="flex items-center justify-between border-b border-slate-800 px-3 py-2 text-xs text-slate-300">
        <span>{title ?? language}</span>
        <button
          type="button"
          onClick={handleCopy}
          className="rounded-md border border-slate-700 px-2 py-1 text-[11px] font-medium text-slate-200 transition hover:bg-slate-800"
        >
          {copied ? 'Copied' : 'Copy'}
        </button>
      </div>
      {/* <pre className="overflow-x-auto p-4 text-sm leading-6">
        <code>{code}</code>
      </pre> */}
      <SyntaxHighlighter language={language} style={dracula} customStyle={{ margin: 0, padding: '1rem', backgroundColor: 'transparent' }}>
        {code}
      </SyntaxHighlighter>
    </div>
  )
}
