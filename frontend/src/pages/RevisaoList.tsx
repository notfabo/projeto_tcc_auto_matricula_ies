import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { listarMatriculasPendentes } from '../services/revisao';
import type { MatriculaResumoDTO } from '../types/revisao';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';

type FiltroStatus = 'pendente' | 'aprovado' | 'TODOS';

export default function RevisaoList() {
  const navigate = useNavigate();
  const [itens, setItens] = useState<MatriculaResumoDTO[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [erro, setErro] = useState<string | null>(null);
  const [status, setStatus] = useState<FiltroStatus>('pendente');
  const [page, setPage] = useState(1);
  const [size, setSize] = useState(10);

  async function carregar() {
    try {
      setLoading(true);
      setErro(null);
      const filtro = status === 'TODOS' ? undefined : status;
      const { itens, total, page: pg, size: sz } = await listarMatriculasPendentes({ status: filtro as any, page, size });
      setItens(itens);
      setTotal(total);
      setPage(pg);
      setSize(sz);
    } catch (e: any) {
      setErro(e?.message ?? 'Falha ao carregar');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    carregar();
  }, [status, page, size]);

  const numPaginas = useMemo(() => Math.max(1, Math.ceil(total / size)), [total, size]);

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="sticky top-0 z-10 border-b backdrop-blur">
        <div className="mx-auto max-w-6xl py-4">
          <h1 className="text-xl font-semibold text-gray-900">Revisão de Matrículas pré aprovadas pela IA</h1>
          <p className="text-sm text-gray-600">Pendentes: <span className="font-medium">{total}</span></p>
        </div>
      </header>

      <main className="mx-auto max-w-6xl p-4">
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
          <div className="inline-flex items-center gap-2">
            <label className="text-sm text-gray-600">Status</label>
            <select
              className="rounded border border-gray-300 bg-white px-3 py-2 text-sm"
              value={status}
              onChange={(e) => { setPage(1); setStatus(e.target.value as FiltroStatus); }}
            >
              <option value="TODOS">Todos</option>
              <option value="pendente">Pendentes</option>
              <option value="aprovado">Aprovadas</option>
            </select>
          </div>

          <div className="inline-flex items-center gap-2">
            <label className="text-sm text-gray-600">Por página</label>
            <select className="rounded border border-gray-300 bg-white px-2 py-1 text-sm" value={size} onChange={(e)=>{setPage(1); setSize(Number(e.target.value));}}>
              <option value={10}>10</option>
              <option value={20}>20</option>
              <option value={50}>50</option>
            </select>
          </div>
        </div>

        {loading && <LoadingSpinner label="Carregando matrículas..." />}
        {erro && (
          <div className="rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700">{erro}</div>
        )}

        {!loading && !erro && itens.length === 0 && (
          <div className="rounded border border-gray-200 bg-white p-6 text-center text-gray-600">Nenhuma matrícula encontrada.</div>
        )}

        {!loading && !erro && itens.length > 0 && (
          <div className="overflow-hidden rounded-lg border border-gray-200 bg-white shadow-sm">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Candidato</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">CPF</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Status Matrícula</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Status Pré-Matrícula</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Data inscrição</th>
                  <th className="px-4 py-3" />
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {itens.map((m) => (
                  <tr key={m.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm text-gray-900">{m.nomeCandidato}</td>
                    <td className="px-4 py-3 text-sm text-gray-700">{m.cpf}</td>
                    <td className="px-4 py-3 text-sm">
                      <span className={
                        `rounded px-2 py-1 text-xs ` +
                        (String(m.status).toLowerCase() === 'aprovado'
                          ? 'bg-green-50 text-green-700'
                          : 'bg-blue-50 text-blue-700')
                      }>{m.status}</span>
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <span className={
                        `rounded px-2 py-1 text-xs ` +
                        (String(m.statusPreMatricula).toLowerCase() === 'aprovado'
                          ? 'bg-green-50 text-green-700'
                          : m.statusPreMatricula === 'pendente'
                            ? 'bg-yellow-50 text-yellow-700'
                            : 'bg-red-50 text-red-700')
                      }>
                        {m.statusPreMatricula}
                        {m.motivoPreMatricula && (
                          <span className="ml-1 cursor-help" title={m.motivoPreMatricula}>ℹ️</span>
                        )}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-700">{new Date(m.dataInscricao).toLocaleDateString()}</td>
                    <td className="px-4 py-3 text-right">
                      <button
                        className="rounded bg-blue-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700"
                        onClick={() => navigate(`/admin/usuarios/revisao/${String(m.id)}`)}
                      >
                        Revisar
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <div className="mt-4 flex items-center justify-between">
          <div className="text-sm text-gray-600">Página {page} de {numPaginas}</div>
          <div className="inline-flex items-center gap-2">
            <button
              className="rounded border border-gray-300 bg-white px-3 py-1.5 text-sm disabled:opacity-50"
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page <= 1}
            >Anterior</button>
            <button
              className="rounded border border-gray-300 bg-white px-3 py-1.5 text-sm disabled:opacity-50"
              onClick={() => setPage((p) => Math.min(numPaginas, p + 1))}
              disabled={page >= numPaginas}
            >Próxima</button>
          </div>
        </div>
      </main>
    </div>
  );
}


