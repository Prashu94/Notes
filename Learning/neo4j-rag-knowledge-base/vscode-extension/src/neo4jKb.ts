/**
 * Neo4j Knowledge Base Manager
 */
import neo4j, { Driver, Session } from 'neo4j-driver';
import { OllamaEmbeddings } from './ollamaProvider';

export interface Document {
    content: string;
    metadata: {
        source?: string;
        fileName?: string;
        fileType?: string;
        chunkId?: number;
        [key: string]: any;
    };
}

export class Neo4jKnowledgeBase {
    private driver: Driver;
    private database: string;
    private embeddings: OllamaEmbeddings;

    constructor(
        uri: string,
        username: string,
        password: string,
        database: string,
        embeddings: OllamaEmbeddings
    ) {
        this.driver = neo4j.driver(uri, neo4j.auth.basic(username, password));
        this.database = database;
        this.embeddings = embeddings;
    }

    public async testConnection(): Promise<boolean> {
        const session = this.driver.session({ database: this.database });
        try {
            await session.run('RETURN 1');
            return true;
        } catch (error) {
            return false;
        } finally {
            await session.close();
        }
    }

    public async createIndexes(): Promise<void> {
        const session = this.driver.session({ database: this.database });
        try {
            // Create vector index
            try {
                await session.run(`
                    CREATE VECTOR INDEX document_embeddings IF NOT EXISTS
                    FOR (d:Document)
                    ON d.embedding
                    OPTIONS {indexConfig: {
                        \`vector.dimensions\`: 768,
                        \`vector.similarity_function\`: 'cosine'
                    }}
                `);
            } catch (error) {
                // Index might already exist
            }

            // Create full-text index
            try {
                await session.run(`
                    CREATE FULLTEXT INDEX document_content IF NOT EXISTS
                    FOR (d:Document)
                    ON EACH [d.content]
                `);
            } catch (error) {
                // Index might already exist
            }

            // Create constraint
            try {
                await session.run(`
                    CREATE CONSTRAINT document_id IF NOT EXISTS
                    FOR (d:Document)
                    REQUIRE d.id IS UNIQUE
                `);
            } catch (error) {
                // Constraint might already exist
            }
        } finally {
            await session.close();
        }
    }

    public async addDocuments(documents: Document[]): Promise<void> {
        const session = this.driver.session({ database: this.database });
        
        try {
            for (const doc of documents) {
                // Generate embedding
                const embedding = await this.embeddings.embedText(doc.content);
                
                // Add document to Neo4j
                await session.run(`
                    CREATE (d:Document {
                        id: randomUUID(),
                        content: $content,
                        embedding: $embedding,
                        source: $source,
                        fileName: $fileName,
                        fileType: $fileType,
                        chunkId: $chunkId
                    })
                `, {
                    content: doc.content,
                    embedding: embedding,
                    source: doc.metadata.source || '',
                    fileName: doc.metadata.fileName || '',
                    fileType: doc.metadata.fileType || '',
                    chunkId: doc.metadata.chunkId || 0
                });

                // Create file relationship if source exists
                if (doc.metadata.source) {
                    await session.run(`
                        MERGE (f:File {path: $source})
                        SET f.name = $fileName,
                            f.type = $fileType
                        WITH f
                        MATCH (d:Document {content: $content})
                        MERGE (d)-[:FROM_FILE]->(f)
                    `, {
                        source: doc.metadata.source,
                        fileName: doc.metadata.fileName || '',
                        fileType: doc.metadata.fileType || '',
                        content: doc.content
                    });
                }
            }
        } finally {
            await session.close();
        }
    }

    public async similaritySearch(query: string, k: number = 5): Promise<Document[]> {
        const session = this.driver.session({ database: this.database });
        
        try {
            // Generate query embedding
            const queryEmbedding = await this.embeddings.embedText(query);
            
            // Perform vector similarity search
            const result = await session.run(`
                MATCH (d:Document)
                WITH d, gds.similarity.cosine(d.embedding, $queryEmbedding) AS score
                RETURN d.content AS content,
                       d.source AS source,
                       d.fileName AS fileName,
                       d.fileType AS fileType,
                       d.chunkId AS chunkId,
                       score
                ORDER BY score DESC
                LIMIT $k
            `, {
                queryEmbedding: queryEmbedding,
                k: neo4j.int(k)
            });

            return result.records.map(record => ({
                content: record.get('content'),
                metadata: {
                    source: record.get('source'),
                    fileName: record.get('fileName'),
                    fileType: record.get('fileType'),
                    chunkId: record.get('chunkId'),
                    score: record.get('score')
                }
            }));
        } finally {
            await session.close();
        }
    }

    public async getDocumentCount(): Promise<number> {
        const session = this.driver.session({ database: this.database });
        
        try {
            const result = await session.run('MATCH (d:Document) RETURN count(d) as count');
            return result.records[0].get('count').toNumber();
        } finally {
            await session.close();
        }
    }

    public async deleteAllDocuments(): Promise<void> {
        const session = this.driver.session({ database: this.database });
        
        try {
            await session.run('MATCH (n) DETACH DELETE n');
        } finally {
            await session.close();
        }
    }

    public async close(): Promise<void> {
        await this.driver.close();
    }
}
