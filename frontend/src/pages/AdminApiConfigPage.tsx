import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Header } from '../components/layout/Header';
import api from '../services/api';
import { Modal } from '../components/ui/Modal';

const reportOptions = [
  {
    label: 'Exportar Candidatos Aprovados',
    endpoint: '/api/admin/export/aprovados-para-erp',
    filename: 'candidatos_aprovados',
    description: 'Exporta os dados consolidados apenas dos candidatos com matrícula aprovada.'
  },
  {
    label: 'Exportar Todos Candidatos',
    endpoint: '/api/admin/export/geral',
    filename: 'relatorio_geral_candidatos',
    description: 'Exporta os dados consolidados de TODOS os candidatos, incluindo o status da matrícula.'
  },
];

const exportTypes = [
  { label: 'CSV', value: 'csv', ext: 'csv' },
  { label: 'Excel', value: 'excel', ext: 'xlsx' },
  { label: 'JSON', value: 'json', ext: 'json' },
];

export const AdminApiConfigPage: React.FC<{ onLogout: () => void }> = ({ onLogout }) => {
  const navigate = useNavigate();
  const [selectedReportOption, setSelectedReportOption] = React.useState(reportOptions[0]);
  const [selectedExportType, setSelectedExportType] = React.useState(exportTypes[0].value);
  const [isExporting, setIsExporting] = React.useState(false);
  const [isZipProcessing, setIsZipProcessing] = React.useState(false);
  const [feedbackMessage, setFeedbackMessage] = React.useState('');

  const handleExport = async () => {
    setIsExporting(true);
    try {
      const token = localStorage.getItem('token');
      if (!token) throw new Error('Token não encontrado. Faça login novamente.');

      const res = await api.get(
        `${selectedReportOption.endpoint}?format=${selectedExportType}`,
        {
          responseType: 'blob',
        }
      );
      
      const blob = res.data;
      const exportTypeObj = exportTypes.find(t => t.value === selectedExportType);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${selectedReportOption.filename}.${exportTypeObj?.ext || 'csv'}`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      console.error(err);
      alert(err.response?.data?.message || err.message || 'Erro ao exportar dados');
    } finally {
      setIsExporting(false);
    }
  };

  const pollJobStatus = (jobId: string) => {
    const interval = setInterval(async () => {
      try {
        const res = await api.get(`/api/admin/export/status/${jobId}`);
        const { status, downloadUrl, message } = res.data;

        setFeedbackMessage(message || `Status: ${status}`);

        if (status === 'COMPLETED') {
          clearInterval(interval);
          setIsZipProcessing(false);
          setFeedbackMessage('Download pronto! Baixando automaticamente...');
          window.location.href = downloadUrl;
        } else if (status === 'FAILED') {
          clearInterval(interval);
          setIsZipProcessing(false);
          setFeedbackMessage(`Falha ao gerar o arquivo: ${message}`);
        }
      } catch (error) {
        clearInterval(interval);
        setIsZipProcessing(false);
        setFeedbackMessage('Erro ao verificar o status da exportação.');
        console.error('Erro no polling', error);
      }
    }, 5000);
  };

  const handleZipExportGeral = async () => {
    setIsZipProcessing(true);
    setFeedbackMessage('Solicitando geração do arquivo...');
    try {
      const res = await api.post('/api/admin/export/documentos-zip/geral');
      const { jobId } = res.data;

      if (jobId) {
        setFeedbackMessage('Processando... O arquivo está sendo gerado em segundo plano. Isso pode levar vários minutos.');
        pollJobStatus(jobId);
      } else {
        throw new Error('Não foi possível iniciar o job de exportação.');
      }
    } catch (err: any) {
      console.error(err);
      setFeedbackMessage('Ocorreu uma falha ao solicitar a exportação geral.');
      setIsZipProcessing(false);
    }
  };

  const [isConfirmOpen, setIsConfirmOpen] = React.useState(false);
  const confirmAndSendZip = async () => {
    setIsConfirmOpen(false);
    await handleZipExportGeral();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header onLogout={onLogout} admin />
      <div className="max-w-6xl mx-auto px-4 py-4">
        <button
          type="button"
          onClick={() => navigate('/admin')}
          className="inline-flex items-center gap-2 px-3 py-1.5 rounded border border-gray-300 bg-white text-sm cursor-pointer"
        >
          ← Voltar ao Painel
        </button>
      </div>
      <main className="flex flex-col md:flex-row items-start md:items-stretch justify-center p-6 gap-6 md:gap-10">
        <div className="w-full md:max-w-md bg-white rounded-lg shadow p-8 flex flex-col items-stretch space-y-4">
          <h2 className="text-2xl md:text-3xl font-bold">Exportação de Dados</h2>
          <p className="text-gray-600 text-sm md:text-base">
            {selectedReportOption.description}
          </p>

          <div className="w-full">
            <label id="report-type-label" className="block text-sm font-medium mb-1">Tipo de Relatório</label>
            <p id="report-type-desc" className="text-xs text-gray-500 mb-1">Escolha o relatório a exportar.</p>
            <select
              aria-labelledby="report-type-label"
              aria-describedby="report-type-desc"
              className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-black mb-2 cursor-pointer hover:border-black transition"
              value={selectedReportOption.endpoint}
              disabled={isExporting}
              onChange={e => {
                const opt = reportOptions.find(o => o.endpoint === e.target.value);
                if (opt) setSelectedReportOption(opt);
              }}
            >
              {reportOptions.map((opt) => (
                <option key={opt.endpoint} value={opt.endpoint}>{opt.label}</option>
              ))}
            </select>
          </div>

          <div className="w-full">
            <label id="format-label" className="block text-sm font-medium mb-1">Formato do Arquivo</label>
            <select
              aria-labelledby="format-label"
              className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-black mb-2 cursor-pointer hover:border-black transition"
              value={selectedExportType}
              onChange={e => setSelectedExportType(e.target.value)}
              disabled={isExporting}
            >
              {exportTypes.map((type) => (
                <option key={type.value} value={type.value}>{type.label}</option>
              ))}
            </select>
          </div>

          <button
            className="mt-2 px-6 py-2 rounded bg-black text-white font-medium flex items-center justify-center gap-3 transition hover:bg-gray-900 cursor-pointer focus:outline-none focus:ring-2 focus:ring-black disabled:bg-gray-400"
            onClick={handleExport}
            type="button"
            disabled={isExporting}
            aria-busy={isExporting}
          >
            {isExporting ? <span className="inline-flex items-center gap-2"><span className="h-4 w-4 animate-spin rounded-full border-2 border-gray-300 border-t-white"></span>Exportando...</span> : 'Exportar'}
          </button>
        </div>

        <div className="w-full md:max-w-md bg-white rounded-lg shadow p-8 flex flex-col items-stretch space-y-4">
            <h2 className="text-2xl md:text-3xl font-bold">Exportação Geral de Documentos</h2>
            <p className="text-gray-600 text-sm md:text-base">
              Gere um único arquivo .zip com todos os documentos de todos os candidatos, organizados por turma e por aluno. Este processo é executado em segundo plano.
            </p>
            
            <div className="w-full pt-2">
               <p className="text-gray-500 text-sm mb-3">Atenção: Esta operação pode ser muito demorada e consumir recursos significativos do servidor.</p>
          <button onClick={() => setIsConfirmOpen(true)} disabled={isZipProcessing} className="w-full px-4 py-2 rounded bg-black text-white font-medium transition hover:bg-gray-900 disabled:bg-gray-400 flex items-center justify-center gap-2" aria-disabled={isZipProcessing}>
            {isZipProcessing ? <span className="inline-flex items-center gap-2"><span className="h-4 w-4 animate-spin rounded-full border-2 border-gray-300 border-t-white"></span>Processando...</span> : 'Gerar ZIP de TODOS os Documentos'}
              </button>
            </div>

            {feedbackMessage && (
              <div className="mt-2 p-3 w-full text-center bg-green-100 text-green-800 rounded" role="status">
                {feedbackMessage}
              </div>
            )}
          </div>
  </main>

      <Modal isOpen={isConfirmOpen} onClose={() => setIsConfirmOpen(false)} title="Confirmar exportação">
        <p className="text-gray-700">Você tem certeza que deseja gerar o ZIP com todos os documentos? Esta operação pode levar muito tempo e consumir recursos do servidor.</p>
        <div className="mt-4 flex justify-end gap-3">
          <button onClick={() => setIsConfirmOpen(false)} className="px-4 py-2 rounded bg-gray-100 text-gray-700">Cancelar</button>
          <button onClick={confirmAndSendZip} className="px-4 py-2 rounded bg-black text-white">Confirmar e enviar</button>
        </div>
      </Modal>
    </div>
  );
};