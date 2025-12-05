export interface MatriculaResumoDTO {
  id: number;
  nomeCandidato: string;
  cpf: string;
  dataInscricao: string; 
  status?: 'pendente' | 'aprovado';
  statusPreMatricula: 'pendente' | 'aprovado';
  motivoPreMatricula?: string;
}

export interface DocumentoRevisaoDTO {
  id: number;
  tipo: string;
  status: 'aprovado' | 'reprovado' | 'revisao' | 'pendente';
  dadosExtraidos?: string | null;
  motivoErro?: string | null;
  caminhoArquivo?: string | null;
}

export interface MatriculaDetalhesDTO {
  id: number;
  candidato: {
    nome: string;
    cpf: string;
    email: string;
    telefone: string;
    dataNascimento: string;
  };
  documentos: DocumentoRevisaoDTO[];
  status?: 'pendente' | 'aprovado';
  statusPreMatricula: 'pendente' | 'aprovado';
  motivoPreMatricula?: string;
  dataInscricao: string;
}

export interface AprovarRequest {
  observacoes: string;
}

export interface ReprovarRequest {
  observacoes: string;
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

