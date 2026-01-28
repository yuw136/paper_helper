import { useState, useEffect } from 'react';
import * as React from 'react';
import {
  ChevronRight,
  ChevronDown,
  File,
  Folder,
  FolderOpen,
} from 'lucide-react';
import { FileNode } from '../types';

interface FileDirectoryProps {
  //root node
  node: FileNode;
  selectedId: string;
  onSelect: (node: FileNode) => void;
}

interface FileTreeItemProps {
  node: FileNode;
  level: number;
  selectedId: string;
  onSelect: (node: FileNode) => void;
}

//FileTreeItem shows tree structure of the file system
const FileTreeItem = ({
  node,
  level,
  onSelect,
  selectedId,
}: FileTreeItemProps) => {
  const [isExpanded, setIsExpanded] = useState(level < 1);

  // Auto-expand when this folder is selected
  useEffect(() => {
    if (selectedId === node.id && node.type === 'folder') {
      setIsExpanded(true);
    }
  }, [selectedId, node.id, node.type]);

  const handleClick = (e: React.MouseEvent) => {
    e.stopPropagation();

    onSelect(node);

    if (node.type === 'folder') {
      setIsExpanded(!isExpanded);
    }
  };

  const isSelected = selectedId === node.id;

  const childrenArray = node.children ? Array.from(node.children.values()) : [];
  const hasChildren = childrenArray.length > 0;

  return (
    <div>
      <div
        className={`flex items-center py-1 px-2 cursor-pointer transition-colors duration-150 ease-in-out ${
          isSelected
            ? 'bg-blue-100 text-blue-700'
            : 'hover:bg-gray-200 text-gray-700'
        }`}
        style={{ paddingLeft: `${level * 12 + 12}px` }} // Increase indentation
        onClick={handleClick}
      >
        {/* 1. folder icon*/}
        <span className="mr-1.5 flex-shrink-0">
          {node.type === 'folder' ? (
            isExpanded ? (
              <ChevronDown className="w-4 h-4 text-gray-500" />
            ) : (
              <ChevronRight className="w-4 h-4 text-gray-400" />
            )
          ) : (
            <span className="w-4 h-4 block" />
          )}
        </span>

        {/* 2. file icon   */}
        <span className="mr-2 flex-shrink-0">
          {node.type === 'file' ? (
            <File className="w-4 h-4 text-gray-500" />
          ) : isExpanded ? (
            <FolderOpen className="w-4 h-4 text-yellow-500 fill-yellow-500" />
          ) : (
            <Folder className="w-4 h-4 text-yellow-500 fill-yellow-500" />
          )}
        </span>

        {/* 3. file name */}
        <span className="text-sm truncate select-none">{node.name}</span>
      </div>

      {/* sub nodes area */}
      {node.type === 'folder' && isExpanded && hasChildren && (
        <div>
          {childrenArray.map((child) => (
            <FileTreeItem
              key={child.id}
              node={child}
              level={level + 1}
              selectedId={selectedId}
              onSelect={onSelect}
            />
          ))}
        </div>
      )}
    </div>
  );
};

// Left side bar component
export function FileDirectory({
  node,
  selectedId,
  onSelect,
}: FileDirectoryProps) {
  // we don't render the root node, only render its children
  if (!node || !node.children) {
    return <div className="p-4 text-gray-400 text-xs">Loading files...</div>;
  }

  const rootChildren = Array.from(node.children.values());

  return (
    <div className="h-full flex flex-col bg-gray-50 select-none">
      <div className="flex-1 overflow-y-auto py-2">
        {rootChildren.length === 0 ? (
          <div className="px-4 text-gray-400 text-sm">No files found</div>
        ) : (
          rootChildren.map((child) => (
            <FileTreeItem
              key={child.id}
              node={child}
              level={0}
              selectedId={selectedId}
              onSelect={onSelect}
            />
          ))
        )}
      </div>
    </div>
  );
}
