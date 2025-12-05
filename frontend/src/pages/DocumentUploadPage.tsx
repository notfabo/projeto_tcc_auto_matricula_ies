import React from 'react';
import { useAuth } from '../hooks/useAuth';
import { useDocumentManagementContext } from '../hooks/DocumentManagementContext';
import { DocumentUploadStage } from '../components/stages'; 

export const DocumentUploadPage = () => {
  const { user, isLoggedIn, isInitializing } = useAuth();

  const {
    documents,
    isLoading,
    selectedFiles,
    pendingUploads,
    handleFileSelect,
    handleFileUpload,
    handleReupload,
  } = useDocumentManagementContext();

  if (isInitializing) {
    return <div>Carregando...</div>;
  }

  if (!user) {
    return <div>Não autenticado</div>;
  }

  return (
    <DocumentUploadStage
      documents={documents}
      isLoading={isLoading}
      selectedFiles={selectedFiles}
      pendingUploads={pendingUploads}
      onFileSelect={handleFileSelect}
      onFileUpload={handleFileUpload}
      onRemove={handleReupload}
    />
  );
};