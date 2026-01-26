export interface FileNode {
  id: string;
  name: string;
  type: 'file' | 'folder';
  path: string;
  parentId?: string;
  children?: Map<string, FileNode>;
}

export interface PdfExcerpt {
  id: string;
  content: string;
  pageNumber?: number;
  boundingRect?: {
    x1: number;
    y1: number;
    x2: number;
    y2: number;
  };
  timestamp?: number;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'ai' | 'system';
  content: string;
  excerpts?: PdfExcerpt[];
  timestamp: number;
}

export interface ChatHistory {
  id: string;
  fileId: string;
  title: string;
  createdAt: number;
  updatedAt: number;
}

export interface StreamEvent {
  node: string;           
  output: {
    answer?: string;      
    documents?: string[];
  };
}