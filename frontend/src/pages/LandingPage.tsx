import { useState } from 'react';
import { useNavigate } from 'react-router';
import { Resizable } from 're-resizable';
import { PanelLeftClose, PanelLeftOpen, LogOut } from 'lucide-react';
import { FileDirectory, mockFileSystem } from '../components/FileDirectory';
import { FileSystemView } from './FileSystemView';
import { FileNode } from '../App';

export function LandingPage() {
  const navigate = useNavigate();
  const [isLeftPanelCollapsed, setIsLeftPanelCollapsed] = useState(false);
  const [leftPanelWidth, setLeftPanelWidth] = useState(280);

  // Get all PDF files from the file system
  const getAllFiles = (nodes: FileNode[]): FileNode[] => {
    let files: FileNode[] = [];
    for (const node of nodes) {
      if (node.type === 'file') {
        files.push(node);
      }
      if (node.children) {
        files = files.concat(getAllFiles(node.children));
      }
    }
    return files;
  };

  const allPdfFiles = getAllFiles(mockFileSystem);

  const handleFileSelect = (file: FileNode) => {
    if (file.type === 'file') {
      navigate(`/pdf/${file.id}`);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('isAuthenticated');
    localStorage.removeItem('userEmail');
    localStorage.removeItem('userName');
    navigate('/login');
  };

  return (
    <div className="flex h-screen bg-white text-black overflow-hidden">
      {/* Left Sidebar - File Directory */}
      {!isLeftPanelCollapsed && (
        <Resizable
          size={{ width: leftPanelWidth, height: '100%' }}
          onResizeStop={(e, direction, ref, d) => {
            setLeftPanelWidth(leftPanelWidth + d.width);
          }}
          minWidth={100}
          maxWidth={600}
          enable={{ right: true }}
          className="bg-gray-50 border-r border-gray-300 flex-shrink-0"
        >
          <div className="h-full flex flex-col">
            <div className="px-4 py-3 border-b border-gray-300 flex items-center justify-between">
              <h2 className="text-sm font-semibold text-gray-700">PAPER_HELPER</h2>
              <button
                onClick={handleLogout}
                className="p-1.5 hover:bg-gray-200 rounded transition-colors text-gray-600"
                title="Logout"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
            <div className="flex-1 overflow-hidden">
              <FileDirectory onFileSelect={handleFileSelect} selectedFile={null} />
            </div>
          </div>
        </Resizable>
      )}

      {/* Left Panel Toggle Button */}
      <button
        onClick={() => setIsLeftPanelCollapsed(!isLeftPanelCollapsed)}
        className="absolute top-4 z-10 p-2 bg-white border border-gray-300 rounded hover:bg-gray-100 shadow-sm transition-all"
        style={{ left: isLeftPanelCollapsed ? '8px' : `${leftPanelWidth + 8}px` }}
        title={isLeftPanelCollapsed ? 'Show file directory' : 'Hide file directory'}
      >
        {isLeftPanelCollapsed ? <PanelLeftOpen className="w-4 h-4" /> : <PanelLeftClose className="w-4 h-4" />}
      </button>

      {/* Main Content - File System Grid View */}
      <FileSystemView files={allPdfFiles} />
    </div>
  );
}
