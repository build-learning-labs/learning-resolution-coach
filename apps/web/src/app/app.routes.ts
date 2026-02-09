import { Routes } from '@angular/router';
import { authGuard } from './core/guards/auth.guard';
import { LayoutComponent } from './layout/layout.component';

export const routes: Routes = [
    // 1. Landing Page
    {
        path: '',
        pathMatch: 'full',
        loadComponent: () => import('./features/landing/landing.component').then(m => m.LandingComponent)
    },

    // 2. Auth Routes
    {
        path: 'auth',
        children: [
            { path: 'login', loadComponent: () => import('./features/auth/login/login.component').then(m => m.LoginComponent) },
            { path: 'register', loadComponent: () => import('./features/auth/register/register.component').then(m => m.RegisterComponent) },
            { path: '', redirectTo: 'login', pathMatch: 'full' }
        ]
    },

    // 3. Protected App (Dashboard, Plan, Resources, etc.)
    {
        path: '',
        component: LayoutComponent,
        canActivate: [authGuard], // This protects everything inside
        children: [
            { path: 'dashboard', loadComponent: () => import('./features/dashboard/dashboard.component').then(m => m.DashboardComponent) },

            // MOVED HERE: Now it shares the Sidebar layout!
            { path: 'resources', loadComponent: () => import('./features/resources/resources.component').then(m => m.ResourcesComponent) },

            { path: 'setup', loadComponent: () => import('./features/setup/intake-wizard/intake-wizard.component').then(m => m.IntakeWizardComponent) },
            { path: 'plan', loadComponent: () => import('./features/plan/plan.component').then(m => m.PlanComponent) },
            { path: 'profile', loadComponent: () => import('./features/profile/profile.component').then(m => m.ProfileComponent) },
            {
                path: 'checkin',
                loadComponent: () => import('./features/checkin/checkin-layout.component').then(m => m.CheckinLayoutComponent),
                children: [{ path: '', loadComponent: () => import('./features/checkin/checkin-form/checkin-form.component').then(m => m.CheckinFormComponent) }]
            }
        ]
    },

    { path: '**', redirectTo: '' }
];