import { StrictMode } from 'react'
import './index.css'
import { RouterProvider } from 'react-router-dom'
import { router } from './routes/route'
import { AuthBootstrap } from './storage/AuthBootstrap';
import { createRoot } from 'react-dom/client'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AuthBootstrap />
    <RouterProvider router={router} />
  </StrictMode>,
);

