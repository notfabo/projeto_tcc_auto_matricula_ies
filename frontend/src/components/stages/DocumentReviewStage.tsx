import React, { useEffect } from 'react';
import { CheckCircle2, RefreshCcw } from 'lucide-react';
import { Document } from '../../types/documento';
import { DataSheet } from '../forms/DataSheet';
import { useExtractedData } from '../../hooks/useExtractedData';
import { toast } from 'react-hot-toast/headless';
import { updateCandidatoAdicional } from '../../services/candidato';

interface DocumentReviewStageProps {
  documents: Document[];
  onReupload: (docId: number) => void;
  token: string | null;
}

export const DocumentReviewStage: React.FC<DocumentReviewStageProps> = ({
  documents,
  onReupload,
}) => {
  const token = localStorage.getItem('token');
  const { extractedData, handleFieldChange } = useExtractedData(documents, token);
  const approvedDocuments = documents.filter(doc => doc.status === 'sucesso' || doc.status === 'aprovado');
  const reviewingDocuments = documents.filter(doc => doc.status === 'revisao');
  const errorDocuments = documents.filter(doc => doc.status === 'reprovado');

  const handleSaveAdicional = async (additionalInfo: any) => {
    if (!token) {
      toast.error('Token não encontrado. Faça login novamente.');
      return;
    }

    try {
      await updateCandidatoAdicional(token, {
        nomeSocial: additionalInfo['Nome social'] || '',
        estadoCivil: additionalInfo['Estado civil'] || '',
        racaCandidato: additionalInfo['Você se identifica com qual raça e/ou cor?'] || '',
        orientacaoSexual: additionalInfo['Qual sua orientação sexual?'] || '',
        identidadeGenero: additionalInfo['Qual sua identidade de gênero?'] || '',
        possuiDeficiencia: additionalInfo['Você possui alguma deficiência?'] || '',
        numeroCid: additionalInfo['Informe o Número do CID apresentado no seu laudo médico'] || '',
      });
      toast.success('Informações adicionais salvas com sucesso!');
    } catch (error: any) {
      console.error('Erro ao salvar informações adicionais:', error);
      toast.error('Erro ao salvar informações adicionais.');
    }
  };

  return (
    <div className="space-y-8">
      <DataSheet
        data={extractedData}
        onFieldChange={handleFieldChange}
        onSaveChanges={handleSaveAdicional}
      />

      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Status dos Documentos</h2>
        <div className="space-y-4">

          {approvedDocuments.map(doc => (
            <div key={doc.id} className="flex items-center justify-between p-4 bg-green-50 rounded-lg border border-green-200">
              <span className="font-medium text-green-800">{doc.nome}</span>
              <div className="flex items-center space-x-2">
                <span className="text-sm text-green-700">Documento Aprovado</span>
                <CheckCircle2 className="h-6 w-6 text-green-500" />
              </div>
            </div>
          ))}

          {reviewingDocuments.map(doc => (
            <div key={doc.id} className="flex items-center justify-between p-4 bg-yellow-50 rounded-lg border border-yellow-200">
              <span className="font-medium text-yellow-800">{doc.nome}</span>
              <div className="flex items-center space-x-2">
                <span className="text-sm text-yellow-700">Em revisão...</span>
                <RefreshCcw className="h-5 w-5 text-yellow-500 animate-spin" />
              </div>
            </div>
          ))}

          {errorDocuments.map(doc => (
            <div key={doc.id} className="flex items-center justify-between p-4 bg-red-50 rounded-lg border border-red-200">
              <div>
                <span className="font-medium text-red-800">{doc.nome}</span>
                {doc.motivoErro && <p className="text-sm text-red-600">{doc.motivoErro}</p>}
              </div>
              <button
                onClick={() => onReupload(doc.id)}
                className="px-4 py-2 text-sm font-semibold text-white bg-red-600 rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 cursor-pointer"
              >
                Reenviar
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};