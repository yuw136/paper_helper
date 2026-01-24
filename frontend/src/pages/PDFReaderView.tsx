import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router';
import { Resizable } from 're-resizable';
import { PanelLeftClose, PanelLeftOpen, PanelRightClose, PanelRightOpen, ArrowLeft } from 'lucide-react';
import { FileDirectory, mockFileSystem } from '../components/FileDirectory';
import { PDFViewer } from '../components/PDFViewer';
import { ChatPanel } from '../components/ChatPanel';
import { FileNode, ChatHistory, ChatMessage } from '../App';

export function PDFReaderView() {
  const { fileId } = useParams<{ fileId: string }>();
  const navigate = useNavigate();
  
  const [selectedFile, setSelectedFile] = useState<FileNode | null>(null);
  const [currentChatHistory, setCurrentChatHistory] = useState<ChatHistory | null>(null);
  const [allChatHistories, setAllChatHistories] = useState<ChatHistory[]>([]);
  const [isLeftPanelCollapsed, setIsLeftPanelCollapsed] = useState(false);
  const [isRightPanelCollapsed, setIsRightPanelCollapsed] = useState(false);
  const [leftPanelWidth, setLeftPanelWidth] = useState(280);
  const [rightPanelWidth, setRightPanelWidth] = useState(384);

  // Helper function to find file by ID
  const findFileById = (id: string, nodes: FileNode[] = mockFileSystem): FileNode | null => {
    for (const node of nodes) {
      if (node.id === id) {
        return node;
      }
      if (node.children) {
        const found = findFileById(id, node.children);
        if (found) return found;
      }
    }
    return null;
  };

  // Load file based on URL parameter
  useEffect(() => {
    if (fileId) {
      const file = findFileById(fileId);
      if (file && file.type === 'file') {
        setSelectedFile(file);
        
        // Find or create chat history for this file
        const existingHistory = allChatHistories.find(h => h.fileId === file.id);
        if (existingHistory) {
          setCurrentChatHistory(existingHistory);
        } else {
          // Create new chat history for this file
          const newHistory: ChatHistory = {
            id: `chat-${file.id}`,
            fileId: file.id,
            fileName: file.name,
            messages: [],
            lastUpdated: new Date(),
          };
          setAllChatHistories([...allChatHistories, newHistory]);
          setCurrentChatHistory(newHistory);
        }
      }
    }
  }, [fileId]);

  const handleFileSelect = (file: FileNode) => {
    if (file.type === 'file') {
      navigate(`/pdf/${file.id}`);
    }
  };

  const handleSendMessage = (content: string) => {
    if (!currentChatHistory) return;

    const newMessage: ChatMessage = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content,
      timestamp: new Date(),
    };

    const updatedHistory = {
      ...currentChatHistory,
      messages: [...currentChatHistory.messages, newMessage],
      lastUpdated: new Date(),
    };

    // Simulate AI response
    const aiResponse: ChatMessage = {
      id: `msg-${Date.now() + 1}`,
      role: 'assistant',
      content: 'This is a simulated AI response. In a real application, this would connect to an AI API to analyze the PDF content.',
      timestamp: new Date(),
    };

    const finalHistory = {
      ...updatedHistory,
      messages: [...updatedHistory.messages, aiResponse],
    };

    setCurrentChatHistory(finalHistory);
    setAllChatHistories(
      allChatHistories.map(h => h.id === finalHistory.id ? finalHistory : h)
    );
  };

  const handleSelectChatHistory = (historyId: string) => {
    const history = allChatHistories.find(h => h.id === historyId);
    if (history) {
      setCurrentChatHistory(history);
      // Navigate to the corresponding file
      navigate(`/pdf/${history.fileId}`);
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
              <h2 className="text-sm font-semibold text-gray-700">PAPER_HELPER</h2>
              <button
                onClick={() => navigate('/')}
                className="p-1.5 hover:bg-gray-200 rounded transition-colors text-gray-600"
                title="Back to home"
              >
                <ArrowLeft className="w-4 h-4" />
              </button>
            </div>
            <div className="flex-1 overflow-hidden">
              <FileDirectory onFileSelect={handleFileSelect} selectedFile={selectedFile} />
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

      {/* Center Panel - PDF Viewer */}
      <div className="flex-1 bg-white overflow-hidden">
        <PDFViewer file={selectedFile} />
      </div>

      {/* Right Panel Toggle Button */}
      <div
        className="absolute top-4 z-10"
        style={{ right: isRightPanelCollapsed ? '8px' : `${rightPanelWidth + 8}px` }}
      >
        <button
          onClick={() => setIsRightPanelCollapsed(!isRightPanelCollapsed)}
          className="p-2 bg-white border border-gray-300 rounded hover:bg-gray-100 shadow-sm transition-colors"
          title={isRightPanelCollapsed ? 'Show chat panel' : 'Hide chat panel'}
        >
          {isRightPanelCollapsed ? <PanelRightOpen className="w-4 h-4" /> : <PanelRightClose className="w-4 h-4" />}
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
            left: { left: 0, width: '4px', cursor: 'ew-resize' }
          }}
          className="bg-gray-50 border-l border-gray-300 flex-shrink-0"
        >
          <ChatPanel
            chatHistory={currentChatHistory}
            allChatHistories={allChatHistories}
            onSendMessage={handleSendMessage}
            onSelectChatHistory={handleSelectChatHistory}
          />
        </Resizable>
      )}
    </div>
  );
}
