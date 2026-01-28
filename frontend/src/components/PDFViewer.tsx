import React, { useEffect, useRef, useState } from 'react';
import { useParams } from 'react-router';
import * as pdfjs from 'pdfjs-dist';
import {
  PdfLoader,
  PdfHighlighter,
} from 'react-pdf-highlighter-plus';
import type {
  PdfHighlighterUtils,
  PdfSelection,
} from 'react-pdf-highlighter-plus';

import { getFileById } from '../apis/Api';
import { SelectionTip } from './SelectionTip';

// import css styles - if one of them is not imported/working, need to add corresponnding css
// manually
import 'react-pdf-highlighter-plus/style/style.css';
import 'pdfjs-dist/web/pdf_viewer.css';

// set worker thread - required for pdf.js to work
pdfjs.GlobalWorkerOptions.workerSrc = `https://unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;

interface PDFViewerProps {
  onSelectExcerpt: (selection: PdfSelection) => void;
}

// // add inline style component to fix css issues (if 'pdfjs-dist/web/pdf_viewer.css' not working)
// const TextLayerFixStyles = () => (
//   <style>{`
//     /* fix annotationLayer blocking text selection and highlighting */
//     .annotationLayer {
//       pointer-events: none !important;
//     }
    
//     /* keep PDF internal link clicking functionality */
//     .annotationLayer .linkAnnotation,
//     .annotationLayer .buttonWidgetAnnotation {
//       pointer-events: auto !important;
//     }
    
//     /* fix text layer transparency and alignment issues */
//     .textLayer {
//       position: absolute !important;
//       left: 0 !important;
//       top: 0 !important;
//       right: 0 !important;
//       bottom: 0 !important;
//       overflow: hidden !important;
//       line-height: 1 !important;
//       text-size-adjust: none !important;
//       forced-color-adjust: none !important;
//       transform-origin: 0 0 !important;
//       z-index: 2 !important;
//     }
    
//     .textLayer span,
//     .textLayer br {
//       color: transparent !important; 
//       position: absolute !important;
//       white-space: pre !important;
//       cursor: text !important;
//       transform-origin: 0% 0% !important;
//     }
    
//     .textLayer ::selection {
//       background: rgba(0, 0, 255, 0.3) !important;
//     }
    
//     /* ensure canvas and textLayer are aligned in the same container */
//     .page {
//       position: relative !important;
//     }
    
//     /* PDF.js viewer container style */
//     .pdfViewer .page {
//       margin: 0 auto;
//     }
    
//     /* ensure selection tip box is in the correct z-index */
//     .PdfHighlighter__tip-container {
//       z-index: 10 !important;
//     }
//   `}</style>
// );

export function PDFViewer({ onSelectExcerpt }: PDFViewerProps) {
  const { fileId } = useParams();
  const highlighterUtilsRef = useRef<PdfHighlighterUtils | null>(null);
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [highlights, setHighlights] = useState([]);

  useEffect(() => {
    if (!fileId) return;
    async function getPdfUrl() {
      try {
        const res = await getFileById(fileId);
        setPdfUrl(res.path);
        console.log('PDF URL:', res.path);
      } catch (error) {
        console.error('Error getting PDF URL:', error);
      }
    }
    getPdfUrl();
  }, [fileId]);

  if (!fileId) {
    return (
      <div className="h-full flex items-center justify-center text-gray-500 bg-white">
        <div className="text-center">
          <p className="text-lg">No PDF file selected</p>
          <p className="text-sm mt-2">
            Click a PDF file from the directory to view
          </p>
        </div>
      </div>
    );
  }

  if (!pdfUrl) {
    return (
      <div className="h-full flex items-center justify-center text-gray-500 bg-white">
        <div>Loading PDF...</div>
      </div>
    );
  }

  return (
    <div className="h-full w-full bg-white relative overflow-hidden">
      {/* inject fix styles */}
      {/* <TextLayerFixStyles /> */}
      
      {/* outer relative as positioning context, inner absolute to satisfy PDF.js requirements */}
      <div className="absolute inset-0 overflow-auto">
        <PdfLoader
          document={pdfUrl}
          beforeLoad={() => (
            <div
              style={{
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                height: '100%',
              }}
            >
              <div>Loading PDF...</div>
            </div>
          )}
        >
          {(pdfDocument) => (
            <PdfHighlighter
              highlights={highlights}
              pdfDocument={pdfDocument}
              utilsRef={(_pdfHighlighterUtils) => {
                highlighterUtilsRef.current = _pdfHighlighterUtils;
              }}
              selectionTip={
                <SelectionTip onConfirm={onSelectExcerpt}></SelectionTip>
              }
            >
              <div></div>
            </PdfHighlighter>
          )}
        </PdfLoader>
      </div>
    </div>
  );
}