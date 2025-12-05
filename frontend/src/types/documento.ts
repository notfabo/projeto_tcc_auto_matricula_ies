export type Stage = 'upload' | 'review' | 'approved';

export type ApiDocumentStatus = 'sucesso' | 'reprovado' | 'revisao' | 'pendente';

export type UiDocumentStatus = ApiDocumentStatus | 'enviado' | 'aprovado';

export interface Document {
  id: number;
  tipo: string;
  nome: string;
  status: UiDocumentStatus
  required: boolean;
  file?: File;
  type?: 'identity' | string;
  docType?: 'CIN' | 'RG' | string;
  dadosExtraidos?: string | null;
  motivoErro?: string | null;
  dataUpload: string | null;
} 

export interface DocumentoUsuario {
  id: number;
  tipo: string;
  status: 'sucesso' | 'erro' | 'revisando';
  dadosExtraidos: string | null;
  motivoErro: string | null;
  dataUpload: string;
}

export const DOCUMENT_TYPES: { [key: string]: string } = {
  '1': 'RG ou CIN',
  '2': 'Declaração ou Certificado de Conclusão de Ensino Médio',
  '3': 'Histórico Escolar',
  '4': 'Comprovante de Residência',
  '5': 'Documento do Responsável',
  '6': 'Certificado de Reservista',
  '7': 'Certidão de Nascimento ou Casamento',
  '8': 'Boletim do ENEM',
};


export const getDocumentName = (typeId: string): string => {
  return DOCUMENT_TYPES[typeId] || 'Documento Desconhecido';
};