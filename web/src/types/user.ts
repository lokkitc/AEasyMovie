export interface User {
  id: number;
  username: string;
  email: string;
  photo?: string;
  createdAt: string;
  updatedAt: string;
}

export interface UserResponse {
  users: User[];
  total: number;
  page: number;
  limit: number;
} 