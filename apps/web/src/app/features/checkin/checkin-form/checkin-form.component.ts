import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { CheckinService, AgentDecision } from '../../../core/services/checkin.service';
import { AgentService } from '../../../core/services/agent.service';

@Component({
  selector: 'app-checkin-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  template: `
    <div class="checkin-card">
      <!-- Header -->
      <div class="card-header">
        <div class="icon-badge">📝</div>
        <h2>Daily Standup</h2>
        <p>Log your progress to get personalized advice</p>
      </div>

      <!-- Loading State -->
      <div *ngIf="isLoading" class="loading-state">
        <div class="spinner"></div>
        <p>Analyzing your progress...</p>
      </div>

      <!-- Success/Advice State -->
      <div *ngIf="decision" class="advice-state">
        <div class="advice-header">
          <div class="score-badge" [class]="decision.signals.status">
            {{ decision.signals.status | titlecase }}
          </div>
          <h3>Plan Updated</h3>
        </div>

        <div class="advice-content">
          <p class="highlight-text">{{ decision.reason }}</p>
          
          <div *ngIf="decision.advice" class="ai-insight">
            <span class="ai-icon">✨</span>
            <p>{{ decision.advice }}</p>
          </div>

          <div class="next-tasks">
            <h4>Recommended Focus</h4>
            <div *ngFor="let task of decision.next_tasks" class="task-item">
              <span class="task-icon">👉</span>
              <div class="task-details">
                <span class="task-name">{{ task.task }}</span>
                <span class="task-meta">{{ task.timebox_min }} min • {{ task.type }}</span>
              </div>
            </div>
          </div>
        </div>

        <button (click)="goToDashboard()" class="btn-primary full-width">
          Go to Dashboard
        </button>
      </div>

      <!-- Input Form -->
      <form *ngIf="!isLoading && !decision" [formGroup]="checkinForm" (ngSubmit)="onSubmit()">
        
        <!-- Yesterday -->
        <div class="form-group">
          <div class="label-row">
            <label>What did you accomplish yesterday?</label>
            <span class="date-hint">{{ yesterdayDate | date:'mediumDate' }}</span>
          </div>
          
          <!-- Smart Suggestions -->
          <div *ngIf="suggestedTasks.length > 0" class="suggestions">
            <span class="suggestion-label">Suggested from plan:</span>
            <div class="chips">
              <button *ngFor="let task of suggestedTasks" 
                      type="button" 
                      class="chip" 
                      (click)="addSuggestion(task)">
                + {{ task.task }}
              </button>
            </div>
          </div>

          <textarea 
            formControlName="yesterday" 
            placeholder="I completed the intro module..."
            rows="3"
          ></textarea>
        </div>

        <!-- Today -->
        <div class="form-group">
          <label>What is your goal for today?</label>
          <textarea 
            formControlName="today" 
            placeholder="I plan to build the..."
            rows="3"
          ></textarea>
        </div>

        <!-- Blockers -->
        <div class="form-group">
          <label>Any blockers standing in your way?</label>
          <textarea 
            formControlName="blockers" 
            placeholder="No blockers"
            rows="2"
          ></textarea>
        </div>

        <div class="form-actions">
          <button type="button" (click)="goToDashboard()" class="btn-text">Cancel</button>
          <button type="submit" [disabled]="checkinForm.invalid" class="btn-primary">
            Submit Check-in
          </button>
        </div>
      </form>
    </div>
  `,
  styles: [`
    .checkin-card {
      background: white;
      border-radius: 1.5rem;
      padding: 2.5rem;
      box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
      width: 100%;
    }

    .card-header {
      text-align: center;
      margin-bottom: 2rem;
    }

    .icon-badge {
      font-size: 2.5rem;
      margin-bottom: 1rem;
      display: inline-block;
      background: #f3f4f6;
      width: 80px;
      height: 80px;
      border-radius: 50%;
      line-height: 80px;
    }

    h2 {
      font-size: 1.75rem;
      color: #111827;
      margin-bottom: 0.5rem;
      font-weight: 700;
    }

    p {
      color: #6b7280;
    }

    /* Form Styles */
    .form-group {
      margin-bottom: 1.5rem;
    }

    label {
      display: block;
      font-weight: 600;
      color: #374151;
      margin-bottom: 0.5rem;
      font-size: 0.95rem;
    }

    textarea {
      width: 100%;
      padding: 0.875rem;
      border: 2px solid #e5e7eb;
      border-radius: 0.75rem;
      font-family: inherit;
      font-size: 1rem;
      transition: all 0.2s;
      resize: vertical;
    }

    textarea:focus {
      outline: none;
      border-color: #6366f1;
      box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1);
    }

    .form-actions {
      display: flex;
      justify-content: flex-end;
      gap: 1rem;
      margin-top: 2rem;
    }

    /* Buttons */
    .btn-primary {
      background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
      color: white;
      border: none;
      padding: 0.875rem 2rem;
      border-radius: 0.75rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s;
      box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
    }

    .btn-primary:hover:not(:disabled) {
      transform: translateY(-2px);
      box-shadow: 0 6px 16px rgba(79, 70, 229, 0.4);
    }

    .btn-primary:disabled {
      opacity: 0.7;
      cursor: not-allowed;
    }

    .btn-text {
      background: none;
      border: none;
      color: #6b7280;
      font-weight: 600;
      cursor: pointer;
      padding: 0.875rem 1rem;
    }

    .btn-text:hover {
      color: #111827;
    }

    .full-width {
      width: 100%;
      margin-top: 1.5rem;
    }

    /* Success State */
    .advice-state {
      animation: fadeIn 0.5s ease-out;
    }

    .advice-header {
      display: flex;
      align-items: center;
      gap: 1rem;
      margin-bottom: 1.5rem;
      padding-bottom: 1rem;
      border-bottom: 1px solid #e5e7eb;
    }

    .score-badge {
      padding: 0.25rem 0.75rem;
      border-radius: 99px;
      font-size: 0.875rem;
      font-weight: 600;
      text-transform: uppercase;
    }

    .score-badge.active { background: #dcfce7; color: #166534; }
    .score-badge.at_risk { background: #fee2e2; color: #991b1b; }
    .score-badge.recovering { background: #fef3c7; color: #92400e; }

    .highlight-text {
      font-size: 1.1rem;
      color: #1f2937;
      margin-bottom: 1.5rem;
      line-height: 1.6;
    }

    .ai-insight {
      background: #f5f3ff;
      border: 1px solid #ddd6fe;
      border-radius: 1rem;
      padding: 1rem;
      display: flex;
      gap: 0.75rem;
      margin-bottom: 1.5rem;
    }

    .ai-icon { font-size: 1.25rem; }

    .next-tasks h4 {
      font-size: 0.9rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: #6b7280;
      margin-bottom: 1rem;
    }

    .task-item {
      display: flex;
      gap: 0.75rem;
      background: #f9fafb;
      padding: 1rem;
      border-radius: 0.75rem;
      margin-bottom: 0.75rem;
      border: 1px solid #f3f4f6;
    }

    .task-name {
      display: block;
      font-weight: 600;
      color: #111827;
    }

    .task-meta {
      font-size: 0.85rem;
      color: #6b7280;
    }

    /* Loading */
    .loading-state {
      text-align: center;
      padding: 4rem 0;
    }

    .spinner {
      width: 40px;
      height: 40px;
      border: 3px solid #e5e7eb;
      border-top-color: #6366f1;
      border-radius: 50%;
      margin: 0 auto 1rem;
      animation: spin 1s linear infinite;
    }

    @keyframes spin { to { transform: rotate(360deg); } }
    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

    /* Suggestions */
    .label-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 0.5rem;
    }
    .date-hint {
      font-size: 0.8rem;
      color: #9ca3af;
    }
    .suggestions {
      margin-bottom: 0.75rem;
    }
    .suggestion-label {
      font-size: 0.75rem;
      color: #6b7280;
      display: block;
      margin-bottom: 0.25rem;
    }
    .chips {
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
    }
    .chip {
      background: #eef2ff;
      border: 1px solid #c7d2fe;
      color: #4f46e5;
      padding: 0.25rem 0.75rem;
      border-radius: 99px;
      font-size: 0.8rem;
      cursor: pointer;
      transition: all 0.2s;
    }
    .chip:hover {
      background: #e0e7ff;
      transform: translateY(-1px);
    }
  `]
})
export class CheckinFormComponent {
  checkinForm: FormGroup;
  isLoading = false;
  decision: AgentDecision | null = null;
  suggestedTasks: any[] = [];
  yesterdayDate = new Date();

  constructor(
    private fb: FormBuilder,
    private checkinService: CheckinService,
    private agentService: AgentService,
    private router: Router
  ) {
    // Set yesterday date
    this.yesterdayDate.setDate(this.yesterdayDate.getDate() - 1);

    this.checkinForm = this.fb.group({
      yesterday: ['', [Validators.required, Validators.minLength(3)]],
      today: ['', [Validators.required, Validators.minLength(3)]],
      blockers: ['']
    });
  }

  ngOnInit() {
    this.fetchPlanSuggestions();
  }

  fetchPlanSuggestions() {
    this.agentService.getPlan().subscribe({
      next: (data) => {
        if (data && data.plan && data.plan.schedule) {
          // Logic to find tasks for "Yesterday"
          // Assuming plan.schedule is array of days with 'date' or 'day' field
          // Simple approach: Match by date string YYYY-MM-DD
          const yStr = this.yesterdayDate.toISOString().split('T')[0];

          // Filter schedule for yesterday
          const dayPlan = data.plan.schedule.find((d: any) => d.date === yStr);
          if (dayPlan && dayPlan.tasks) {
            this.suggestedTasks = dayPlan.tasks;
          }
        }
      },
      error: (err) => console.log('Could not load plan for suggestions', err)
    });
  }

  addSuggestion(task: any) {
    const currentVal = this.checkinForm.get('yesterday')?.value || '';
    const newVal = currentVal ? `${currentVal}\n- Completed: ${task.task}` : `- Completed: ${task.task}`;
    this.checkinForm.patchValue({ yesterday: newVal });
  }

  onSubmit(): void {
    if (this.checkinForm.invalid) return;

    this.isLoading = true;
    const request = this.checkinForm.value;

    this.checkinService.submitCheckin(request).subscribe({
      next: (res) => {
        this.isLoading = false;
        this.decision = res;
      },
      error: (err) => {
        console.error('Checkin failed', err);
        this.isLoading = false;
        // Ideally show error toast
      }
    });
  }

  goToDashboard(): void {
    this.router.navigate(['/dashboard']);
  }
}
