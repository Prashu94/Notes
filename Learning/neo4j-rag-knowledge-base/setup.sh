#!/bin/bash

# Setup script for Neo4j RAG Knowledge Base

set -e

echo "=========================================="
echo "Neo4j RAG Knowledge Base Setup"
echo "=========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

echo "✅ Docker is installed"

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker Compose is installed"

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "⚠️  Ollama is not installed. Please install Ollama from https://ollama.ai"
    echo "   After installation, run: ollama pull llama3.2 && ollama pull nomic-embed-text"
else
    echo "✅ Ollama is installed"
fi

# Setup Python environment
echo ""
echo "Setting up Python environment..."
cd langchain-python

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python 3 is installed"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment and install dependencies
echo "Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Python dependencies installed"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env file and set your Neo4j password"
else
    echo "✅ .env file already exists"
fi

cd ..

# Start Neo4j with Docker Compose
echo ""
echo "Starting Neo4j database..."
docker-compose up -d

echo ""
echo "Waiting for Neo4j to be ready..."
sleep 10

# Check if Neo4j is running
if docker ps | grep -q neo4j-rag-kb; then
    echo "✅ Neo4j is running"
    echo ""
    echo "Neo4j Browser: http://localhost:7474"
    echo "Neo4j Bolt: bolt://localhost:7687"
    echo "Default credentials: neo4j / password"
else
    echo "❌ Failed to start Neo4j"
    exit 1
fi

# Pull Ollama models if Ollama is installed
if command -v ollama &> /dev/null; then
    echo ""
    echo "Checking Ollama models..."
    
    if ! ollama list | grep -q "llama3.2"; then
        echo "Pulling llama3.2 model (this may take a while)..."
        ollama pull llama3.2
    else
        echo "✅ llama3.2 model is available"
    fi
    
    if ! ollama list | grep -q "nomic-embed-text"; then
        echo "Pulling nomic-embed-text model..."
        ollama pull nomic-embed-text
    else
        echo "✅ nomic-embed-text model is available"
    fi
fi

echo ""
echo "=========================================="
echo "Setup Complete! 🎉"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit langchain-python/.env and set your Neo4j password"
echo "2. Activate Python environment: cd langchain-python && source venv/bin/activate"
echo "3. Load documents: python main.py --mode load --documents ../sample-data"
echo "4. Query knowledge base: python main.py --mode query --question 'What is RAG?'"
echo "5. Start chat: python main.py --mode chat"
echo ""
echo "For VSCode extension:"
echo "1. cd vscode-extension"
echo "2. npm install"
echo "3. Press F5 to launch extension development host"
echo ""
