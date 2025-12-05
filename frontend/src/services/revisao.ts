import api from "./api";
import type {
  MatriculaResumoDTO,
  MatriculaDetalhesDTO,
  AprovarRequest,
  ReprovarRequest,
} from "../types/revisao";

export async function listarMatriculasPendentes(params?: {
  status?: "pendente" | "aprovado";
  page?: number;
  size?: number;
}): Promise<{
  itens: MatriculaResumoDTO[];
  total: number;
  page: number;
  size: number;
}> {
  const { status, page = 1, size = 10 } = params || {};
  const query = new URLSearchParams();
  if (status) query.set("status", status);
  query.set("page", String(page));
  query.set("size", String(size));
  const url = query.toString()
    ? `/api/admin/matriculas/revisao?${query.toString()}`
    : "/api/admin/matriculas/revisao";
  const { data } = await api.get(url);
  if (Array.isArray(data)) {
    const itens = (data as any[]).map((it) => ({
      id: it.id ?? it.idMatricula,
      nomeCandidato: it.nomeCandidato ?? it.nome ?? it.candidatoNome,
      cpf: it.cpfCandidato,
      dataInscricao: it.dataInscricao ?? it.criadoEm ?? it.data,
      status: it.statusMatricula,
      statusPreMatricula: it.statusPreMatricula ?? 'pendente',
      motivoPreMatricula: it.motivoPreMatricula,
    })) as MatriculaResumoDTO[];
    return { itens, total: itens.length, page, size };
  }
  const payload = data as {
    itens: any[];
    total: number;
    page: number;
    size: number;
  };
  const itens = (payload.itens || []).map((it: any) => ({
    id: it.id ?? it.idMatricula,
    nomeCandidato: it.nomeCandidato ?? it.nome ?? it.candidatoNome,
    cpf: it.cpfCandidato,
    dataInscricao: it.dataInscricao ?? it.criadoEm ?? it.data,
    status: it.statusMatricula,
    statusPreMatricula: it.statusPreMatricula ?? 'pendente',
    motivoPreMatricula: it.motivoPreMatricula,
  })) as MatriculaResumoDTO[];
  return {
    itens,
    total: payload.total,
    page: payload.page,
    size: payload.size,
  };
}

export async function obterMatriculaDetalhes(
  id: number
): Promise<MatriculaDetalhesDTO> {
  const { data } = await api.get(`/api/admin/matriculas/${id}`);
  return {
    id: data.idMatricula ?? data.id,
    status: data.statusMatricula,
    statusPreMatricula: data.statusPreMatricula ?? 'pendente',
    motivoPreMatricula: data.motivoPreMatricula,
    candidato: data.candidato,
    documentos: (data.documentos ?? []).map((doc: any) => ({
      ...doc,
      caminhoArquivo: doc.caminhoArquivo,
    })),
    dataInscricao: data.dataInscricao,
  } as MatriculaDetalhesDTO;
}

export async function aprovarMatricula(
  id: number,
  body: AprovarRequest
): Promise<void> {
  await api.post(`/api/admin/matriculas/${id}/aprovar`, body);
}

export async function reprovarMatricula(
  id: number,
  body: ReprovarRequest
): Promise<void> {
  await api.post(`/api/admin/matriculas/${id}/reprovar`, body);
}
