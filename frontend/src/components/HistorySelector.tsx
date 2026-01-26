import { ChatHistory } from '../types';
import { MessageSquare, Clock, History } from 'lucide-react';

interface HistorySelectorProps {
  histories: ChatHistory[];
  selectedId: string | null;
  onSelect: (historyId: string) => void;
}

export const HistorySelector = ({
  histories,
  selectedId,
  onSelect,
}: HistorySelectorProps) => {
  return (
    <div className="flex-1 overflow-y-auto">
      {/* if no histories, show a message */}
      {histories.length === 0 ? (
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
          {/* sort histories by updatedAt (most recent first) */}
          {histories
            .sort((a, b) => b.updatedAt - a.updatedAt)
            .map((history) => (
              <button
                key={history.id}
                onClick={() => onSelect(history.id)}
                className={`w-full text-left p-4 mb-2 rounded-lg border hover:border-blue-400 hover:bg-blue-50 transition-all ${selectedId === history.id
                  ? 'bg-gray-100 border-gray-300'
                  : 'bg-white border-gray-300'
                  }`}
              >
                <div className="flex items-start justify-between gap-2 mb-2">
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-800 truncate">
                      {history.title}
                    </p>
                  </div>

                  {/* show active chat */}
                  {selectedId === history.id && (
                    <span className="text-xs bg-blue-500 text-white px-2 py-0.5 rounded-full">
                      Active
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-3 text-xs text-gray-500">
                  <div className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    <span>
                      {new Date(history.updatedAt).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              </button>
            ))}
        </div>
      )}
    </div>
  );
};
