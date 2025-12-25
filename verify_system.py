#!/usr/bin/env python3
"""
Comprehensive Model & System Verification Script
Tests all AI models, API endpoints, and system health for WordAssistantAI backend.
"""

import requests
import os
from typing import Dict, Tuple

# Base URL for local backend
BASE_URL = "http://localhost:8000"

# Terminal colors
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_pass(msg: str):
    print(f"{GREEN}✓ [PASS]{RESET} {msg}")

def print_fail(msg: str):
    print(f"{RED}✗ [FAIL]{RESET} {msg}")

def print_info(msg: str):
    print(f"{BLUE}ℹ [INFO]{RESET} {msg}")

def print_warn(msg: str):
    print(f"{YELLOW}⚠ [WARN]{RESET} {msg}")

def test_health_check() -> bool:
    """Test basic system health endpoint."""
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print_pass("System Health Check: Online")
            return True
        else:
            print_fail(f"System Health Check: HTTP {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_fail("System Health Check: Cannot connect to backend (is server running?)")
        return False
    except Exception as e:
        print_fail(f"System Health Check: {type(e).__name__}: {e}")
        return False

def test_all_models() -> Dict[str, str]:
    """Test all available AI model providers."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Testing All AI Model Providers{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    models = {
        "gemini": "Google Gemini",
        "ollama": "Ollama (Local)",
        "openai": "OpenAI GPT",
        "deepseek": "DeepSeek",
        "grok": "Grok (xAI)",
        "zhipu": "Zhipu AI"
    }
    
    results = {}
    
    try:
        response = requests.get(f"{BASE_URL}/api/models/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            for model_id, model_name in models.items():
                status = data.get(model_id, "unknown")
                results[model_id] = status
                
                if status == "ok":
                    print_pass(f"{model_name:20s} → Available")
                elif status == "not configured":
                    print_warn(f"{model_name:20s} → Not Configured")
                elif status == "error":
                    print_fail(f"{model_name:20s} → Error")
                else:
                    print_info(f"{model_name:20s} → {status}")
        else:
            print_fail(f"Model Status Endpoint: HTTP {response.status_code}")
    except Exception as e:
        print_fail(f"Model Status Check: {type(e).__name__}: {e}")
    
    return results

def test_environment_variables() -> None:
    """Check if required environment variables are set."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Checking Environment Variables{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    env_vars = {
        "GEMINI_API_KEY": "Google Gemini",
        "OPENAI_API_KEY": "OpenAI",
        "DEEPSEEK_API_KEY": "DeepSeek",
        "GROK_API_KEY": "Grok",
        "ZHIPU_API_KEY": "Zhipu AI",
    }
    
    for var, provider in env_vars.items():
        if os.getenv(var):
            print_pass(f"{provider:20s} → API key configured")
        else:
            print_warn(f"{provider:20s} → API key not found")

def print_summary(model_results: Dict[str, str]) -> None:
    """Print summary of all tests."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Verification Summary{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    total = len(model_results)
    available = sum(1 for status in model_results.values() if status == "ok")
    
    print_info(f"Models Available: {available}/{total}")
    
    if available > 0:
        print_pass(f"System is ready to use with {available} model(s)")
    else:
        print_fail("No models are currently available")

def main():
    """Main verification routine."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}WordAssistantAI System Verification{RESET}")
    print(f"{BLUE}Backend URL: {BASE_URL}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    # Test 1: Health Check
    if not test_health_check():
        print_fail("\n⚠ Backend server is not running. Please start it with:")
        print_info("  cd backend && python main.py")
        return
    
    # Test 2: Environment Variables
    test_environment_variables()
    
    # Test 3: All Models
    model_results = test_all_models()
    
    # Summary
    print_summary(model_results)
    
    print(f"\n{BLUE}{'='*60}{RESET}\n")

if __name__ == "__main__":
    main()
