import api from './api';

interface UploadDocumentoResponse {
  id: string;
  nome: string;
  tipo: string;
  docType?: string;
  status: string;
  url: string;
  dataUpload: string;
  tamanho: number;
  extensao: string;
}

export const uploadDocumento = async (
  file: File,
  tipoDocumento: string,
  token: string,
  subtipo?: string
): Promise<UploadDocumentoResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('tipoDocumento', tipoDocumento);
  if (subtipo) {
    formData.append('subtipo', subtipo);
  }

  const response = await api.post('/api/documentos/upload', formData, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

export const reuploadDocumento = async (
  file: File,
  documentoId: number,
  token: string,
  subtipo?: string
): Promise<UploadDocumentoResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('documentoId', String(documentoId));
  if (subtipo) {
    formData.append('subtipo', subtipo);
  }

  const response = await api.post('/api/documentos/reupload', formData, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

export interface TipoDocumento {
  id: number;
  nome: string;
  obrigatorio: boolean;
}

export const getTiposDocumento = async (): Promise<TipoDocumento[]> => {
  const response = await api.get('/api/documentos/tipos');
  return response.data;
};

export interface DocumentoUsuarioResponse {
  id: number;
  tipo: string;
  status: 'sucesso' | 'reprovado' | 'revisao';
  dadosExtraidos: string | null;
  motivoErro: string | null;
  dataUpload: string;
}

export const getMeusDocumentos = async (): Promise<DocumentoUsuarioResponse[]> => {
  const response = await api.get('/api/documentos/me');
  return response.data;
};