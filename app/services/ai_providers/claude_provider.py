"""
Anthropic Claude AI Provider - Optimized for expert research and technical writing.
"""

import requests
import time
import json
from typing import Generator
from datetime import datetime
from .base_provider import BaseAIProvider


class ClaudeProvider(BaseAIProvider):
    """Anthropic Claude AI provider with streaming and expert prompting."""
    
    EXPERT_SYSTEM_PROMPT = """You are a Senior Research Scientist and Technical Expert with 20+ years of experience.

Write professional, well-structured content using natural formatting.

For tables, use HTML with blue captions:
<p style="color:#0066cc; font-weight:600; margin:10px 0 5px 0;">Table 1: Title</p>
<table style="width:100%; border-collapse:collapse; margin:20px 0; border:1px solid #ddd;">
<thead style="background:#f0f0f0;">
<tr><th style="border:1px solid #ddd; padding:8px;">Header</th></tr>
</thead>
<tbody>
<tr><td style="border:1px solid #ddd; padding:8px;">Data</td></tr>
</tbody>
</table>

For diagrams/architecture, you MUST generate actual Excalidraw JSON (it renders automatically):

EXAMPLE FORMAT - Generic System Architecture:
{"type": "excalidraw", "version": 2, "source": "AI", "elements": [{"id": "comp1", "type": "rectangle", "x": 100, "y": 100, "width": 150, "height": 80, "strokeColor": "#1e1e1e", "backgroundColor": "#a5d8ff", "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid", "roughness": 0, "opacity": 100, "roundness": {"type": 3}}, {"id": "text1", "type": "text", "x": 130, "y": 130, "width": 90, "height": 25, "text": "Component 1", "fontSize": 16, "fontFamily": 1, "textAlign": "center", "strokeColor": "#1e1e1e", "backgroundColor": "transparent"}, {"id": "comp2", "type": "rectangle", "x": 350, "y": 100, "width": 150, "height": 80, "strokeColor": "#1e1e1e", "backgroundColor": "#b2f2bb", "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid", "roughness": 0, "opacity": 100, "roundness": {"type": 3}}, {"id": "text2", "type": "text", "x": 375, "y": 130, "width": 100, "height": 25, "text": "Component 2", "fontSize": 16, "fontFamily": 1, "textAlign": "center", "strokeColor": "#1e1e1e", "backgroundColor": "transparent"}, {"id": "comp3", "type": "rectangle", "x": 600, "y": 100, "width": 150, "height": 80, "strokeColor": "#1e1e1e", "backgroundColor": "#ffc9c9", "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid", "roughness": 0, "opacity": 100, "roundness": {"type": 3}}, {"id": "text3", "type": "text", "x": 625, "y": 130, "width": 100, "height": 25, "text": "Component 3", "fontSize": 16, "fontFamily": 1, "textAlign": "center", "strokeColor": "#1e1e1e", "backgroundColor": "transparent"}, {"id": "arrow1", "type": "arrow", "x": 250, "y": 140, "width": 100, "height": 0, "strokeColor": "#1e1e1e", "strokeWidth": 2, "startArrowhead": null, "endArrowhead": "arrow"}, {"id": "arrow2", "type": "arrow", "x": 500, "y": 140, "width": 100, "height": 0, "strokeColor": "#1e1e1e", "strokeWidth": 2, "startArrowhead": null, "endArrowhead": "arrow"}]}

CRITICAL RULES:
- When user asks for "diagram", "architecture", "flowchart", "workflow" → ALWAYS generate Excalidraw JSON
- Adapt the example above to match what user requests (change labels, add/remove boxes, adjust layout)
- Output ONLY the raw JSON on its own line
- NO markdown code blocks, NO backticks, NO explanatory text around the JSON
- JSON must be valid and complete
- Use: rectangles for boxes/components, arrows for connections, text for labels
- Use different colors: #a5d8ff (blue), #b2f2bb (green), #ffc9c9 (red), #ffec99 (yellow)

Write clear, evidence-based content with proper structure. Include APA references."""
    
    def __init__(self, api_key: str, api_url: str, model: str = "claude-3-5-sonnet-20240620"):
        super().__init__(api_key, api_url)
        self.model = model
        self.max_retries = 3
        self.retry_delay = 2
        # Connection pooling for performance
        self._session = None
    
    @property
    def session(self):
        """Lazy-loaded HTTP session for connection reuse."""
        if self._session is None:
            self._session = requests.Session()
            # Keep connections alive
            self._session.headers.update({
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
                "x-api-key": self.api_key
            })
        return self._session
    
    def generate(self, prompt: str) -> str:
        """Generate response from Claude API."""
        if not self.is_configured:
            raise Exception("CLAUDE_API_KEY not set. Please check your .env file.")
        
        # Timing: Start
        start_time = time.time()
        
        payload = {
            "model": self.model,
            "max_tokens": 8192,  # Increased for complete reports
            "temperature": 0.3,  # Lower temperature for more focused, deterministic output
            "system": self.EXPERT_SYSTEM_PROMPT,
            "messages": [
                {" role": "user", "content": prompt}
            ]
        }
        
        retry_delay = self.retry_delay
        
        for attempt in range(self.max_retries):
            try:
                response = self.session.post(
                    self.api_url,
                    json=payload,
                    timeout=60  # Claude can take longer for complex responses
                )
                
                # Timing: First byte received (TTFB)
                ttfb = time.time() - start_time
                
                if response.status_code == 200:
                    print(f"✅ Claude API success | TTFB: {ttfb:.2f}s")
                    break
                    
                elif response.status_code == 429:
                    print(f"Rate limit (429). Waiting {retry_delay}s...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    
                elif response.status_code >= 500:
                    print(f"Server error {response.status_code}. Retrying...")
                    time.sleep(retry_delay)
                    
                else:
                    error_data = response.json() if response.content else {}
                    error_msg = error_data.get('error', {}).get('message', response.text)
                    print(f"Claude API Error: {response.status_code} - {error_msg}")
                    raise Exception(f"API Error {response.status_code}: {error_msg}")
                    
            except requests.exceptions.RequestException as e:
                print(f"Network error communicating with Claude: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    raise Exception(f"Claude Network Error: {str(e)}")
        else:
            raise Exception("Service unavailable after retries (Rate Limit or Network).")
        
        # Parse response
        data = response.json()
        try:
            content = data["content"][0]["text"]
            
            # Timing: Total time
            total_time = time.time() - start_time
            print(f"⚡ Total generation time: {total_time:.2f}s | Chars: {len(content)} | Speed: {len(content)/total_time:.0f} chars/s")
            
            return content.strip()
            
        except (KeyError, IndexError) as e:
            print(f"Invalid response format: {data}")
            raise Exception(f"Invalid response format from Claude API: {str(e)}")
    
    def generate_stream(self, prompt: str, system_prompt: str = None) -> Generator[str, None, None]:
        """
        Generate streaming response from Claude API for faster TTFB (Time To First Byte).
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt. If None, uses EXPERT_SYSTEM_PROMPT
        """
        if not self.is_configured:
            raise Exception("CLAUDE_API_KEY not set. Please check your .env file.")
        
        # Timing: Start
        start_time = time.time()
        first_chunk_time = None
        char_count = 0
        
        payload = {
            "model": self.model,
            "max_tokens": 8192,  # Increased for complete reports
            "temperature": 0.3,
            "system": system_prompt if system_prompt else self.EXPERT_SYSTEM_PROMPT,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "stream": True  # Enable streaming
        }
        
        try:
            response = self.session.post(
                self.api_url,
                json=payload,
                timeout=60,
                stream=True  # Stream the response
            )
            
            if response.status_code != 200:
                error_data = response.json() if response.content else {}
                error_msg = error_data.get('error', {}).get('message', response.text)
                raise Exception(f"Claude API Error {response.status_code}: {error_msg}")
            
            # Parse Server-Sent Events (SSE) stream
            for line in response.iter_lines():
                if not line:
                    continue
                
                line = line.decode('utf-8')
                
                # Claude uses SSE format: "data: {json}"
                if line.startswith('data: '):
                    data_str = line[6:]  # Remove "data: " prefix
                    
                    # Skip event stream markers
                    if data_str == '[DONE]':
                        break
                    
                    try:
                        chunk_data = json.loads(data_str)
                        
                        # Handle different event types
                        event_type = chunk_data.get('type')
                        
                        if event_type == 'content_block_delta':
                            # Extract text from delta
                            delta = chunk_data.get('delta', {})
                            if delta.get('type') == 'text_delta':
                                text = delta.get('text', '')
                                if text:
                                    # Timing: First chunk (TTFB)
                                    if first_chunk_time is None:
                                        first_chunk_time = time.time() - start_time
                                        print(f"✅ First chunk received | TTFB: {first_chunk_time:.2f}s")
                                    char_count += len(text)
                                    yield text
                        
                        elif event_type == 'message_stop':
                            # End of stream
                            break
                            
                    except json.JSONDecodeError:
                        # Skip malformed JSON
                        continue
            
            # Timing: Total time
            total_time = time.time() - start_time
            if char_count > 0:
                print(f"⚡ Streaming completed | Total: {total_time:.2f}s | Chars: {char_count} | Speed: {char_count/total_time:.0f} chars/s")
            
        except requests.exceptions.RequestException as e:
            print(f"Network error during Claude streaming: {e}")
            raise Exception(f"Claude Streaming Error: {str(e)}")
    
    def check_status(self) -> str:
        """Check Claude API status."""
        if not self.is_configured:
            return "not configured"
        
        try:
            # Quick test with minimal tokens
            test_payload = {
                "model": self.model,
                "max_tokens": 10,
                "messages": [{"role": "user", "content": "Hi"}]
            }
            response = self.session.post(
                self.api_url,
                json=test_payload,
                timeout=10
            )
            
            if response.status_code == 200:
                return "ok"
            elif response.status_code == 429:
                return "rate_limited"
            elif response.status_code == 401:
                return "invalid_key"
            else:
                return "error"
                
        except Exception as e:
            print(f"Claude status check failed: {e}")
            return "error"
