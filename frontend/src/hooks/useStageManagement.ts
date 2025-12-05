import { useState } from 'react';
import { Stage } from '../types/documento';

export const useStageManagement = () => {
  const [currentStage, setCurrentStage] = useState<Stage>('upload');
  

  const canProceedToNextStage = (documents: any[]) => {
    if (currentStage === 'upload') {
      const canProceed = documents.some(doc => 
        doc.status === 'enviado' || 
        doc.status === 'revisando' || 
        doc.status === 'aprovado'
      );
      return canProceed;
    }
    if (currentStage === 'review') {
      const documentosObrigatorios = documents.filter(doc => doc.required);
      const canProceed = documentosObrigatorios.length > 0 && documentosObrigatorios.every(doc => doc.status === 'aprovado');
      return canProceed;
    }
    return false;
  };

  const handleNextStage = (documents: any[], updateDocumentsToReviewStage?: () => void) => {
    if (currentStage === 'upload') {
      setCurrentStage('review');
      if (updateDocumentsToReviewStage) {
        updateDocumentsToReviewStage();
      }
    } else if (currentStage === 'review') {
      setCurrentStage('approved');
    }
  };

  const handlePreviousStage = () => {
    if (currentStage === 'review') {
      setCurrentStage('upload');
    } else if (currentStage === 'approved') {
      setCurrentStage('review');
    }
  };

  return {
    currentStage,
    canProceedToNextStage,
    handleNextStage,
    handlePreviousStage,
  };
};
