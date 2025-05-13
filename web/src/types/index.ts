export interface User {
  user_id: number;
  username: string;
  email: string;
  name: string;
  surname: string;
  photo: string;
  header_photo: string;
  about: string;
  location: string;
  age: number;
  created_at: string;
  updated_at: string;
  is_premium: boolean;
  premium_until: string | null;
  money: number;
  level: number;
  title: string;
} 