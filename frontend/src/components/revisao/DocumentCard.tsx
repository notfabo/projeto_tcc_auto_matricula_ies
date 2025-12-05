import React from 'react';
import { Download } from 'lucide-react';
import type { DocumentoRevisaoDTO } from '../../types/revisao';
import { DOCUMENT_TYPES } from '../../types/revisao';
import api from '../../services/api';

function statusToChip(status: string) {
    switch (status) {
        case 'aprovado':
            return 'bg-green-100 text-green-700';
        case 'reprovado':
            return 'bg-red-100 text-red-700';
        case 'revisao':
            return 'bg-blue-100 text-blue-700';
        case 'pendente':
            return 'bg-yellow-100 text-yellow-700';
        default:
            return 'bg-gray-100 text-gray-700';
    }
}

function formatarDadosExtraidos(dadosExtraidos: string, tipoDocumento: string): React.ReactNode {
    try {
        const dados = JSON.parse(dadosExtraidos);
        
        // Para RG (tipo 1)
        if (tipoDocumento === '1') {
            const dadosOrganizados = dados.dados_organizados || dados;
            return (
                <div className="space-y-2">
                    {dadosOrganizados.nome && (
                        <div className="flex">
                            <span className="font-medium text-gray-700 w-32">Nome:</span>
                            <span className="text-gray-900">{dadosOrganizados.nome}</span>
                        </div>
                    )}
                    {dadosOrganizados.cpf && (
                        <div className="flex">
                            <span className="font-medium text-gray-700 w-32">CPF:</span>
                            <span className="text-gray-900">{dadosOrganizados.cpf}</span>
                        </div>
                    )}
                    {dadosOrganizados.registro_geral && (
                        <div className="flex">
                            <span className="font-medium text-gray-700 w-32">RG:</span>
                            <span className="text-gray-900">{dadosOrganizados.registro_geral}</span>
                        </div>
                    )}
                    {dadosOrganizados.data_nascimento && (
                        <div className="flex">
                            <span className="font-medium text-gray-700 w-32">Data de Nascimento:</span>
                            <span className="text-gray-900">{dadosOrganizados.data_nascimento}</span>
                        </div>
                    )}
                    {dadosOrganizados.data_expedicao && (
                        <div className="flex">
                            <span className="font-medium text-gray-700 w-32">Data de Expedição:</span>
                            <span className="text-gray-900">{dadosOrganizados.data_expedicao}</span>
                        </div>
                    )}
                    {dadosOrganizados.filiacao && (
                        <div className="mt-2 pt-2 border-t border-gray-200">
                            <div className="text-xs font-semibold text-gray-600 mb-1">FILIAÇÃO</div>
                            {dadosOrganizados.filiacao.mae && (
                                <div className="flex">
                                    <span className="font-medium text-gray-700 w-32">Mãe:</span>
                                    <span className="text-gray-900">{dadosOrganizados.filiacao.mae}</span>
                                </div>
                            )}
                            {dadosOrganizados.filiacao.pai && (
                                <div className="flex">
                                    <span className="font-medium text-gray-700 w-32">Pai:</span>
                                    <span className="text-gray-900">{dadosOrganizados.filiacao.pai}</span>
                                </div>
                            )}
                        </div>
                    )}
                    {dadosOrganizados.naturalidade && (
                        <div className="flex">
                            <span className="font-medium text-gray-700 w-32">Naturalidade:</span>
                            <span className="text-gray-900">{dadosOrganizados.naturalidade}</span>
                        </div>
                    )}
                </div>
            );
        }
        
        // Para Histórico Escolar (tipo 3)
        if (tipoDocumento === '3') {
            const dadosOrganizados = dados.dados_organizados || dados;
            return (
                <div className="space-y-2">
                    {dadosOrganizados.nome_aluno && (
                        <div className="flex">
                            <span className="font-medium text-gray-700 w-40">Nome do Aluno:</span>
                            <span className="text-gray-900">{dadosOrganizados.nome_aluno}</span>
                        </div>
                    )}
                    {dadosOrganizados.instituicao_ensino && (
                        <div className="flex">
                            <span className="font-medium text-gray-700 w-40">Instituição:</span>
                            <span className="text-gray-900">{dadosOrganizados.instituicao_ensino}</span>
                        </div>
                    )}
                    {dadosOrganizados.nivel_ensino && (
                        <div className="flex">
                            <span className="font-medium text-gray-700 w-40">Nível de Ensino:</span>
                            <span className="text-gray-900">{dadosOrganizados.nivel_ensino}</span>
                        </div>
                    )}
                    {dadosOrganizados.tempo_letivo && (
                        <div className="flex">
                            <span className="font-medium text-gray-700 w-40">Tempo Letivo:</span>
                            <span className="text-gray-900">{dadosOrganizados.tempo_letivo}</span>
                        </div>
                    )}
                    {(dadosOrganizados.cidade || dadosOrganizados.estado) && (
                        <div className="flex">
                            <span className="font-medium text-gray-700 w-40">Localização:</span>
                            <span className="text-gray-900">
                                {dadosOrganizados.cidade || ''} {dadosOrganizados.estado ? `- ${dadosOrganizados.estado}` : ''}
                            </span>
                        </div>
                    )}
                    {dadosOrganizados.certificacao_conclusao !== undefined && (
                        <div className="flex">
                            <span className="font-medium text-gray-700 w-40">Certificação:</span>
                            <span className="text-gray-900">
                                {dadosOrganizados.certificacao_conclusao ? 'Concluído' : 'Não concluído'}
                            </span>
                        </div>
                    )}
                </div>
            );
        }
        
        // Para Comprovante de Residência (tipo 4)
        if (tipoDocumento === '4') {
            const dadosOrganizados = dados.dados_organizados || dados;
            return (
                <div className="space-y-2">
                    {dadosOrganizados.rua_avenida && (
                        <div className="flex">
                            <span className="font-medium text-gray-700 w-40">Logradouro:</span>
                            <span className="text-gray-900">{dadosOrganizados.rua_avenida}</span>
                        </div>
                    )}
                    {dadosOrganizados.numero_endereco && (
                        <div className="flex">
                            <span className="font-medium text-gray-700 w-40">Número:</span>
                            <span className="text-gray-900">{dadosOrganizados.numero_endereco}</span>
                        </div>
                    )}
                    {dadosOrganizados.bairro && (
                        <div className="flex">
                            <span className="font-medium text-gray-700 w-40">Bairro:</span>
                            <span className="text-gray-900">{dadosOrganizados.bairro}</span>
                        </div>
                    )}
                    {(dadosOrganizados.cidade || dadosOrganizados.estado_uf) && (
                        <div className="flex">
                            <span className="font-medium text-gray-700 w-40">Cidade/Estado:</span>
                            <span className="text-gray-900">
                                {dadosOrganizados.cidade || ''} {dadosOrganizados.estado_uf ? `- ${dadosOrganizados.estado_uf}` : ''}
                            </span>
                        </div>
                    )}
                    {dadosOrganizados.cep && (
                        <div className="flex">
                            <span className="font-medium text-gray-700 w-40">CEP:</span>
                            <span className="text-gray-900">{dadosOrganizados.cep}</span>
                        </div>
                    )}
                    {dadosOrganizados.data_emissao && (
                        <div className="flex">
                            <span className="font-medium text-gray-700 w-40">Data de Emissão:</span>
                            <span className="text-gray-900">{dadosOrganizados.data_emissao}</span>
                        </div>
                    )}
                    {dadosOrganizados.cpf_vinculado && (
                        <div className="flex">
                            <span className="font-medium text-gray-700 w-40">CPF Vinculado:</span>
                            <span className="text-gray-900">{dadosOrganizados.cpf_vinculado}</span>
                        </div>
                    )}
                </div>
            );
        }
        
        // Para outros tipos de documentos, formatação genérica
        return (
            <div className="space-y-2">
                {Object.entries(dados.dados_organizados || dados).map(([key, value]) => {
                    if (value === null || value === undefined || (typeof value === 'object' && Object.keys(value).length === 0)) {
                        return null;
                    }
                    const label = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                    return (
                        <div key={key} className="flex">
                            <span className="font-medium text-gray-700 w-40">{label}:</span>
                            <span className="text-gray-900">
                                {typeof value === 'object' ? JSON.stringify(value, null, 2) : String(value)}
                            </span>
                        </div>
                    );
                })}
            </div>
        );
    } catch (e) {
        // Se não for JSON válido, retorna o texto original
        return <pre className="whitespace-pre-wrap text-sm text-gray-800">{dadosExtraidos}</pre>;
    }
}

