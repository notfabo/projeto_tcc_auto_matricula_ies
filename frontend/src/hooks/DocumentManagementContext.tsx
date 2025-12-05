import React, { createContext, useContext, ReactNode } from 'react';
import { useDocumentManagement } from './useDocumentManagement';
import { useAuth } from './useAuth';

type DocumentManagementContextValue = ReturnType<typeof useDocumentManagement>;

const DocumentManagementContext = createContext<DocumentManagementContextValue | undefined>(undefined);

export const DocumentManagementProvider = ({ children }: { children: ReactNode }) => {
  const { user, isLoggedIn } = useAuth();
  const value = useDocumentManagement(user?.token ?? '', isLoggedIn);

  return (
    <DocumentManagementContext.Provider value={value}>
      {children}
    </DocumentManagementContext.Provider>
  );
};

export const useDocumentManagementContext = (): DocumentManagementContextValue => {
  const ctx = useContext(DocumentManagementContext);
  if (!ctx) {
    throw new Error('useDocumentManagementContext must be used within a DocumentManagementProvider');
  }
  return ctx;
};

export default DocumentManagementContext;
