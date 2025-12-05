import { useState, useEffect, useCallback  } from 'react';
import { toast } from 'react-hot-toast';
import { Document, UiDocumentStatus, ApiDocumentStatus } from '../types/documento';
import { getTiposDocumento, getMeusDocumentos, uploadDocumento, reuploadDocumento } from '../services/documento';

const mapApiStatusToUiStatus = (apiStatus: ApiDocumentStatus): UiDocumentStatus => {
  if (apiStatus === 'sucesso') return 'aprovado';
  if (apiStatus === 'reprovado') return 'reprovado';
  return apiStatus; 
};

export const useDocumentManagement = (token: string, isLoggedIn: boolean) => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedFiles, setSelectedFiles] = useState<{ [docId: number]: File | undefined }>({});
  const [pendingUploads, setPendingUploads] = useState<Set<number>>(new Set());
  const [awaitingReupload, setAwaitingReupload] = useState<Set<number>>(new Set());

const fetchAndMergeDocuments = useCallback(async (showLoading = true) => {
    if (!isLoggedIn || !token) {
      if (showLoading) setIsLoading(false);
      setDocuments([]);
      return;
    }

    if (showLoading) setIsLoading(true);
    try {
      const [tipos, meusDocs] = await Promise.all([
        getTiposDocumento(),
        getMeusDocumentos()
      ]);

      const mergedDocuments: Document[] = tipos.map((tipo, index) => {
        const docExistente = meusDocs.find(d => d.tipo === String(tipo.id));

        if (docExistente) {
          // se o usuário clicou em 'Reenviar' e está aguardando selecionar arquivo, preservar o estado local
          if (awaitingReupload.has(docExistente.id)) {
            const local = documents.find(d => d.id === docExistente.id);
            if (local) return local;
          }

          return {
            id: docExistente.id,
            tipo: docExistente.tipo,
            nome: tipo.nome,
            required: tipo.obrigatorio,
            status: mapApiStatusToUiStatus(docExistente.status),
            dadosExtraidos: docExistente.dadosExtraidos,
            motivoErro: docExistente.motivoErro,
            dataUpload: docExistente.dataUpload,
          };
        } else {
          return {
            id: tipo.id + 10000,
            tipo: String(tipo.id),
            nome: tipo.nome,
            required: tipo.obrigatorio,
            status: 'pendente',
            dadosExtraidos: null,
            motivoErro: null,
            dataUpload: null,
          };
        }
      });

      setDocuments(mergedDocuments);
    } catch (error) {
      console.error("Erro ao buscar documentos:", error);
      toast.error("Não foi possível carregar seus documentos.");
    } finally {
      if (showLoading) setIsLoading(false);
    }
  }, [isLoggedIn, token]);

  useEffect(() => {
    fetchAndMergeDocuments();
  }, [fetchAndMergeDocuments]);;

  // Polling para manter o frontend sincronizado com o backend
  useEffect(() => {
    if (!isLoggedIn || !token) return;
    const interval = setInterval(() => {
      fetchAndMergeDocuments(false).catch(err => console.error('Erro no polling de documentos', err));
    }, 10000); // cada 10 segundos

    return () => clearInterval(interval);
  }, [isLoggedIn, token, fetchAndMergeDocuments]);

  const handleFileSelect = (docId: number, file: File | undefined) => {
      setSelectedFiles(prev => ({ ...prev, [docId]: file }));
      // Se o usuário selecionou um arquivo para um documento que estava em modo 'reenviar',
      // remover da lista awaitingReupload para que o polling não mantenha o status local indefinidamente.
      setAwaitingReupload(prev => {
        if (!prev.has(docId)) return prev;
        const next = new Set(prev);
        next.delete(docId);
        return next;
      });
      // Não gerenciar pendingUploads aqui - isso deve ser feito apenas no upload
    };

  const handleFileUpload = async (docId: number, file?: File) => {
    const currentDoc = documents.find(d => d.id === docId);;
    const fileToUpload = file || selectedFiles[docId];
    if (!currentDoc || !fileToUpload) return;
    
    if (!['application/pdf', 'image/png', 'image/jpeg'].includes(fileToUpload.type)) {
      toast.error('Tipo de arquivo não suportado. Envie PDF, PNG ou JPEG.');
      return;
    }
    if (fileToUpload.size > 10 * 1024 * 1024) {
      toast.error('Arquivo excede o limite de 10MB.');
      return;
    }
    
    let subtipo: string | undefined;
    if (currentDoc.nome.toLowerCase().includes('identidade')) {
      subtipo = 'rg';
    }
    
  setPendingUploads(prev => new Set([...prev, docId]));
    
    try {
      // se o documento já existe no backend (ids reais não têm o offset 10000 que usamos para pendentes),
      // chamar o endpoint /reupload para que o backend trate como reenvio explicitamente
      let response: any;
      try {
        if (currentDoc.id && currentDoc.id < 10000) {
          // reupload
          response = await reuploadDocumento(fileToUpload, currentDoc.id, token, subtipo);
        } else {
          response = await uploadDocumento(fileToUpload, currentDoc.tipo, token, subtipo);
        }
      } catch (e) {
        throw e;
      }
      
      setDocuments(docs =>
        docs.map(doc => {
          if (doc.id === docId) {
            // mapeia o status vindo do backend para o estado no frontend
            const status = mapApiStatusToUiStatus(response.status);
            
            return { 
              ...doc, 
              status, 
              dataUpload: response.dataUpload,
              id: typeof response.id === 'number' ? response.id : doc.id
            };
          }
          return doc;
        })
      );
      
      setSelectedFiles(prev => {
        const newFiles = { ...prev };
        delete newFiles[docId];
        return newFiles;
      });

      // caso tenha sido uma tentativa de reenviar (estava aguardando reupload), garantir remoção
      setAwaitingReupload(prev => {
        const newSet = new Set([...prev]);
        newSet.delete(docId);
        return newSet;
      });
      
      setPendingUploads(prev => {
        const newSet = new Set([...prev]);
        newSet.delete(docId);
        return newSet;
      });
      
      // Após upload, refetch para sincronizar status definitivo que o backend pode ter
      try {
        await fetchAndMergeDocuments(false);
      } catch (err) {
        // já logado na chamada original se falhar
      }

      // garantir que pendingUploads foi removido mesmo que o fetch tenha trocado o id
      setPendingUploads(prev => {
        const newSet = new Set([...prev]);
        newSet.delete(docId);
        return newSet;
      });

      toast.success('Documento enviado com sucesso!');
    } catch (err) {
      console.error('Upload error:', err);
      toast.error('Erro ao enviar documento.');
    }
  };

  const handleReupload = (docId: number) => {
    setAwaitingReupload(prev => new Set([...prev, docId]));
  };

  const updateDocumentsToReviewStage = () => {
    setDocuments(docs =>
      docs.map(doc => {
        if (doc.status === 'enviado') {
          return { ...doc, status: 'revisao' as const };
        }
        return doc;
      })
    );
  };

  return {
    documents,
    isLoading, 
    selectedFiles,
    pendingUploads,
    handleFileSelect,
    handleFileUpload,
    handleReupload,
    updateDocumentsToReviewStage,
    refreshDocuments: fetchAndMergeDocuments, 
  };
};
