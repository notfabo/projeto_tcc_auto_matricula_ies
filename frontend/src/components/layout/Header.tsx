import { LogOut } from 'lucide-react';
import { useEffect, useState } from 'react';
import { getCandidatoLogado } from '../../services/candidato';

interface HeaderProps {
  onLogout: () => void;
  admin?: boolean;
}

export const Header = ({ onLogout, admin }: HeaderProps) => {
  const [candidato, setCandidato] = useState<{nome: string} | null>(null);

  useEffect(() => {
    if (admin) return;
    const token = localStorage.getItem('token');
    if (token) {
      getCandidatoLogado(token).then(setCandidato).catch(console.error);
    }
  }, [admin]);

  if (!admin && !candidato) return <div className="h-20"></div>;

  return (
    <div className="bg-white shadow">
      <div className="max-w-7xl mx-auto px-4 py-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            {admin ? 'Boas vindas, Administrador!' : `Olá, ${candidato?.nome}!`}
          </h1>
          <p className="mt-1 text-sm text-gray-600">
            {admin ? 'Gerencie as configurações do sistema' : 'Complete sua matrícula seguindo estas etapas'}
          </p>
        </div>
        <button
          onClick={onLogout}
          className="ml-4 flex items-center gap-2 px-3 py-2 rounded hover:bg-red-50 transition text-red-600 border border-red-200 cursor-pointer focus:outline-none focus:ring-2 focus:ring-red-300"
          title="Sair"
          type="button"
        >
          <LogOut size={20} />
          <span className="hidden sm:inline">Sair</span>
        </button>
      </div>
    </div>
  );
};