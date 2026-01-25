import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, tap, catchError, of } from 'rxjs';
import { ApiService } from './api.service';
import { User, AuthResponse } from '../models/user.model';
import { Router } from '@angular/router';

@Injectable({
    providedIn: 'root'
})
export class AuthService {
    private currentUserSubject = new BehaviorSubject<User | null>(null);
    public currentUser$ = this.currentUserSubject.asObservable();
    private initialized = false;

    constructor(private apiService: ApiService, private router: Router) {
        this.initializeAuth();
    }

    private initializeAuth(): void {
        if (this.initialized) return;
        this.initialized = true;

        const token = localStorage.getItem('access_token');
        if (token) {
            this.fetchMe().pipe(
                catchError(() => {
                    // Token invalid, clean up
                    this.clearTokens();
                    return of(null);
                })
            ).subscribe();
        }
    }

    register(credentials: { email: string; password: string; full_name: string }): Observable<User> {
        return this.apiService.post<User>('/auth/register', credentials);
    }

    login(credentials: { email: string; password: string }): Observable<AuthResponse> {
        return this.apiService.post<AuthResponse>('/auth/login', credentials).pipe(
            tap((response: AuthResponse) => {
                this.setTokens(response.access_token, response.refresh_token);
                // Fetch user profile after login
                this.fetchMe().subscribe();
            })
        );
    }

    fetchMe(): Observable<User> {
        return this.apiService.get<User>('/auth/me').pipe(
            tap((user: User) => this.currentUserSubject.next(user)),
            catchError((error) => {
                this.currentUserSubject.next(null);
                throw error;
            })
        );
    }

    logout(): void {
        this.clearTokens();
        this.currentUserSubject.next(null);
        this.router.navigate(['/auth/login']);
    }

    private setTokens(accessToken: string, refreshToken: string): void {
        localStorage.setItem('access_token', accessToken);
        localStorage.setItem('refresh_token', refreshToken);
    }

    private clearTokens(): void {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
    }

    get isAuthenticated(): boolean {
        return !!localStorage.getItem('access_token');
    }

    get currentUser(): User | null {
        return this.currentUserSubject.value;
    }

    getToken(): string | null {
        return localStorage.getItem('access_token');
    }

    getRefreshToken(): string | null {
        return localStorage.getItem('refresh_token');
    }
}
