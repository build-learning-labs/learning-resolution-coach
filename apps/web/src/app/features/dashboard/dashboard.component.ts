import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { AgentService } from '../../core/services/agent.service';
import { TodayTasksWidgetComponent } from './widgets/today-tasks/today-tasks.component';
import { ProgressOverviewComponent } from './widgets/progress-overview/progress-overview.component';
import { WeeklyPlanSummaryComponent } from './widgets/weekly-plan-summary/weekly-plan-summary.component';
import { forkJoin, of } from 'rxjs';
import { catchError } from 'rxjs/operators';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    TodayTasksWidgetComponent,
    ProgressOverviewComponent,
    WeeklyPlanSummaryComponent
  ],
  template: `
    <div class="dashboard-container">
      
      <header class="content-header">
        <div>
          <h1>Dashboard</h1>
          <p>Track your learning progress and daily tasks.</p>
        </div>
        <button (click)="loadData()" class="btn-refresh" [disabled]="isLoading" [class.loading]="isLoading">
          <span class="refresh-icon">↻</span> {{ isLoading ? 'Loading...' : 'Refresh' }}
        </button>
      </header>

      <div *ngIf="errorMessage" class="error-banner">
        <span>⚠️ {{ errorMessage }}</span>
        <button (click)="loadData()" class="btn-retry">Retry</button>
      </div>

      <div *ngIf="hasPlanFailure" class="error-state-card">
        <div class="error-icon">⚠️</div>
        <h2>Plan Generation Failed</h2>
        <p>We saved your goal, but the AI couldn't generate your plan (likely due to a connection timeout).</p>
        <div class="action-buttons">
          <button (click)="retryPlan()" class="btn-retry-primary" [disabled]="isLoading">
            {{ isLoading ? 'Retrying...' : 'Retry Generation' }}
          </button>
          <button (click)="deleteCommitment()" class="btn-text-danger">Cancel & Start Over</button>
        </div>
      </div>

      <div *ngIf="isLoading && !hasData && !hasPlanFailure" class="loading-state">
        <div class="spinner"></div>
        <p>Loading your dashboard...</p>
      </div>

      <div *ngIf="!isLoading && !currentPlan && !currentCommitment && !errorMessage && !hasPlanFailure" class="empty-state">
        <div class="empty-icon">📋</div>
        <h2>No Learning Plan Yet</h2>
        <p>Complete your intake to get a personalized learning plan.</p>
        <a routerLink="/setup" class="btn-primary">Start Setup</a>
      </div>

      <section *ngIf="hasData && !errorMessage" class="dashboard-grid">
        <div class="full-width">
          <app-progress-overview [metrics]="metrics"></app-progress-overview>
        </div>
        
        <div class="main-col">
          <app-today-tasks-widget 
            [tasks]="todayTasks" 
            (taskToggle)="onToggleTask($event)"
          ></app-today-tasks-widget>
        </div>

        <div class="side-col">
          <app-weekly-plan-summary [plan]="currentPlan"></app-weekly-plan-summary>
        </div>
      </section>

    </div>
  `,
  styles: [`
    :host {
      display: block;
      width: 100%;
    }

    .dashboard-container {
      padding: 2rem;
      max-width: 1400px;
      margin: 0 auto;
    }

    .content-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 2.5rem;
    }
    .content-header h1 { font-size: 2.25rem; margin-bottom: 0.5rem; color: #0f172a; font-weight: 700; }
    .content-header p { color: #64748b; font-size: 1.1rem; }
    
    .btn-refresh {
      background: white;
      border: 1px solid #e2e8f0;
      padding: 0.6rem 1.2rem;
      border-radius: 0.5rem;
      font-weight: 600;
      color: #64748b;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      transition: all 0.2s;
    }
    .btn-refresh:hover { background: #f8fafc; color: #4f46e5; border-color: #cbd5e1; }
    .btn-refresh.loading .refresh-icon { animation: spin 1s linear infinite; display: inline-block; }
    @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

    .dashboard-grid {
      display: grid;
      grid-template-columns: 2fr 1fr;
      gap: 2rem;
    }
    .full-width { grid-column: span 2; }

    /* Error Banner */
    .error-banner {
      background: #fef2f2;
      border: 1px solid #fecaca;
      border-radius: 0.75rem;
      padding: 1rem 1.5rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1.5rem;
      color: #dc2626;
    }
    .btn-retry {
      background: #dc2626;
      color: white;
      border: none;
      padding: 0.5rem 1rem;
      border-radius: 0.5rem;
      cursor: pointer;
      font-weight: 600;
    }

    /* Loading State */
    .loading-state {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 6rem;
      color: #64748b;
    }
    .spinner {
      width: 40px;
      height: 40px;
      border: 3px solid #e2e8f0;
      border-top-color: #4f46e5;
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin-bottom: 1rem;
    }

    /* Empty State */
    .empty-state {
      text-align: center;
      padding: 5rem 2rem;
      background: white;
      border-radius: 1rem;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
      border: 1px solid #e2e8f0;
    }
    .empty-icon { font-size: 3.5rem; margin-bottom: 1.5rem; display: block; }
    .empty-state h2 { color: #1e293b; margin-bottom: 0.75rem; font-size: 1.5rem; }
    .empty-state p { color: #64748b; margin-bottom: 2rem; max-width: 400px; margin-left: auto; margin-right: auto; }
    .empty-state .btn-primary {
      display: inline-block;
      padding: 0.875rem 2rem;
      background: #4f46e5;
      color: white;
      border-radius: 0.75rem;
      text-decoration: none;
      font-weight: 600;
      transition: background 0.2s;
    }
    .empty-state .btn-primary:hover { background: #4338ca; }
    
    @media (max-width: 1024px) {
      .dashboard-grid { grid-template-columns: 1fr; }
      .full-width { grid-column: span 1; }
      .content-header { flex-direction: column; gap: 1rem; }
      .btn-refresh { width: 100%; justify-content: center; }
    }

    /* Failed State Card */
    .error-state-card {
      text-align: center;
      padding: 3rem;
      background: white;
      border: 1px solid #fecaca;
      border-radius: 1rem;
      margin-bottom: 2rem;
      box-shadow: 0 4px 6px -1px rgba(220, 38, 38, 0.1);
    }
    .error-icon { font-size: 3rem; margin-bottom: 1rem; }
    .error-state-card h2 { color: #b91c1c; margin-bottom: 0.5rem; }
    .error-state-card p { color: #7f1d1d; margin-bottom: 1.5rem; }
    .action-buttons {
      display: flex;
      gap: 1rem;
      justify-content: center;
      align-items: center;
    }
    .btn-retry-primary {
      background: #dc2626;
      color: white;
      border: none;
      padding: 0.75rem 1.5rem;
      border-radius: 0.5rem;
      font-weight: 600;
      cursor: pointer;
    }
    .btn-text-danger {
      background: none;
      border: none;
      color: #dc2626;
      font-weight: 600;
      cursor: pointer;
      text-decoration: underline;
    }
  `]
})
export class DashboardComponent implements OnInit {
  isLoading = false;
  errorMessage = '';

