import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators, FormArray } from '@angular/forms';
import { Router } from '@angular/router';
import { AgentService } from '../../../core/services/agent.service';
import { AuthService } from '../../../core/services/auth.service';
import { CURRICULUM_CATEGORIES, getTracksForCategory, Track, getDefaultToolsForTrack } from '../../../core/config/curriculums.config';

// Angular Material Datepicker
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';

import { StrictDateInputDirective } from '../../../shared/directives/strict-date-input.directive';

@Component({
  selector: 'app-intake-wizard',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, MatDatepickerModule, MatNativeDateModule, MatInputModule, MatFormFieldModule, StrictDateInputDirective],
  template: `
    <div class="wizard-container">
      <div class="header-actions">
        <button (click)="logout()" class="btn-text">Logout</button>
      </div>
      <div class="wizard-card">
        <div class="wizard-steps">
          <div [class.active]="currentStep >= 1" class="step">1. Goal</div>
          <div [class.active]="currentStep >= 2" class="step">2. Schedule</div>
          <div [class.active]="currentStep >= 3" class="step">3. Premortem</div>
          <div [class.active]="currentStep >= 4" class="step">4. Review</div>
        </div>

        <div class="wizard-content">
          <!-- Step 1: Goal & Level -->
          <div *ngIf="currentStep === 1">
            <h2>Define Your Learning Goal</h2>
            <p>Tell us what you want to master and where you're starting from.</p>
            <form [formGroup]="goalForm" class="step-form">
              
              <!-- Category Dropdown -->
              <div class="form-field">
                <label for="category">Learning Category</label>
                <select id="category" formControlName="category" (change)="onCategoryChange()">
                  <option value="" disabled>Select a category</option>
                  <option *ngFor="let cat of categories" [value]="cat.id">{{ cat.label }}</option>
                </select>
              </div>

              <!-- Track Dropdown (Dynamic) -->
              <div class="form-field" *ngIf="availableTracks.length > 0">
                <label for="track">Specific Track</label>
                <select id="track" formControlName="track" (change)="onTrackChange()">
                  <option value="" disabled>Select a track</option>
                  <option *ngFor="let track of availableTracks" [value]="track.id">{{ track.label }}</option>
                </select>
              </div>

              <!-- Other / Custom Goal Textarea -->
              <div class="form-field" *ngIf="showCustomGoal">
                <label for="goal">Describe Your Goal</label>
                <textarea id="goal" formControlName="goal" placeholder="e.g., I want to build a custom RAG pipeline for legal documents using Open Source models."></textarea>
              </div>

              <div class="form-field">
                <label for="target_date">Target Completion Date</label>
                <mat-form-field appearance="outline" class="date-field">
                  <input matInput 
                         [matDatepicker]="picker" 
                         formControlName="target_date" 
                         [min]="minDate"
                         placeholder="MM/DD/YYYY"
                         appStrictDateInput>
                  <mat-datepicker-toggle matIconSuffix [for]="picker"></mat-datepicker-toggle>
                  <mat-datepicker #picker></mat-datepicker>
                </mat-form-field>
              </div>
              <div class="form-field">
                <label for="baseline_level">Current level</label>
                <select id="baseline_level" formControlName="baseline_level">
                  <option value="beginner">Beginner</option>
                  <option value="intermediate">Intermediate</option>
                  <option value="advanced">Advanced</option>
                </select>
              </div>

              <!-- Optional: Preferred Tooling (for advanced users) -->
              <div class="form-field">
                <label for="preferred_tooling">Preferred Tools/Libraries (Optional)</label>
                <input type="text" id="preferred_tooling" formControlName="preferred_tooling" placeholder="e.g., PyTorch, TensorFlow, LangChain">
                <span class="field-hint">Leave blank to use recommended defaults.</span>
              </div>
              <button (click)="nextStep()" [disabled]="goalForm.invalid" class="btn-primary">Next: Schedule</button>
            </form>
          </div>

          <!-- Step 2: Schedule & Style -->
          <div *ngIf="currentStep === 2">
            <h2>Your Learning Commitment</h2>
            <p>How much time can you dedicate and how do you learn best?</p>
            <form [formGroup]="scheduleForm" class="step-form">
              <div class="form-field">
                <label for="weekly_hours">Hours per week (1-40)</label>
                <input type="number" id="weekly_hours" formControlName="weekly_hours" min="1" max="40">
              </div>
              <div class="form-field">
                <label for="learning_style">Preferred Learning Style</label>
                <select id="learning_style" formControlName="learning_style">
                  <option value="mixed">Mixed (Reading + Coding)</option>
                  <option value="coding">Coding-First (Practical)</option>
                  <option value="reading">Reading-First (Theoretical)</option>
                </select>
              </div>
              <div class="btn-group">
                <button (click)="prevStep()" class="btn-secondary">Back</button>
                <button (click)="nextStep()" [disabled]="scheduleForm.invalid" class="btn-primary">Next: Risks</button>
              </div>
            </form>
          </div>

          <!-- Step 3: Premortem -->
          <div *ngIf="currentStep === 3">
            <h2>The Premortem</h2>
            <p>"Imagine 4 weeks from now you failed. Why did it happen?"</p>
            <div class="field-hint" style="margin-bottom: 1rem;">
              Common reasons: 
              <span class="chip" (click)="addExample('Getting too busy with work')">Work Stress</span>
              <span class="chip" (click)="addExample('Losing motivation after week 1')">Loss of Interest</span>
              <span class="chip" (click)="addExample('Struggling with difficult concepts')">Too Hard</span>
            </div>

            <form [formGroup]="premortemForm" class="step-form">
              <div formArrayName="failure_reasons">
                <div *ngFor="let reason of failureReasons.controls; let i=index" class="reason-field">
                  <input [formControlName]="i" placeholder="e.g., I binged Netflix instead of studying">
                  <button type="button" (click)="removeReason(i)" class="btn-icon" *ngIf="failureReasons.length > 1">×</button>
                </div>
              </div>
              <button type="button" (click)="addReason()" class="btn-text">+ Add Another Reason</button>
              
              <div class="btn-group">
                <button type="button" (click)="prevStep()" class="btn-secondary">Back</button>
                <button type="button" (click)="nextStep()" [disabled]="premortemForm.invalid || premortemForm.pristine" class="btn-primary">Next: Review</button>
              </div>
            </form>
          </div>

          <!-- Step 4: Review -->
          <div *ngIf="currentStep === 4">
            <h2>Commitment Contract</h2>
            <p>Review your information before generating your plan.</p>
            <div class="summary">
              <div class="summary-item"><strong>Goal:</strong> {{ getGoalDisplay() }}</div>
              <div class="summary-item"><strong>Date:</strong> {{ goalForm.value.target_date }}</div>
              <div class="summary-item"><strong>Commitment:</strong> {{ scheduleForm.value.weekly_hours }} hrs/week</div>
              <div class="summary-item"><strong>Style:</strong> {{ scheduleForm.value.learning_style }}</div>
              <div class="summary-item">
                <strong>Potential Obstacles:</strong>
                <ul>
                  <li *ngFor="let r of premortemForm.value.failure_reasons">{{ r }}</li>
                </ul>
              </div>
            </div>
            
            <div *ngIf="errorMessage" class="error-message">{{ errorMessage }}</div>
            
            <div class="btn-group">
              <button (click)="prevStep()" class="btn-secondary">Back</button>
              <button (click)="submit()" [disabled]="isLoading" class="btn-primary">
                {{ isLoading ? 'Generating Plan...' : 'Sign Contract & Generate Plan' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .wizard-container {
      display: flex;
      justify-content: center;
      padding: 2rem 1rem;
    }
    .wizard-card {
      background: white;
      padding: 2.5rem;
      border-radius: 1.5rem;
      box-shadow: 0 10px 25px rgba(0,0,0,0.05);
      width: 100%;
      max-width: 650px;
    }
    .wizard-steps {
      display: flex;
      gap: 1rem;
      margin-bottom: 2.5rem;
      border-bottom: 1px solid #edf2f7;
      padding-bottom: 1rem;
    }
    .step {
      font-size: 0.875rem;
      font-weight: 600;
      color: #cbd5e0;
      flex: 1;
      text-align: center;
    }
    .step.active {
      color: #4f46e5;
    }
    .wizard-content h2 {
      font-size: 1.5rem;
      color: #2d3748;
      margin-bottom: 0.5rem;
    }
    .wizard-content p {
      color: #718096;
      margin-bottom: 2rem;
    }
    .step-form {
      display: flex;
      flex-direction: column;
      gap: 1.5rem;
    }
    .form-field {
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
    }
    .form-field label {
      font-weight: 600;
      font-size: 0.9rem;
      color: #4a5568;
    }
    .form-field input, .form-field select, .form-field textarea {
      padding: 0.75rem 1rem;
      border: 1px solid #e2e8f0;
      border-radius: 0.75rem;
      font-size: 1rem;
    }
    .form-field textarea {
      height: 100px;
      resize: vertical;
    }
    .reason-field {
      display: flex;
      gap: 0.5rem;
      margin-bottom: 0.75rem;
    }
    .reason-field input {
      flex: 1;
      padding: 0.75rem;
      border: 1px solid #e2e8f0;
      border-radius: 0.5rem;
    }
    .btn-icon {
      background: #f7fafc;
      border: 1px solid #e2e8f0;
      border-radius: 0.5rem;
      width: 40px;
      font-size: 1.25rem;
      cursor: pointer;
    }
    .btn-text {
      background: none;
      border: none;
      color: #4f46e5;
      font-weight: 600;
      cursor: pointer;
      text-align: left;
      padding: 0;
      margin-bottom: 1.5rem;
    }
    .btn-group {
      display: flex;
      gap: 1rem;
      margin-top: 1rem;
    }
    .btn-primary {
      padding: 0.875rem 1.5rem;
      background: #4f46e5;
      color: white;
      border: none;
      border-radius: 0.75rem;
      font-weight: 600;
      cursor: pointer;
    }
    .btn-secondary {
      padding: 0.875rem 1.5rem;
      background: #f7fafc;
      color: #4a5568;
      border: 1px solid #e2e8f0;
      border-radius: 0.75rem;
      font-weight: 600;
      cursor: pointer;
    }
    .summary {
      background: #f8fafc;
      padding: 1.5rem;
      border-radius: 1rem;
      margin-bottom: 1.5rem;
    }
    .summary-item {
      margin-bottom: 0.75rem;
      font-size: 0.95rem;
    }
    .field-hint {
      font-size: 0.75rem;
      color: #9ca3af;
      margin-top: 0.25rem;
    }
    .date-field {
      width: 100%;
    }
    .date-field .mat-mdc-form-field-infix {
      padding: 0.75rem 0;
    }
    .chip {
      display: inline-block;
      padding: 0.25rem 0.75rem;
      background: #e0e7ff;
      color: #4338ca;
      border-radius: 1rem;
      font-size: 0.75rem;
      font-weight: 600;
      margin-right: 0.5rem;
      cursor: pointer;
      transition: background 0.2s;
    }
    .chip:hover {
      background: #c7d2fe;
    }
    .error-message {
      color: #dc2626;
      background: #fef2f2;
      padding: 0.75rem;
      border-radius: 0.5rem;
      margin-bottom: 1rem;
    }
  `]
})
export class IntakeWizardComponent {
  currentStep = 1;
  isLoading = false;
  errorMessage = '';

