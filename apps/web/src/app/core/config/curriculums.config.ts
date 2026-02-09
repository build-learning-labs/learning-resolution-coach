/**
 * Curriculum Configuration
 * Updated: 2026 Holistic AI Strategy (Technical + Human Skills)
 */

export interface Track {
    id: string;
    label: string;
    defaultTools?: string[];
}

export interface Category {
    id: string;
    label: string;
    tracks: Track[];
}

export const CURRICULUM_CATEGORIES: Category[] = [
    {
        id: 'holistic_ai_2026',  // REMOVED: ikigai_2026
        label: 'Holistic AI Strategy (2026)', // REMOVED: Ikigai
        tracks: [
            // --- TECHNICAL SKILLS ---
            {
                id: 'tech_agentic',
                label: 'Technical: Agentic Design Patterns',
                defaultTools: ['LangGraph', 'CrewAI', 'AutoGen', 'DSPy']
            },
            {
                id: 'tech_edge',
                label: 'Technical: Edge AI & Privacy',
                defaultTools: ['Ollama', 'MLX', 'ExecuTorch', 'Phi-3']
            },
            {
                id: 'tech_evals',
                label: 'Technical: AI Red Teaming & Evals',
                defaultTools: ['Ragas', 'Garak', 'Arize Phoenix', 'LangSmith']
            },

            // --- HUMAN SKILLS ---
            {
                id: 'non_tech_ethics',
                label: 'Human: AI Governance & Ethics',
                defaultTools: ['EU AI Act', 'NIST RMF', 'Bias Auditing']
            },
            {
                id: 'non_tech_product',
                label: 'Human: AI Product Management',
                defaultTools: ['Jobs-to-be-Done', 'Trust Calibration', 'UX Patterns']
            },
            {
                id: 'non_tech_mind',
                label: 'Human: Cognitive Resilience',
                defaultTools: ['Deep Work', 'Second Brain', 'Dopamine Detox']
            }
        ]
    },
    // Keep a standard category for fallback
    {
        id: 'standard_ml',
        label: 'Standard Machine Learning',
        tracks: [
            { id: 'ml_foundations', label: 'ML Foundations', defaultTools: ['Scikit-Learn'] },
            { id: 'deep_learning', label: 'Deep Learning', defaultTools: ['PyTorch'] },
        ]
    }
];

export function getTracksForCategory(categoryId: string): Track[] {
    const category = CURRICULUM_CATEGORIES.find(c => c.id === categoryId);
    return category?.tracks || [];
}

export function getDefaultToolsForTrack(categoryId: string, trackId: string): string[] {
    const tracks = getTracksForCategory(categoryId);
    const track = tracks.find(t => t.id === trackId);
    return track?.defaultTools || [];
}