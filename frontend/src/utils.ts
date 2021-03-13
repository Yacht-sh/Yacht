export interface User {
  username: string;
  id: number;
  is_active: boolean;
  authDisabled: boolean;
}

export const mockUser: User = {
  username: "admin@yacht.local",
  id: 0,
  is_active: true,
  authDisabled: true,
};
