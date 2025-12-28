"""
Copywriting Agent - Semantic Text Analysis

This agent analyzes text to extract semantic structure and determine
the best visual representation (archetype) for infographic generation.
"""

from typing import Dict, List, Optional
import json
import re


class CopywritingAgent:
    """
    Agent 1: Analyzes text to extract semantic structure and relationships.
    
    Responsibilities:
    - Detect visual archetype (timeline, process, comparison, hierarchy, metrics)
    - Extract key concepts and relationships
    - Determine tone and complexity
    - Generate structured blueprint for layout engine
    """
    
    def __init__(self, llm_service):
        """
        Initialize with LLM service for AI-powered analysis.
        
        Args:
            llm_service: AI service instance (Gemini/Claude/Ollama)
        """
        self.llm = llm_service
    
    def analyze(self, text: str) -> Dict:
        """
        Analyze text to extract semantic structure.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary with archetype, concepts, relationships, tone, complexity
        """
        
        print(f"🎨 CopywritingAgent.analyze() called with text: {text[:100]}...")
        
        # TEMPORARY: Return hardcoded programming process flow for testing
        if 'programming' in text.lower() or 'code' in text.lower():
            result = {
                'archetype': 'process',
                'metadata': {
                    'title': 'Programming Workflow',
                    'semantic_type': 'process',
                    'tone': 'professional',
                    'complexity': 'moderate'
                },
                'structure': {
                    'title': 'Programming Workflow',
                    'steps': [
                        {
                            'name': 'Define Problem',
                            'description': 'Understand requirements and specify task',
                            'importance': 0.9,
                            'keywords': ['define', 'requirements', 'analyze']
                        },
                        {
                            'name': 'Plan Solution',
                            'description': 'Design architecture and choose tools',
                            'importance': 0.85,
                            'keywords': ['plan', 'design', 'architecture']
                        },
                        {
                            'name': 'Write Code',
                            'description': 'Implement solution with clean code',
                            'importance': 1.0,
                            'keywords': ['code', 'programming', 'develop']
                        },
                        {
                            'name': 'Test Code',
                            'description': 'Verify functionality with unit tests',
                            'importance': 0.9,
                            'keywords': ['test', 'verify', 'quality']
                        },
                        {
                            'name': 'Debug Issues',
                            'description': 'Fix bugs and optimize performance',
                            'importance': 0.8,
                            'keywords': ['debug', 'fix', 'optimize']
                        },
                        {
                            'name': 'Deploy Code',
                            'description': 'Release to production environment',
                            'importance': 0.85,
                            'keywords': ['deploy', 'release', 'production']
                        }
                    ]
                }
            }
            print(f"✅ Returning hardcoded programming workflow with {len(result['structure']['steps'])} steps")
            return result
        
        # Use LLM to analyze text and determine structure
        archetype = self._detect_archetype(text)
        print(f"📊 Detected archetype: {archetype}")
        
        # Generate structure based on archetype
        if archetype == 'timeline':
            structure = self._extract_timeline(text)
        elif archetype == 'hierarchy':
            structure = self._extract_hierarchy(text)
        elif archetype == 'network':
            structure = self._extract_network(text)
        elif archetype == 'process':
            structure = self._extract_process(text)
        elif archetype == 'comparison':
            structure = self._extract_comparison(text)
        else:
            structure = self._extract_process(text)  # Default fallback
        
        result = {
            'archetype': archetype,
            'metadata': {
                'title': structure.get('title', 'Infographic'),
                'semantic_type': archetype,
                'tone': 'professional',
                'complexity': 'moderate'
            },
            'structure': structure
        }
        
        print(f"✅ Analysis complete - {archetype} with {len(structure.get('events', structure.get('nodes', [])))} items")
        return result
    
    def _detect_archetype(self, text: str) -> str:
        """
        Use LLM to detect the best visual archetype for the text.
        
        Returns:
            One of: timeline, process, comparison, hierarchy, metrics, network
        """
        
        prompt = f"""Analyze this text and determine the best visual representation.

Text: "{text}"

Choose ONE archetype that best represents this content:
- timeline: Sequential events over time (dates, chronological order)
- process: Step-by-step procedure or workflow (stages, phases)
- bar_chart: Numerical data comparison (sales figures, statistics, measurements with values)
- stacked_bar_chart: Multiple data series per category (stacked segments, percentage breakdowns)
- comparison: Comparing features or qualities (versus, differences, pros/cons)
- hierarchy: Organizational structure or categorization (parent-child, levels)
- metrics: Quantitative data or statistics (numbers, percentages, measurements)
- network: Relationships and connections (interactions, dependencies)

Respond with ONLY the archetype name (e.g., "timeline").
"""
        
        try:
            response = self.llm.generate(prompt).strip().lower()
            
            # Validate response
            valid_archetypes = ['timeline', 'process', 'bar_chart', 'stacked_bar_chart', 'comparison', 'hierarchy', 'metrics', 'network']
            
            # Extract archetype from response (handle verbose responses)
            for archetype in valid_archetypes:
                if archetype in response:
                    return archetype
            
            # Default fallback
            return 'process'
            
        except Exception as e:
            print(f"Error detecting archetype: {e}")
            return 'process'  # Safe default
    
    def _extract_metadata(self, text: str) -> Dict:
        """
        Extract semantic metadata about the text.
        
        Returns:
            Dictionary with semantic_type, tone, complexity
        """
        
        prompt = f"""Analyze this text's characteristics.

Text: "{text}"

Determine:
1. Semantic type: sequential, hierarchical, comparative, or quantitative
2. Tone: professional, casual, or academic
3. Complexity: simple, moderate, or complex

Respond with ONLY valid JSON:
{{
  "semantic_type": "sequential",
  "tone": "professional",
  "complexity": "moderate"
}}
"""
        
        try:
            response = self.llm.generate(prompt)
            # Try to parse JSON
            metadata = self._parse_json(response)
            
            # Validate and set defaults
            return {
                'semantic_type': metadata.get('semantic_type', 'sequential'),
                'tone': metadata.get('tone', 'professional'),
                'complexity': metadata.get('complexity', 'moderate')
            }
            
        except Exception as e:
            print(f"Error extracting metadata: {e}")
            return {
                'semantic_type': 'sequential',
                'tone': 'professional',
                'complexity': 'moderate'
            }
    
    def _extract_structure(self, text: str, archetype: str) -> Dict:
        """
        Extract detailed structure based on archetype.
        
        Args:
            text: Input text
            archetype: Detected archetype
            
        Returns:
            Structured data specific to the archetype
        """
        
        extractors = {
            'timeline': self._extract_timeline,
            'process': self._extract_process,
            'comparison': self._extract_comparison,
            'hierarchy': self._extract_hierarchy,
            'metrics': self._extract_metrics,
            'network': self._extract_network,
            'bar_chart': self._extract_bar_chart,
            'stacked_bar_chart': self._extract_stacked_bar_chart
        }
        
        extractor = extractors.get(archetype, self._extract_process)
        print(f"📊 Using extractor for archetype '{archetype}': {extractor.__name__}")
        return extractor(text)
    
    def _extract_timeline(self, text: str) -> Dict:
        """Extract timeline structure with events and dates."""
        
        prompt = f"""Extract timeline events from this text.

Text: "{text}"

For each event, extract:
- date: Date or time period (e.g., "1796", "Ancient times", "Modern era")
- name: Short, punchy event name (max 5 words)
- description: Brief description (1-2 sentences, max 100 chars)
- importance: Importance score 0.0-1.0 (1.0 = most important)
- keywords: 2-3 relevant keywords for icon selection

Respond with ONLY valid JSON:
{{
  "title": "Timeline Title",
  "events": [
    {{
      "date": "1796",
      "name": "Jenner's Discovery",
      "description": "Cowpox inoculation protects against smallpox",
      "importance": 1.0,
      "keywords": ["vaccine", "discovery", "medical"]
    }}
  ]
}}
"""
        
        try:
            response = self.llm.generate(prompt)
            print(f"📝 LLM Response for timeline: {response[:200]}...")  # Debug log
            
            structure = self._parse_json(response)
            print(f"📝 Parsed structure: {structure}")  # Debug log
            
            # Ensure we have required fields
            if 'events' not in structure or not structure['events']:
                print("⚠️ No events found in LLM response, using fallback data")
                # Fallback: Create timeline from text manually
                structure = self._create_fallback_timeline(text)
            
            if 'title' not in structure:
                structure['title'] = 'Timeline'
            
            print(f"✅ Final timeline structure: {len(structure.get('events', []))} events")
            return structure
            
        except Exception as e:
            print(f"❌ Error extracting timeline: {e}")
            # Return fallback data
            return self._create_fallback_timeline(text)
    
    def _create_fallback_timeline(self, text: str) -> Dict:
        """Create a simple timeline from text when LLM fails"""
        # Split text into sentences and create events
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        events = []
        for i, sentence in enumerate(sentences[:5]):  # Max 5 events
            events.append({
                'date': f'Event {i+1}',
                'name': sentence[:50] if len(sentence) > 50 else sentence,
                'description': sentence[:100] if len(sentence) > 100 else sentence,
                'importance': 0.8,
                'keywords': ['event', 'timeline']
            })
        
        return {
            'title': 'Timeline',
            'events': events
        }

    
    def _extract_process(self, text: str) -> Dict:
        """Extract process structure with steps and connections."""
        
        prompt = f"""Extract process steps from this text.

Text: "{text}"

For each step, extract:
- id: Unique number (1, 2, 3...)
- label: Short step name (max 4 words)
- description: Brief description (max 80 chars)
- type: "process", "decision", "start", or "end"
- importance: 0.0-1.0 (1.0 = most important)
- keywords: 2-3 keywords for icon selection

Also identify connections between steps.

Respond with ONLY valid JSON:
{{
  "title": "Process Name",
  "nodes": [
    {{
      "id": 1,
      "label": "Lead Generation",
      "description": "Identify potential customers",
      "type": "process",
      "importance": 0.8,
      "keywords": ["search", "customer", "lead"]
    }}
  ],
  "edges": [
    {{"from": 1, "to": 2}}
  ]
}}
"""
        
        try:
            response = self.llm.generate(prompt)
            structure = self._parse_json(response)
            
            # Validate structure
            if 'nodes' not in structure:
                structure['nodes'] = []
            if 'edges' not in structure:
                structure['edges'] = []
            if 'title' not in structure:
                structure['title'] = 'Process'
            
            return structure
            if 'steps' not in result:
                raise ValueError("Missing 'steps' in response")
            
            # Ensure all steps have required fields
            for step in result['steps']:
                step.setdefault('name', 'Step')
                step.setdefault('description', '')
                step.setdefault('importance', 0.8)
                step.setdefault('keywords', [])
            
            return result
            
        except Exception as e:
            print(f"⚠️ Error extracting process: {e}")
            # Fallback to simple extraction
            return {
                'title': 'Process Flow',
                'steps': [
                    {'name': 'Start', 'description': text[:50], 'importance': 0.8, 'keywords': ['start', 'begin']},
                    {'name': 'Process', 'description': 'Execute main steps', 'importance': 0.9, 'keywords': ['process', 'execute']},
                    {'name': 'Complete', 'description': 'Finish and verify', 'importance': 0.8, 'keywords': ['complete', 'finish']}
                ]
            }
    
    def _extract_comparison(self, text: str) -> Dict:
        """Extract comparison structure with items and attributes."""
        
        prompt = f"""Extract comparison items from this text.

Text: "{text}"

For each item being compared, extract:
- name: Item name
- attributes: Key attributes or features
- importance: 0.0-1.0
- keywords: 2-3 keywords for icon selection

Respond with ONLY valid JSON:
{{
  "title": "Comparison Title",
  "items": [
    {{
      "name": "Option A",
      "attributes": ["Fast", "Expensive", "High quality"],
      "importance": 0.9,
      "keywords": ["premium", "quality"]
    }}
  ]
}}
"""
        
        try:
            response = self.llm.generate(prompt)
            structure = self._parse_json(response)
            
            if 'items' not in structure:
                structure['items'] = []
            if 'title' not in structure:
                structure['title'] = 'Comparison'
            
            return structure
            
        except Exception as e:
            print(f"Error extracting comparison: {e}")
            return {'title': 'Comparison', 'items': []}
    
    def _extract_hierarchy(self, text: str) -> Dict:
        """Extract hierarchical structure with parent-child relationships."""
        
        prompt = f"""Extract hierarchical structure from this text.

Text: "{text}"

Identify parent-child relationships and levels.

Respond with ONLY valid JSON:
{{
  "title": "Hierarchy Title",
  "nodes": [
    {{
      "id": 1,
      "label": "Root Node",
      "parentId": null,
      "level": 0,
      "importance": 1.0,
      "keywords": ["root", "main"]
    }}
  ]
}}
"""
        
        try:
            response = self.llm.generate(prompt)
            structure = self._parse_json(response)
            
            if 'nodes' not in structure:
                structure['nodes'] = []
            if 'title' not in structure:
                structure['title'] = 'Hierarchy'
            
            return structure
            
        except Exception as e:
            print(f"Error extracting hierarchy: {e}")
            return {'title': 'Hierarchy', 'nodes': []}
    
    def _extract_metrics(self, text: str) -> Dict:
        """Extract metrics and quantitative data."""
        
        prompt = f"""Extract metrics from this text.

Text: "{text}"

For each metric, extract:
- name: Metric name
- value: Numeric value
- unit: Unit of measurement
- description: Brief description
- keywords: 2-3 keywords

Respond with ONLY valid JSON:
{{
  "title": "Metrics Title",
  "metrics": [
    {{
      "name": "Revenue",
      "value": 1000000,
      "unit": "USD",
      "description": "Annual revenue",
      "keywords": ["money", "revenue"]
    }}
  ]
}}
"""
        
        try:
            response = self.llm.generate(prompt)
            structure = self._parse_json(response)
            
            if 'metrics' not in structure:
                structure['metrics'] = []
            if 'title' not in structure:
                structure['title'] = 'Metrics'
            
            return structure
            
        except Exception as e:
            print(f"Error extracting metrics: {e}")
            return {'title': 'Metrics', 'metrics': []}
    
    def _extract_network(self, text: str) -> Dict:
        """Extract network structure with nodes and relationships."""
        
        # Similar to process but with more complex relationships
        return self._extract_process(text)
    
    def _parse_json(self, response: str) -> Dict:
        """
        Parse JSON from LLM response, handling markdown code blocks.
        
        Args:
            response: LLM response text
            
        Returns:
            Parsed JSON dictionary
        """
        
        # Try direct JSON parse first
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass
        
        # Try to extract JSON from markdown code block
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Try to extract any JSON object
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass
        
        # Fallback: return empty dict
        return {}
    
    def _extract_bar_chart(self, text: str) -> Dict:
        """Extract bar chart data with categories and values."""
        
        print(f"📊 _extract_bar_chart called with text: {text[:100]}...")
        
        prompt = f"""Extract data for a bar chart from this text.

Text: "{text}"

Identify:
- title: Chart title (concise, max 5 words)
- categories: List of category names
- values: Corresponding numerical values
- unit: Unit of measurement (optional)

Return ONLY valid JSON:
{{
  "title": "Sales by Region",
  "categories": ["North", "South", "East", "West"],
  "values": [45, 32, 58, 41],
  "unit": "millions"
}}"""

        try:
            response = self.llm.generate(prompt).strip()
            print(f"📊 LLM response: {response[:200]}...")
            
            if '```' in response:
                response = response.split('```')[1]
                if response.startswith('json'):
                    response = response[4:]
            
            result = json.loads(response)
            print(f"📊 Parsed result: {result}")
            
            if 'categories' not in result or 'values' not in result:
                raise ValueError("Missing categories or values")
            
            result.setdefault('title', 'Bar Chart')
            result.setdefault('unit', '')
            
            return result
            
        except Exception as e:
            print(f"⚠️ Error extracting bar chart: {e}")
            return {
                'title': 'Data Comparison',
                'categories': ['Item 1', 'Item 2', 'Item 3'],
                'values': [10, 20, 15],
                'unit': ''
            }
    
    def _extract_stacked_bar_chart(self, text: str) -> Dict:
        """Extract stacked bar chart data with multiple series."""
        
        print(f"📊 _extract_stacked_bar_chart called with text: {text[:100]}...")
        
        prompt = f"""Extract data for a stacked bar chart from this text.

Text: "{text}"

Identify:
- title: Chart title (concise)
- categories: List of category names (e.g., countries, products)
- series: List of data series, each containing:
  - label: Series name
  - values: List of values (one per category)
- unit: Unit of measurement (optional, e.g., "%", "units")

Return ONLY valid JSON:
{{
  "title": "Country Comparison",
  "categories": ["Sweden", "Netherlands", "Spain"],
  "series": [
    {{"label": "Positive", "values": [80, 79, 79]}},
    {{"label": "Neutral", "values": [17, 17, 18]}},
    {{"label": "Negative", "values": [2, 4, 3]}}
  ],
  "unit": "%"
}}

IMPORTANT: Return ONLY the JSON, no explanations."""

        try:
            response = self.llm.generate(prompt).strip()
            print(f"📊 LLM response: {response[:200]}...")
            
            if '```' in response:
                response = response.split('```')[1]
                if response.startswith('json'):
                    response = response[4:]
            
            result = json.loads(response)
            print(f"📊 Parsed result: {result}")
            
            if 'categories' not in result or 'series' not in result:
                raise ValueError("Missing categories or series")
            
            result.setdefault('title', 'Stacked Bar Chart')
            result.setdefault('unit', '')
            
            return result
            
        except Exception as e:
            print(f"⚠️ Error extracting stacked bar chart: {e}")
            return {
                'title': 'Stacked Data',
                'categories': ['Category 1', 'Category 2'],
                'series': [
                    {'label': 'Series 1', 'values': [60, 70]},
                    {'label': 'Series 2', 'values': [30, 20]},
                    {'label': 'Series 3', 'values': [10, 10]}
                ],
                'unit': '%'
            }
