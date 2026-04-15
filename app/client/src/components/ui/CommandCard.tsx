import { CodeBlock } from './CodeBlock'

type CommandCardProps = {
  command: string
  title?: string
}

export const CommandCard = ({ command, title = 'Terminal' }: CommandCardProps) => {
  return <CodeBlock code={command} language="bash" title={title} />
}
