import { api } from '../config/api';
import { API_ENDPOINTS } from '../config/api';
import type { User, UserResponse } from '../types/user';

export const userService = {
  async getUsers(page = 1, limit = 10): Promise<UserResponse> {
    try {
      const response = await api.get<User[]>(API_ENDPOINTS.USERS, {
        params: {
          page,
          limit,
        },
      });
      
      // Преобразуем ответ в формат UserResponse
      return {
        users: Array.isArray(response.data) ? response.data : [],
        total: Array.isArray(response.data) ? response.data.length : 0,
        page,
        limit,
      };
    } catch (error) {
      console.error('Error fetching users:', error);
      throw error;
    }
  },

  async getUserById(id: number): Promise<User> {
    try {
      const response = await api.get<User>(`${API_ENDPOINTS.USERS}/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching user ${id}:`, error);
      throw error;
    }
  },
}; 