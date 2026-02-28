"""
Memory Observatory — Configuration Settings
"""

# Model configuration — StepFun Step 3.5 Flash via OpenRouter
# 196B MoE (11B active), 256K context, strong reasoning, tool calling
MODEL = "stepfun/step-3.5-flash"
MAX_TOKENS = 4096
TEMPERATURE = 0.3

# OpenRouter configuration
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_APP_NAME = "Memory Observatory"

# Cost rates (per 1K tokens — Step 3.5 Flash via OpenRouter)
# Input: $0.10/M tokens = $0.0001/1K tokens
# Output: $0.30/M tokens = $0.0003/1K tokens
INPUT_COST_PER_1K = 0.0001
OUTPUT_COST_PER_1K = 0.0003

# Memory settings
MAX_MEMORIES_PER_RETRIEVAL = 8
MAX_MEMORY_TOKENS = 2000
RETRIEVAL_WEIGHTS = {
    "relevance": 0.4,
    "importance": 0.3,
    "recency": 0.2,
    "type_match": 0.1,
}

# Phase-aware type weights for memory retrieval
# Each phase prioritizes different memory types
PHASE_TYPE_WEIGHTS = {
    "planning": {
        "procedural": 0.4,
        "reflective": 0.3,
        "semantic": 0.2,
        "episodic": 0.1,
    },
    "execution": {
        "semantic": 0.4,
        "episodic": 0.3,
        "procedural": 0.2,
        "reflective": 0.1,
    },
    "review": {
        "reflective": 0.5,
        "semantic": 0.2,
        "episodic": 0.2,
        "procedural": 0.1,
    },
}

# Agent settings
MAX_ITERATIONS_PER_TASK = 15

# Recency decay factor (exponential decay based on session distance)
RECENCY_DECAY_FACTOR = 0.3

# Embedding settings
# Priority: sentence-transformers > sklearn TF-IDF > bag-of-words
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Used if sentence-transformers available
SIMILARITY_THRESHOLD = 0.85  # For deduplication in consolidator

# Output paths
OUTPUT_DIR = "output"
TRACES_DIR = "output/traces"
MEMORIES_DIR = "output/memories"
COSTS_DIR = "output/costs"

# Agent identity prompt
AGENT_IDENTITY = """You are a senior investment research analyst. You value accuracy and thoroughness.
You work methodically: gather data, analyze it, identify risks, and provide clear recommendations.
You are especially attentive to red flags in financial data, governance issues, and risk factors
that may not be immediately obvious."""
