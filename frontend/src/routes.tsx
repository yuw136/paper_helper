import { createBrowserRouter, Navigate } from 'react-router';

import { LandingPage } from './pages/LandingPage';
import { PDFReaderPage } from './pages/PDFReaderPage';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Navigate to="/files" replace />,
  },
  {
    path: '/files',
    element: <LandingPage />,
  },
  {
    path: '/files/:fileId',
    element: <PDFReaderPage />,
  },
  {
    path: '/files/upload',
    element: <div />,
  },
  {
    path: '*',
    element: <Navigate to="/files" replace />,
  },
]);
