import { Component } from '@angular/core';
import { IntakeWizardComponent } from './intake-wizard/intake-wizard.component';

@Component({
    standalone: true,
    imports: [IntakeWizardComponent],
    template: `
    <div class="setup-layout">
      <app-intake-wizard></app-intake-wizard>
    </div>
  `,
    styles: [`
    .setup-layout {
      min-height: 100vh;
      background: #f8fafc;
    }
  `]
})
export class SetupComponent { }
