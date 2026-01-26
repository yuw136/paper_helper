import {
  PdfSelection,
  usePdfHighlighterContext,
} from 'react-pdf-highlighter-plus';

interface SelectionTipProps {
  // callback to send highlighted text
  onConfirm: (selection: PdfSelection) => void;
}

export const SelectionTip = ({ onConfirm }: SelectionTipProps) => {
  const { getCurrentSelection } = usePdfHighlighterContext();

  const handleClick = () => {
    const selection = getCurrentSelection();

    if (selection?.content?.text) {
      onConfirm(selection);
    } else {
      console.warn('no text selected');
    }
  };

  return (
    <div className="bg-gray-800 text-white p-2 rounded shadow-lg flex gap-2 items-center text-xs z-50">
      <button className="hover:text-gray-600 font-bold" onClick={handleClick}>
        chat in chatbox
      </button>
      {/* can add more buttons for other actions*/}
    </div>
  );
};
