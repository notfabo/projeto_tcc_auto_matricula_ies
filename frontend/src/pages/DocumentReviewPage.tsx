import { useState } from 'react';
import { DocumentReviewStage } from '../components/stages';
import { useAuth } from '../hooks/useAuth';
import { useDocumentManagementContext } from '../hooks/DocumentManagementContext';
import { toast } from 'react-hot-toast';
import { updateCandidatoAdicional } from '../services/candidato';

export const DocumentReviewPage = () => {
  const { user, isLoggedIn, isInitializing } = useAuth();
  const documentManagement = useDocumentManagementContext();
  const [isSaving, setIsSaving] = useState(false);

  if (isInitializing) {
    return <div>Carregando...</div>;
  }

  if (!user) {
    return <div>Carregando...</div>;
  }

  const { documents, handleReupload } = documentManagement;

  const token = user?.token || null;
  const handleSubmit = async (additionalInfo: any) => {
    if (!user.token) {
      toast.error("Você não está autenticado.");
      return;
    }

    setIsSaving(true);
    try {
      console.log("Enviando dados adicionais:", additionalInfo);

      await updateCandidatoAdicional(user.token, additionalInfo);

      toast.success("Informações salvas com sucesso!");
    } catch (error) {
      console.error("Erro ao salvar informações:", error);
      toast.error("Não foi possível salvar as informações. Tente novamente.");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <DocumentReviewStage
      documents={documents}
      onReupload={handleReupload}
      token={token}
    />
  );
};