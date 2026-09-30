export type Role = 'admin' | 'coach' | 'member';
export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  roles: Role[];
  is_active: boolean;
  coach_id: number | null;
}
export interface AppConfig {
  name: string;
  timezone: string;
  registration_enabled: boolean;
  terms_version: string;
  privacy_version: string;
  terms_url: string;
  privacy_url: string;
}
export const roleLabels: Record<Role, string> = {
  admin: 'Administrador',
  coach: 'Entrenador',
  member: 'Cliente',
};
