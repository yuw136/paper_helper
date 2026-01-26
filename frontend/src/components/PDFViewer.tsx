import React, { useEffect, useRef, useState } from 'react';
import { useParams } from 'react-router';
import { ZoomIn, ZoomOut, ChevronLeft, ChevronRight } from 'lucide-react';
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

// import css style
import 'react-pdf-highlighter-plus/dist/style.css';

//set worker thread
pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;

interface PDFViewerProps {
  //used to pass to chatbox
  onSelectExcerpt: (selection: PdfSelection) => void;
}

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

  return (
    <div className="h-full flex flex-col bg-white">
      <PdfLoader
        document={pdfUrl}
        beforeLoad={() => (
          <div
            style={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              height: '100vh',
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
  );
}
