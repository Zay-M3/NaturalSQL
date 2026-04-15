import { useEffect, useState } from 'react'

type GitHubRepoResponse = {
	stargazers_count?: number
	html_url?: string
	full_name?: string
	description?: string | null
}

type GitHubUserResponse = {
	login?: string
	name?: string | null
	bio?: string | null
	avatar_url?: string
	html_url?: string
}

export type GitHubProjectData = {
	owner: string
	repo: string
	repoFullName: string
	repoUrl: string
	repoDescription: string | null
	stars: number
	profileLogin: string
	profileName: string | null
	profileBio: string | null
	profileAvatarUrl: string
	profileUrl: string
}

type UseGitHubProjectResult = {
	data: GitHubProjectData | null
	isLoading: boolean
	error: string | null
}

export function useGitHubProject(owner: string, repo: string): UseGitHubProjectResult {
	const [data, setData] = useState<GitHubProjectData | null>(null)
	const [isLoading, setIsLoading] = useState(true)
	const [error, setError] = useState<string | null>(null)

	useEffect(() => {
		let ignore = false
		const controller = new AbortController()

		const fetchProject = async () => {
			setIsLoading(true)
			setError(null)

			try {
				const [repoResponse, userResponse] = await Promise.all([
					fetch(`https://api.github.com/repos/${owner}/${repo}`, {
						signal: controller.signal,
						headers: { Accept: 'application/vnd.github+json' },
					}),
					fetch(`https://api.github.com/users/${owner}`, {
						signal: controller.signal,
						headers: { Accept: 'application/vnd.github+json' },
					}),
				])

				if (!repoResponse.ok) {
					throw new Error(`GitHub repo request failed with status ${repoResponse.status}`)
				}

				const repoData = (await repoResponse.json()) as GitHubRepoResponse
				const userData = userResponse.ok ? ((await userResponse.json()) as GitHubUserResponse) : null

				if (ignore) return

				setData({
					owner,
					repo,
					repoFullName: repoData.full_name ?? `${owner}/${repo}`,
					repoUrl: repoData.html_url ?? `https://github.com/${owner}/${repo}`,
					repoDescription: repoData.description ?? null,
					stars: repoData.stargazers_count ?? 0,
					profileLogin: userData?.login ?? owner,
					profileName: userData?.name ?? null,
					profileBio: userData?.bio ?? null,
					profileAvatarUrl: userData?.avatar_url ?? '',
					profileUrl: userData?.html_url ?? `https://github.com/${owner}`,
				})
			} catch (fetchError) {
				if (ignore || controller.signal.aborted) return
				setError(fetchError instanceof Error ? fetchError.message : 'Unable to load GitHub data')
			} finally {
				if (!ignore) {
					setIsLoading(false)
				}
			}
		}

		void fetchProject()

		return () => {
			ignore = true
			controller.abort()
		}
	}, [owner, repo])

	return { data, isLoading, error }
}
