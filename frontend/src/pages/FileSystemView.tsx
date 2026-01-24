import { useNavigate } from 'react-router';
import { FileText, Folder } from 'lucide-react';
import { FileNode } from '../App';

interface FileSystemViewProps {
  files: FileNode[];
}

export function FileSystemView({ files }: FileSystemViewProps) {
  const navigate = useNavigate();

  const handleFileClick = (file: FileNode) => {
    if (file.type === 'file') {
      navigate(`/pdf/${file.id}`);
    }
  };

  return (
    <div className="flex-1 bg-white overflow-auto p-8">
      <div className="max-w-7xl mx-auto">
        <h2 className="text-2xl font-semibold text-gray-800 mb-6">Your Documents</h2>
        
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-6">
          {files.map((file) => (
            <button
              key={file.id}
              onClick={() => handleFileClick(file)}
              className="flex flex-col items-center p-4 rounded-lg hover:bg-gray-50 transition-colors group"
            >
              <div className="relative mb-3">
                {file.type === 'folder' ? (
                  <div className="w-20 h-20 flex items-center justify-center bg-yellow-100 rounded-lg group-hover:bg-yellow-200 transition-colors">
                    <Folder className="w-12 h-12 text-yellow-600" fill="currentColor" />
                  </div>
                ) : (
                  <div className="w-20 h-20 flex items-center justify-center bg-red-50 border-2 border-red-400 rounded-lg group-hover:bg-red-100 transition-colors">
                    <FileText className="w-10 h-10 text-red-600" />
                    <div className="absolute bottom-2 left-1/2 transform -translate-x-1/2 text-xs font-semibold text-red-600">
                      PDF
                    </div>
                  </div>
                )}
              </div>
              <p className="text-sm text-gray-800 text-center line-clamp-2 w-full">
                {file.name.length > 30 ? file.name.substring(0, 30) + '...' : file.name}
              </p>
            </button>
          ))}
        </div>

        {files.length === 0 && (
          <div className="text-center py-20">
            <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">No documents found</p>
          </div>
        )}
      </div>
    </div>
  );
}
