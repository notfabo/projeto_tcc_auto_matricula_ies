import { Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

interface ProtectedRouteProps {
  children: React.ReactNode;
  userType?: 'student' | 'admin';
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, userType }) => {
  const { isLoggedIn, user, isInitializing } = useAuth();

  if (isInitializing) {
    return <div>Verificando autenticação...</div>;
  }

  if (!isLoggedIn) {
    return <Navigate to="/login" replace />;
  }

  if (userType && user?.type !== userType) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};