  todayTasks: any[] = [];
  metrics: any = {};
  currentPlan: any = null;
  currentCommitment: any = null;

  get hasData(): boolean {
    return this.currentPlan !== null || this.todayTasks.length > 0;
  }

  // Smart check: If commitment exists but plan is missing, generation failed.
  get hasPlanFailure(): boolean {
    return !!this.currentCommitment && !this.currentPlan && !this.isLoading;
  }

  constructor(private agentService: AgentService) {}

  ngOnInit(): void {
    this.loadData();
  }

  loadData(): void {
    this.isLoading = true;
    this.errorMessage = '';

    forkJoin({
      // Wrap in catchError to allow partial loading if needed, 
      // though here we mostly treat as a group.
      tasks: this.agentService.getTodayTasks().pipe(catchError(() => of({ tasks: [] }))),
      metrics: this.agentService.getMetrics().pipe(catchError(() => of({}))),
      plan: this.agentService.getPlan().pipe(catchError(() => of(null))),
      commitment: this.agentService.getCommitment().pipe(catchError(() => of(null)))
    }).subscribe({
      next: (res) => {
        this.todayTasks = res.tasks?.tasks || [];
        this.metrics = res.metrics || {};
        this.currentPlan = res.plan || null;
        this.currentCommitment = res.commitment || null;
        this.isLoading = false;
      },
      error: (err: any) => {
        this.isLoading = false;
        this.errorMessage = 'Failed to load dashboard data. Please refresh.';
        console.error('Dashboard load error', err);
      }
    });
  }

  // Manually retry generation
  retryPlan() {
    this.isLoading = true;
    this.agentService.generatePlan(true).subscribe({
      next: () => {
        this.loadData(); // Reload everything on success
      },
      error: (err) => {
        this.isLoading = false;
        this.errorMessage = 'Plan generation failed again. Please check AI service status.';
      }
    });
  }

  // For "Start Over" - clear the bad state
  deleteCommitment() {
    // In a real app: DELETE /api/v1/intake
    // For now, redirecting to setup to overwrite is acceptable for MVP
    window.location.href = '/setup';
  }

  onToggleTask(taskId: number): void {
    // Optimistic update
    const task = this.todayTasks.find(t => t.id === taskId);
    if (task) {
      const originalStatus = task.status;
      task.status = task.status === 'completed' ? 'pending' : 'completed';

      this.agentService.put(`/tasks/${taskId}/complete`, {}).subscribe({
        error: () => {
          // Revert on error
          task.status = originalStatus;
        },
        next: () => {
          // Refresh metrics to show update without full reload
          this.agentService.getMetrics().subscribe(m => this.metrics = m);
        }
      });
    }
  }
}
