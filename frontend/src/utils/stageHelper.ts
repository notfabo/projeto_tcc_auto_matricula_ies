import { DocumentoUsuarioResponse } from '../services/documento'; 
import { Stage } from '../types/documento';

export const determineStageFromDocuments = (documents: DocumentoUsuarioResponse[]): Stage => {
  if (!documents || documents.length === 0) {
    return 'upload';
  }

  const isFullyApproved =
    documents.some(doc => doc.tipo === '1' && doc.status === 'sucesso') && // <--- Ajustado para 'sucesso'
    documents.some(doc => doc.tipo === '3' && doc.status === 'sucesso');   // <--- Ajustado para 'sucesso'

  if (isFullyApproved) {
    return 'approved';
  }

  const hasSubmittedDocuments = documents.some(doc => 
    doc.status === 'revisao' || doc.status === 'sucesso' || doc.status === 'reprovado'
  );

  if (hasSubmittedDocuments) {
    return 'review';
  }
  
  return 'upload';
};