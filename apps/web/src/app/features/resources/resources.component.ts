import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { CURRICULUM_CATEGORIES, Category } from '../../core/config/curriculums.config';

@Component({
  selector: 'app-resources',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <div class="min-h-screen bg-gray-50">
      
      <div class="bg-white shadow-sm border-b border-gray-200">
        <div class="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8 flex justify-between items-center">
          <h1 class="text-2xl font-bold text-gray-900">Knowledge Library</h1>
          <a routerLink="/dashboard" class="text-sm text-blue-600 hover:text-blue-800 font-medium flex items-center gap-1">
            <span>←</span> Back to Dashboard
          </a>
        </div>
      </div>

      <div class="max-w-7xl mx-auto px-4 py-12 sm:px-6 lg:px-8">
        
        <div *ngFor="let category of categories" class="mb-12">
          <h2 class="text-xl font-bold text-gray-800 mb-6 border-l-4 border-blue-600 pl-4">
            {{ category.label }}
          </h2>

          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div *ngFor="let track of category.tracks" 
                 class="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow duration-200 border border-gray-100 overflow-hidden flex flex-col h-full">
              
              <div class="p-6 border-b border-gray-50">
                <h3 class="text-lg font-semibold text-gray-900">{{ track.label }}</h3>
              </div>

              <div class="p-6 bg-gray-50/50 flex-1">
                <p class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
                  Key Technologies & Concepts
                </p>
                <div class="flex flex-wrap gap-2">
                  <span *ngFor="let tool of track.defaultTools" 
                        class="px-2.5 py-1 rounded-md text-xs font-medium bg-blue-100 text-blue-700 border border-blue-200">
                    {{ tool }}
                  </span>
                </div>
              </div>

              <div class="p-4 bg-gray-50 border-t border-gray-100 text-center">
                 <a routerLink="/setup" 
                    class="text-sm font-medium text-blue-600 hover:text-blue-800 hover:underline">
                   Generate Plan for this Track →
                 </a>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  `
})
export class ResourcesComponent {
    categories: Category[] = CURRICULUM_CATEGORIES;
}