export function DocumentCard({ doc }: { doc: DocumentoRevisaoDTO }) {
    const tipoDocumento = DOCUMENT_TYPES[doc.tipo] || `Tipo ${doc.tipo}`;
    const isNaoEnviado = doc.id < 0; // ID negativo indica documento não enviado
    
    const handleDownload = async () => {
        try {
            const response = await api.get(
                `/api/admin/matriculas/documentos/${doc.id}/download`,
                { 
                    responseType: 'blob' 
                }
            );
            
            // Criar um link temporário para download
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            
            // Determinar o nome do arquivo baseado no tipo de documento
            const extension = doc.caminhoArquivo?.split('.').pop() || 'pdf';
            link.setAttribute('download', `${tipoDocumento.replace(/\s+/g, '_')}_${doc.id}.${extension}`);
            
            document.body.appendChild(link);
            link.click();
            link.parentNode?.removeChild(link);
            window.URL.revokeObjectURL(url);
        } catch (error: any) {
            console.error('Erro ao baixar documento:', error);
            alert('Erro ao baixar documento. Por favor, tente novamente.');
        }
    };
    
    return (
        <div className={`rounded-lg border p-4 shadow-sm ${
            isNaoEnviado 
                ? 'border-yellow-300 bg-yellow-50' 
                : 'border-gray-200 bg-white'
        }`}>
            <div className="flex items-start justify-between">
                <div className="flex-1">
                    <h4 className="font-medium text-gray-900">{tipoDocumento}</h4>
                    {isNaoEnviado && (
                        <p className="text-xs text-yellow-700 mt-1">Documento ainda não enviado pelo candidato</p>
                    )}
                </div>
                <div className="flex items-center gap-2">
                    {!isNaoEnviado && doc.caminhoArquivo && (
                        <button
                            onClick={handleDownload}
                            className="flex items-center gap-1 px-2 py-1 text-xs text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded transition-colors"
                            title="Baixar documento"
                        >
                            <Download className="h-4 w-4" />
                            <span>Baixar</span>
                        </button>
                    )}
                    <span className={`px-2 py-1 text-xs rounded ${statusToChip(doc.status)}`}>
                        {doc.status}
                    </span>
                </div>
            </div>

            {!isNaoEnviado && doc.dadosExtraidos && (
                <div className="mt-3">
                    <div className="text-xs uppercase text-gray-500 mb-2">Dados extraídos</div>
                    <div className="rounded bg-gray-50 p-4 border border-gray-200">
                        {formatarDadosExtraidos(doc.dadosExtraidos, doc.tipo)}
                    </div>
                </div>
            )}

            {!isNaoEnviado && doc.motivoErro && (
                <div className="mt-3">
                    <div className="text-xs uppercase text-gray-500">Motivo do erro</div>
                    <div className="mt-1 rounded bg-red-50 p-2 text-sm text-red-700">{doc.motivoErro}</div>
                </div>
            )}
        </div>
    );
}


