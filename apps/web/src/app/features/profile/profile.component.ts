import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="p-8">
      <h1 class="text-2xl font-bold text-gray-900 mb-6">User Profile</h1>
      <div class="bg-white shadow rounded-lg p-6 border border-gray-200">
        <div class="flex items-center gap-4 mb-6">
          <div class="w-16 h-16 bg-gray-200 rounded-full flex items-center justify-center text-gray-500 text-xl font-bold">
            U
          </div>
          <div>
            <h2 class="text-lg font-bold text-gray-900">User Name</h2>
            <p class="text-sm text-gray-500">user&#64;example.com</p>
          </div>
        </div>
        <p class="text-gray-600">Profile settings are coming soon.</p>
      </div>
    </div>
  `
})
export class ProfileComponent { }
