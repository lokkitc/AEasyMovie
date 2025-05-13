import { useState, useEffect } from 'react';
import { userService } from '../services/userService';
import type { User, UserResponse } from '../types/user';

export const useUsers = (page = 1, limit = 10) => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        setLoading(true);
        const response = await userService.getUsers(page, limit);
        setUsers(response.users || []);
        setTotal(response.total || 0);
        setError(null);
      } catch (err) {
        console.error('Error fetching users:', err);
        setError(err instanceof Error ? err.message : 'Произошла ошибка при загрузке пользователей');
        setUsers([]);
        setTotal(0);
      } finally {
        setLoading(false);
      }
    };

    fetchUsers();
  }, [page, limit]);

  return { users, loading, error, total };
}; 