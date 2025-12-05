import React, { useCallback, useRef, useEffect } from 'react';
import { Upload, FileText, Check, X, FileClock, FileX2, FileCheck2, AlertCircle } from 'lucide-react';
import { UiDocumentStatus } from '../../../types/documento';
import { Tooltip, TooltipProvider, TooltipContent, TooltipTrigger } from '@radix-ui/react-tooltip';

export type FileStatus = 'idle' | 'selected' | 'error';

interface FileUploadCardProps {
  documentName: string;
  documentId: number;

  onFileSelect: (docId: number, file: File | undefined) => void;
  onUpload: (docId: number) => void;
  onRemove: (docId: number) => void;

  selectedFile?: File;
  currentStatus: UiDocumentStatus;
  disabled?: boolean;
  motivoErro?: string | null;
  infoMessage?: string | null;
}

const FileUploadCard: React.FC<FileUploadCardProps> = ({
  documentName,
  documentId,
  onFileSelect,
  onUpload,
  onRemove,
  selectedFile,
  currentStatus,
  disabled = false,
  motivoErro,
  infoMessage,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  // não considerar 'reprovado' como uploaded para permitir reenvio
  const isUploaded = currentStatus === 'aprovado' || currentStatus === 'revisao' || currentStatus === 'enviado';
  // quando reprovado, permitir reenvio (não disabled) mas mostrar botão Reenviar
  const showReenviarButton = isUploaded || currentStatus === 'reprovado';
  const isDisabled = disabled || isUploaded;

  const handleFileChange = useCallback((file: File | null) => {
    onFileSelect(documentId, file || undefined);
  }, [documentId, onFileSelect]);

  const handleSelectClick = useCallback(() => {
    if (isDisabled) return;
    fileInputRef.current?.click();
  }, [isDisabled]);

  const handleUploadClick = useCallback(() => {
    onUpload(documentId);
  }, [documentId, onUpload]);

  const handleRemoveClick = useCallback(() => {
    if (fileInputRef.current) fileInputRef.current.value = '';
    onRemove(documentId);
    setTimeout(() => {
      fileInputRef.current?.click();
    }, 50);
  }, [documentId, onRemove]);

  const renderStatusIcon = () => {
    if (currentStatus === 'aprovado') {
      return (
        <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center">
          <FileCheck2 className="w-5 h-5 text-green-600" />
        </div>
      );
    }
    if (currentStatus === 'reprovado') {
      return (
        <div className="w-8 h-8 rounded-full bg-red-100 flex items-center justify-center">
          <FileX2 className="w-5 h-5 text-red-600" />
        </div>
      );
    }
    if (currentStatus === 'revisao') {
      return (
        <div className="w-8 h-8 rounded-full bg-yellow-100 flex items-center justify-center">
          <FileClock className="w-5 h-5 text-yellow-600" />
        </div>
      );
    }
    return (
      <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center">
        <FileText className="w-5 h-5 text-gray-600" />
      </div>
    );
  };

  const getMotivoErroMessage = (erroJson: string) => {
    try {
      const parsed = JSON.parse(erroJson);
      return parsed.mensagem;
    } catch (e) {
      return erroJson;
    }
  };

  return (
    <TooltipProvider>
    <div className="w-full bg-white rounded-xl shadow-sm border-gray-200">
      <div className="p-4 flex items-center justify-between">
        <div className="flex items-center space-x-4 flex-1 min-w-0">
          {renderStatusIcon()}
          <div className="flex-1 min-w-0">
            <Tooltip>
              <TooltipTrigger asChild>
                <h2 className="text-lg font-medium text-gray-900 break-words" style={{ maxHeight: '3.6em', overflow: 'hidden', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical' }}>{documentName}</h2>
              </TooltipTrigger>
              <TooltipContent sideOffset={5} className="bg-gray-900 text-white text-sm p-2 rounded-lg shadow-lg max-w-md z-50">
                <p className="break-words">{documentName}</p>
              </TooltipContent>
            </Tooltip>
            {selectedFile && !isUploaded && (
              <p className="text-sm text-gray-500 mt-1 break-words">{selectedFile.name}</p>
            )}
            <div className="flex items-center space-x-2 mt-1">
              <p className={`text-sm ${currentStatus === 'aprovado' ? 'text-green-600' :
                currentStatus === 'revisao' ? 'text-yellow-600' :
                  currentStatus === 'reprovado' ? 'text-red-600' :
                    'text-gray-600'
                }`}>
                {currentStatus === 'aprovado' ? 'Aprovado' :
                  currentStatus === 'revisao' ? 'Em revisão' :
                    currentStatus === 'reprovado' ? 'Rejeitado' :
                      'Pendente'}
              </p>
              {currentStatus === 'reprovado' && motivoErro && (
                <Tooltip>
                  <TooltipTrigger asChild>
                    <AlertCircle className="w-4 h-4 text-red-600 cursor-pointer mt-1/2" />
                  </TooltipTrigger>
                  <TooltipContent sideOffset={5} className="bg-white text-red-600 text-sm p-2 rounded-lg shadow-lg max-w-xs border border-red-600">
                    <p>Motivo de ser rejeitado:</p>
                    <p className="mt-1">{getMotivoErroMessage(motivoErro)}</p>
                  </TooltipContent>
                </Tooltip>
              )}
            </div>
          </div>
        </div>

         <div className="flex items-center space-x-2">
          {showReenviarButton && !selectedFile ? (
            <button
              onClick={handleRemoveClick}
              className="flex items-center space-x-1 px-3 py-1.5 rounded-lg text-sm font-medium text-red-600 hover:bg-red-50 cursor-pointer"
              title="Reenviar documento"
            >
              <X size={16} />
              <span>Reenviar</span>
            </button>
          ) : selectedFile ? (
            <>
              <button onClick={handleSelectClick} className="px-3 py-1.5 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-100">Alterar</button>
              <button onClick={handleUploadClick} className="px-4 py-1.5 rounded-lg text-sm font-medium text-white bg-blue-600 hover:bg-blue-700">Enviar</button>
            </>
          ) : (
            <button
              onClick={handleSelectClick}
              className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white cursor-pointer"
              disabled={isDisabled}
            >
              <Upload size={18} />
              <span>Selecionar Arquivo</span>
            </button>
          )}
        </div>
      </div>
      <input
        type="file"
        ref={fileInputRef}
        onChange={(e) => handleFileChange(e.target.files?.[0] || null)}
        className="hidden"
        accept=".pdf,.png,.jpeg,.jpg"
      />
      {infoMessage && (
        <div className="px-4 pb-4">
          <div className="mt-2 ml-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-sm text-blue-800">
              <strong>Importante:</strong> {infoMessage}
            </p>
          </div>
        </div>
      )}
    </div>
    </TooltipProvider>
  );
};

export default FileUploadCard;