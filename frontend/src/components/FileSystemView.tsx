import { useState } from 'react';
import { useNavigate } from 'react-router';
import { FileText, Folder } from 'lucide-react';
import { FileNode } from '../types';

//This is the file system view in the middle, mimicing windows/mac folder view

interface FileSystemViewProps {
  nodes: FileNode[];
  onSelect: (node: FileNode) => void;
}

export function FileSystemView({ nodes, onSelect }: FileSystemViewProps) {
  const navigate = useNavigate();
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const handleNodeClick = (node: FileNode) => {
    setSelectedId(node.id);
  };

  const handleNodeDoubleClick = (node: FileNode) => {
    onSelect(node);
  };

  return (
    <div className="flex-1 bg-white overflow-auto p-8">
      <div className="max-w-7xl mx-auto">
        <h2 className="text-2xl font-semibold text-gray-800 mb-6">
          Your Documents
        </h2>

        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-6">
          {nodes.map((node) => {
            const isSelected = selectedId === node.id;
            return (
              <button
                key={node.id}
                onClick={() => handleNodeClick(node)}
                onDoubleClick={() => handleNodeDoubleClick(node)}
                className={`flex flex-col items-center p-4 rounded-lg transition-colors group ${isSelected ? 'bg-blue-600 text-white' : 'hover:bg-gray-50'
                  }`}
              >
                <div className="relative mb-3">
                  {node.type === 'folder' ? (
                    <div
                      className={`w-20 h-20 flex items-center justify-center rounded-lg transition-colors ${isSelected
                        ? 'bg-blue-500'
                        : 'bg-yellow-100 group-hover:bg-yellow-200'
                        }`}
                    >
                      <Folder
                        className={`w-12 h-12 ${isSelected ? 'text-white' : 'text-yellow-600'}`}
                        fill="currentColor"
                      />
                    </div>
                  ) : (
                    <div
                      className={`w-20 h-20 flex items-center justify-center border-2 rounded-lg transition-colors ${isSelected
                        ? 'bg-blue-500 border-blue-400'
                        : 'bg-red-50 border-red-400 group-hover:bg-red-100'
                        }`}
                    >
                      <FileText
                        className={`w-10 h-10 ${isSelected ? 'text-white' : 'text-red-600'}`}
                      />
                      <div
                        className={`absolute bottom-2 left-1/2 transform -translate-x-1/2 text-xs font-semibold ${isSelected ? 'text-white' : 'text-red-600'
                          }`}
                      >
                        PDF
                      </div>
                    </div>
                  )}
                </div>
                <p
                  className={`text-sm text-center line-clamp-2 w-full ${isSelected ? 'text-white' : 'text-gray-800'
                    }`}
                >
                  {node.name.length > 30
                    ? node.name.substring(0, 30) + '...'
                    : node.name}
                </p>
              </button>
            );
          })}
        </div>

        {nodes.length === 0 && (
          <div className="text-center py-20">
            <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">This folder is empty.</p>
          </div>
        )}
      </div>
    </div>
  );
}
