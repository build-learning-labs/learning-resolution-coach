import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-today-tasks-widget',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="widget-card">
      <div class="widget-header">
        <h3>Today's Learning Path</h3>
        <span class="date">{{ today | date:'mediumDate' }}</span>
      </div>

      <div class="task-list" *ngIf="tasks.length > 0; else noTasks">
        <div *ngFor="let task of tasks" class="task-item" [class.completed]="task.status === 'completed'">
          <div class="task-info">
            <span class="task-type" [class]="task.type">{{ task.type }}</span>
            <p class="task-desc">{{ task.task }}</p>
            <span class="timebox">{{ task.timebox_min }} min</span>
          </div>
          <div class="task-actions">
            <button 
              (click)="onStartActivity(task.task)" 
              class="btn-start"
              *ngIf="task.status !== 'completed'"
            >
              Start
            </button>
            <button 
              (click)="onToggleStatus(task.id)" 
              class="status-toggle"
              [class.active]="task.status === 'completed'"
            >
              {{ task.status === 'completed' ? '✓ Done' : 'Complete' }}
            </button>
          </div>
        </div>
      </div>

      <ng-template #noTasks>
        <div class="empty-state">
          <p>No tasks scheduled for today. Enjoy your rest or plan ahead!</p>
        </div>
      </ng-template>
    </div>
  `,
  styles: [`
    .widget-card {
      background: white;
      border-radius: 1rem;
      padding: 1.5rem;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .widget-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1.5rem;
    }
    .widget-header h3 {
      font-size: 1.25rem;
      font-weight: 700;
      color: #1e293b;
    }
    .date {
      font-size: 0.875rem;
      color: #64748b;
    }
    .task-list {
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }
    .task-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 1rem;
      border-radius: 0.75rem;
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      transition: all 0.2s;
    }
    .task-item.completed {
      background: #f0fdf4;
      border-color: #bbf7d0;
    }
    .task-info {
      flex: 1;
    }
    .task-type {
      font-size: 0.7rem;
      font-weight: 700;
      text-transform: uppercase;
      padding: 0.2rem 0.5rem;
      border-radius: 9999px;
      margin-bottom: 0.5rem;
      display: inline-block;
    }
    .task-type.reading { background: #dcfce7; color: #166534; }
    .task-type.coding { background: #dbeafe; color: #1e40af; }
    .task-type.review { background: #fef9c3; color: #854d0e; }
    
    .task-desc {
      font-weight: 600;
      color: #334155;
      margin: 0.25rem 0;
    }
    .timebox {
      font-size: 0.8rem;
      color: #64748b;
    }
    .task-actions {
      display: flex;
      gap: 0.5rem;
      align-items: center;
    }
    .btn-start {
      padding: 0.5rem 1rem;
      border-radius: 0.5rem;
      font-weight: 600;
      font-size: 0.875rem;
      cursor: pointer;
      border: none;
      background: #6366f1;
      color: white;
      transition: all 0.2s;
    }
    .btn-start:hover {
      background: #4f46e5;
      transform: translateY(-1px);
    }
    .status-toggle {
      padding: 0.5rem 1rem;
      border-radius: 0.5rem;
      font-weight: 600;
      font-size: 0.875rem;
      cursor: pointer;
      border: 1px solid #e2e8f0;
      background: white;
      transition: all 0.2s;
    }
    .status-toggle:hover {
      background: #f1f5f9;
    }
    .status-toggle.active {
      background: #22c55e;
      color: white;
      border-color: #22c55e;
    }
    .empty-state {
      text-align: center;
      padding: 2rem;
      color: #64748b;
    }
  `]
})
export class TodayTasksWidgetComponent {
  @Input() tasks: any[] = [];
  @Output() taskToggle = new EventEmitter<number>();
  today = new Date();

  onToggleStatus(id: number) {
    this.taskToggle.emit(id);
  }

  onStartActivity(taskName: string) {
    // Smart activity start: Open a search for the task
    const query = encodeURIComponent(taskName);
    window.open(`https://www.youtube.com/results?search_query=${query}`, '_blank');
  }
}
