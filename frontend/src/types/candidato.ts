export interface CandidatoLogado {
  email: string;
  telefone: string; 
  nomeCurso: string;
}

export interface CandidatoAdicionalData {
  nomeSocial?: string;
  estadoCivil?: string;
  racaCandidato?: string;
  orientacaoSexual?: string;
  identidadeGenero?: string;
  possuiDeficiencia?: string;
  numeroCid?: string;
}