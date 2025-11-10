/**
 * Document loader for PDF and TXT files
 */
import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';
import { Document } from './neo4jKb';

export class DocumentLoader {
    private chunkSize: number;
    private chunkOverlap: number;

    constructor(chunkSize: number, chunkOverlap: number) {
        this.chunkSize = chunkSize;
        this.chunkOverlap = chunkOverlap;
    }

    public async loadDirectory(dirPath: string): Promise<Document[]> {
        const documents: Document[] = [];
        const files = await this.getFilesRecursively(dirPath);

        for (const filePath of files) {
            const ext = path.extname(filePath).toLowerCase();
            
            if (ext === '.txt') {
                const docs = await this.loadTextFile(filePath);
                documents.push(...docs);
            } else if (ext === '.pdf') {
                // For PDF, we'll need to use an external tool or library
                // For now, skip PDFs or show a message
                vscode.window.showWarningMessage(
                    `PDF support requires additional setup. Skipping ${path.basename(filePath)}`
                );
            }
        }

        return documents;
    }

    private async loadTextFile(filePath: string): Promise<Document[]> {
        const content = fs.readFileSync(filePath, 'utf-8');
        const fileName = path.basename(filePath);
        
        const chunks = this.splitText(content);
        
        return chunks.map((chunk, index) => ({
            content: chunk,
            metadata: {
                source: filePath,
                fileName: fileName,
                fileType: 'txt',
                chunkId: index
            }
        }));
    }

    private splitText(text: string): string[] {
        const chunks: string[] = [];
        let startIndex = 0;

        while (startIndex < text.length) {
            const endIndex = Math.min(startIndex + this.chunkSize, text.length);
            chunks.push(text.slice(startIndex, endIndex));
            startIndex += this.chunkSize - this.chunkOverlap;
        }

        return chunks;
    }

    private async getFilesRecursively(dirPath: string): Promise<string[]> {
        const files: string[] = [];
        const entries = fs.readdirSync(dirPath, { withFileTypes: true });

        for (const entry of entries) {
            const fullPath = path.join(dirPath, entry.name);
            
            if (entry.isDirectory()) {
                const subFiles = await this.getFilesRecursively(fullPath);
                files.push(...subFiles);
            } else if (entry.isFile()) {
                const ext = path.extname(entry.name).toLowerCase();
                if (ext === '.txt' || ext === '.pdf') {
                    files.push(fullPath);
                }
            }
        }

        return files;
    }
}
