import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router';
import { Resizable } from 're-resizable';
import {
  PanelLeftClose,
  PanelLeftOpen,
  PanelRightClose,
  PanelRightOpen,
  ArrowLeft,
} from 'lucide-react';
import { FileDirectory } from '../components/FileDirectory';
import { PDFViewer } from '../components/PDFViewer';
import { ChatPanel } from '../components/ChatPanel';
import { FileNode, ChatHistory, ChatMessage, PdfExcerpt } from '../types';
import { transformFileTree } from '../utils/TransformFileTree';
import { getFiles, getFileById } from '../apis/Api';
import { PdfSelection } from 'react-pdf-highlighter-plus';

export function PDFReaderPage() {
  const navigate = useNavigate();
  const { fileId } = useParams<{ fileId: string }>();

  const [fileSystem, setFileSystem] = useState<FileNode | null>(null);
  const [lookupTable, setLookupTable] = useState<Map<string, FileNode>>(
    new Map<string, FileNode>()
  );
  const [selectedFileId, setSelectedFileId] = useState<string>('');
  const [pdfUrl, setPdfUrl] = useState<string>('');

  const [PdfExcerpts, setPdfExcerpts] = useState<PdfExcerpt[]>([]);

  const [currentChatHistory, setCurrentChatHistory] =
    useState<ChatHistory | null>(null);
  const [allChatHistories, setAllChatHistories] = useState<ChatHistory[]>([]);

  const [isLeftPanelCollapsed, setIsLeftPanelCollapsed] = useState(false);
  const [isRightPanelCollapsed, setIsRightPanelCollapsed] = useState(false);
  const [leftPanelWidth, setLeftPanelWidth] = useState(280);
  const [rightPanelWidth, setRightPanelWidth] = useState(384);

  // Load file based on URL parameter
  useEffect(() => {
    async function init() {
      if (!fileId) return;

      // 获取文件系统（左边栏需要）
      const files = await getFiles();
      const { root, lookupTable } = transformFileTree(files);
      setFileSystem(root);
      setLookupTable(lookupTable);
      setSelectedFileId(fileId);

      // 根据 fileId 获取 PDF URL
      const file = await getFileById(fileId);
      setPdfUrl(file.path);
    }
    init();
  }, [fileId]);

  const handleFileSelect = (file: FileNode) => {
    if (file.type === 'file') {
      // 更新 URL，会触发 fileId 变化，进而触发 useEffect 重新加载
      navigate(`/files/${file.id}`);
    }
  };

  const handleSelectExcerpt = (selection: PdfSelection) => {
    const excerpt: PdfExcerpt = {
      id: `excerpt_${Date.now()}`,
      content: selection.content?.text || '',
      boundingRect: selection.position?.boundingRect,
      timestamp: Date.now()
    };
    setPdfExcerpts([...PdfExcerpts, excerpt]);
  };

  const handleDeleteExcerpt = (excerpt: PdfExcerpt) => {
    setPdfExcerpts(PdfExcerpts.filter((e) => e.id !== excerpt.id));
  };

  const handleSendMessage = (content: string) => {
    setPdfExcerpts([]);
  };

  const handleSelectChatHistory = (historyId: string) => {
    const history = allChatHistories.find((h) => h.id === historyId);
    if (history) {
      setCurrentChatHistory(history);
      // Navigate to the corresponding file
      navigate(`/files/${history.fileId}`);
    }
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
                Back to Home
              </h2>
              <button
                onClick={() => navigate('/files')}
                className="p-1.5 hover:bg-gray-200 rounded transition-colors text-gray-600"
                title="Back to home"
              >
                <ArrowLeft className="w-4 h-4" />
              </button>
            </div>
            <div className="flex-1 overflow-hidden">
              <FileDirectory
                node={fileSystem}
                selectedId={selectedFileId}
                onSelect={handleFileSelect}
              />
            </div>
          </div>
        </Resizable>
      )}

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

      {/* Center Panel - PDF Viewer */}
      <div className="flex-1 bg-white overflow-hidden">
        <PDFViewer onSelectExcerpt={handleSelectExcerpt} />
      </div>

      {/* Right Panel Toggle Button */}
      <div
        className="absolute top-4 z-10"
        style={{
          right: isRightPanelCollapsed ? '8px' : `${rightPanelWidth + 8}px`,
        }}
      >
        <button
          onClick={() => setIsRightPanelCollapsed(!isRightPanelCollapsed)}
          className="p-2 bg-white border border-gray-300 rounded hover:bg-gray-100 shadow-sm transition-colors"
          title={isRightPanelCollapsed ? 'Show chat panel' : 'Hide chat panel'}
        >
          {isRightPanelCollapsed ? (
            <PanelRightOpen className="w-4 h-4" />
          ) : (
            <PanelRightClose className="w-4 h-4" />
          )}
        </button>
      </div>

      {/* Right Sidebar - Chat Panel */}
      {!isRightPanelCollapsed && (
        <Resizable
          size={{ width: rightPanelWidth, height: '100%' }}
          onResize={(e, direction, ref, d) => {
            setRightPanelWidth(rightPanelWidth + d.width);
          }}
          minWidth={150}
          maxWidth={800}
          enable={{ left: true }}
          handleStyles={{
            left: { left: 0, width: '4px', cursor: 'ew-resize' },
          }}
          className="bg-gray-50 border-l border-gray-300 flex-shrink-0"
        >
          <ChatPanel
            fileId={fileId}
            pdfExcerpts={PdfExcerpts}
            onRemoveExcerpt={handleDeleteExcerpt}
          />
        </Resizable>
      )}
    </div>
  );
}
