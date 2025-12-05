import React from 'react';
import { CheckCircle2 } from 'lucide-react';

export const ApprovedStage: React.FC = () => {
  return (
    <div className="bg-white rounded-xl shadow-lg overflow-hidden">
      <div className="bg-gradient-to-r from-green-600 to-green-800 p-8 text-center">
        <div className="flex justify-center mb-4">
          <div className="bg-white rounded-full p-3 shadow-lg">
            <CheckCircle2 className="h-12 w-12 text-green-600" />
          </div>
        </div>
        <h2 className="text-3xl font-bold text-white mb-2">Matrícula Aprovada!</h2>
        <p className="text-green-100 text-lg">
          Parabéns! Sua matrícula foi concluída com sucesso.
        </p>
      </div>

      <div className="p-8">
        <div className="max-w-2xl mx-auto">
          <div className="bg-green-50 rounded-lg p-6 mb-6">
            <h3 className="text-lg font-semibold text-green-800 mb-4">Próximos Passos</h3>
            <ul className="space-y-3">
              <li className="flex items-start">
                <CheckCircle2 className="h-5 w-5 text-green-500 mt-1 mr-3 flex-shrink-0" />
                <span className="text-gray-700">
                  Você receberá um e-mail com as instruções para acesso ao portal do aluno
                </span>
              </li>
              <li className="flex items-start">
                <CheckCircle2 className="h-5 w-5 text-green-500 mt-1 mr-3 flex-shrink-0" />
                <span className="text-gray-700">
                  O calendário acadêmico será disponibilizado em breve
                </span>
              </li>
              <li className="flex items-start">
                <CheckCircle2 className="h-5 w-5 text-green-500 mt-1 mr-3 flex-shrink-0" />
                <span className="text-gray-700">
                  Acompanhe seu e-mail para mais informações sobre o início das aulas
                </span>
              </li>
            </ul>
          </div>

          <div className="bg-blue-50 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-blue-800 mb-4">Dúvidas?</h3>
            <p className="text-gray-700 mb-4">
              Entre em contato com nossa equipe de suporte:
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-white rounded-lg p-4 shadow-sm">
                <p className="text-sm text-gray-500">E-mail</p>
                <p className="text-blue-600 font-medium">suporte@faculdade.com.br</p>
              </div>
              <div className="bg-white rounded-lg p-4 shadow-sm">
                <p className="text-sm text-gray-500">Telefone</p>
                <p className="text-blue-600 font-medium">(11) 1234-5678</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
