import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { Header } from '../components/layout/Header';

export default function AdminUsersPage() {
  const navigate = useNavigate();
  return (
    <div className="min-h-screen bg-gray-50">
      <Header onLogout={() => (window.location.href = '/login')} admin />
      <div className="max-w-6xl mx-auto px-4 py-4">
        <button
          type="button"
          onClick={() => navigate('/admin')}
          className="inline-flex items-center gap-2 px-3 py-1.5 rounded border border-gray-300 bg-white text-sm cursor-pointer"
        >
          ← Voltar ao Painel
        </button>
      </div>
      <div className="mx-auto max-w-6xl px-4 py-6">
        {/* <h1 className="text-2xl font-semibold text-gray-900">Gerenciar Candidatos</h1>
        <p className="text-sm text-gray-600">Administre usuários e revise pré-matrículas</p> */}
        <div className="">
          <Outlet />
        </div>
      </div>
    </div>
  );
}


