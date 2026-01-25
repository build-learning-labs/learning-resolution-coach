import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
    selector: 'app-progress-overview',
    standalone: true,
    imports: [CommonModule],
    template: `
    <div class="metrics-grid">
      <div class="metric-card">
        <span class="label">Adherence</span>
        <div class="value-row">
          <span class="value">{{ metrics.adherence_score * 100 | number:'1.0-0' }}%</span>
          <div class="progress-bg">
            <div class="progress-fill adherence" [style.width.%]="metrics.adherence_score * 100"></div>
          </div>
        </div>
        <p class="hint">Consistency in completing tasks</p>
      </div>

      <div class="metric-card">
        <span class="label">Knowledge</span>
        <div class="value-row">
          <span class="value">{{ metrics.knowledge_score * 100 | number:'1.0-0' }}%</span>
          <div class="progress-bg">
            <div class="progress-fill knowledge" [style.width.%]="metrics.knowledge_score * 100"></div>
          </div>
        </div>
        <p class="hint">Performance in quiz evaluations</p>
      </div>

      <div class="metric-card">
        <span class="label">Status</span>
        <div class="status-badge" [class]="metrics.status">
          {{ metrics.status | uppercase }}
        </div>
        <p class="hint">Current motivation standing</p>
      </div>

      <div class="metric-card secondary">
        <span class="label">Timeline</span>
        <div class="timeline-row">
          <span class="week">Week {{ metrics.current_week }}</span>
          <span class="remaining">{{ metrics.weeks_remaining }} weeks left</span>
        </div>
      </div>
    </div>
  `,
    styles: [`
    .metrics-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 1.5rem;
      margin-bottom: 2rem;
    }
    .metric-card {
      background: white;
      padding: 1.5rem;
      border-radius: 1rem;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
    }
    .metric-card.secondary {
      background: #f8fafc;
      box-shadow: none;
      border: 1px solid #e2e8f0;
    }
    .label {
      font-size: 0.875rem;
      font-weight: 600;
      color: #64748b;
    }
    .value-row {
      display: flex;
      align-items: center;
      gap: 1rem;
    }
    .value {
      font-size: 1.5rem;
      font-weight: 700;
      color: #1e293b;
      min-width: 3.5rem;
    }
    .progress-bg {
      flex: 1;
      height: 8px;
      background: #f1f5f9;
      border-radius: 9999px;
      overflow: hidden;
    }
    .progress-fill {
      height: 100%;
      border-radius: 9999px;
      transition: width 0.5s ease-out;
    }
    .progress-fill.adherence { background: #4f46e5; }
    .progress-fill.knowledge { background: #06b6d4; }
    
    .status-badge {
      display: inline-block;
      padding: 0.25rem 0.75rem;
      border-radius: 9999px;
      font-size: 0.875rem;
      font-weight: 700;
      text-align: center;
      width: fit-content;
    }
    .status-badge.active { background: #dcfce7; color: #166534; }
    .status-badge.at_risk { background: #fef2f2; color: #991b1b; }
    .status-badge.recovering { background: #fff7ed; color: #9a3412; }

    .hint {
      font-size: 0.75rem;
      color: #94a3b8;
    }
    .timeline-row {
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      margin-top: 0.5rem;
    }
    .week {
      font-size: 1.25rem;
      font-weight: 700;
      color: #1e293b;
    }
    .remaining {
      font-size: 0.875rem;
      color: #64748b;
    }
  `]
})
export class ProgressOverviewComponent {
    @Input() metrics: any = {
        adherence_score: 0,
        knowledge_score: 0,
        retention_score: 0,
        status: 'active',
        current_week: 1,
        weeks_remaining: 0
    };
}
