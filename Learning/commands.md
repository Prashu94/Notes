brew services start postgresql@15
brew services stop postgresql@15
echo 'export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"' >> ~/.zshrc
/Volumes/MyPassport
mv ~/.ollama /Volumes/MyPassport/.ollama
ln -s /Volumes/MyPassport/.ollama ~/.ollama
export OLLAMA_HOME=/Volumes/MyPassport/.ollama
source ~/.zshrc
ollama run llama2
ollama stop llama2
brew install redis
brew services start redis
redis-server
brew services stop redis
redis-cli
# Simple POC that:
# 1) pulls rows from Postgres
# 2) renders narrative documents
# 3) embeds + stores in Chroma
# 4) answers questions with retrieval + citations

import os
import psycopg2
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.schema import Document
from langchain.chains import RetrievalQA

# 1) Extract data
conn = psycopg2.connect(os.environ["PG_DSN"])  # e.g., "postgresql://user:pass@host:5432/db"
cur = conn.cursor()
cur.execute("""
    SELECT p.id, p.name, p.category, p.description, s.stock_level, s.warehouse, pr.price, pr.currency
    FROM products p
    LEFT JOIN stock s ON s.product_id = p.id
    LEFT JOIN prices pr ON pr.product_id = p.id
    LIMIT 1000
""")
rows = cur.fetchall()
cols = [d[0] for d in cur.description]

# 2) Turn rows into readable docs
def render_product_doc(row):
    r = dict(zip(cols, row))
    return f"""
Product: {r['name']} (ID: {r['id']})
Category: {r.get('category')}
Price: {r.get('price')} {r.get('currency')}
Stock: {r.get('stock_level')} at {r.get('warehouse')}
Description: {r.get('description')}

Guidance:
- When recommending, consider category relevance and stock availability.
- For out-of-stock items, suggest similar category alternatives.
Sources: products, stock, prices tables.
""".strip()

docs = []
for row in rows:
    text = render_product_doc(row)
    metadata = {
        "table": "product_view",
        "product_id": dict(zip(cols, row))["id"],
    }
    docs.append(Document(page_content=text, metadata=metadata))

# 3) Chunk, embed, and store
splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=100)
chunks = splitter.split_documents(docs)

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")  # or Azure variant
vs = Chroma(collection_name="kb_products", embedding_function=embeddings)
vs.add_documents(chunks)

# 4) Retrieval QA with citations
retriever = vs.as_retriever(search_kwargs={"k": 5})
llm = ChatOpenAI(model="gpt-4o-mini")  # pick your model

qa = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    chain_type="stuff",
    chain_type_kwargs={
        "prompt": None  # use default, or supply a stricter grounded prompt
    },
    return_source_documents=True,
)

question = "Which mid-range products in audio category are in stock and what should agents suggest?"
result = qa({"query": question})
print("Answer:\n", result["result"])
print("\nCitations:")
for d in result["source_documents"]:
    print(d.metadata)

import os
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent

# Set PG_DSN like: postgresql+psycopg2://user:pass@host:5432/db
db = SQLDatabase.from_uri(
    os.environ["PG_DSN"],
    include_tables=["orders", "customers", "shipments"],  # whitelist
    sample_rows_in_table_info=2,  # helps the model learn value shapes
)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

agent = create_sql_agent(
    llm=llm,
    db=db,
    agent_type="openai-tools",  # tool-calling agent
    verbose=True,
    top_k=5,  # limit rows shown to the LLM in intermediate steps
)

resp = agent.invoke({"input": "How many orders were shipped last week by region?"})
print(resp["output"])  # final natural-language answer
# Optional: inspect SQL used
# print(resp["intermediate_steps"])

import os
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# SQL tool (joins happen here when needed)
db = SQLDatabase.from_uri(
    os.environ["PG_DSN"],
    include_tables=["orders", "customers", "regions"],  # whitelist
    sample_rows_in_table_info=2,
)
sql_agent = create_sql_agent(llm=llm, db=db, agent_type="openai-tools", verbose=False)

# RAG tool (explanations/policies, not numbers)
emb = OpenAIEmbeddings(model="text-embedding-3-small")
vs = Chroma(collection_name="kb_docs", embedding_function=emb)
retriever = vs.as_retriever(search_kwargs={"k": 5})
rag = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

def answer(question: str):
    needs_sql = any(w in question.lower() for w in ["how many", "count", "sum", "latest", "by region", "average", "trend", "this week", "last month"])
    if needs_sql:
        return sql_agent.invoke({"input": question})["output"]
    else:
        return rag({"query": question})["result"]

print(answer("How many orders were shipped last week by region?"))      # SQL
print(answer("What is our return policy for refurbished items?"))       # RAG


brew services start mongodb-community@8.2
brew services stop mongodb-community@8.2


brew services start neo4j
brew services list
brew services stop neo4j

sudo systemctl stop neo4j
sudo systemctl disable neo4j

rm /lib/systemd/system/neo4j.service
rm -rf NEO4J_HOME
