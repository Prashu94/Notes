/**
 * Configuration management for Neo4j RAG Knowledge Base VSCode Extension
 */
import * as vscode from 'vscode';

export interface Neo4jConfig {
    uri: string;
    username: string;
    password: string;
    database: string;
}

export interface OllamaConfig {
    baseUrl: string;
    embeddingModel: string;
}

export interface DocumentConfig {
    chunkSize: number;
    chunkOverlap: number;
}

export interface RAGConfig {
    retrievalK: number;
}

export class ConfigManager {
    private config: vscode.WorkspaceConfiguration;

    constructor() {
        this.config = vscode.workspace.getConfiguration('neo4jRagKb');
    }

    public refresh(): void {
        this.config = vscode.workspace.getConfiguration('neo4jRagKb');
    }

    public getNeo4jConfig(): Neo4jConfig {
        return {
            uri: this.config.get<string>('neo4j.uri', 'bolt://localhost:7687'),
            username: this.config.get<string>('neo4j.username', 'neo4j'),
            password: this.config.get<string>('neo4j.password', 'password'),
            database: this.config.get<string>('neo4j.database', 'neo4j')
        };
    }

    public getOllamaConfig(): OllamaConfig {
        return {
            baseUrl: this.config.get<string>('ollama.baseUrl', 'http://localhost:11434'),
            embeddingModel: this.config.get<string>('ollama.embeddingModel', 'nomic-embed-text')
        };
    }

    public getDocumentConfig(): DocumentConfig {
        return {
            chunkSize: this.config.get<number>('document.chunkSize', 1000),
            chunkOverlap: this.config.get<number>('document.chunkOverlap', 200)
        };
    }

    public getRAGConfig(): RAGConfig {
        return {
            retrievalK: this.config.get<number>('rag.retrievalK', 5)
        };
    }

    public async updateConfig(section: string, value: any): Promise<void> {
        await this.config.update(section, value, vscode.ConfigurationTarget.Global);
        this.refresh();
    }
}
