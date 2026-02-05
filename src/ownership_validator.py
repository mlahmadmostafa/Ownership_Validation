"""
Ownership Validator
-------------------
If you can't explain the system, then you don't own it.
This script generates a 30-question quiz from a given code file to help developers understand and "own" the code.
It uses Llama Index with Ollama for both LLM and Embeddings.
"""

import argparse
import sys
import os
import yaml
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.llms.openai import OpenAI
# from llama_index.embeddings.ollama import OllamaEmbedding # Removed for BM25
from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import Settings
from llama_index.core.schema import Document

# Default Constants
DEFAULT_LLM_MODEL = "z-ai/glm-4.7-flash:free"
DEFAULT_EMBEDDING_MODEL = "ollama/embeddinggemma:300m-qat-q4_0"
DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"

def setup_llama_index(llm_model: str, embedding_model: str, api_key: str = None, base_url: str = None):
    """Configures Llama Index with a Generic OpenAI-compatible LLM and Ollama Embeddings."""
    print(f"Setting up Llama Index with LLM='{llm_model}' and Embeddings='{embedding_model}'...")
    
    # Setup LLM (Generic / OpenRouter)
    if not api_key:
        api_key = os.getenv("LLM_API_KEY")
    if not base_url:
        base_url = os.getenv("LLM_BASE_URL", DEFAULT_BASE_URL)
        
    if not api_key:
        print("Error: LLM_API_KEY not found in environment variables or arguments.")
        sys.exit(1)

    Settings.llm = OpenAI(
        model=llm_model,
        api_key=api_key,
        api_base=base_url,
        request_timeout=360.0
    )
    
    # Settings.embed_model = OllamaEmbedding(model_name=embedding_model)
    Settings.embed_model = None

def load_prompts():
    """Loads prompts from the YAML file."""
    # Build path to prompts/ownership_validator.yaml relative to this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    prompt_path = os.path.join(project_root, "prompts", "ownership_validator.yaml")
    
    if not os.path.exists(prompt_path):
        print(f"Error: Prompt file not found at {prompt_path}")
        sys.exit(1)
        
    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            prompts = yaml.safe_load(f)
            return prompts
    except Exception as e:
        print(f"Error reading prompt file: {e}")
        sys.exit(1)

def generate_quiz(file_path: str, model_name: str, api_key: str):
    """Reads the file and generates a quiz."""
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)

    print(f"Reading file: {file_path}")
    
    # Read file content
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    # Create Document
    document = Document(text=content, metadata={"filename": os.path.basename(file_path)})

    # Code Splitting for BM25
    ids = [os.path.basename(file_path)]
    documents = [document]

    # Initialize generic LLM if API key is provided directly (e.g. from server)
    if api_key:
        setup_llama_index(model_name or DEFAULT_LLM_MODEL, "", api_key=api_key)

    # Split nodes
    splitter = SentenceSplitter(chunk_size=1024, chunk_overlap=20)
    nodes = splitter.get_nodes_from_documents(documents)

    # Create BM25 Retriever
    print("Indexing content with BM25...")
    retriever = BM25Retriever.from_defaults(nodes=nodes, similarity_top_k=10)
    
    # Create Query Engine
    query_engine = RetrieverQueryEngine.from_args(retriever, llm=Settings.llm)
    
    # Load Prompts
    prompts = load_prompts()
    prompt = prompts.get("quiz_generation_prompt")
    
    if not prompt:
        print("Error: 'quiz_generation_prompt' not found in prompt file.")
        sys.exit(1)
    
    print("Generating quiz (this may take a minute)...")
    response = query_engine.query(prompt)
    
    print("\n" + "="*40)
    print(f"OWNERSHIP QUIZ FOR: {os.path.basename(file_path)}")
    print("="*40 + "\n")
    print(str(response))
    print("\n" + "="*40)

def main():
    parser = argparse.ArgumentParser(description="Generate an ownership quiz for a code script.")
    parser.add_argument("file", help="Path to the code script file.")
    parser.add_argument("--model", default=DEFAULT_LLM_MODEL, help=f"LLM model to use (default: {DEFAULT_LLM_MODEL})")
    parser.add_argument("--embedding", default=DEFAULT_EMBEDDING_MODEL, help=f"Ollama embedding model (default: {DEFAULT_EMBEDDING_MODEL})")
    parser.add_argument("--api-key", help="LLM API Key (overrides LLM_API_KEY env var)")
    parser.add_argument("--base-url", help=f"LLM Base URL (overrides LLM_BASE_URL env var, default: {DEFAULT_BASE_URL})")
    
    args = parser.parse_args()
    
    setup_llama_index(args.model, args.embedding, args.api_key, args.base_url)
    generate_quiz(args.file, args.model, args.api_key)

if __name__ == "__main__":
    main()
