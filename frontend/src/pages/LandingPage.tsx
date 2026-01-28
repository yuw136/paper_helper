import { SetStateAction, useEffect, useState } from 'react';
import { useNavigate } from 'react-router';
import { Resizable } from 're-resizable';
import {
  PanelLeftClose,
  PanelLeftOpen,
  LogOut,
  ChevronLeft,
  ChevronUp,
  RotateCw,
} from 'lucide-react';
import { FileDirectory } from '../components/FileDirectory';
import { FileSystemView } from '../components/FileSystemView';
import { FileNode } from '../types';
import { getFiles } from '../apis/Api';
import { transformFileTree } from '../utils/TransformFileTree';

export function LandingPage() {
  const navigate = useNavigate();
  const [isLeftPanelCollapsed, setIsLeftPanelCollapsed] = useState(false);
  const [leftPanelWidth, setLeftPanelWidth] = useState(280);
  const [fileSystem, setFileSystem] = useState<FileNode>({
    id: 'root',
    name: 'root',
    type: 'folder',
    path: '',
    children: new Map<string, FileNode>(),
  });
  const [lookupTable, setLookupTable] = useState(new Map<String, FileNode>());
  const [currentNodeId, setCurrentNodeId] = useState<string>('root');
  const [selectedId, setSelectedId] = useState<string>('root');

  const currentNode = lookupTable.get(currentNodeId) || fileSystem;

  useEffect(() => {
    async function initFileSystem() {
      const response = await getFiles();
      const allFiles = [...(response.papers || []), ...(response.reports || [])];
      const { root, lookupTable } = transformFileTree(allFiles);
      setFileSystem(root);
      setLookupTable(lookupTable);
    }

    initFileSystem();
  }, []);

  const handleSelect = (node: FileNode) => {
    setCurrentNodeId(node.id);
    setSelectedId(node.id);
    if (node.type === 'file') {
      //give fileSystem, nodeId, lookupTable
      navigate(`/files/${node.id}`);
    }
  };

  // Handle single click in middle panel - just update selection, not navigation
  const handleSingleClick = (node: FileNode) => {
    setSelectedId(node.id);
  };

  // const handleGoBack = () => {
  //   if(!currentNode.parentId) {
  //     console.log("already at root")
  //     return;
  //   }
  //   setCurrentNodeId(currentNode.parentId);
  // }

  const handleGoUp = () => {
    if (!currentNode.parentId) {
      console.log('already at root');
      return;
    }
    setCurrentNodeId(currentNode.parentId);
    setSelectedId(currentNode.parentId);
  };

  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      const response = await getFiles();
      const allFiles = [...(response.papers || []), ...(response.reports || [])];
      const { root, lookupTable: newLookupTable } = transformFileTree(allFiles);
      setFileSystem(root);
      setLookupTable(newLookupTable);
      // Keep current node if it still exists, otherwise go to root
      if (!newLookupTable.has(currentNodeId)) {
        setCurrentNodeId('root');
      }
      if (!newLookupTable.has(selectedId)) {
        setSelectedId('root');
      }
    } catch (error) {
      console.error('Failed to refresh files:', error);
    } finally {
      setIsRefreshing(false);
    }
  };

  //Give FileSystem Grid View
  const gridViewNodes = (nodeId: string) => {
    return currentNode.type === 'folder' && currentNode.children
      ? Array.from(currentNode.children.values())
      : [];
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
              <h2 className="text-sm font-semibold text-gray-700">
                PAPER HELPER
              </h2>
            </div>
            <div className="flex-1 overflow-hidden">
              <FileDirectory
                node={fileSystem}
                selectedId={selectedId}
                onSelect={handleSelect}
              />
            </div>
          </div>
        </Resizable>
      )}

      {/* Navigation Toolbar - Windows Explorer Style */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <div className="flex items-center gap-1 px-2 py-2 bg-gray-100 border-b border-gray-300">
          {/* Up Button */}
          <button
            onClick={handleGoUp}
            disabled={!currentNode.parentId}
            className="p-1.5 rounded hover:bg-gray-200 disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:bg-transparent transition-colors"
            title="Up to parent folder"
          >
            <ChevronUp className="w-5 h-5 text-gray-600" />
          </button>

          {/* Refresh Button */}
          <button
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="p-1.5 rounded hover:bg-gray-200 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            title="Refresh"
          >
            <RotateCw
              className={`w-5 h-5 text-gray-600 ${isRefreshing ? 'animate-spin' : ''}`}
            />
          </button>

          {/* Path Display */}
          <div className="flex-1 ml-2">
            <div className="flex items-center bg-white border border-gray-300 rounded px-3 py-1.5 text-sm text-gray-700">
              <span className="truncate">{currentNode.path || '/'}</span>
            </div>
          </div>
        </div>

        {/* Main Content - File System Grid View */}
        <div className="flex-1 overflow-auto">
          <FileSystemView
            nodes={gridViewNodes(currentNodeId)}
            selectedId={selectedId}
            onSelect={handleSelect}
            onSingleClick={handleSingleClick}
          />
        </div>
      </div>

      {/* Left Panel Toggle Button */}
      <button
        onClick={() => setIsLeftPanelCollapsed(!isLeftPanelCollapsed)}
        className="absolute top-4 z-10 p-2 bg-white border border-gray-300 rounded hover:bg-gray-100 shadow-sm transition-all"
        style={{
          left: isLeftPanelCollapsed ? '8px' : `${leftPanelWidth + 8}px`,
        }}
        title={
          isLeftPanelCollapsed ? 'Show file directory' : 'Hide file directory'
        }
      >
        {isLeftPanelCollapsed ? (
          <PanelLeftOpen className="w-4 h-4" />
        ) : (
          <PanelLeftClose className="w-4 h-4" />
        )}
      </button>
    </div>
  );
}
