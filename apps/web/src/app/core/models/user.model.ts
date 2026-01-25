export interface User {
    id: number;
    email: string;
    full_name?: string;
    is_active: boolean;
}

export interface AuthResponse {
    access_token: string;
    refresh_token: string;
    token_type: string;
    expires_in: number;
}
