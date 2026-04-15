import { useEffect } from 'react'

import { useAuthStore } from './authStore'

export const AuthBootstrap = () => {
  const initAuthListener = useAuthStore((state) => state.initAuthListener)

  useEffect(() => {
    initAuthListener()
  }, [initAuthListener])

  return null
}
