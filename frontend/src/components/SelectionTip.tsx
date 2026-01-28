import {
  PdfSelection,
  usePdfHighlighterContext,
} from 'react-pdf-highlighter-plus';

interface SelectionTipProps {
  // callback to send highlighted text
  onConfirm: (selection: PdfSelection) => void;
}

export const SelectionTip = ({ onConfirm }: SelectionTipProps) => {
  const { getCurrentSelection, setTip } = usePdfHighlighterContext();

  const handleClick = () => {
    const selection = getCurrentSelection();

    if (selection?.content?.text) {
      onConfirm(selection);
      // Hide the selection tip
      setTip(null);
    } else {
      console.warn('no text selected');
    }
  };

  return (
    <div 
      className="text-white p-2 rounded shadow-lg flex gap-2 items-center text-xs z-50"
      style={{ backgroundColor: 'var(--color-gray-600)' }}
    >
      <button 
        className="font-bold px-2 py-1 rounded transition-colors"
        style={{ 
          backgroundColor: 'transparent'
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.backgroundColor = 'var(--color-gray-300)';
          e.currentTarget.style.color = 'var(--color-gray-800)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.backgroundColor = 'transparent';
          e.currentTarget.style.color = 'inherit';
        }}
        onClick={handleClick}
      >
        chat in chatbox
      </button>
      {/* can add more buttons for other actions*/}
    </div>
  );
};
