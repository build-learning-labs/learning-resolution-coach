/**
 * Curriculum Configuration
 * 
 * This file contains all available learning categories and tracks.
 * Edit this file to add/remove/modify curriculum options.
 */

export interface Track {
    id: string;
    label: string;
    /** Optional: Default tools/libraries for this track (used by AI Plan Generator) */
    defaultTools?: string[];
}

export interface Category {
    id: string;
    label: string;
    tracks: Track[];
}

export const CURRICULUM_CATEGORIES: Category[] = [
    {
        id: 'ai_ml',
        label: 'AI/ML Upskilling',
        tracks: [
            { id: 'ml_foundations', label: 'Machine Learning Foundations', defaultTools: ['Scikit-Learn', 'NumPy', 'Pandas'] },
            { id: 'deep_learning', label: 'Deep Learning & Neural Networks', defaultTools: ['PyTorch', 'TensorFlow'] },
            { id: 'nlp', label: 'Natural Language Processing', defaultTools: ['Hugging Face Transformers', 'spaCy'] },
            { id: 'llm_ops', label: 'LLMOps & Deployment', defaultTools: ['FastAPI', 'Docker', 'LangChain'] },
            { id: 'gen_ai', label: 'Generative AI Engineering', defaultTools: ['LangChain', 'OpenAI API', 'RAG Pipelines'] },
            { id: 'computer_vision', label: 'Computer Vision', defaultTools: ['OpenCV', 'YOLO', 'PyTorch'] },
            { id: 'other', label: 'Other AI Topic' }
        ]
    },
    {
        id: 'interview',
        label: 'Job Interview Prep',
        tracks: [
            { id: 'software_eng', label: 'Software Engineer (General)', defaultTools: ['LeetCode', 'System Design'] },
            { id: 'data_science', label: 'Data Scientist', defaultTools: ['SQL', 'Statistics', 'Python'] },
            { id: 'ml_engineer', label: 'Machine Learning Engineer', defaultTools: ['ML System Design', 'PyTorch'] },
            { id: 'frontend', label: 'Frontend Developer', defaultTools: ['React', 'TypeScript', 'CSS'] },
            { id: 'backend', label: 'Backend Developer', defaultTools: ['Node.js', 'PostgreSQL', 'REST APIs'] },
            { id: 'other', label: 'Other Role' }
        ]
    },
    {
        id: 'exam',
        label: 'Exam Certification',
        tracks: [
            { id: 'aws_sa', label: 'AWS Solutions Architect', defaultTools: ['AWS Console', 'CloudFormation'] },
            { id: 'aws_dev', label: 'AWS Developer Associate', defaultTools: ['Lambda', 'DynamoDB', 'API Gateway'] },
            { id: 'tensorflow_cert', label: 'TensorFlow Developer Certificate', defaultTools: ['TensorFlow', 'Keras'] },
            { id: 'ckad', label: 'Kubernetes Application Developer (CKAD)', defaultTools: ['kubectl', 'Helm'] },
            { id: 'az900', label: 'Azure Fundamentals (AZ-900)', defaultTools: ['Azure Portal'] },
            { id: 'other', label: 'Other Certification' }
        ]
    },
    {
        id: 'other',
        label: 'Other / Custom',
        tracks: [] // No predefined tracks for custom goals
    }
];

/**
 * Helper function to get tracks for a category
 */
export function getTracksForCategory(categoryId: string): Track[] {
    const category = CURRICULUM_CATEGORIES.find(c => c.id === categoryId);
    return category?.tracks || [];
}

/**
 * Helper function to get default tools for a track
 */
export function getDefaultToolsForTrack(categoryId: string, trackId: string): string[] {
    const tracks = getTracksForCategory(categoryId);
    const track = tracks.find(t => t.id === trackId);
    return track?.defaultTools || [];
}
