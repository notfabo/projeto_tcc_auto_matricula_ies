import { Navigate, useParams } from 'react-router-dom';

export function LegacyRevisaoRedirect() {
  const { id } = useParams();
  const target = id ? `/admin/usuarios/revisao/${id}` : '/admin/usuarios/revisao';
  return <Navigate to={target} replace />;
}


