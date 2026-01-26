import { X } from 'lucide-react';
import { PdfExcerpt } from '../types';

interface ExcerptTagProps {
  excerpt: PdfExcerpt;
  onRemove: (excerpt: PdfExcerpt) => void;
}

export const ExcerptTag = ({ excerpt, onRemove }: ExcerptTagProps) => {
  return (
    <div className="inline-flex items-center gap-2 bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-xs">
      <span className="max-w-[150px] truncate">
        {excerpt.content.slice(0, 20)}...
      </span>
      <button
        onClick={() => onRemove(excerpt)}
        className="hover:bg-blue-200 rounded-full p-0.5 transition-colors"
        title="Remove"
      >
        <X className="w-3 h-3" />
      </button>
    </div>
  );
};
