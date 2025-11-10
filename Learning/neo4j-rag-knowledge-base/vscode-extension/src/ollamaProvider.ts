/**
 * Ollama integration for embeddings
 */
import axios from 'axios';

export interface EmbeddingResponse {
    embedding: number[];
}

export class OllamaEmbeddings {
    private baseUrl: string;
    private model: string;

    constructor(baseUrl: string, model: string) {
        this.baseUrl = baseUrl;
        this.model = model;
    }

    public async embedText(text: string): Promise<number[]> {
        try {
            const response = await axios.post<EmbeddingResponse>(
                `${this.baseUrl}/api/embeddings`,
                {
                    model: this.model,
                    prompt: text
                },
                {
                    timeout: 60000 // 60 second timeout
                }
            );

            return response.data.embedding;
        } catch (error) {
            throw new Error(`Failed to generate embedding: ${error}`);
        }
    }

    public async embedDocuments(texts: string[]): Promise<number[][]> {
        const embeddings: number[][] = [];
        
        for (const text of texts) {
            const embedding = await this.embedText(text);
            embeddings.push(embedding);
        }

        return embeddings;
    }

    public async checkHealth(): Promise<boolean> {
        try {
            await axios.get(`${this.baseUrl}/api/tags`);
            return true;
        } catch (error) {
            return false;
        }
    }

    public async listModels(): Promise<string[]> {
        try {
            const response = await axios.get(`${this.baseUrl}/api/tags`);
            return response.data.models.map((m: any) => m.name);
        } catch (error) {
            throw new Error(`Failed to list models: ${error}`);
        }
    }

    public async ensureModel(): Promise<boolean> {
        try {
            const models = await this.listModels();
            const modelExists = models.some(m => m.startsWith(this.model));
            
            if (modelExists) {
                return true;
            }

            // Pull model if it doesn't exist
            console.log(`Pulling model: ${this.model}`);
            await axios.post(`${this.baseUrl}/api/pull`, {
                name: this.model
            });

            return true;
        } catch (error) {
            console.error(`Failed to ensure model: ${error}`);
            return false;
        }
    }
}
