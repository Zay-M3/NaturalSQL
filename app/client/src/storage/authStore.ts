import { GoogleAuthProvider, onAuthStateChanged, signInWithPopup, signOut } from 'firebase/auth'
import { create } from 'zustand'

import { firebaseAuth } from './firebase'

type AuthUser = {
  uid: string
  email: string | null
  messagesChat: number
}

type AuthState = {
  user: AuthUser | null
  isLoading: boolean
  error: string | null
  isInitialized: boolean
  initAuthListener: () => void
  loginWithGoogle: () => Promise<void>
  logout: () => Promise<void>
  incrementMessagesChat: () => void
}

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isLoading: false,
  error: null,
  isInitialized: false,
  initAuthListener: () => {
    onAuthStateChanged(firebaseAuth, (firebaseUser) => {
      if (!firebaseUser) {
        set({ user: null, isInitialized: true })
        return
      }

      fetch(`${apiBaseUrl}/api/auth/me`, {
        method: 'GET',
        credentials: 'include',
      })
        .then(async (response) => {
          if (!response.ok) {
            throw new Error('Unable to load user profile')
          }
          return response.json()
        })
        .then((data: { uid: string; email: string | null; messages_chat: number }) => {
          set({
            user: {
              uid: data.uid,
              email: data.email,
              messagesChat: data.messages_chat,
            },
            isInitialized: true,
          })
        })
        .catch(() => {
          set({
            user: {
              uid: firebaseUser.uid,
              email: firebaseUser.email,
              messagesChat: 0,
            },
            isInitialized: true,
          })
        })
    })
  },
  loginWithGoogle: async () => {
    set({ isLoading: true, error: null })
    try {
      const provider = new GoogleAuthProvider()
      const credential = await signInWithPopup(firebaseAuth, provider)
      const idToken = await credential.user.getIdToken()

      const response = await fetch(`${apiBaseUrl}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ idToken }),
      })

      if (!response.ok) {
        throw new Error('Unable to complete backend login')
      }

      const meResponse = await fetch(`${apiBaseUrl}/api/auth/me`, {
        method: 'GET',
        credentials: 'include',
      })

      if (!meResponse.ok) {
        throw new Error('Unable to load user profile')
      }

      const meData: { uid: string; email: string | null; messages_chat: number } = await meResponse.json()

      set({
        user: {
          uid: meData.uid,
          email: meData.email,
          messagesChat: meData.messages_chat,
        },
        isLoading: false,
      })
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Authentication failed',
        isLoading: false,
      })
    }
  },
  logout: async () => {
    set({ isLoading: true, error: null })
    try {
      await fetch(`${apiBaseUrl}/api/auth/logout`, {
        method: 'POST',
        credentials: 'include',
      })
      await signOut(firebaseAuth)
      set({ user: null, isLoading: false })
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Logout failed',
        isLoading: false,
      })
    }
  },
  incrementMessagesChat: () => {
    set((state) => {
      if (!state.user) {
        return state
      }

      return {
        user: {
          ...state.user,
          messagesChat: state.user.messagesChat + 1,
        },
      }
    })
  },
}))
