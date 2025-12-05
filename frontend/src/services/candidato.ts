import { CandidatoAdicionalData } from '../types/candidato';
import api from './api';

export const getCandidatoLogado = async (token: string) => {
  const response = await api.get('/api/candidatos/me', {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return response.data;
};

export const updateCandidatoAdicional = async (token: string, data: CandidatoAdicionalData) => {
  const response = await api.patch('/api/candidatos/me/additional-info', data, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return response.data;
};
