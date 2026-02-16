import { createRoot } from 'react-dom/client';
import App from './App.tsx';
import './styles/globals.css';

type AppRootStore = {
  __paperHelperRoot?: ReturnType<typeof createRoot>;
  __paperHelperRootInitStack?: string;
};

const container = document.getElementById('root');
if (!container) {
  throw new Error('Root container #root was not found');
}

const rootStore = globalThis as typeof globalThis & AppRootStore;
if (import.meta.env.DEV && rootStore.__paperHelperRoot) {
  // Debug duplicate entry execution in dev (often HMR or duplicate script import).
  console.warn('[main.tsx] Reusing existing React root. Entry executed again.', {
    firstCreateRootStack: rootStore.__paperHelperRootInitStack,
    currentExecutionStack: new Error().stack,
  });
}

const root = rootStore.__paperHelperRoot ?? createRoot(container);
rootStore.__paperHelperRoot = root;
if (!rootStore.__paperHelperRootInitStack) {
  rootStore.__paperHelperRootInitStack = new Error().stack;
}

root.render(<App />);
