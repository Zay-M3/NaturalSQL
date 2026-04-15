import { useGitHubProject } from '../../hooks/useGitHubProject'

type GitHubProjectBadgeProps = {
	owner: string
	repo: string
	variant?: 'compact' | 'detailed'
	className?: string
	creatorName?: string
	showCreator?: boolean
	showBio?: boolean
}

const formatNumber = (value: number) => new Intl.NumberFormat('en-US').format(value)

export const GitHubProjectBadge = ({
	owner,
	repo,
	variant = 'compact',
	className = '',
	creatorName,
	showCreator = false,
	showBio = true,
}: GitHubProjectBadgeProps) => {
	const { data, isLoading } = useGitHubProject(owner, repo)

	if (variant === 'compact') {
		return (
			<a
				href={data?.repoUrl ?? `https://github.com/${owner}/${repo}`}
				target="_blank"
				rel="noreferrer"
				aria-label={`${owner}/${repo} repository and star count`}
				className={`inline-flex items-center gap-2 text-slate-700 transition-colors hover:text-emerald-700 ${className}`.trim()}
			>
				<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="h-5 w-5">
					<path d="M12 2A10 10 0 0 0 8.84 21.5c.5.08.68-.22.68-.48v-1.7c-2.78.6-3.37-1.34-3.37-1.34-.45-1.15-1.1-1.45-1.1-1.45-.9-.62.07-.6.07-.6 1 .07 1.53 1.02 1.53 1.02.88 1.5 2.31 1.07 2.87.82.09-.64.35-1.07.63-1.31-2.22-.25-4.56-1.1-4.56-4.93 0-1.1.4-2 1.03-2.72-.1-.25-.45-1.27.1-2.64 0 0 .84-.27 2.75 1.04a9.6 9.6 0 0 1 5 0c1.9-1.3 2.74-1.04 2.74-1.04.55 1.37.2 2.39.1 2.64.64.72 1.03 1.62 1.03 2.72 0 3.84-2.34 4.67-4.57 4.92.36.3.68.9.68 1.82v2.7c0 .27.18.57.69.47A10 10 0 0 0 12 2Z" />
				</svg>
				<span className="inline-flex items-center gap-1 text-xs font-semibold uppercase tracking-[0.14em]">
					<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="h-4 w-4">
						<path d="M12 2.5l2.92 5.92 6.53.95-4.72 4.6 1.11 6.5L12 17.39l-5.84 3.08 1.11-6.5-4.72-4.6 6.53-.95L12 2.5Z" />
					</svg>
					{isLoading ? '...' : formatNumber(data?.stars ?? 0)}
				</span>
			</a>
		)
	}

	return (
		<article className={`rounded-2xl  p-4 text-slate-800 ${className}`.trim()}>
			<div className="flex items-center gap-3">
				{data?.profileAvatarUrl ? (
					<img src={data.profileAvatarUrl} alt={`${data.profileLogin} avatar`} className="h-12 w-12 rounded-full border border-emerald-100" />
				) : (
					<div className="h-12 w-12 rounded-full border border-emerald-100 bg-emerald-50" aria-hidden="true" />
				)}
				<div>
					<p className="text-[11px] uppercase tracking-[0.14em] text-slate-500">GitHub Profile</p>
					<a
						href={data?.profileUrl ?? `https://github.com/${owner}`}
						target="_blank"
						rel="noreferrer"
						className="font-semibold tracking-wide text-slate-900 underline decoration-emerald-300 underline-offset-2"
					>
						{data?.profileName ?? data?.profileLogin ?? owner}
					</a>
				</div>
			</div>

			{showCreator && creatorName ? (
				<p className="mt-3 text-sm leading-relaxed text-slate-600">
					Created by <span className="font-semibold text-slate-800">{creatorName}</span>
				</p>
			) : null}

			{showBio && data?.profileBio ? <p className="mt-3 text-sm leading-relaxed text-slate-600">{data.profileBio}</p> : null}

			<a
				href={data?.repoUrl ?? `https://github.com/${owner}/${repo}`}
				target="_blank"
				rel="noreferrer"
				className="mt-4 inline-flex items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1.5 text-xs font-semibold uppercase tracking-[0.12em] text-emerald-800"
			>
				<span>{data?.repoFullName ?? `${owner}/${repo}`}</span>
				<span aria-hidden="true">•</span>
				<span>{isLoading ? 'Loading stars...' : `${formatNumber(data?.stars ?? 0)} stars`}</span>
			</a>
		</article>
	)
}
