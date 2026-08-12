import axios from 'axios';

// Las solicitudes pasan por el proxy same-origin configurado en Next.js.
const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
});

// Interceptor para agregar el token JWT a las peticiones
api.interceptors.request.use(
  (config) => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export const espacioService = {
  // Obtener todos los espacios (con filtro opcional por estado)
  getEspacios: async (estado = null) => {
    try {
      const params = estado ? { estado } : {};
      const response = await api.get('/espacios/', { params });
      return response.data;
    } catch (error) {
      throw error.response?.data || new Error('Error al obtener los espacios');
    }
  },

  // Obtener un espacio por ID
  getEspacioById: async (id) => {
    try {
      const response = await api.get(`/espacios/${id}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || new Error('Error al obtener el espacio');
    }
  },

  // Crear un nuevo espacio (solo para administradores)
  createEspacio: async (espacioData) => {
    try {
      const response = await api.post('/espacios/', espacioData);
      return response.data;
    } catch (error) {
      throw error.response?.data || new Error('Error al crear el espacio');
    }
  },

  // Actualizar un espacio existente (solo para administradores)
  updateEspacio: async (id, espacioData) => {
    try {
      const response = await api.put(`/espacios/${id}`, espacioData);
      return response.data;
    } catch (error) {
      throw error.response?.data || new Error('Error al actualizar el espacio');
    }
  },

  // Eliminar un espacio (solo para administradores)
  deleteEspacio: async (id) => {
    try {
      await api.delete(`/espacios/${id}`);
    } catch (error) {
      throw error.response?.data || new Error('Error al eliminar el espacio');
    }
  }
};

export default espacioService;
