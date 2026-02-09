import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-plan',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <div class="p-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-6">My Learning Plan</h1>
      
      <div class="bg-white rounded-lg shadow p-12 text-center border border-gray-200">
        <div class="text-gray-400 mb-4 flex justify-center">
          <svg class="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"></path>
          </svg>
        </div>
        
        <h3 class="text-lg font-medium text-gray-900">No Active Plan</h3>
        <p class="text-gray-500 mt-2">Complete the onboarding to generate your first AI Learning Plan.</p>
        
        <button routerLink="/setup" class="mt-6 px-6 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors">
          Start Onboarding
        </button>
      </div>
    </div>
  `
})
export class PlanComponent { }