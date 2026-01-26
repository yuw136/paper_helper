import { useState, useRef, useEffect, useCallback } from 'react';
import { v4 as uuidv4 } from 'uuid';
import * as React from 'react';
import { Send, History, ArrowLeft, Clock, MessageSquare, Loader2 } from 'lucide-react';
import { ChatHistory, ChatMessage, PdfExcerpt, StreamEvent } from '../types';
import { HistorySelector } from './HistorySelector';
import { MessageList } from './MessageList';
import { ExcerptTag } from './ExcerptTag';
import { createChatHistory, getChatHistories, getMessages, sendMessageStream } from '../apis/Api';

interface ChatPanelProps {
  fileId: string;
  pdfExcerpts: PdfExcerpt[];
  onRemoveExcerpt: (excerpt: PdfExcerpt) => void;
}

export function ChatPanel({ fileId, pdfExcerpts, onRemoveExcerpt }: ChatPanelProps) {
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [chatHistories, setChatHistories] = useState<ChatHistory[]>([]);
  const [selectedChatHistoryId, setSelectedChatHistoryId] = useState<string | null>(null);
  const [inputMessage, setInputMessage] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isHistoryPanelOpen, setIsHistoryPanelOpen] = useState<boolean>(false);
  const [streamingContent, setStreamingContent] = useState<string>('');

  const abortControllerRef = useRef<AbortController | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const loadChatHistories = async () => {
      try {
        const histories = await getChatHistories(fileId);
        if (histories.length > 0) {
          setChatHistories(histories);
        } else {
          setChatHistories([]);
        }
      } catch (error) {
        console.error('Error loading chat histories:', error);
      }
    }
    loadChatHistories();
  }, [fileId]);

  const handleNewChat = async () => {
    if (!fileId) return;

    try {
      const threadId = uuidv4();
      const newHistory: ChatHistory = {
        id: threadId,
        fileId: fileId,
        title: 'New Chat',
        createdAt: Date.now(),
        updatedAt: Date.now(),
      }
      const newSession = await createChatHistory(newHistory);
      
      setSelectedChatHistoryId(threadId);
      setChatMessages([]);
      setChatHistories(chatHistories => [newHistory, ...chatHistories]);
      
      console.log('Created new chat session:', newSession.id);
    } catch (error) {
      console.error('Failed to create new chat:', error);
      alert('Failed to create new chat session');
    }
  };

  const handleSelectHistory = async (historyId: string) => {
    if (historyId === selectedChatHistoryId) return;
    setIsLoading(true);
    try {
      const messages = await getMessages(historyId);
      setChatMessages(messages);
      setSelectedChatHistoryId(historyId);
    } catch (error) {
      console.error('Failed to get messages:', error);
      alert('Failed to get messages');
    } finally {
      setIsHistoryPanelOpen(false);
      setIsLoading(false);
    }
  }


  const processStreamMessage = useCallback((event:StreamEvent)=> {
    const { node, output } = event;
    console.log(`[Stream] Node: ${node}`, output)
    switch (node) {
      case 'retrieve':
        return { answer: null, status: 'Searching documents...' };
      case 'web_search':
        return { answer: null, status: 'Searching the web...' };
      case 'grade_documents':
        return { answer: null, status: 'Evaluating relevance...' };
      case 'generate':
        return { answer: output.answer, status: 'Generating answer...' };
      case 'not_found':
        return { answer: 'I couldn\'t find any relevant information.', status: null };
      default:
        return { answer: null, status: null };
    }
  }, [])

  const handleSendMessage = async () => {
    if (!inputMessage.trim() && pdfExcerpts.length === 0) {
      return;
    }
    if (!fileId) return;

    let threadId = selectedChatHistoryId;

    // Auto-create a new chat history if none selected
    if (!threadId) {
      try {
        threadId = uuidv4();
        const newHistory: ChatHistory = {
          id: threadId,
          fileId: fileId,
          title: 'New Chat',
          createdAt: Date.now(),
          updatedAt: Date.now(),
        };
        await createChatHistory(newHistory);

        setSelectedChatHistoryId(threadId);
        setChatHistories(prev => [newHistory, ...prev]);
        console.log('Auto-created new chat session:', threadId);
      } catch (error) {
        console.error('Failed to auto-create chat:', error);
        alert('Failed to create chat session');
        return;
      }
    }

    const messageId = uuidv4();
    const timestamp = Date.now();
    const userMessage: ChatMessage = {
      id: messageId,
      role: 'user',
      content: inputMessage,
      excerpts: pdfExcerpts,
      timestamp: timestamp,
    }

    setChatMessages([...chatMessages, userMessage]);
    setInputMessage('');
    pdfExcerpts.forEach(excerpt => onRemoveExcerpt(excerpt));

    setIsLoading(true);
    setStreamingContent('');

    //just a placeholder
    let aiMessageId = uuidv4();

    try {
      abortControllerRef.current = new AbortController();
      let accumulatedAnswer = '';

      for await (const event of sendMessageStream({
        threadId: threadId,
        messageId: messageId,
        fileId: fileId,
        content: inputMessage,
        excerpts: pdfExcerpts,
        timestamp: timestamp})){
          const answerChunk = processStreamMessage(event);
          if (answerChunk){
            if (answerChunk.answer){
              accumulatedAnswer += answerChunk.answer;
              setStreamingContent(accumulatedAnswer);
            } else if (answerChunk.status) {
              setStreamingContent(answerChunk.status);
            }
          }
        }
      
      //stream finished, finalize ai message
      if  (accumulatedAnswer) {
        const aiMessage: ChatMessage = {
          id: aiMessageId,
          role: 'ai',
          content: accumulatedAnswer,
          timestamp: Date.now(),
        };
        setChatMessages(prev => [...prev, aiMessage]);
      }
    } catch (error) {
      console.error('Error during streaming:', error);
      // Add an error message to the message list
      const errorMessage: ChatMessage = {
        id: aiMessageId,
        role: 'ai',
        content: 'Sorry, an error occurred while processing your request.',
        timestamp: Date.now(),
      };
      setChatMessages(prev => [...prev, errorMessage]);

    } finally {
      setIsLoading(false);
      setStreamingContent('');
      abortControllerRef.current = null;
    }

  }

  //auto scroll to bottom when new message is added
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages])


  const renderChatInterface = () => (
    <div className="h-full flex flex-col bg-white">
      {/* Header */}
      <div className="p-4 bg-gray-800 text-white">
        <div className="flex items-center justify-between">
          <h2 className="font-bold">Chat</h2>
          <div className="flex gap-2">
            <button
              onClick={handleNewChat}
              className="text-xs hover:bg-gray-700 px-2 py-1 rounded"
            >
              + New Chat
            </button>
            <button
              onClick={() => setIsHistoryPanelOpen(true)}
              className="text-xs hover:bg-gray-700 px-2 py-1 rounded flex items-center gap-1"
            >
              <History className="w-4 h-4" />
              History
            </button>
          </div>
        </div>
      </div>

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto p-4">
        {chatMessages.length === 0 && !streamingContent ? (
          <div className="flex items-center justify-center h-full">
            <p className="text-gray-400 text-sm text-center">
              Type a message to start chatting
            </p>
          </div>
        ) : (
          <>
            <MessageList messages={chatMessages} />

            {/* Show streaming content as it arrives */}
            {streamingContent && (
              <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                <div className="text-sm text-gray-500 mb-1">AI</div>
                <div className="whitespace-pre-wrap">{streamingContent}</div>
                <span className="inline-block w-2 h-4 bg-blue-500 animate-pulse ml-1" />
              </div>
            )}

            {/* Loading indicator when waiting for first chunk */}
            {isLoading && !streamingContent && (
              <div className="mt-4 flex items-center gap-2 text-gray-500">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Thinking...</span>
              </div>
            )}

            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* PDF excerpts display */}
      {pdfExcerpts.length > 0 && (
        <div className="p-3 bg-blue-50 border-b flex flex-wrap gap-2">
          {pdfExcerpts.map(excerpt => (
            <ExcerptTag
              key={excerpt.id}
              excerpt={excerpt}
              onRemove={onRemoveExcerpt}
            />
          ))}
        </div>
      )}

      {/* Input area */}
      <div className="p-4 border-t">
        <div className="flex gap-2">
          <input
            type="text"
            value={inputMessage}
            onChange={e => setInputMessage(e.target.value)}
            onKeyDown={e => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSendMessage();
              }
            }}
            placeholder="Ask about the document..."
            className="flex-1 px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
          />
          <button
            onClick={handleSendMessage}
            disabled={isLoading || (!inputMessage.trim() && pdfExcerpts.length === 0)}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center gap-2"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );

  // Toggle between history panel and chat interface
  return isHistoryPanelOpen ? (
    <HistorySelector
      histories={chatHistories}
      selectedId={selectedChatHistoryId}
      onSelect={handleSelectHistory}
    />
  ) : (
    renderChatInterface()
  );
}