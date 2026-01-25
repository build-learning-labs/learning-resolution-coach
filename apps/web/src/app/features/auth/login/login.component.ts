import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterModule, ActivatedRoute } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';
import { AgentService } from '../../../core/services/agent.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule],
  template: `
    <div class="auth-page">
      <div class="auth-container">
        <div class="auth-card">
          <!-- Logo -->
          <div class="logo-section">
            <div class="logo-icon">🎓</div>
            <span class="logo-text">Learning Resolution Coach</span>
          </div>

          <!-- Header -->
          <div class="auth-header">
            <h1>Welcome Back</h1>
            <p>Sign in to continue your learning journey</p>
          </div>

          <!-- Session Expired Alert -->
          <div *ngIf="sessionExpired" class="alert-warning">
            <span class="alert-icon">⚠️</span>
            <span>Your session has expired. Please sign in again.</span>
          </div>
          
          <form [formGroup]="loginForm" (ngSubmit)="onSubmit()" class="auth-form">
            <div class="form-field">
              <label for="email">Email Address</label>
              <div class="input-wrapper">
                <span class="input-icon">📧</span>
                <input type="email" id="email" formControlName="email" placeholder="you@example.com">
              </div>
            </div>
            
            <div class="form-field">
              <label for="password">Password</label>
              <div class="input-wrapper">
                <span class="input-icon">🔒</span>
                <input type="password" id="password" formControlName="password" placeholder="••••••••">
              </div>
            </div>
            
            <div *ngIf="errorMessage" class="error-message">
              <span class="error-icon">⚠</span>
              {{ errorMessage }}
            </div>
            
            <button type="submit" [disabled]="isLoading" class="btn-primary">
              <span *ngIf="isLoading" class="spinner"></span>
              {{ isLoading ? 'Signing in...' : 'Sign In' }}
            </button>
          </form>
          
          <div class="auth-footer">
            <p>Don't have an account? <a routerLink="/auth/register">Create one now</a></p>
          </div>

          <a routerLink="/" class="back-link">← Back to Home</a>
        </div>
      </div>

      <!-- Decorative Background -->
      <div class="auth-decoration">
        <div class="deco-circle deco-1"></div>
        <div class="deco-circle deco-2"></div>
        <div class="deco-circle deco-3"></div>
      </div>
    </div>
  `,
  styles: [`
    .auth-page {
      min-height: 100vh;
      background: linear-gradient(135deg, #f5f7ff 0%, #e8ecff 50%, #f0f4ff 100%);
      position: relative;
      overflow: hidden;
    }

    .auth-container {
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      padding: 2rem;
      position: relative;
      z-index: 1;
    }

    .auth-card {
      background: white;
      padding: 2.5rem;
      border-radius: 1.5rem;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.1);
      width: 100%;
      max-width: 440px;
      animation: slideUp 0.5s ease-out;
    }

    @keyframes slideUp {
      from { opacity: 0; transform: translateY(20px); }
      to { opacity: 1; transform: translateY(0); }
    }

    /* Logo */
    .logo-section {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
      margin-bottom: 2rem;
    }

    .logo-icon {
      font-size: 2rem;
    }

    .logo-text {
      font-weight: 700;
      font-size: 1.1rem;
      color: #1f2937;
    }

    /* Header */
    .auth-header {
      text-align: center;
      margin-bottom: 2rem;
    }

    .auth-header h1 {
      font-size: 1.75rem;
      font-weight: 700;
      color: #111827;
      margin-bottom: 0.5rem;
    }

    .auth-header p {
      color: #6b7280;
      font-size: 0.95rem;
    }

    /* Alert */
    .alert-warning {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      background: #fef3c7;
      border: 1px solid #fcd34d;
      border-radius: 0.75rem;
      padding: 0.75rem 1rem;
      margin-bottom: 1.5rem;
      color: #92400e;
      font-size: 0.875rem;
    }

    .alert-icon {
      font-size: 1rem;
    }

    /* Form */
    .auth-form {
      display: flex;
      flex-direction: column;
      gap: 1.25rem;
    }

    .form-field {
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
    }

    .form-field label {
      font-weight: 600;
      font-size: 0.875rem;
      color: #374151;
    }

    .input-wrapper {
      position: relative;
      display: flex;
      align-items: center;
    }

    .input-icon {
      position: absolute;
      left: 1rem;
      font-size: 1rem;
      pointer-events: none;
    }

    .form-field input {
      width: 100%;
      padding: 0.875rem 1rem 0.875rem 2.75rem;
      border-radius: 0.75rem;
      border: 2px solid #e5e7eb;
      font-size: 1rem;
      transition: all 0.2s;
      background: #fafafa;
    }

    .form-field input:focus {
      outline: none;
      border-color: #6366f1;
      background: white;
      box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1);
    }

    .form-field input::placeholder {
      color: #9ca3af;
    }

    /* Button */
    .btn-primary {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
      padding: 1rem;
      background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
      color: white;
      border: none;
      border-radius: 0.75rem;
      font-weight: 600;
      font-size: 1rem;
      cursor: pointer;
      transition: all 0.2s;
      margin-top: 0.5rem;
      box-shadow: 0 4px 14px rgba(99, 102, 241, 0.3);
    }

    .btn-primary:hover:not(:disabled) {
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4);
    }

    .btn-primary:disabled {
      opacity: 0.7;
      cursor: not-allowed;
      transform: none;
    }

    .spinner {
      width: 18px;
      height: 18px;
      border: 2px solid rgba(255,255,255,0.3);
      border-top-color: white;
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
    }

    @keyframes spin {
      to { transform: rotate(360deg); }
    }

    /* Error */
    .error-message {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      color: #dc2626;
      font-size: 0.875rem;
      background: #fef2f2;
      padding: 0.75rem 1rem;
      border-radius: 0.75rem;
      border: 1px solid #fecaca;
    }

    .error-icon {
      font-size: 1rem;
    }

    /* Footer */
    .auth-footer {
      margin-top: 2rem;
      text-align: center;
      font-size: 0.9rem;
      color: #6b7280;
    }

    .auth-footer a {
      color: #6366f1;
      font-weight: 600;
      text-decoration: none;
      transition: color 0.2s;
    }

    .auth-footer a:hover {
      color: #4f46e5;
      text-decoration: underline;
    }

    .back-link {
      display: block;
      text-align: center;
      margin-top: 1.5rem;
      color: #9ca3af;
      font-size: 0.875rem;
      text-decoration: none;
      transition: color 0.2s;
    }

    .back-link:hover {
      color: #6366f1;
    }

    /* Decorative Background */
    .auth-decoration {
      position: absolute;
      inset: 0;
      pointer-events: none;
      overflow: hidden;
    }

    .deco-circle {
      position: absolute;
      border-radius: 50%;
      background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
    }

    .deco-1 {
      width: 400px;
      height: 400px;
      top: -100px;
      right: -100px;
      animation: float 8s ease-in-out infinite;
    }

    .deco-2 {
      width: 300px;
      height: 300px;
      bottom: -50px;
      left: -50px;
      animation: float 6s ease-in-out infinite reverse;
    }

    .deco-3 {
      width: 200px;
      height: 200px;
      top: 50%;
      left: 10%;
      animation: float 10s ease-in-out infinite;
    }

    @keyframes float {
      0%, 100% { transform: translateY(0) rotate(0deg); }
      50% { transform: translateY(-20px) rotate(5deg); }
    }

    /* Responsive */
    @media (max-width: 480px) {
      .auth-card {
        padding: 1.5rem;
      }

      .auth-header h1 {
        font-size: 1.5rem;
      }
    }
  `]
})
export class LoginComponent implements OnInit {
  loginForm: FormGroup;
  isLoading = false;
  errorMessage = '';
  sessionExpired = false;
  private returnUrl = '/dashboard';

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private agentService: AgentService,
    private router: Router,
    private route: ActivatedRoute
  ) {
    this.loginForm = this.fb.group({
      email: [''],
      password: ['']
    });
  }

  ngOnInit(): void {
    this.returnUrl = this.route.snapshot.queryParams['returnUrl'] || '/dashboard';
    if (this.route.snapshot.queryParams['reason'] === 'session_expired') {
      this.sessionExpired = true;
    }

    if (this.authService.isAuthenticated) {
      this.checkOnboardingAndRedirect();
    }
  }

  onSubmit(): void {
    this.errorMessage = '';

    const email = this.loginForm.get('email')?.value?.trim();
    const password = this.loginForm.get('password')?.value;

    if (!email) {
      this.errorMessage = 'Please enter your email address.';
      return;
    }
    if (!this.isValidEmail(email)) {
      this.errorMessage = 'Please enter a valid email address.';
      return;
    }
    if (!password) {
      this.errorMessage = 'Please enter your password.';
      return;
    }

    this.isLoading = true;
    this.sessionExpired = false;
    this.authService.login({ email, password }).subscribe({
      next: () => {
        this.checkOnboardingAndRedirect();
      },
      error: (err: any) => {
        this.isLoading = false;
        this.errorMessage = err.error?.detail || 'Incorrect email or password.';
      }
    });
  }

  private checkOnboardingAndRedirect(): void {
    this.agentService.getPlan().subscribe({
      next: (response: any) => {
        if (!response.plan) {
          // No active plan -> Redirect to setup wizard
          this.router.navigate(['/setup']);
        } else {
          // Active plan exists -> Redirect to dashboard
          this.router.navigate([this.returnUrl]);
        }
      },
      error: () => {
        // Fallback: If plan check fails, assume setup needed? 
        // Or safer to go to dashboard and let AuthGuard handle (if customized later).
        // For now, let's assume dashboard.
        this.router.navigate([this.returnUrl]);
      }
    });
  }

  private isValidEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }
}
