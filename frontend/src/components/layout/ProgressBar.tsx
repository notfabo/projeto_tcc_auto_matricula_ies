import React from 'react';
import { Upload, FileCheck, CheckCircle2 } from 'lucide-react';
import { Stage } from '../../types/documento';

interface ProgressBarProps {
  currentStage: Stage;
  onNextStage?: () => void;
  onPreviousStage?: () => void;
  canProceed?: boolean;
  hasUploadedFiles?: boolean;
  canViewEnrollment?: boolean;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({ 
  currentStage, 
  onNextStage,
  onPreviousStage,
  canProceed = false,
  hasUploadedFiles = false
  , canViewEnrollment = false
}) => {
  const getStageColor = (stage: Stage) => {
    const stageOrder = ['upload', 'review', 'approved'];
    const currentIndex = stageOrder.indexOf(currentStage);
    const stageIndex = stageOrder.indexOf(stage);

    if (stageIndex < currentIndex) {
      return 'bg-green-500'; 
    } else if (stageIndex === currentIndex) {
      return 'bg-yellow-500'; 
    } else {
      return 'bg-blue-500';
    }
  };

  const isStageCompleted = (stage: Stage) => {
    const stageOrder = ['upload', 'review', 'approved'];
    const currentIndex = stageOrder.indexOf(currentStage);
    const stageIndex = stageOrder.indexOf(stage);
    return stageIndex < currentIndex;
  };

  const getStageTitle = (stage: Stage) => {
    switch (stage) {
      case 'upload':
        return 'Envio de Documentos';
      case 'review':
        return 'Revisão';
      case 'approved':
        return 'Aprovado';
      default:
        return '';
    }
  };

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div className="flex items-center w-full">
          <div className="flex flex-col items-center">
            <div className={`rounded-full h-12 w-12 flex items-center justify-center text-white ${getStageColor('upload')}`}>
              {isStageCompleted('upload') ? (
                <CheckCircle2 className="h-6 w-6" />
              ) : (
                <Upload className="h-6 w-6" />
              )}
            </div>
            <span className="mt-2 text-sm font-medium text-gray-700">{getStageTitle('upload')}</span>
          </div>
          <div className={`flex-1 h-1 mx-4 ${isStageCompleted('upload') ? 'bg-green-500' : 'bg-gray-200'}`} />

          <div className="flex flex-col items-center">
            <div className={`rounded-full h-12 w-12 flex items-center justify-center text-white ${getStageColor('review')}`}>
              {isStageCompleted('review') ? (
                <CheckCircle2 className="h-6 w-6" />
              ) : (
                <FileCheck className="h-6 w-6" />
              )}
            </div>
            <span className="mt-2 text-sm font-medium text-gray-700">{getStageTitle('review')}</span>
          </div>
          <div className={`flex-1 h-1 mx-4 ${isStageCompleted('review') ? 'bg-green-500' : 'bg-gray-200'}`} />

          {/* Approved Stage */}
          <div className="flex flex-col items-center">
            <div className={`rounded-full h-12 w-12 flex items-center justify-center text-white ${getStageColor('approved')}`}>
              {isStageCompleted('approved') ? (
                <CheckCircle2 className="h-6 w-6" />
              ) : (
                <CheckCircle2 className="h-6 w-6" />
              )}
            </div>
            <span className="mt-2 text-sm font-medium text-gray-700">{getStageTitle('approved')}</span>
          </div>
        </div>
      </div>

      {(onNextStage || onPreviousStage) && (
        <div className="flex justify-center space-x-4 mb-4">
          {(currentStage === 'review' || currentStage === 'approved') && onPreviousStage && (
            <button
              onClick={onPreviousStage}
              className="px-6 py-2 rounded-md text-sm font-medium text-gray-700 bg-gray-200 hover:bg-gray-300 transition-colors"
            >
              Voltar
            </button>
          )}

          {currentStage !== 'approved' && onNextStage && (
            <button
              onClick={onNextStage}
              disabled={
                currentStage === 'upload' ? !canProceed : !canViewEnrollment
              }
              className={`px-6 py-2 rounded-md text-sm font-medium text-white ${
                (currentStage === 'upload' ? canProceed : canViewEnrollment)
                  ? 'bg-blue-500 hover:bg-blue-600 cursor-pointer'
                  : 'bg-gray-300 cursor-not-allowed'
              }`}
            >
              {currentStage === 'upload' 
                ? hasUploadedFiles 
                  ? 'Ver Andamento' 
                  : 'Envie pelo menos um documento para continuar'
                : currentStage === 'review'
                  ? canViewEnrollment
                    ? 'Ver aprovação de matrícula'
                    : 'Aguardando aprovação de matrícula'
                  : 'Ver aprovação de matrícula'}
            </button>
          )}
        </div>
      )}
    </div>
  );
}; 