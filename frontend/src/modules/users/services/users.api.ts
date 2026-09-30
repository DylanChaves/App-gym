import { api } from '../../../services/http';
import type { Page } from '../../../types/api.types';
import type { Role, User } from '../../../types/auth.types';

export interface UserInput {
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  roles: Role[];
  is_active: boolean;
  password?: string;
}
export const getUsers = (page = 1, role?: Role, assigned = false) =>
  api<Page<User>>(
    `/users/?page=${page}${role ? `&role=${role}` : ''}${assigned ? '&assigned=me' : ''}`,
  );
export const getUser = (id: number) => api<User>(`/users/${id}/`);
export const createUser = (body: UserInput) => api<User>('/users/', { method: 'POST', body });
export const updateUser = (id: number, body: UserInput) =>
  api<User>(`/users/${id}/`, { method: 'PATCH', body });
export const assignCoach = (id: number, coachId: number | null) =>
  api<User>(`/users/${id}/coach/`, { method: 'POST', body: { coach_id: coachId } });
export async function getCoaches() {
  const users: User[] = [];
  for (let page = 1; ; page++) {
    const result = await getUsers(page, 'coach');
    users.push(...result.results.filter((user) => user.is_active));
    if (!result.next) return users;
  }
}
