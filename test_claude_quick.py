"""Quick test for Claude integration"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.services.ai_providers.claude_provider import ClaudeProvider

# Test Claude
api_key = os.getenv("CLAUDE_API_KEY", "")
api_url = "https://api.anthropic.com/v1/messages"
model = "claude-3-5-sonnet-20241022"

claude = ClaudeProvider(api_key, api_url, model)

print("Testing Claude provider...")
print(f"Is configured: {claude.is_configured}")
print(f"Model: {claude.model}")

print("\nChecking status...")
status = claude.check_status()
print(f"Status: {status}")

if status == "ok":
    print("\nTesting generation...")
    try:
        response = claude.generate("Say 'Hello World' in one sentence.")
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error: {e}")
else:
    print(f"❌ Claude not ready. Status: {status}")
