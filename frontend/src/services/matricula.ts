import api from './api';
import type { MatriculaDetalhesDTO } from '../types/revisao';

export const getMinhaMatricula = async (token: string): Promise<MatriculaDetalhesDTO | null> => {
  try {
    const { data } = await api.get('/api/matriculas/me', {
      headers: { Authorization: `Bearer ${token}` },
    });
    return data as MatriculaDetalhesDTO;
  } catch (err) {
    // Se endpoint não existir ou não autorizado, retornar null para fallback
    console.debug('Não foi possível obter matrícula do usuário logado:', err);
    return null;
  }
};
