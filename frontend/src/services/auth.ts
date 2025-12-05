import api from './api';
import axios, { AxiosError } from 'axios';

interface LoginResponse {
  token: string;
}

interface LoginData {
  cpf: string;
  senha: string;
}

export const login = async (loginData: LoginData): Promise<LoginResponse> => {
  try {
    const response = await api.post<LoginResponse>('/api/auth/login', loginData, {
      headers: {
        'Content-Type': 'application/json',
      },
    });
    return response.data;
  } catch (error) {
    console.error('Erro no login:', error);
    if (axios.isAxiosError(error)) {
      const message = (error.response?.data as any)?.message;
      throw new Error(message || 'Erro ao fazer login');
    }
    throw new Error('Erro desconhecido');
  }
};

export const adminLogin = async (loginData: LoginData): Promise<LoginResponse> => {
  try {
    const response = await api.post<LoginResponse>('/api/admin/auth/login', loginData);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(error.response?.data?.message || 'Erro ao fazer login');
    }
    throw new Error('Erro desconhecido');
  }
};