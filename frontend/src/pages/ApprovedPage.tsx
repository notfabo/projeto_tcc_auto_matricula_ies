import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useDocumentManagementContext } from '../hooks/DocumentManagementContext';
import { ApprovedStage } from '../components/stages/ApprovedStage';
import { getMinhaMatricula } from '../services/matricula';

export const ApprovedPage = () => {
  const navigate = useNavigate();
  const { user, isLoggedIn, isInitializing } = useAuth();

  const { documents, isLoading } = useDocumentManagementContext();

  const [canViewEnrollment, setCanViewEnrollment] = useState<boolean | null>(null);

  useEffect(() => {
    // determina se o candidato pode ver a etapa de matrícula aprovada
    const check = async () => {
      // se não tiver token ainda, aguardar
      if (!user?.token) {
        setCanViewEnrollment(null);
        return;
      }

      // Tentar obter a matrícula do usuário (endpoint assumed /api/matriculas/me)
      const matricula = await getMinhaMatricula(user.token);
      if (matricula) {
        // usar apenas o status da matrícula (não confundir com pré-matrícula)
        setCanViewEnrollment((matricula.status || '').toLowerCase() === 'aprovado');
        return;
      }

      // fallback: caso o endpoint não exista ou retorne erro, manter a lógica antiga
      const fallback =
        documents.some(doc => doc.tipo === '1' && doc.status === 'aprovado') &&
        documents.some(doc => doc.tipo === '3' && doc.status === 'aprovado');
      setCanViewEnrollment(fallback);
    };

    check();
  }, [user?.token, documents]);

  if (isInitializing) {
    return <div>Carregando...</div>;
  }

  if (!user) {
    return <div>Carregando...</div>;
  }

  if (isLoading || canViewEnrollment === null) {
    return <div>Verificando status...</div>;
  }

  return  <ApprovedStage /> 
};
