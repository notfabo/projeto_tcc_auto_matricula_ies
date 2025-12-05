import { useState, useEffect } from 'react';

interface UserData {
  token: string;
  type: 'student' | 'admin';
}

export const useAuth = () => {
  const [user, setUser] = useState<UserData | null>(null);
  const [isInitializing, setIsInitializing] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    const userType = localStorage.getItem('userType') as 'student' | 'admin' | null;
    
    if (token && userType) {
      setUser({ 
        token, 
        type: userType, 
      });
    }
    setIsInitializing(false);
  }, []);

  const handleLogin = (token: string, type: 'student' | 'admin') => {
    localStorage.setItem('token', token);
    localStorage.setItem('userType', type);
    setUser({ token, type });
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('userType');
    setUser(null);
  };

  return {
    user,
    isLoggedIn: !!user,
    isInitializing,
    handleLogin,
    handleLogout,
  };
};