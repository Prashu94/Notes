/**
 * RAG System with GitHub Copilot Chat integration
 */
import * as vscode from 'vscode';
import { Neo4jKnowledgeBase, Document } from './neo4jKb';

export class RAGSystem {
    private kb: Neo4jKnowledgeBase;
    private retrievalK: number;

    constructor(kb: Neo4jKnowledgeBase, retrievalK: number) {
        this.kb = kb;
        this.retrievalK = retrievalK;
    }

    public async query(question: string): Promise<{ answer: string; sources: Document[] }> {
        // Retrieve relevant documents
        const documents = await this.kb.similaritySearch(question, this.retrievalK);

        if (documents.length === 0) {
            return {
                answer: "I couldn't find any relevant information in the knowledge base.",
                sources: []
            };
        }

        // Format context for Copilot
        const context = this.formatContext(documents);

        // Use GitHub Copilot Chat API to generate answer
        const answer = await this.generateAnswerWithCopilot(question, context);

        return {
            answer: answer,
            sources: documents
        };
    }

    private formatContext(documents: Document[]): string {
        const contextParts: string[] = [];

        documents.forEach((doc, index) => {
            const header = `Document ${index + 1} (Source: ${doc.metadata.fileName || 'Unknown'})`;
            contextParts.push(`${header}:\n${doc.content}\n`);
        });

        return contextParts.join('\n---\n');
    }

    private async generateAnswerWithCopilot(question: string, context: string): Promise<string> {
        // Create a prompt for GitHub Copilot
        const prompt = `You are a helpful AI assistant that answers questions based on the provided context from a knowledge base.

Context from knowledge base:
${context}

Question: ${question}

Instructions:
1. Answer the question based ONLY on the information provided in the context above
2. If the context doesn't contain enough information, say "I don't have enough information in the knowledge base to answer this question"
3. Provide specific references to the source documents when possible
4. Be concise but comprehensive in your answer

Answer:`;

        try {
            // Use VS Code language model API with GitHub Copilot
            const models = await vscode.lm.selectChatModels({
                vendor: 'copilot',
                family: 'gpt-4'
            });

            if (models.length === 0) {
                return "GitHub Copilot is not available. Please ensure GitHub Copilot Pro is enabled.";
            }

            const model = models[0];
            const messages = [
                vscode.LanguageModelChatMessage.User(prompt)
            ];

            const response = await model.sendRequest(messages, {}, new vscode.CancellationTokenSource().token);

            let answer = '';
            for await (const chunk of response.text) {
                answer += chunk;
            }

            return answer.trim();
        } catch (error) {
            return `Error generating answer with Copilot: ${error}`;
        }
    }

    public async openChatPanel(): Promise<void> {
        const panel = vscode.window.createWebviewPanel(
            'neo4jRagChat',
            'Neo4j RAG Chat',
            vscode.ViewColumn.Two,
            {
                enableScripts: true,
                retainContextWhenHidden: true
            }
        );

        panel.webview.html = this.getChatWebviewContent();

        // Handle messages from the webview
        panel.webview.onDidReceiveMessage(
            async message => {
                switch (message.command) {
                    case 'query':
                        const result = await this.query(message.text);
                        panel.webview.postMessage({
                            command: 'response',
                            answer: result.answer,
                            sources: result.sources
                        });
                        break;
                }
            },
            undefined,
            []
        );
    }

    private getChatWebviewContent(): string {
        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Neo4j RAG Chat</title>
    <style>
        body {
            font-family: var(--vscode-font-family);
            color: var(--vscode-foreground);
            background-color: var(--vscode-editor-background);
            padding: 20px;
            margin: 0;
        }
        #chat-container {
            max-width: 800px;
            margin: 0 auto;
        }
        #messages {
            height: 500px;
            overflow-y: auto;
            border: 1px solid var(--vscode-panel-border);
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 5px;
        }
        .message {
            margin-bottom: 15px;
            padding: 10px;
            border-radius: 5px;
        }
        .user-message {
            background-color: var(--vscode-input-background);
            text-align: right;
        }
        .assistant-message {
            background-color: var(--vscode-editor-inactiveSelectionBackground);
        }
        .sources {
            margin-top: 10px;
            padding: 10px;
            background-color: var(--vscode-textBlockQuote-background);
            border-left: 3px solid var(--vscode-textBlockQuote-border);
            font-size: 0.9em;
        }
        #input-container {
            display: flex;
            gap: 10px;
        }
        #query-input {
            flex: 1;
            padding: 10px;
            background-color: var(--vscode-input-background);
            color: var(--vscode-input-foreground);
            border: 1px solid var(--vscode-input-border);
            border-radius: 3px;
        }
        #send-button {
            padding: 10px 20px;
            background-color: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border: none;
            border-radius: 3px;
            cursor: pointer;
        }
        #send-button:hover {
            background-color: var(--vscode-button-hoverBackground);
        }
    </style>
</head>
<body>
    <div id="chat-container">
        <h1>Neo4j RAG Knowledge Base Chat</h1>
        <div id="messages"></div>
        <div id="input-container">
            <input type="text" id="query-input" placeholder="Ask a question..." />
            <button id="send-button">Send</button>
        </div>
    </div>

    <script>
        const vscode = acquireVsCodeApi();
        const messagesDiv = document.getElementById('messages');
        const queryInput = document.getElementById('query-input');
        const sendButton = document.getElementById('send-button');

        function addMessage(text, isUser) {
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message ' + (isUser ? 'user-message' : 'assistant-message');
            messageDiv.textContent = text;
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

        function addSources(sources) {
            if (sources && sources.length > 0) {
                const sourcesDiv = document.createElement('div');
                sourcesDiv.className = 'sources';
                sourcesDiv.innerHTML = '<strong>Sources:</strong><br>' + 
                    sources.map((s, i) => \`[\${i+1}] \${s.metadata.fileName || 'Unknown'}\`).join('<br>');
                messagesDiv.appendChild(sourcesDiv);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }
        }

        function sendQuery() {
            const query = queryInput.value.trim();
            if (query) {
                addMessage(query, true);
                vscode.postMessage({ command: 'query', text: query });
                queryInput.value = '';
            }
        }

        sendButton.addEventListener('click', sendQuery);
        queryInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendQuery();
            }
        });

        window.addEventListener('message', event => {
            const message = event.data;
            if (message.command === 'response') {
                addMessage(message.answer, false);
                addSources(message.sources);
            }
        });
    </script>
</body>
</html>`;
    }
}
