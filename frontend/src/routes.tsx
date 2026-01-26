import { createBrowserRouter, Navigate } from 'react-router';
import { Login } from './pages/Login';
import { Signup } from './pages/Signup';
import { LandingPage } from './pages/LandingPage';
import { PDFReaderPage } from './pages/PDFReaderPage';

// Simple auth check (in a real app, this would check actual auth state)
const isAuthenticated = () => {
  return localStorage.getItem('isAuthenticated') === 'true';
};

// Protected Route wrapper
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  return isAuthenticated() ? <>{children}</> : <Navigate to="/login" replace />;
};

export const router = createBrowserRouter([
  {
    path: '/login',
    element: <Login />,
  },
  {
    path: '/signup',
    element: <Signup />,
  },
  {
    path: '/files',
    element: (
      <ProtectedRoute>
        <LandingPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/files/:fileId',
    element: (
      <ProtectedRoute>
        <PDFReaderPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/files/upload',
    element: (
      <ProtectedRoute>
        <div />
      </ProtectedRoute>
    ),
  },
  {
    path: '*',
    element: <Navigate to="/" replace />,
  },
]);
