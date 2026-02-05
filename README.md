# Ownership Validator

This tool helps developers "own" a codebase by generating a comprehensive 30-question quiz based on a provided code script. It uses Llama Index and Ollama to analyze the code's logic, system design, and potential obstacles.

## Prerequisites

1. **Python 3.8+**
2. **Ollama** installed and running (for embeddings).
3. **LLM API Key** (OpenRouter as default).
4. **Ollama Model**:
   - `ollama/embeddinggemma:300m-qat-q4_0`

## Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Ensure Ollama is running:
   ```bash
   ollama serve
   ```

3. Pull necessary embedding model:
   ```bash
   ollama pull ollama/embeddinggemma:300m-qat-q4_0
   ```

4. Set Environment Variables:
   ```bash
   # Windows PowerShell
   $env:LLM_API_KEY = "your_key_here"
   # Optional: $env:LLM_BASE_URL = "https://openrouter.ai/api/v1"
   
   # Linux/Mac
   export LLM_API_KEY="your_key_here"
   # Optional: export LLM_BASE_URL="https://openrouter.ai/api/v1"
   ```

## Usage

Run the validator on a script:

```bash
python src/ownership_validator.py path/to/your/script.py
```

### Optional Arguments

- `--model`: Specify the LLM model to use (default: `google/gemini-2.0-flash-exp:free`).
- `--api-key`:  API Key (overrides env var).
- `--base-url`:  Base URL (overrides env var).
- `--embedding`: Specify the Ollama embedding model (default: `ollama/embeddinggemma:300m-qat-q4_0`).

Example:
```bash
python src/ownership_validator.py src/my_complex_script.py --model meta-llama/llama-3.1-405b-instruct
```

## What it does

It reads your code, indexes it using vector embeddings, and uses a Large Language Model to quiz you on:
- Deep logic handling
- System design decisions
- "Weird" logic explanations
- Maintenance obstacles
