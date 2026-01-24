import { RouterProvider } from 'react-router';
import { router } from './routes';

// Export types for use in other components
export interface FileNode {
  id: string;
  name: string;
  type: 'file' | 'folder';
  path: string;
  children?: FileNode[];
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export interface ChatHistory {
  id: string;
  fileId: string;
  fileName: string;
  messages: ChatMessage[];
  lastUpdated: Date;
}

function App() {
  return <RouterProvider router={router} />;
}

export default App;
