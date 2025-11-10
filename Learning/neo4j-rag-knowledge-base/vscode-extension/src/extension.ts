/**
 * Main extension entry point
 */
import * as vscode from 'vscode';
import { ConfigManager } from './config';
import { OllamaEmbeddings } from './ollamaProvider';
import { Neo4jKnowledgeBase } from './neo4jKb';
import { DocumentLoader } from './documentLoader';
import { RAGSystem } from './ragSystem';

let knowledgeBase: Neo4jKnowledgeBase | undefined;
let ragSystem: RAGSystem | undefined;
let configManager: ConfigManager;

export function activate(context: vscode.ExtensionContext) {
    console.log('Neo4j RAG Knowledge Base extension is now active');

    configManager = new ConfigManager();

    // Register commands
    context.subscriptions.push(
        vscode.commands.registerCommand('neo4j-rag-kb.initializeKB', initializeKnowledgeBase)
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('neo4j-rag-kb.loadDocuments', loadDocuments)
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('neo4j-rag-kb.queryKB', queryKnowledgeBase)
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('neo4j-rag-kb.openChat', openChatInterface)
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('neo4j-rag-kb.clearKB', clearKnowledgeBase)
    );
}

async function initializeKnowledgeBase() {
    try {
        vscode.window.showInformationMessage('Initializing Neo4j Knowledge Base...');

        const neo4jConfig = configManager.getNeo4jConfig();
        const ollamaConfig = configManager.getOllamaConfig();

        // Initialize Ollama embeddings
        const embeddings = new OllamaEmbeddings(
            ollamaConfig.baseUrl,
            ollamaConfig.embeddingModel
        );

        // Check Ollama health
        const ollamaHealthy = await embeddings.checkHealth();
        if (!ollamaHealthy) {
            vscode.window.showErrorMessage(
                'Cannot connect to Ollama. Please ensure Ollama is running at ' + ollamaConfig.baseUrl
            );
            return;
        }

        // Ensure embedding model exists
        await embeddings.ensureModel();

        // Initialize Neo4j knowledge base
        knowledgeBase = new Neo4jKnowledgeBase(
            neo4jConfig.uri,
            neo4jConfig.username,
            neo4jConfig.password,
            neo4jConfig.database,
            embeddings
        );

        // Test Neo4j connection
        const neo4jHealthy = await knowledgeBase.testConnection();
        if (!neo4jHealthy) {
            vscode.window.showErrorMessage(
                'Cannot connect to Neo4j. Please check your connection settings.'
            );
            return;
        }

        // Create indexes
        await knowledgeBase.createIndexes();

        // Initialize RAG system
        const ragConfig = configManager.getRAGConfig();
        ragSystem = new RAGSystem(knowledgeBase, ragConfig.retrievalK);

        vscode.window.showInformationMessage('Knowledge Base initialized successfully!');
    } catch (error) {
        vscode.window.showErrorMessage(`Failed to initialize Knowledge Base: ${error}`);
    }
}

async function loadDocuments() {
    if (!knowledgeBase) {
        vscode.window.showWarningMessage('Please initialize the Knowledge Base first.');
        return;
    }

    try {
        // Ask user to select a folder
        const folderUri = await vscode.window.showOpenDialog({
            canSelectFiles: false,
            canSelectFolders: true,
            canSelectMany: false,
            openLabel: 'Select Documents Folder'
        });

        if (!folderUri || folderUri.length === 0) {
            return;
        }

        const folderPath = folderUri[0].fsPath;

        vscode.window.showInformationMessage(`Loading documents from ${folderPath}...`);

        // Load documents
        const documentConfig = configManager.getDocumentConfig();
        const loader = new DocumentLoader(
            documentConfig.chunkSize,
            documentConfig.chunkOverlap
        );

        const documents = await loader.loadDirectory(folderPath);

        if (documents.length === 0) {
            vscode.window.showWarningMessage('No supported documents found in the selected folder.');
            return;
        }

        // Add documents to knowledge base
        await vscode.window.withProgress(
            {
                location: vscode.ProgressLocation.Notification,
                title: 'Adding documents to Knowledge Base',
                cancellable: false
            },
            async (progress) => {
                await knowledgeBase!.addDocuments(documents);
            }
        );

        const count = await knowledgeBase.getDocumentCount();
        vscode.window.showInformationMessage(
            `Successfully loaded ${documents.length} document chunks. Total documents in KB: ${count}`
        );
    } catch (error) {
        vscode.window.showErrorMessage(`Failed to load documents: ${error}`);
    }
}

async function queryKnowledgeBase() {
    if (!ragSystem) {
        vscode.window.showWarningMessage('Please initialize the Knowledge Base first.');
        return;
    }

    try {
        const question = await vscode.window.showInputBox({
            prompt: 'Enter your question',
            placeHolder: 'What would you like to know?'
        });

        if (!question) {
            return;
        }

        vscode.window.showInformationMessage('Querying Knowledge Base...');

        const result = await ragSystem.query(question);

        // Show result in a new document
        const doc = await vscode.workspace.openTextDocument({
            content: `Question: ${question}\n\n` +
                    `Answer:\n${result.answer}\n\n` +
                    `Sources:\n${result.sources.map((s, i) => 
                        `[${i+1}] ${s.metadata.fileName || 'Unknown'}: ${s.content.substring(0, 100)}...`
                    ).join('\n')}`,
            language: 'markdown'
        });

        await vscode.window.showTextDocument(doc);
    } catch (error) {
        vscode.window.showErrorMessage(`Query failed: ${error}`);
    }
}

async function openChatInterface() {
    if (!ragSystem) {
        vscode.window.showWarningMessage('Please initialize the Knowledge Base first.');
        return;
    }

    try {
        await ragSystem.openChatPanel();
    } catch (error) {
        vscode.window.showErrorMessage(`Failed to open chat interface: ${error}`);
    }
}

async function clearKnowledgeBase() {
    if (!knowledgeBase) {
        vscode.window.showWarningMessage('Knowledge Base is not initialized.');
        return;
    }

    const confirm = await vscode.window.showWarningMessage(
        'Are you sure you want to clear all documents from the Knowledge Base?',
        'Yes', 'No'
    );

    if (confirm === 'Yes') {
        try {
            await knowledgeBase.deleteAllDocuments();
            vscode.window.showInformationMessage('Knowledge Base cleared successfully.');
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to clear Knowledge Base: ${error}`);
        }
    }
}

export function deactivate() {
    if (knowledgeBase) {
        knowledgeBase.close();
    }
}
