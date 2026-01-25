import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';

export interface CheckinRequest {
    yesterday: string;
    today: string;
    blockers?: string;
}

export interface AgentDecision {
    reason: string;
    advice?: string;
    signals: {
        adherence: number;
        knowledge: number;
        retention: number;
        status: 'active' | 'at_risk' | 'recovering';
    };
    action: {
        plan_adjustment: string;
        risk_mitigation: string[];
    };
    next_tasks: Array<{
        task: string;
        timebox_min: number;
        type: string;
        priority?: number;
    }>;
    resources_used: Array<{
        title: string;
        url: string;
        relevance: number;
    }>;
}

@Injectable({
    providedIn: 'root'
})
export class CheckinService {
    constructor(private apiService: ApiService) { }

    submitCheckin(data: CheckinRequest): Observable<AgentDecision> {
        return this.apiService.post<AgentDecision>('/checkin/daily', data);
    }
}
