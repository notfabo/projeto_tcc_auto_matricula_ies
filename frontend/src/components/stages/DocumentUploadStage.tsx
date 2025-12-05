import React, {} from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { Document } from '../../types/documento'; 
import FileUploadCard from '../ui/FileUploadCard';
import { UploadProgressBar } from './UploadProgressBar';

interface DocumentUploadStageProps {
  documents: Document[];
  isLoading: boolean;
  selectedFiles: { [docId: number]: File | undefined };
  pendingUploads: Set<number>; 
  onFileSelect: (docId: number, file: File | undefined) => void;
  onFileUpload: (docId: number) => void; 
  onRemove: (docId: number) => void;
}

export const DocumentUploadStage: React.FC<DocumentUploadStageProps> = ({
  documents,
  isLoading,
  selectedFiles,
  pendingUploads,
  onFileSelect,
  onFileUpload,
  onRemove,
}) => {
  const [showOptionalDocs, setShowOptionalDocs] = React.useState(false);

  if (isLoading) {
    return (
      <div className="text-center p-10">
        <p className="text-gray-600">Carregando seus documentos...</p>
      </div>
    );
  }

  const requiredDocuments = documents.filter(doc => doc.required);
  const optionalDocuments = documents.filter(doc => !doc.required);

  const isIdentityDocument = (docName: string) => {
    return docName.toLowerCase().includes('identidade') || docName.toLowerCase().includes('rg');
  };

  // Função para obter a mensagem informativa específica de cada documento opcional
  const getOptionalDocumentInfo = (docName: string): string | null => {
    const nameLower = docName.toLowerCase();
    
    if (nameLower.includes('declaração') && nameLower.includes('conclusão') && nameLower.includes('ensino médio')) {
      return 'Obrigatório para candidatos que não possuem certificado no histórico escolar';
    }
    
    if (nameLower.includes('responsável') || (nameLower.includes('documento') && nameLower.includes('responsável'))) {
      return 'Obrigatório caso comprovante de residência estiver no nome de responsável';
    }
    
    if (nameLower.includes('reservista') || nameLower.includes('certificado de reservista')) {
      return 'Obrigatório para homens';
    }
    
    if (nameLower.includes('enem') || nameLower.includes('boletim')) {
      return 'Obrigatório para candidatos que entram pelo Sisu ou pela nota do Enem';
    }
    
    return null;
  };

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Documentos Necessários</h2>
        <div className="space-y-4">
          {requiredDocuments.map(doc => (
            <div key={doc.id}>
              <FileUploadCard
                documentId={doc.id}
                documentName={doc.nome}
                onUpload={() => onFileUpload(doc.id)}
                onRemove={() => onRemove(doc.id)}
                onFileSelect={(docId, file) => onFileSelect(docId, file)}
                selectedFile={selectedFiles[doc.id]}
                currentStatus={doc.status}
                motivoErro={doc.motivoErro}
              />
              {isIdentityDocument(doc.nome) && (
                <div className="mt-2 ml-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <p className="text-sm text-blue-800">
                    <strong>Importante:</strong> Apenas é aceito documento de identidade RG com frente e verso no mesmo arquivo (Preferência na horizontal).
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {optionalDocuments.length > 0 && (
         <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
            <button
                onClick={() => setShowOptionalDocs(!showOptionalDocs)}
                className="w-full px-6 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
            >
                <div className="flex items-center space-x-3">
                    <h2 className="text-2xl font-bold text-gray-900">Documentos Opcionais</h2>
                    <span className="px-2 py-1 text-sm font-medium text-gray-600 bg-gray-100 rounded-full">
                        {optionalDocuments.length}
                    </span>
                </div>
                {showOptionalDocs ? (
                    <ChevronUp className="h-6 w-6 text-gray-500" />
                ) : (
                    <ChevronDown className="h-6 w-6 text-gray-500" />
                )}
            </button>

            {showOptionalDocs && (
                <div className="p-6 border-t border-gray-200">
                    <p className="text-gray-600 mb-6">
                        Estes documentos não são obrigatórios, mas podem ser solicitados futuramente.
                    </p>
                    <div className="space-y-4">
                        {optionalDocuments.map(doc => (
                            <FileUploadCard
                                key={doc.id}
                                documentId={doc.id}
                                documentName={doc.nome}
                                onUpload={() => onFileUpload(doc.id)}
                                onRemove={() => onRemove(doc.id)}
                                onFileSelect={(docId, file) => onFileSelect(docId, file)}
                                selectedFile={selectedFiles[doc.id]}
                                currentStatus={doc.status}
                                motivoErro={doc.motivoErro}
                                infoMessage={getOptionalDocumentInfo(doc.nome)}
                            />
                        ))}
                    </div>
                </div>
            )}
        </div>
      )}
      
      <UploadProgressBar
        pendingUploads={pendingUploads}
        documents={documents}
      />
    </div>
  );
};