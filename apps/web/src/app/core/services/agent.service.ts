import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';

@Injectable({
    providedIn: 'root'
})
export class AgentService {
    constructor(private apiService: ApiService) { }

    submitIntake(data: any): Observable<any> {
        return this.apiService.post('/api/v1/intake', data);
    }

    submitPremortem(data: any): Observable<any> {
        return this.apiService.post('/api/v1/premortem', data);
    }

    getCommitment(): Observable<any> {
        // Correct endpoint found in backend routes
        return this.apiService.get('/api/v1/commitment/current');
    }

    getPlan(): Observable<any> {
        return this.apiService.get('/api/v1/plan/current');
    }

    generatePlan(force = false): Observable<any> {
        return this.apiService.post(`/api/v1/plan/weekly?force=${force}`, {});
    }

    getTodayTasks(): Observable<any> {
        return this.apiService.get('/api/v1/tasks/today');
    }

    getMetrics(): Observable<any> {
        return this.apiService.get('/api/v1/metrics/summary');
    }

    post(url: string, body: any): Observable<any> {
        return this.apiService.post(`/api/v1${url}`, body);
    }

    put(url: string, body: any): Observable<any> {
        return this.apiService.put(`/api/v1${url}`, body);
    }
}
