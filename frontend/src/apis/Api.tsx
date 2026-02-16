import { ChatHistory, ChatMessage, PdfExcerpt, StreamEvent } from '../types';

// API Base URL - empty for development (uses Vite proxy), set for production
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

export const getPapers = async () => {
  const response = await fetch(`${API_BASE_URL}/api/papers`);
  if (!response.ok) {
    throw new Error('Failed to fetch papers: ' + response.statusText);
  }
  console.log('fetch papers response: ' + response);

  return await response.json();
};

export const getFiles = async () => {
  const response = await fetch(`${API_BASE_URL}/api/files`);
  if (!response.ok) {
    throw new Error('Failed to fetch all files: ' + response.statusText);
  }
  console.log('fetch files response: ' + response);

  return await response.json();
};

export const getFileById = async (fileId: string) => {
  const response = await fetch(`${API_BASE_URL}/api/${fileId}`);
  if (!response.ok) {
    throw new Error('Failed to fetch file: ' + response.statusText);
  }
  console.log('fetch file response: ' + response);

  return await response.json();
};

/**
 * Get the actual PDF URL for loading.
 * - Local mode: returns the API endpoint URL (backend streams the file)
 * - Supabase mode: returns a signed URL from Supabase Storage
 */
export const getPdfUrl = async (fileId: string): Promise<string> => {
  const response = await fetch(`${API_BASE_URL}/api/pdf-url/${fileId}`);

  if (!response.ok) {
    throw new Error('Failed to get PDF URL: ' + response.statusText);
  }

  const data = await response.json();

  if (data.type === 'url') {
    // Supabase mode: use the signed URL directly
    console.log('Using Supabase signed URL');
    return data.url;
  } else if (data.type === 'api') {
    // Local mode: use the API endpoint URL
    console.log('Using local API URL');
    return `${API_BASE_URL}${data.url}`;
  }

  throw new Error('Invalid response format from server');
};

export const uploadFile = async (file: File) => {
  const response = await fetch(`${API_BASE_URL}/api/upload`, {
    method: 'POST',
    body: file,
  });
  console.log(response);
};

export const getChatHistories = async (
  fileId: string
): Promise<ChatHistory[]> => {
  const response = await fetch(`${API_BASE_URL}/api/chat_histories/${fileId}`);
  if (!response.ok) {
    throw new Error('Failed to fetch chat histories: ' + response.statusText);
  }
  console.log('fetch chat histories response: ' + response);
  return await response.json();
};

export const createChatHistory = async (history: ChatHistory) => {
  const response = await fetch(`${API_BASE_URL}/api/create_chat_history`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session: history }),
  });
  if (!response.ok) {
    throw new Error('Failed to create chat history: ' + response.statusText);
  }
  console.log('create chat history response: ' + response);
  return await response.json();
};

export const getMessages = async (
  historyId: string
): Promise<ChatMessage[]> => {
  const response = await fetch(`${API_BASE_URL}/api/messages/${historyId}`);
  if (!response.ok) {
    throw new Error('Failed to fetch messages: ' + response.statusText);
  }
  console.log('fetch messages response: ' + response);
  return await response.json();
};

/**
 * Sends a message and returns an async generator that yields stream events.
 * This allows the caller to process events as they arrive in real-time.
 */
export async function* sendMessageStream(data: {
  threadId: string;
  messageId: string;
  fileId: string;
  content: string;
  excerpts?: PdfExcerpt[];
  timestamp: number;
}): AsyncGenerator<StreamEvent, void, unknown> {
  // Convert camelCase to snake_case to match backend's ChatRequest model
  const requestBody = {
    thread_id: data.threadId,
    message_id: data.messageId,
    file_id: data.fileId,
    content: data.content,
    excerpts:
      data.excerpts
        ?.filter((e) => typeof e.content === 'string' && e.content.trim().length > 0)
        .map((e) => ({
          id: e.id,
          content: e.content,
          pageNumber: e.pageNumber ?? undefined,
          boundingRect: e.boundingRect ?? undefined,
          timestamp: e.timestamp ?? undefined
        })) || [],
    timestamp: data.timestamp,
  };

  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(requestBody),
  });

  if (!response.ok) {
    throw new Error(`Failed to send message: ${response.statusText}`);
  }

  if (!response.body) {
    throw new Error('Response body is null - streaming not supported');
  }

  //reader, decoder, buffer for the response stream
  const reader = response.body.getReader();
  const decoder = new TextDecoder('utf-8');
  let buffer = '';

  try {
    while (true) {
      const { done, value } = await reader.read();

      if (done) {
        break;
      }

      // Decode the chunk and add to buffer
      buffer += decoder.decode(value, { stream: true });

      // SSE format: each event is "data: {...}\n\n"
      // Split by double newline to get complete events
      const events = buffer.split('\n\n');

      buffer = events.pop() || '';

      for (const eventStr of events) {
        if (!eventStr.trim()) continue;

        // Remove "data: " prefix if present
        const dataMatch = eventStr.match(/^data:\s*(.+)$/s);
        if (dataMatch) {
          try {
            const parsed: StreamEvent = JSON.parse(dataMatch[1]);
            yield parsed;
          } catch (e) {
            console.warn('Failed to parse SSE event:', eventStr, e);
          }
        }
      }
    }

    // Process any remaining data in buffer
    if (buffer.trim()) {
      const dataMatch = buffer.match(/^data:\s*(.+)$/s);
      if (dataMatch) {
        try {
          const parsed: StreamEvent = JSON.parse(dataMatch[1]);
          yield parsed;
        } catch (e) {
          console.warn('Failed to parse final SSE event:', buffer, e);
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
}
