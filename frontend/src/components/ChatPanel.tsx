import { useState, useRef, useEffect } from 'react';
import * as React from 'react';
import { Send, History, ArrowLeft, Clock, MessageSquare } from 'lucide-react';
import { ChatHistory, ChatMessage } from '../App';

interface ChatPanelProps {
  chatHistory: ChatHistory | null;
  allChatHistories: ChatHistory[];
  onSendMessage: (content: string) => void;
  onSelectChatHistory: (historyId: string) => void;
}

export function ChatPanel({
  chatHistory,
  allChatHistories,
  onSendMessage,
  onSelectChatHistory,
}: ChatPanelProps) {
  const [inputValue, setInputValue] = useState('');
  const [showHistoryView, setShowHistoryView] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatHistory?.messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputValue.trim() && chatHistory) {
      onSendMessage(inputValue);
      setInputValue('');
    }
  };

  const formatTime = (date: Date) => {
    return new Date(date).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatDate = (date: Date) => {
    return new Date(date).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const handleHistorySelect = (historyId: string) => {
    onSelectChatHistory(historyId);
    setShowHistoryView(false);
  };

  // History View
  if (showHistoryView) {
    return (
      <div className="h-full flex flex-col bg-gray-50">
        {/* Header */}
        <div className="bg-gray-100 border-b border-gray-300 px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowHistoryView(false)}
              className="p-1 hover:bg-gray-200 rounded transition-colors text-gray-700"
              title="Back to chat"
            >
              <ArrowLeft className="w-4 h-4" />
            </button>
            <h2 className="text-sm font-semibold text-gray-800">Chat History</h2>
          </div>
        </div>

        {/* History List */}
        <div className="flex-1 overflow-y-auto">
          {allChatHistories.length === 0 ? (
            <div className="h-full flex items-center justify-center text-gray-500 text-center px-4">
              <div>
                <History className="w-12 h-12 mx-auto mb-3 text-gray-400" />
                <p className="text-sm">No chat history yet</p>
                <p className="text-xs mt-2 text-gray-600">
                  Start a conversation with a PDF to see it here
                </p>
              </div>
            </div>
          ) : (
            <div className="p-2">
              {allChatHistories
                .sort((a, b) => new Date(b.lastUpdated).getTime() - new Date(a.lastUpdated).getTime())
                .map((history) => (
                  <button
                    key={history.id}
                    onClick={() => handleHistorySelect(history.id)}
                    className={`w-full text-left p-4 mb-2 rounded-lg border hover:border-blue-400 hover:bg-blue-50 transition-all ${
                      chatHistory?.id === history.id
                        ? 'bg-blue-50 border-blue-400'
                        : 'bg-white border-gray-300'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-800 truncate">
                          {history.fileName}
                        </p>
                      </div>
                      {chatHistory?.id === history.id && (
                        <span className="text-xs bg-blue-500 text-white px-2 py-0.5 rounded-full">
                          Active
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-3 text-xs text-gray-500">
                      <div className="flex items-center gap-1">
                        <MessageSquare className="w-3 h-3" />
                        <span>{history.messages.length} messages</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        <span>{formatDate(history.lastUpdated)}</span>
                      </div>
                    </div>
                    {history.messages.length > 0 && (
                      <p className="text-xs text-gray-600 mt-2 truncate">
                        Last: {history.messages[history.messages.length - 1].content.substring(0, 60)}
                        {history.messages[history.messages.length - 1].content.length > 60 ? '...' : ''}
                      </p>
                    )}
                  </button>
                ))}
            </div>
          )}
        </div>
      </div>
    );
  }

  // Chat View
  return (
    <div className="h-full flex flex-col bg-gray-50">
      {/* Header */}
      <div className="bg-gray-100 border-b border-gray-300 px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-2 flex-1 min-w-0">
          <h2 className="text-sm font-semibold text-gray-800 truncate">
            {chatHistory ? chatHistory.fileName : 'AI Chatbox'}
          </h2>
        </div>
        <button
          onClick={() => setShowHistoryView(true)}
          className="p-1.5 hover:bg-gray-200 rounded transition-colors text-gray-700 flex-shrink-0"
          title="View chat history"
        >
          <History className="w-4 h-4" />
        </button>
      </div>

      {/* Chat Messages Area */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
        {!chatHistory ? (
          <div className="h-full flex items-center justify-center text-gray-500 text-center px-4">
            <div>
              <p className="text-sm">Select a PDF to start chatting</p>
              <p className="text-xs mt-2 text-gray-600">
                The AI will help you understand and analyze the document
              </p>
            </div>
          </div>
        ) : chatHistory.messages.length === 0 ? (
          <div className="h-full flex items-center justify-center text-gray-500 text-center px-4">
            <div>
              <p className="text-sm">No messages yet</p>
              <p className="text-xs mt-2 text-gray-600">
                Ask a question about the PDF to get started
              </p>
            </div>
          </div>
        ) : (
          <>
            {chatHistory.messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${
                  message.role === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                <div
                  className={`max-w-[85%] rounded-lg px-4 py-2 ${
                    message.role === 'user'
                      ? 'bg-blue-500 text-white'
                      : 'bg-white text-gray-800 border border-gray-300'
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                  <p
                    className={`text-xs mt-1 ${
                      message.role === 'user' ? 'text-blue-100' : 'text-gray-500'
                    }`}
                  >
                    {formatTime(message.timestamp)}
                  </p>
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-300 p-4 bg-white">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder={
              chatHistory
                ? 'Ask a question about the PDF...'
                : 'Select a PDF first...'
            }
            disabled={!chatHistory}
            className="flex-1 bg-white border border-gray-300 rounded px-3 py-2 text-sm text-gray-800 focus:outline-none focus:border-blue-500 disabled:opacity-50 disabled:cursor-not-allowed disabled:bg-gray-100"
          />
          <button
            type="submit"
            disabled={!chatHistory || !inputValue.trim()}
            className="bg-blue-500 hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed px-4 py-2 rounded transition-colors text-white"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
        <p className="text-xs text-gray-500 mt-2">
          This is a demo. Messages will be answered with simulated AI responses.
        </p>
      </div>
    </div>
  );
}
