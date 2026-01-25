import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet } from '@angular/router';

@Component({
    selector: 'app-checkin-layout',
    standalone: true,
    imports: [CommonModule, RouterOutlet],
    template: `
    <div class="checkin-container">
      <!-- Premium Background Steps -->
      <div class="background-shapes">
        <div class="shape shape-1"></div>
        <div class="shape shape-2"></div>
      </div>

      <!-- Main Content Area -->
      <div class="content-wrapper">
        <router-outlet></router-outlet>
      </div>
    </div>
  `,
    styles: [`
    .checkin-container {
      min-height: 100vh;
      width: 100%;
      background: linear-gradient(135deg, #f8fafc 0%, #eff6ff 100%);
      position: relative;
      overflow: hidden;
      display: flex;
      justify-content: center;
      align-items: center;
      padding: 1rem;
    }

    .content-wrapper {
      position: relative;
      z-index: 10;
      width: 100%;
      max-width: 600px;
      animation: slideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1);
    }

    @keyframes slideUp {
      from { opacity: 0; transform: translateY(20px); }
      to { opacity: 1; transform: translateY(0); }
    }

    /* Ambient Background Shapes */
    .background-shapes {
      position: absolute;
      inset: 0;
      overflow: hidden;
      pointer-events: none;
    }

    .shape {
      position: absolute;
      border-radius: 50%;
      filter: blur(80px);
      opacity: 0.6;
    }

    .shape-1 {
      width: 400px;
      height: 400px;
      background: rgba(99, 102, 241, 0.2); /* Indigo */
      top: -100px;
      right: -100px;
      animation: float 15s infinite ease-in-out;
    }

    .shape-2 {
      width: 300px;
      height: 300px;
      background: rgba(139, 92, 246, 0.2); /* Purple */
      bottom: -50px;
      left: -50px;
      animation: float 20s infinite ease-in-out reverse;
    }

    @keyframes float {
      0%, 100% { transform: translate(0, 0); }
      50% { transform: translate(30px, -30px); }
    }
  `]
})
export class CheckinLayoutComponent { }
