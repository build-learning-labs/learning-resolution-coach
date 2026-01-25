import { Routes } from '@angular/router';
import { authGuard } from './core/guards/auth.guard';

export const routes: Routes = [
    {
        path: '',
        loadComponent: () => import('./features/landing/landing.component').then(m => m.LandingComponent)
    },
    {
        path: 'auth',
        children: [
            {
                path: 'login',
                loadComponent: () => import('./features/auth/login/login.component').then(m => m.LoginComponent)
            },
            {
                path: 'register',
                loadComponent: () => import('./features/auth/register/register.component').then(m => m.RegisterComponent)
            },
            { path: '', redirectTo: 'login', pathMatch: 'full' }
        ]
    },
    {
        path: '',
        canActivate: [authGuard],
        children: [
            {
                path: 'dashboard',
                loadComponent: () => import('./features/dashboard/dashboard.component').then(m => m.DashboardComponent)
            },
            {
                path: 'setup',
                loadComponent: () => import('./features/setup/intake-wizard/intake-wizard.component').then(m => m.IntakeWizardComponent)
            },
            {
                path: 'checkin',
                loadComponent: () => import('./features/checkin/checkin-layout.component').then(m => m.CheckinLayoutComponent),
                children: [
                    {
                        path: '',
                        loadComponent: () => import('./features/checkin/checkin-form/checkin-form.component').then(m => m.CheckinFormComponent)
                    }
                ]
            }
        ]
    },
    { path: '**', redirectTo: '' }
];
