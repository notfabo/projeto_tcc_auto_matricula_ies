import React from 'react';
import { Document } from '../../types/documento'; 

interface UploadProgressBarProps {
  pendingUploads: Set<number>;
  documents: Document[];
}

export const UploadProgressBar: React.FC<UploadProgressBarProps> = ({
  pendingUploads,
  documents,
}) => {
  if (pendingUploads.size === 0) {
    return null;
  }

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 p-4 shadow-lg animate-fade-in-up">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex flex-col sm:flex-row sm:items-center sm:space-x-4">
          <span className="font-medium text-gray-800">
            {pendingUploads.size} {pendingUploads.size === 1 ? 'documento pronto' : 'documentos prontos'} para envio
          </span>
        </div>
      </div>
    </div>
  );
};