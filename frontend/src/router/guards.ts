import type { Role } from '../types/auth.types';

export function canEnter(roles: Role[], required: Role | undefined): boolean {
  return required === undefined || roles.includes(required);
}
