import { useState } from 'react';
import * as React from 'react';
import { ChevronRight, ChevronDown, File, Folder, FolderOpen } from 'lucide-react';
import { FileNode } from '../App';

interface FileDirectoryProps {
  onFileSelect: (file: FileNode) => void;
  selectedFile: FileNode | null;
}

// Mock file system data
export const mockFileSystem: FileNode[] = [
  {
    id: 'server',
    name: 'server',
    type: 'folder',
    path: '/server',
    children: [
      {
        id: 'data',
        name: 'data',
        type: 'folder',
        path: '/server/data',
        children: [
          {
            id: 'pdfs',
            name: 'pdfs',
            type: 'folder',
            path: '/server/data/pdfs',
            children: [
              {
                id: 'pdf1',
                name: '2310.01340v2_Extensions_of_Schoen_Simon.pdf',
                type: 'file',
                path: '/server/data/pdfs/2310.01340v2_Extensions_of_Schoen_Simon.pdf',
              },
              {
                id: 'pdf2',
                name: 'Machine_Learning_Research.pdf',
                type: 'file',
                path: '/server/data/pdfs/Machine_Learning_Research.pdf',
              },
              {
                id: 'pdf3',
                name: 'Quantum_Computing_Basics.pdf',
                type: 'file',
                path: '/server/data/pdfs/Quantum_Computing_Basics.pdf',
              },
            ],
          },
        ],
      },
      {
        id: 'pycache',
        name: '__pycache__',
        type: 'folder',
        path: '/server/__pycache__',
        children: [],
      },
    ],
  },
  {
    id: 'chatbox',
    name: 'chatbox',
    type: 'folder',
    path: '/chatbox',
    children: [],
  },
  {
    id: 'managers',
    name: 'managers',
    type: 'folder',
    path: '/managers',
    children: [],
  },
  {
    id: 'models',
    name: 'models',
    type: 'folder',
    path: '/models',
    children: [],
  },
  {
    id: 'public',
    name: 'public',
    type: 'folder',
    path: '/public',
    children: [],
  },
];

interface FileTreeItemProps {
  node: FileNode;
  level: number;
  onFileSelect: (file: FileNode) => void;
  selectedFile: FileNode | null;
}

const FileTreeItem: React.FC<FileTreeItemProps> = ({ node, level, onFileSelect, selectedFile }) => {
  const [isExpanded, setIsExpanded] = useState(level < 3); // Auto-expand first 3 levels
  const [clickTimeout, setClickTimeout] = useState<NodeJS.Timeout | null>(null);

  const handleClick = () => {
    if (node.type === 'folder') {
      setIsExpanded(!isExpanded);
    } else {
      // Single click for files - just toggle expansion or select
      if (clickTimeout) {
        // This is a double click
        clearTimeout(clickTimeout);
        setClickTimeout(null);
        onFileSelect(node);
      } else {
        // Wait for potential second click
        const timeout = setTimeout(() => {
          setClickTimeout(null);
        }, 300);
        setClickTimeout(timeout);
      }
    }
  };

  const handleDoubleClick = () => {
    if (clickTimeout) {
      clearTimeout(clickTimeout);
      setClickTimeout(null);
    }
    if (node.type === 'file') {
      onFileSelect(node);
    }
  };

  const isSelected = selectedFile?.id === node.id;

  return (
    <div>
      <div
        className={`flex items-center py-1 px-2 cursor-pointer hover:bg-gray-200 ${
          isSelected ? 'bg-blue-100' : ''
        }`}
        style={{ paddingLeft: `${level * 12 + 8}px` }}
        onClick={handleClick}
        onDoubleClick={handleDoubleClick}
      >
        {node.type === 'folder' && (
          <span className="mr-1 text-gray-600">
            {isExpanded ? (
              <ChevronDown className="w-4 h-4" />
            ) : (
              <ChevronRight className="w-4 h-4" />
            )}
          </span>
        )}
        {node.type === 'file' ? (
          <File className="w-4 h-4 mr-2 text-gray-600" />
        ) : isExpanded ? (
          <FolderOpen className="w-4 h-4 mr-2 text-yellow-600" />
        ) : (
          <Folder className="w-4 h-4 mr-2 text-yellow-600" />
        )}
        <span className="text-sm truncate text-gray-800" title={node.name}>
          {node.name}
        </span>
      </div>
      {node.type === 'folder' && isExpanded && node.children && (
        <div>
          {node.children.map(child => (
            <FileTreeItem
              key={child.id}
              node={child}
              level={level + 1}
              onFileSelect={onFileSelect}
              selectedFile={selectedFile}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export function FileDirectory({ onFileSelect, selectedFile }: FileDirectoryProps) {
  return (
    <div className="h-full flex flex-col bg-gray-50">
      <div className="flex-1 overflow-y-auto">
        {mockFileSystem.map(node => (
          <FileTreeItem
            key={node.id}
            node={node}
            level={0}
            onFileSelect={onFileSelect}
            selectedFile={selectedFile}
          />
        ))}
      </div>
    </div>
  );
}