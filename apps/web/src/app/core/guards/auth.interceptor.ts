import { HttpInterceptorFn, HttpRequest, HttpHandlerFn, HttpEvent, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { inject } from '@angular/core';
import { Router } from '@angular/router';

export const authInterceptor: HttpInterceptorFn = (req: HttpRequest<unknown>, next: HttpHandlerFn): Observable<HttpEvent<unknown>> => {
    const router = inject(Router);
    const token = localStorage.getItem('access_token');

    let authReq = req;
    if (token) {
        authReq = req.clone({
            setHeaders: {
                Authorization: `Bearer ${token}`
            }
        });
    }

    return next(authReq).pipe(
        catchError((error: HttpErrorResponse) => {
            // Handle 401 Unauthorized - auto logout
            if (error.status === 401) {
                // Don't redirect if already on auth pages
                const currentUrl = router.url;
                if (!currentUrl.startsWith('/auth')) {
                    localStorage.removeItem('access_token');
                    localStorage.removeItem('refresh_token');
                    router.navigate(['/auth/login'], {
                        queryParams: { returnUrl: currentUrl, reason: 'session_expired' }
                    });
                }
            }
            return throwError(() => error);
        })
    );
};