  // Minimum date for datepicker (today - only future dates allowed)
  minDate = new Date();

  goalForm: FormGroup;
  scheduleForm: FormGroup;
  premortemForm: FormGroup;

  // Use external configuration
  categories = CURRICULUM_CATEGORIES;
  availableTracks: Track[] = [];
  showCustomGoal = false;

  constructor(
    private fb: FormBuilder,
    private agentService: AgentService,
    private authService: AuthService,
    private router: Router
  ) {
    this.goalForm = this.fb.group({
      category: ['', Validators.required],
      track: [''],
      goal: ['', Validators.required], // This stores the final text sent to backend
      target_date: ['', Validators.required],
      baseline_level: ['beginner', Validators.required],
      preferred_tooling: [''] // Optional input for advanced users
    });

    this.scheduleForm = this.fb.group({
      weekly_hours: [10, [Validators.required, Validators.min(1), Validators.max(40)]],
      learning_style: ['mixed', Validators.required]
    });

    this.premortemForm = this.fb.group({
      failure_reasons: this.fb.array([
        this.fb.control('', Validators.required)
      ])
    });
  }

  get failureReasons() {
    return this.premortemForm.get('failure_reasons') as FormArray;
  }

  addReason() {
    this.failureReasons.push(this.fb.control('', Validators.required));
  }

