"""
Ownership Validator
-------------------
If you can't explain the system, then you don't own it.
This script generates a 30-question quiz from a given code file or repository to help developers understand and "own" the code.
It uses Llama Index with a ReAct Agent to explore the codebase.
"""

import argparse
import sys
import os
import yaml
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI
from llama_index.core.tools import FunctionTool
from llama_index.core.agent import ReActAgent

# Attempt direct import, fallback to src.tools if needed
try:
    import tools
except ImportError:
    # If running from root, src.tools might be needed, or ensure src is in path
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
    try:
        import tools
    except ImportError:
         print("Warning: Could not import 'tools' module. Agent tools will be missing.")
         tools = None

# Default Constants
DEFAULT_LLM_MODEL = "z-ai/glm-4.7-flash:free"
DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"

def setup_llama_index(llm_model: str, api_key: str = None, base_url: str = None):
    """Configures Llama Index with a Generic OpenAI-compatible LLM."""
    print(f"Setting up Llama Index with LLM='{llm_model}'...")
    
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

def generate_quiz(target_path: str, model_name: str, api_key: str):
    """Investigates the target path (file or folder) and generates a quiz."""
    if not os.path.exists(target_path):
        print(f"Error: Path '{target_path}' not found.")
        sys.exit(1)

    print(f"Investigating target: {target_path}")

    # Initialize generic LLM
    if api_key:
        setup_llama_index(model_name or DEFAULT_LLM_MODEL, api_key=api_key)

    # Setup Tools
    tool_list = []
    if tools:
        if hasattr(tools, 'bread_crumb'):
            tool_list.append(FunctionTool.from_defaults(fn=tools.bread_crumb))
        if hasattr(tools, 'get_file_content'):
            tool_list.append(FunctionTool.from_defaults(fn=tools.get_file_content))
    else:
        print("No tools available for the agent.")

    # Initialize Agent
    agent = ReActAgent.from_tools(tool_list, llm=Settings.llm, verbose=True)
    
    # Load Prompts
    prompts = load_prompts()
    base_prompt = prompts.get("quiz_generation_prompt")
    
    if not base_prompt:
        print("Error: 'quiz_generation_prompt' not found in prompt file.")
        sys.exit(1)
    
    # Create Agent Prompt
    prompt = (
        f"You are analyzing the codebase located at: {target_path}\n"
        f"{base_prompt}\n"
        "Use the provided tools to explore the directory structure and read files as needed "
        "to understand the system design and logic. "
        "If the target is a file, read it directly. If it is a folder, explore it."
    )
    
    print("Agent is querying the codebase (this may take time)...")
    response = agent.chat(prompt)
    
    print("\n" + "="*40)
    print(f"OWNERSHIP QUIZ FOR: {os.path.basename(target_path)}")
    print("="*40 + "\n")
    print(str(response))
    print("\n" + "="*40)

def main():
    parser = argparse.ArgumentParser(description="Generate an ownership quiz for a code script or repository.")
    parser.add_argument("file", help="Path to the code script file or folder.")
    parser.add_argument("--model", default=DEFAULT_LLM_MODEL, help=f"LLM model to use (default: {DEFAULT_LLM_MODEL})")
    # parser.add_argument("--embedding", default=DEFAULT_EMBEDDING_MODEL, help=f"Ollama embedding model (default: {DEFAULT_EMBEDDING_MODEL})")
    parser.add_argument("--api-key", help="LLM API Key (overrides LLM_API_KEY env var)")
    parser.add_argument("--base-url", help=f"LLM Base URL (overrides LLM_BASE_URL env var, default: {DEFAULT_BASE_URL})")
    
    args = parser.parse_args()
    
    setup_llama_index(args.model, args.api_key, args.base_url)
    generate_quiz(args.file, args.model, args.api_key)

if __name__ == "__main__":
    main()
