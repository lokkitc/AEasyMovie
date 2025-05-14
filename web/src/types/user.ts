export interface User {
  user_id: number;
  username: string;
  name: string;
  surname: string;
  email: string;
  photo: string;
  header_photo: string;
  about: string;
  location: string;
  age: number;
  created_at: string;
  updated_at: string;
  is_premium: boolean;
  level: number;
  title: string;
}

export interface UserResponse {
  users: User[];
  total: number;
  page: number;
  limit: number;
} 