# Installation Guide

This guide covers the installation and setup of CogniFlow.

## Prerequisites

- Python 3.8+ (Python 3.11+ recommended)
- pip package manager
- Git (for development installation)

## Quick Installation

### 1. Clone the Repository

```bash
git clone https://github.com/voidfemme/llm_playground.git
cd llm_playground
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

Create a `.env` file:

```bash
ANTHROPIC_API_KEY=your_anthropic_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
OPENWEATHER_API_KEY=your_openweather_api_key_here
```

### 4. Verify Installation

```bash
python -m pytest tests/ -v
python examples/basic_usage.py
```

For detailed installation instructions, see the complete documentation.
