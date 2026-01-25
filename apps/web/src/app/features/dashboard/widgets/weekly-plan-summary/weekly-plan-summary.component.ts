import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
    selector: 'app-weekly-plan-summary',
    standalone: true,
    imports: [CommonModule],
    template: `
    <div class="summary-card">
      <div class="header">
        <h3>Weekly Roadmap</h3>
        <span class="focus">{{ plan?.week_focus || 'Loading focus...' }}</span>
      </div>

      <div class="content" *ngIf="plan; else loading">
        <div class="section" *ngIf="plan.plan?.micro_project">
          <label>Micro-Project</label>
          <p>{{ plan.plan.micro_project }}</p>
        </div>

        <div class="section" *ngIf="plan.plan?.review_topics?.length > 0">
          <label>Core Concept Review</label>
          <div class="tags">
            <span *ngFor="let topic of plan.plan.review_topics" class="tag">{{ topic }}</span>
          </div>
        </div>
      </div>

      <ng-template #loading>
        <div class="skeleton-loader">
          <div class="line"></div>
          <div class="line short"></div>
        </div>
      </ng-template>
    </div>
  `,
    styles: [`
    .summary-card {
      background: white;
      padding: 1.5rem;
      border-radius: 1rem;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
      height: 100%;
    }
    .header {
      margin-bottom: 1.5rem;
    }
    .header h3 {
      font-size: 1.25rem;
      font-weight: 700;
      color: #1e293b;
      margin-bottom: 0.25rem;
    }
    .focus {
      font-size: 0.95rem;
      color: #6366f1;
      font-weight: 600;
    }
    .section {
      margin-bottom: 1.25rem;
    }
    .section label {
      display: block;
      font-size: 0.75rem;
      font-weight: 700;
      text-transform: uppercase;
      color: #94a3b8;
      letter-spacing: 0.05em;
      margin-bottom: 0.5rem;
    }
    .section p {
      font-size: 0.95rem;
      color: #334155;
      line-height: 1.5;
    }
    .tags {
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
    }
    .tag {
      background: #f1f5f9;
      color: #475569;
      padding: 0.25rem 0.75rem;
      border-radius: 0.5rem;
      font-size: 0.8rem;
      font-weight: 600;
    }
    .skeleton-loader {
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
    }
    .line {
      height: 1rem;
      background: #f1f5f9;
      border-radius: 0.25rem;
      width: 100%;
    }
    .line.short { width: 60%; }
  `]
})
export class WeeklyPlanSummaryComponent {
    @Input() plan: any;
}
