export type LoginRequest = {
  organization_id: number;
  email: string;
  password: string;
};

export type AccessTokenResponse = {
  access_token: string;
  token_type: string;
  expires_at: string;
};

export type CurrentUserResponse = {
  user_id: number;
  organization_id: number;
  email: string;
  full_name: string;
  active: boolean;
  verified: boolean;
};
