import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule],
  template: `
    <div class="auth-page">
      <div class="auth-container">
        <div class="auth-card">
          <!-- Form State -->
          <div *ngIf="!isSuccess">
            <!-- Logo -->
            <div class="logo-section">
              <div class="logo-icon">🎓</div>
              <span class="logo-text">Learning Resolution Coach</span>
            </div>

            <!-- Header -->
            <div class="auth-header">
              <h1>Create Your Account</h1>
              <p>Start your AI-powered learning journey today</p>
            </div>
          
            <form [formGroup]="registerForm" (ngSubmit)="onSubmit()" class="auth-form">
              <div class="form-field">
                <label for="full_name">Full Name</label>
                <div class="input-wrapper">
                  <span class="input-icon">👤</span>
                  <input type="text" id="full_name" formControlName="full_name" placeholder="John Doe">
                </div>
              </div>

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
                  <input type="password" id="password" formControlName="password" placeholder="Min. 8 characters">
                </div>
                <span class="field-hint">Must be at least 8 characters</span>
              </div>
              
              <div *ngIf="errorMessage" class="error-message">
                <span class="error-icon">⚠</span>
                {{ errorMessage }}
              </div>
              
              <button type="submit" [disabled]="isLoading" class="btn-primary">
                <span *ngIf="isLoading" class="spinner"></span>
                {{ isLoading ? 'Creating account...' : 'Create Account' }}
              </button>
            </form>
            
            <div class="auth-footer">
              <p>Already have an account? <a routerLink="/auth/login">Sign in</a></p>
            </div>

            <a routerLink="/" class="back-link">← Back to Home</a>
          </div>

          <!-- Success State -->
          <div *ngIf="isSuccess" class="success-container">
            <div class="success-circle">
              <svg class="checkmark" viewBox="0 0 52 52">
                <circle class="checkmark-circle" cx="26" cy="26" r="25" fill="none"/>
                <path class="checkmark-check" fill="none" d="M14.1 27.2l7.1 7.2 16.7-16.8"/>
              </svg>
            </div>
            <h2>Welcome Aboard!</h2>
            <p class="success-message">Your account has been created successfully.<br/>You're ready to start your AI learning journey.</p>
            <div class="success-features">
              <div class="feature-item"><span class="feature-icon">🎯</span> Set personalized learning goals</div>
              <div class="feature-item"><span class="feature-icon">📈</span> Track your daily progress</div>
              <div class="feature-item"><span class="feature-icon">🤖</span> Get AI-powered coaching</div>
            </div>
            <a routerLink="/auth/login" class="btn-success">Continue to Sign In</a>
          </div>
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

    .field-hint {
      font-size: 0.75rem;
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

    /* Success State */
    .success-container {
      text-align: center;
      padding: 1rem 0;
      animation: fadeIn 0.5s ease-out;
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(10px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .success-circle {
      width: 80px;
      height: 80px;
      margin: 0 auto 1.5rem;
    }

    .checkmark {
      width: 100%;
      height: 100%;
      border-radius: 50%;
      display: block;
    }

    .checkmark-circle {
      stroke-dasharray: 166;
      stroke-dashoffset: 166;
      stroke-width: 2;
      stroke-miterlimit: 10;
      stroke: #10b981;
      animation: stroke 0.6s cubic-bezier(0.65, 0, 0.45, 1) forwards;
    }

    .checkmark-check {
      transform-origin: 50% 50%;
      stroke-dasharray: 48;
      stroke-dashoffset: 48;
      stroke: #10b981;
      stroke-width: 3;
      stroke-linecap: round;
      animation: stroke 0.3s cubic-bezier(0.65, 0, 0.45, 1) 0.6s forwards;
    }

    @keyframes stroke {
      100% { stroke-dashoffset: 0; }
    }

    .success-container h2 {
      font-size: 1.75rem;
      font-weight: 700;
      color: #111827;
      margin-bottom: 0.75rem;
    }

    .success-message {
      color: #6b7280;
      font-size: 1rem;
      line-height: 1.6;
      margin-bottom: 2rem;
    }

    .success-features {
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
      background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%);
      border: 1px solid #bbf7d0;
      border-radius: 1rem;
      padding: 1.25rem;
      margin-bottom: 2rem;
    }

    .feature-item {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      font-size: 0.95rem;
      color: #166534;
      font-weight: 500;
    }

    .feature-icon {
      font-size: 1.25rem;
    }

    .btn-success {
      display: inline-block;
      padding: 1rem 2rem;
      background: linear-gradient(135deg, #10b981 0%, #059669 100%);
      color: white;
      border: none;
      border-radius: 0.75rem;
      font-weight: 600;
      font-size: 1rem;
      text-decoration: none;
      cursor: pointer;
      transition: transform 0.2s, box-shadow 0.2s;
      box-shadow: 0 4px 14px rgba(16, 185, 129, 0.3);
    }

    .btn-success:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
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
export class RegisterComponent {
  registerForm: FormGroup;
  isLoading = false;
  isSuccess = false;
  errorMessage = '';

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {
    this.registerForm = this.fb.group({
      full_name: [''],
      email: [''],
      password: ['']
    });
  }

  onSubmit(): void {
    this.errorMessage = '';

    const fullName = this.registerForm.get('full_name')?.value?.trim();
    const email = this.registerForm.get('email')?.value?.trim();
    const password = this.registerForm.get('password')?.value;

    if (!fullName) {
      this.errorMessage = 'Please enter your full name.';
      return;
    }
    if (!email) {
      this.errorMessage = 'Please enter your email address.';
      return;
    }
    if (!this.isValidEmail(email)) {
      this.errorMessage = 'Please enter a valid email address.';
      return;
    }
    if (!password) {
      this.errorMessage = 'Please enter a password.';
      return;
    }
    if (password.length < 8) {
      this.errorMessage = 'Password must be at least 8 characters long.';
      return;
    }

    this.isLoading = true;
    this.authService.register({ full_name: fullName, email, password }).subscribe({
      next: () => {
        this.isLoading = false;
        this.isSuccess = true;
      },
      error: (err: any) => {
        this.isLoading = false;
        if (err.status === 422 && err.error?.detail) {
          const details = Array.isArray(err.error.detail)
            ? err.error.detail.map((d: any) => `${d.loc.join('.')}: ${d.msg}`).join(', ')
            : err.error.detail;
          this.errorMessage = `Validation Error: ${details}`;
        } else if (err.status === 400) {
          this.errorMessage = err.error?.detail || 'Email already registered.';
        } else {
          this.errorMessage = err.error?.detail || 'An error occurred during registration.';
        }
      }
    });
  }

  private isValidEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }
}
