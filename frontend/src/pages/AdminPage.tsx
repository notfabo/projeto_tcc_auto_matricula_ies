import React from 'react';
import { Header } from '../components/layout/Header';

interface AdminPageProps {
  onLogout: () => void;
}

export const AdminPage: React.FC<AdminPageProps> = ({ onLogout }) => {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header onLogout={onLogout} admin />
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">Painel Administrativo</h1>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Exportação de Dados</h3>
              <p className="text-gray-600 mb-4">Exporte dados de candidatos, matrículas e documentos</p>
              <button 
                onClick={() => window.location.href = '/admin/export'}
                className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition cursor-pointer"
              >
                Acessar
              </button>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Gerenciar Candidatos</h3>
              <p className="text-gray-600 mb-4">Visualize usuários e revise pré-matrículas</p>
              <button 
                onClick={() => window.location.href = '/admin/usuarios/revisao'}
                className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition cursor-pointer"
              >
                Acessar
              </button>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Relatórios</h3>
              <p className="text-gray-600 mb-4">Gere relatórios e estatísticas</p>
              <button 
                disabled
                className="bg-gray-400 text-white px-4 py-2 rounded cursor-not-allowed"
              >
                Em breve
              </button>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Informações do Sistema</h2>
            <div className="text-gray-600">
              <p className="mb-2">• Sistema de gestão de documentos</p>
              <p className="mb-2">• Autenticação JWT implementada</p>
              <p className="mb-2">• Controle de acesso por tipo de usuário</p>
              <p className="mb-2">• Interface responsiva e moderna</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};
