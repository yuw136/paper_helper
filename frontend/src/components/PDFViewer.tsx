import { useState } from 'react';
import * as React from 'react';
import { ZoomIn, ZoomOut, ChevronLeft, ChevronRight } from 'lucide-react';
import { FileNode } from '../App';

interface PDFViewerProps {
  file: FileNode | null;
}

export function PDFViewer({ file }: PDFViewerProps) {
  const [currentPage, setCurrentPage] = useState(1);
  const [zoom, setZoom] = useState(100);
  const totalPages = 34; // Mock total pages

  const handleZoomIn = () => {
    setZoom(prev => Math.min(prev + 10, 200));
  };

  const handleZoomOut = () => {
    setZoom(prev => Math.max(prev - 10, 50));
  };

  const handlePrevPage = () => {
    setCurrentPage(prev => Math.max(prev - 1, 1));
  };

  const handleNextPage = () => {
    setCurrentPage(prev => Math.min(prev + 1, totalPages));
  };

  if (!file) {
    return (
      <div className="h-full flex items-center justify-center text-gray-500 bg-white">
        <div className="text-center">
          <p className="text-lg">No PDF file selected</p>
          <p className="text-sm mt-2">Double-click a PDF file from the directory to view</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-white">
      {/* Header with file path */}
      <div className="bg-gray-100 border-b border-gray-300 px-4 py-2 flex items-center justify-between">
        <div className="flex items-center gap-2 flex-1 min-w-0">
          <span className="text-xs text-gray-600 truncate">{file.path}</span>
        </div>
      </div>

      {/* PDF Controls */}
      <div className="bg-gray-50 border-b border-gray-300 px-4 py-2 flex items-center gap-4">
        <div className="flex items-center gap-2">
          <button
            onClick={handlePrevPage}
            disabled={currentPage === 1}
            className="p-1 hover:bg-gray-200 rounded disabled:opacity-50 disabled:cursor-not-allowed text-gray-700"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <span className="text-sm">
            <input
              type="number"
              value={currentPage}
              onChange={(e) => {
                const page = parseInt(e.target.value);
                if (page >= 1 && page <= totalPages) {
                  setCurrentPage(page);
                }
              }}
              className="w-12 bg-white border border-gray-300 rounded px-2 py-1 text-center text-gray-800"
              min={1}
              max={totalPages}
            />
            <span className="ml-2 text-gray-600">of {totalPages}</span>
          </span>
          <button
            onClick={handleNextPage}
            disabled={currentPage === totalPages}
            className="p-1 hover:bg-gray-200 rounded disabled:opacity-50 disabled:cursor-not-allowed text-gray-700"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleZoomOut}
            className="p-1 hover:bg-gray-200 rounded text-gray-700"
          >
            <ZoomOut className="w-4 h-4" />
          </button>
          <select
            value={zoom}
            onChange={(e) => setZoom(parseInt(e.target.value))}
            className="bg-white border border-gray-300 rounded px-2 py-1 text-sm text-gray-800"
          >
            <option value={50}>50%</option>
            <option value={75}>75%</option>
            <option value={100}>100%</option>
            <option value={125}>125%</option>
            <option value={150}>150%</option>
            <option value={200}>200%</option>
          </select>
          <button
            onClick={handleZoomIn}
            className="p-1 hover:bg-gray-200 rounded text-gray-700"
          >
            <ZoomIn className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* PDF Content Area */}
      <div className="flex-1 overflow-auto bg-gray-100 p-8">
        <div className="max-w-4xl mx-auto bg-white shadow-2xl" style={{ transform: `scale(${zoom / 100})`, transformOrigin: 'top center' }}>
          <div className="p-12">
            <h1 className="text-4xl font-serif text-center mb-8">
              Extensions of Schoen–Simon–Yau and Schoen–Simon theorems via iteration à la De Giorgi
            </h1>
            <p className="text-center text-xl mb-12">Costante Bellettini</p>
            
            <h2 className="text-2xl font-semibold mb-4">Abstract</h2>
            <p className="text-gray-800 leading-relaxed mb-4">
              We give an alternative proof of the Schoen-Simon-Yau curvature estimates and associated Bernstein-type theorems (1975), 
              and extend the original result by including the case of 6-dimensional (stable minimal) immersions. The key step is an 
              epsilon-regularity theorem, that assumes smoothness of the scale-invariant energy on a ball of radius 1, to deduce, on a ball 
              of radius 1/2, smallness of the second fundamental form.
            </p>
            <p className="text-gray-800 leading-relaxed mb-4">
              Further, we obtain a graph description, in the Lipschitz multi-valued sense, for any stable minimal immersion of dimension 
              less than or equal to 6, on a set of locally finite measure, and that is weakly close to a hyperplane. (In fact, if the 
              measure is finite and singular on at most a singular set of dimension less than or equal to n - 8, then it is in fact a graph.)
            </p>
            <p className="text-gray-800 leading-relaxed">
              This follows from an epsilon-regularity theorem that assumes control of the scale-invariant energy, in a suitably weak sense, 
              to conclude that the conclusion is strengthened to a union of smooth graphs.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}