  removeReason(index: number) {
    this.failureReasons.removeAt(index);
  }

  logout() {
    this.authService.logout();
  }

  // Pre-fill premortem example
  addExample(text: string) {
    // Fill the first control if empty, or add a new one
    const firstControl = this.failureReasons.at(0);
    if (firstControl && !firstControl.value) {
      firstControl.setValue(text);
      firstControl.markAsDirty(); // Enables the button
    } else {
      this.failureReasons.push(this.fb.control(text, Validators.required));
      this.premortemForm.markAsDirty();
    }
  }

  // Handle Category Selection
  onCategoryChange() {
    const category = this.goalForm.get('category')?.value;

    // Reset track and goal
    this.goalForm.patchValue({ track: '', goal: '' });
    this.showCustomGoal = false;

    if (category === 'other') {
      this.availableTracks = [];
      this.showCustomGoal = true;
      this.goalForm.get('track')?.clearValidators();
    } else {
      this.availableTracks = getTracksForCategory(category);
      this.goalForm.get('track')?.setValidators(Validators.required);
    }

    this.goalForm.get('track')?.updateValueAndValidity();
  }

  // Handle Track Selection
  onTrackChange() {
    const category = this.goalForm.get('category')?.value;
    const trackId = this.goalForm.get('track')?.value;

    if (trackId === 'other') {
      this.showCustomGoal = true;
      this.goalForm.patchValue({ goal: '' });
    } else {
      this.showCustomGoal = false;
      // Auto-populate the goal for the backend
      const categoryLabel = this.categories.find(c => c.id === category)?.label;
      const trackLabel = this.availableTracks.find(t => t.id === trackId)?.label;
      this.goalForm.patchValue({ goal: `${categoryLabel} - ${trackLabel}` });
    }
  }

