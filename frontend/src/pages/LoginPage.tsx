import { useState } from 'react';
import { useNavigate } from 'react-router-dom'; 
import { LoginForm } from '../components/forms/LoginForm';
import { AdminLoginForm } from '../components/forms/AdminLoginForm';
import { useAuth } from '../hooks/useAuth';

interface LoginResponse {
  token: string;
}

export function LoginPage() {
  const [formType, setFormType] = useState<'student' | 'admin'>('student');
  const { handleLogin } = useAuth();
  const navigate = useNavigate();

  const onLoginSuccess = (loginResponse: LoginResponse) => {
    const userType = formType;
    
    const defaultStage = userType === 'admin' ? 'upload' : 'upload';
    
    handleLogin(loginResponse.token, userType);

    if (userType === 'admin') {
      navigate('/admin');
    } else {
      navigate('/dashboard/upload');
    }
  };

  return (
    <div>
      {formType === 'student' ? (
        <LoginForm 
          onLoginSuccess={onLoginSuccess} 
          onAdminClick={() => setFormType('admin')}
        />
      ) : (
        <AdminLoginForm 
          onLoginSuccess={onLoginSuccess} 
          onStudentClick={() => setFormType('student')}
        />
      )}
    </div>
  );
}