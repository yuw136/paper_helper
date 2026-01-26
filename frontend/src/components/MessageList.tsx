// MessageList.tsx
import { ChatMessage } from '../types';

interface MessageListProps {
  messages: ChatMessage[];
}

export const MessageList = ({ messages }: MessageListProps) => {
  return (
    <div className="space-y-4">
      {messages.map((message) => (
        <MessageBubble key={message.id} message={message} />
      ))}
    </div>
  );
};

export const MessageBubble = ({ message }: { message: ChatMessage }) => {
  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[80%] rounded-lg p-3 ${
          isUser ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-800'
        }`}
      >
        {/* timestamp */}
        <div className={`text-xs mt-1 opacity-70`}>
          {new Date(message.timestamp).toLocaleTimeString()}
        </div>

        {/* message content */}
        <div className="text-sm whitespace-pre-wrap">{message.content}</div>

        {/* show excerpts*/}
        {message.excerpts && message.excerpts.length > 0 && (
          <div className="mb-2 pb-2 border-b border-opacity-20 border-white">
            {message.excerpts.map((excerpt) => (
              <div key={excerpt.id} className="text-xs opacity-80 mb-1">
                "{excerpt.content.slice(0, 50)}..."
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