  getGoalDisplay(): string {
    return this.goalForm.get('goal')?.value;
  }

  nextStep() {
    if (this.currentStep < 4) this.currentStep++;
  }

  prevStep() {
    if (this.currentStep > 1) this.currentStep--;
  }

  submit() {
    this.isLoading = true;
    this.errorMessage = '';

    // Prepare intake data for backend
    let goalText = this.goalForm.get('goal')?.value;
    const preferredTools = this.goalForm.get('preferred_tooling')?.value?.trim();

    // Append tooling preference to goal if user specified any
    if (preferredTools) {
      goalText = `${goalText}. Preferred Tools: ${preferredTools}.`;
    }

    // Material Datepicker returns a Date object; convert to ISO string for backend
    const targetDateValue = this.goalForm.get('target_date')?.value;
    let targetDateStr = '';
    if (targetDateValue instanceof Date) {
      targetDateStr = targetDateValue.toISOString().split('T')[0]; // YYYY-MM-DD
    } else {
      targetDateStr = targetDateValue; // Already a string (fallback)
    }

    const intakeData = {
      goal: goalText,
      target_date: targetDateStr,
      baseline_level: this.goalForm.get('baseline_level')?.value,
      ...this.scheduleForm.value
    };

    const premortemData = {
      failure_reasons: this.premortemForm.value.failure_reasons
    };

    // Chain the calls: Intake -> Premortem -> Generate Plan
    this.agentService.submitIntake(intakeData).subscribe({
      next: () => {
        this.agentService.submitPremortem(premortemData).subscribe({
          next: () => {
            // Generate initial plan
            this.agentService.generatePlan().subscribe({
              next: () => {
                this.router.navigate(['/dashboard']);
              },
              error: (err: any) => this.handleError(err)
            });
          },
          error: (err: any) => this.handleError(err)
        });
      },
      error: (err: any) => this.handleError(err)
    });
  }

  private handleError(err: any) {
    this.isLoading = false;
    this.errorMessage = err.error?.detail || 'An error occurred. Please try again.';
  }
}
