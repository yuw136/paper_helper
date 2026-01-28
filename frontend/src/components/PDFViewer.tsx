import React, { useEffect, useRef, useState } from 'react';
import { useParams } from 'react-router';
import * as pdfjs from 'pdfjs-dist';
import { PdfLoader, PdfHighlighter } from 'react-pdf-highlighter-plus';
import type {
  PdfHighlighterUtils,
  PdfSelection,
} from 'react-pdf-highlighter-plus';

import { getPdfUrl } from '../apis/Api';
import { SelectionTip } from './SelectionTip';

// import css styles - if one of them is not imported/working, need to add corresponnding css file manually
import 'react-pdf-highlighter-plus/style/style.css';
import 'pdfjs-dist/web/pdf_viewer.css';

// set worker thread - required for pdf.js to work
pdfjs.GlobalWorkerOptions.workerSrc = `https://unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;

interface PDFViewerProps {
  onSelectExcerpt: (selection: PdfSelection) => void;
}

export function PDFViewer({ onSelectExcerpt }: PDFViewerProps) {
  const { fileId } = useParams();
  const highlighterUtilsRef = useRef<PdfHighlighterUtils | null>(null);
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [highlights, setHighlights] = useState([]);

  useEffect(() => {
    if (!fileId) return;
    async function loadPdfUrl() {
      try {
        const url = await getPdfUrl(fileId);
        setPdfUrl(url);
        console.log('PDF URL:', url);
      } catch (error) {
        console.error('Error getting PDF URL:', error);
      }
    }
    loadPdfUrl();
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
