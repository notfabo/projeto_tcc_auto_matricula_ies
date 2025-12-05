import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import toast from 'react-hot-toast';
import { aprovarMatricula, obterMatriculaDetalhes, reprovarMatricula } from '../services/revisao';
import type { MatriculaDetalhesDTO } from '../types/revisao';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { DocumentCard } from '../components/revisao/DocumentCard';

export default function RevisaoDetalhes() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [detalhes, setDetalhes] = useState<MatriculaDetalhesDTO | null>(null);
  const [loading, setLoading] = useState(true);
  const [erro, setErro] = useState<string | null>(null);
  const [observacoes, setObservacoes] = useState('');
  const numId = Number(id);

  async function carregar() {
    try {
      setLoading(true);
      setErro(null);
      const data = await obterMatriculaDetalhes(numId);
      setDetalhes(data);
    } catch (e: any) {
      setErro(e?.message ?? 'Falha ao carregar');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (!Number.isFinite(numId)) {
      setErro('ID inválido');
      setLoading(false);
      return;
    }
    carregar();
  }, [id]);

  async function handleAprovar() {
    try {
      await aprovarMatricula(numId, { observacoes });
      toast.success('Matrícula aprovada com sucesso');
      navigate('/admin/usuarios/revisao');
    } catch (e: any) {
      toast.error(e?.message ?? 'Falha ao aprovar');
    }
  }

  async function handleReprovar() {
    try {
      if (!observacoes.trim()) {
        toast.error('Informe observações para justificar a reprovação');
        return;
      }
      await reprovarMatricula(numId, { observacoes });
      toast.success('Matrícula reprovada');
      navigate('/admin/usuarios/revisao');
    } catch (e: any) {
      toast.error(e?.message ?? 'Falha ao reprovar');
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="sticky top-0 z-10 border-b bg-white/80 backdrop-blur">
        <div className="mx-auto max-w-6xl px-4 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold text-gray-900">Revisão de Matrículas</h1>
            <p className="text-sm text-gray-600">Detalhes da matrícula</p>
          </div>
          <button className="rounded border border-gray-300 bg-white px-3 py-1.5 text-sm" onClick={() => navigate('/admin/usuarios/revisao')}>Voltar</button>
        </div>
      </header>

      <main className="mx-auto max-w-6xl p-4">
        {loading && <LoadingSpinner label="Carregando detalhes..." />}
        {erro && (
          <div className="rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700">{erro}</div>
        )}

        {!loading && !erro && detalhes && (
          <div className="space-y-6">
            <section className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
              <h2 className="text-lg font-medium text-gray-900">Dados do candidato</h2>
              <div className="mt-4 grid gap-3 sm:grid-cols-2">
                <Info label="Nome" value={detalhes.candidato.nome} />
                <Info label="CPF" value={detalhes.candidato.cpf} />
                <Info label="E-mail" value={detalhes.candidato.email} />
                <Info label="Telefone" value={detalhes.candidato.telefone} />
                <Info label="Nascimento" value={new Date(detalhes.candidato.dataNascimento).toLocaleDateString()} />
              </div>
            </section>

            {detalhes.motivoPreMatricula && (
              <section className="rounded-lg border border-blue-200 bg-blue-50 p-4 shadow-sm">
                <h2 className="text-lg font-medium text-gray-900 mb-2">Análise da Pré-Matrícula</h2>
                <div className="mt-2">
                  <div className="text-xs uppercase text-gray-600 mb-1">Status da Pré-Matrícula</div>
                  <div className="text-sm font-medium text-gray-900 mb-3">
                    {detalhes.statusPreMatricula === 'aprovado' ? (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        Aprovado
                      </span>
                    ) : (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                        Pendente
                      </span>
                    )}
                  </div>
                  <div className="text-xs uppercase text-gray-600 mb-1">Motivo / Observações da IA</div>
                  <div className="text-sm text-gray-800 whitespace-pre-wrap bg-white rounded p-3 border border-blue-200">
                    {detalhes.motivoPreMatricula}
                  </div>
                </div>
              </section>
            )}

            <section className="space-y-4">
              <h3 className="text-lg font-medium text-gray-900">Documentos</h3>
              
              {/* Documentos Pendentes - Destacados no topo */}
              {detalhes.documentos.filter(d => d.status === 'pendente').length > 0 && (
                <div className="space-y-2">
                  <h4 className="text-sm font-medium text-gray-700 flex items-center gap-2">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                      Pendentes
                    </span>
                    <span className="text-gray-500">
                      ({detalhes.documentos.filter(d => d.status === 'pendente').length})
                    </span>
                  </h4>
                  <div className="grid gap-3 sm:grid-cols-2">
                    {detalhes.documentos
                      .filter(d => d.status === 'pendente')
                      .map((d) => (
                        <DocumentCard key={d.id} doc={d} />
                      ))}
                  </div>
                </div>
              )}

              {/* Documentos Aprovados */}
              {detalhes.documentos.filter(d => d.status === 'aprovado').length > 0 && (
                <div className="space-y-2">
                  <h4 className="text-sm font-medium text-gray-700 flex items-center gap-2">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      Aprovados
                    </span>
                    <span className="text-gray-500">
                      ({detalhes.documentos.filter(d => d.status === 'aprovado').length})
                    </span>
                  </h4>
                  <div className="grid gap-3 sm:grid-cols-2">
                    {detalhes.documentos
                      .filter(d => d.status === 'aprovado')
                      .map((d) => (
                        <DocumentCard key={d.id} doc={d} />
                      ))}
                  </div>
                </div>
              )}

              {/* Documentos Reprovados */}
              {detalhes.documentos.filter(d => d.status === 'reprovado').length > 0 && (
                <div className="space-y-2">
                  <h4 className="text-sm font-medium text-gray-700 flex items-center gap-2">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                      Reprovados
                    </span>
                    <span className="text-gray-500">
                      ({detalhes.documentos.filter(d => d.status === 'reprovado').length})
                    </span>
                  </h4>
                  <div className="grid gap-3 sm:grid-cols-2">
                    {detalhes.documentos
                      .filter(d => d.status === 'reprovado')
                      .map((d) => (
                        <DocumentCard key={d.id} doc={d} />
                      ))}
                  </div>
                </div>
              )}

              {/* Documentos em Revisão */}
              {detalhes.documentos.filter(d => d.status === 'revisao').length > 0 && (
                <div className="space-y-2">
                  <h4 className="text-sm font-medium text-gray-700 flex items-center gap-2">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      Em Revisão
                    </span>
                    <span className="text-gray-500">
                      ({detalhes.documentos.filter(d => d.status === 'revisao').length})
                    </span>
                  </h4>
                  <div className="grid gap-3 sm:grid-cols-2">
                    {detalhes.documentos
                      .filter(d => d.status === 'revisao')
                      .map((d) => (
                        <DocumentCard key={d.id} doc={d} />
                      ))}
                  </div>
                </div>
              )}
            </section>

            <section className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
              <h3 className="text-lg font-medium text-gray-900">Observações do administrador</h3>
              <textarea
                className="mt-3 w-full rounded border border-gray-300 p-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
                rows={4}
                placeholder="Escreva observações (usado para aprovar ou reprovar)"
                value={observacoes}
                onChange={(e) => setObservacoes(e.target.value)}
              />

              <div className="mt-4 flex flex-wrap gap-3">
                <button
                  className="rounded bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700"
                  onClick={handleAprovar}
                >Aprovar Matrícula</button>

                <div className="flex-1" />
                <button
                  className="rounded bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700"
                  onClick={handleReprovar}
                >Reprovar Matrícula</button>
              </div>
            </section>
          </div>
        )}
      </main>
    </div>
  );
}

function Info({ label, value }: { label: string; value: string | number }) {
  return (
    <div>
      <div className="text-xs uppercase text-gray-500">{label}</div>
      <div className="text-sm text-gray-900">{String(value)}</div>
    </div>
  );
}


