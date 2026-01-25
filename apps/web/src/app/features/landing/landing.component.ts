import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

@Component({
    selector: 'app-landing',
    standalone: true,
    imports: [CommonModule, RouterModule],
    template: `
    <div class="landing-page">
      <!-- Header -->
      <header class="landing-header">
        <div class="logo">
          <span class="logo-icon">🎓</span>
          <span class="logo-text">Learning Resolution Coach</span>
        </div>
        <nav class="nav-links">
          <a routerLink="/auth/login" class="nav-link">Sign In</a>
          <a routerLink="/auth/register" class="btn-primary-small">Get Started Free</a>
        </nav>
      </header>

      <!-- Hero Section -->
      <section class="hero-section">
        <div class="hero-content">
          <h1 class="hero-title">Turn Learning Goals into Clear, Achievable Plans</h1>
          <p class="hero-subtitle">
            Your AI-powered coach to help you set goals, stay consistent, and make real learning progress.
          </p>
        </div>
        <div class="hero-mockup">
          <div class="mockup-card">
            <div class="mockup-header">
              <span class="greeting">Your AI Learning Dashboard</span>
              <span class="greeting-sub">Track progress and stay on course</span>
            </div>
            <div class="mockup-progress">
              <span class="progress-label">Weekly Learning Plan</span>
              <div class="progress-bar-container">
                <div class="progress-bar" style="width: 57%"></div>
              </div>
              <span class="progress-percent">57%</span>
            </div>
            <div class="mockup-tasks">
              <h4>Today's Tasks</h4>
              <div class="task-item"><span class="task-check">☑</span> Complete Neural Networks module</div>
              <div class="task-item"><span class="task-check">☐</span> Practice with TensorFlow basics</div>
              <div class="task-item"><span class="task-check">☐</span> Review ML model evaluation</div>
            </div>
            <div class="mockup-reflect">
              <span>💡 Reflect: What's one thing you learned today?</span>
            </div>
          </div>
          <!-- Floating decorations -->
          <div class="floating-deco deco-1">💡</div>
          <div class="floating-deco deco-2">📈</div>
          <div class="floating-deco deco-3">⭐</div>
        </div>
      </section>

      <!-- Tagline Section -->
      <section class="tagline-section">
        <p>Your AI-powered coach to help you transform intentions into structured learning paths.</p>
      </section>
    </div>
  `,
    styles: [`
    .landing-page {
      min-height: 100vh;
      background: linear-gradient(180deg, #f8f9fc 0%, #eef1f8 100%);
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Header */
    .landing-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 1.5rem 4rem;
      max-width: 1400px;
      margin: 0 auto;
    }

    .logo {
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }

    .logo-icon {
      font-size: 1.5rem;
    }

    .logo-text {
      font-weight: 600;
      font-size: 1.1rem;
      color: #1f2937;
    }

    .nav-links {
      display: flex;
      align-items: center;
      gap: 1.5rem;
    }

    .nav-link {
      color: #4b5563;
      text-decoration: none;
      font-weight: 500;
      font-size: 0.95rem;
      transition: color 0.2s;
    }

    .nav-link:hover {
      color: #6366f1;
    }

    .btn-primary-small {
      padding: 0.6rem 1.25rem;
      background: #6366f1;
      color: white;
      border-radius: 0.5rem;
      text-decoration: none;
      font-weight: 600;
      font-size: 0.9rem;
      transition: background 0.2s, transform 0.2s;
    }

    .btn-primary-small:hover {
      background: #4f46e5;
      transform: translateY(-1px);
    }

    /* Hero Section */
    .hero-section {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 4rem 4rem 2rem;
      max-width: 1400px;
      margin: 0 auto;
      gap: 4rem;
    }

    .hero-content {
      flex: 1;
      max-width: 500px;
    }

    .hero-title {
      font-size: 3rem;
      font-weight: 700;
      color: #111827;
      line-height: 1.15;
      margin-bottom: 1.5rem;
    }

    .hero-subtitle {
      font-size: 1.15rem;
      color: #6b7280;
      line-height: 1.7;
      margin-bottom: 2rem;
    }

    .hero-cta {
      display: flex;
      gap: 1rem;
    }

    .btn-primary {
      padding: 0.9rem 1.75rem;
      background: #6366f1;
      color: white;
      border-radius: 0.75rem;
      text-decoration: none;
      font-weight: 600;
      font-size: 1rem;
      transition: background 0.2s, transform 0.2s, box-shadow 0.2s;
      box-shadow: 0 4px 14px rgba(99, 102, 241, 0.3);
    }

    .btn-primary:hover {
      background: #4f46e5;
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4);
    }

    .btn-secondary {
      padding: 0.9rem 1.75rem;
      background: white;
      color: #374151;
      border: 1px solid #d1d5db;
      border-radius: 0.75rem;
      text-decoration: none;
      font-weight: 600;
      font-size: 1rem;
      transition: background 0.2s, border-color 0.2s;
    }

    .btn-secondary:hover {
      background: #f9fafb;
      border-color: #9ca3af;
    }

    /* Mockup Card */
    .hero-mockup {
      flex: 1;
      position: relative;
      display: flex;
      justify-content: center;
    }

    .mockup-card {
      background: white;
      border-radius: 1.25rem;
      padding: 1.75rem;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.15);
      width: 100%;
      max-width: 380px;
      position: relative;
      z-index: 1;
    }

    .mockup-header {
      margin-bottom: 1.5rem;
    }

    .greeting {
      display: block;
      font-weight: 600;
      font-size: 1.1rem;
      color: #111827;
    }

    .greeting-sub {
      display: block;
      font-size: 0.85rem;
      color: #9ca3af;
      margin-top: 0.25rem;
    }

    .mockup-progress {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      margin-bottom: 1.5rem;
    }

    .progress-label {
      font-size: 0.85rem;
      font-weight: 500;
      color: #374151;
      white-space: nowrap;
    }

    .progress-bar-container {
      flex: 1;
      height: 8px;
      background: #e5e7eb;
      border-radius: 4px;
      overflow: hidden;
    }

    .progress-bar {
      height: 100%;
      background: linear-gradient(90deg, #6366f1 0%, #a78bfa 100%);
      border-radius: 4px;
    }

    .progress-percent {
      font-size: 0.85rem;
      font-weight: 600;
      color: #6366f1;
    }

    .mockup-tasks h4 {
      font-size: 0.9rem;
      font-weight: 600;
      color: #374151;
      margin-bottom: 0.75rem;
    }

    .task-item {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      padding: 0.5rem 0;
      font-size: 0.85rem;
      color: #4b5563;
      border-bottom: 1px solid #f3f4f6;
    }

    .task-item:last-child {
      border-bottom: none;
    }

    .task-check {
      font-size: 1rem;
    }

    .mockup-reflect {
      margin-top: 1.25rem;
      padding: 0.75rem;
      background: #fef3c7;
      border-radius: 0.5rem;
      font-size: 0.8rem;
      color: #92400e;
    }

    /* Floating Decorations */
    .floating-deco {
      position: absolute;
      font-size: 1.5rem;
      animation: float 3s ease-in-out infinite;
    }

    .deco-1 {
      top: -20px;
      left: 20px;
      animation-delay: 0s;
    }

    .deco-2 {
      top: 20%;
      right: -10px;
      animation-delay: 0.5s;
    }

    .deco-3 {
      bottom: 10%;
      left: -15px;
      animation-delay: 1s;
    }

    @keyframes float {
      0%, 100% { transform: translateY(0); }
      50% { transform: translateY(-10px); }
    }

    /* Tagline Section */
    .tagline-section {
      text-align: center;
      padding: 3rem 2rem;
      max-width: 700px;
      margin: 0 auto;
    }

    .tagline-section p {
      font-size: 1.15rem;
      color: #4b5563;
      line-height: 1.7;
    }

    /* Responsive */
    @media (max-width: 900px) {
      .hero-section {
        flex-direction: column;
        text-align: center;
        padding: 2rem;
      }

      .hero-content {
        max-width: 100%;
      }

      .hero-title {
        font-size: 2.25rem;
      }

      .hero-cta {
        justify-content: center;
      }

      .hero-mockup {
        margin-top: 2rem;
      }

      .landing-header {
        padding: 1rem 1.5rem;
      }
    }
  `]
})
export class LandingComponent { }
