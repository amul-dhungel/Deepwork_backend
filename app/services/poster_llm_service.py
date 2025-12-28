"""
Poster LLM Service
Generates custom poster layouts using LLM based on user specifications and RAG-retrieved references
"""

import json
import re
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class PosterLLMService:
    """Service for generating custom poster layouts using LLM"""
    
    def __init__(self):
        self.default_width = 900
        self.default_height = 600
        
    def parse_user_requirements(self, query: str) -> Dict[str, Any]:
        """
        Use LLM to parse user query and extract layout requirements
        
        Args:
            query: User's layout description
            
        Returns:
            Dictionary with parsed requirements
        """
        from ..llm.llm_service import LLMService
        
        llm = LLMService()
        
        prompt = f"""Analyze this poster layout request and extract the structure.

User request: "{query}"

Determine:
1. Grid layout: How many columns and rows for content sections (NOT including title)
2. Total sections needed (excluding title)
3. Number of image sections desired
4. Layout style (scientific, conference, business, creative)

IMPORTANT: 
- Title is ALWAYS separate (full-width header)
- Only count content sections in grid
- Recognize patterns: "3*2", "3x2", "3 by 2", "3 column 2 row" all mean 3 columns, 2 rows
- If no specific grid mentioned, suggest best professional layout

Return ONLY valid JSON:
{{
  "columns": 3,
  "rows": 2,
  "total_sections": 6,
  "images": 2,
  "style": "scientific",
  "has_title": true,
  "description": "3x2 grid with title header"
}}"""

        try:
            response = llm.generate(prompt).strip()
            
            # Clean response
            if '```' in response:
                response = response.split('```')[1]
                if response.startswith('json'):
                    response = response[4:]
            
            result = json.loads(response)
            
            # Validate and set defaults
            requirements = {
                'columns': result.get('columns', 2),
                'rows': result.get('rows', 2),
                'sections': result.get('total_sections'),
                'images': result.get('images', 0),
                'grid': True,  # Always use grid for LLM-generated layouts
                'style': result.get('style', 'scientific'),
                'has_title': result.get('has_title', True),
                'description': result.get('description', '')
            }
            
            logger.info(f"LLM parsed requirements: {requirements}")
            return requirements
            
        except Exception as e:
            logger.error(f"Error parsing with LLM: {e}")
            # Fallback to default
            return {
                'columns': 2,
                'rows': 2,
                'sections': 4,
                'images': 1,
                'grid': True,
                'style': 'scientific',
                'has_title': True,
                'description': 'Default 2x2 grid'
            }
    
    def calculate_grid_positions(self, cols: int, rows: int, 
                                 width: int = None, height: int = None) -> List[Dict]:
        """
        Calculate section positions for grid layout
        
        Args:
            cols: Number of columns
            rows: Number of rows
            width: Total poster width
            height: Total poster height
            
        Returns:
            List of position dictionaries
        """
        width = width or self.default_width
        height = height or self.default_height
        
        # Add padding and minimum gap between containers
        padding = 20  # Increased from 10 for better spacing
        min_gap = 15  # Minimum gap between containers
        
        # Calculate available space
        available_width = width - (2 * padding) - ((cols - 1) * min_gap)
        available_height = height - (2 * padding) - ((rows - 1) * min_gap)
        
        cell_width = available_width / cols
        cell_height = available_height / rows
        
        positions = []
        section_id = 0
        
        for row in range(rows):
            for col in range(cols):
                x = padding + col * (cell_width + min_gap)
                y = padding + row * (cell_height + min_gap)
                
                positions.append({
                    'id': str(section_id),
                    'x': int(x),
                    'y': int(y),
                    'width': int(cell_width),
                    'height': int(cell_height)
                })
                section_id += 1
                
        return positions
    
    def generate_poster_from_grid(self, cols: int, rows: int, 
                                  requirements: Dict = None) -> Dict:
        """
        Generate poster JSON from grid specifications
        
        Args:
            cols: Number of columns for content
            rows: Number of rows for content
            requirements: Additional requirements (images, sections, etc.)
            
        Returns:
            Poster JSON with title + grid layout
        """
        poster_json = {"section": {}}
        
        # Section 0: Full-width title (separate from grid)
        poster_json["section"]["0"] = {
            "category": "title",
            "title": "Your Poster Title",
            "xy": [0, 0, self.default_width, 80]  # Full width, 80px height
        }
        
        # Calculate grid positions for content sections (below title)
        title_height = 80
        content_start_y = title_height + 10  # 10px gap after title
        available_height = self.default_height - title_height - 10
        
        positions = self.calculate_grid_positions(
            cols, rows, 
            width=self.default_width, 
            height=available_height
        )
        
        # Adjust Y positions to account for title
        for pos in positions:
            pos['y'] += content_start_y
        
        # Determine section categories
        total_sections = len(positions)
        categories = self._assign_categories(total_sections, requirements)
        
        # Add content sections (starting from index 1)
        for i, pos in enumerate(positions):
            section_id = i + 1  # Start from 1 (0 is title)
            poster_json["section"][str(section_id)] = {
                "category": categories[i],
                "title": f"{categories[i].capitalize()} content",
                "xy": [pos['x'], pos['y'], pos['width'], pos['height']]
            }
            
        return poster_json
    
    def _assign_categories(self, total: int, requirements: Dict = None) -> List[str]:
        """Assign section categories based on requirements (title is separate)"""
        categories = []
        
        # Determine image vs text sections
        num_images = 0
        if requirements and requirements.get('images'):
            num_images = min(requirements['images'], total)
        else:
            # Default: 30% images
            num_images = int(total * 0.3)
            
        # Add image sections
        for _ in range(num_images):
            categories.append("image")
            
        # Fill remaining with text sections
        text_categories = ["introduction", "methods", "results", "discussion", "conclusion", "references"]
        remaining_text = total - num_images
        
        for i in range(remaining_text):
            cat = text_categories[i % len(text_categories)]
            categories.append(cat)
            
        return categories
    
    def generate_custom_layout(self, query: str, reference_layouts: List[Dict] = None) -> Dict:
        """
        Generate custom poster layout based on query and references
        
        Args:
            query: User's layout description
            reference_layouts: RAG-retrieved layouts for inspiration
            
        Returns:
            Generated poster JSON
        """
        # Parse requirements
        requirements = self.parse_user_requirements(query)
        logger.info(f"Parsed requirements: {requirements}")
        
        # Generate based on grid if specified
        if requirements['grid'] and requirements['columns'] and requirements['rows']:
            logger.info(f"Generating grid layout: {requirements['columns']}x{requirements['rows']}")
            return self.generate_poster_from_grid(
                requirements['columns'], 
                requirements['rows'],
                requirements
            )
        
        # Generate based on section count
        if requirements['sections']:
            cols = 2 if requirements['sections'] > 3 else 1
            rows = (requirements['sections'] + cols - 1) // cols
            return self.generate_poster_from_grid(cols, rows, requirements)
        
        # Default: Use reference layout if available
        if reference_layouts and len(reference_layouts) > 0:
            logger.info("Using reference layout as base")
            return reference_layouts[0]['poster_json']
        
        # Fallback: Generate 2x2 grid
        logger.info("Generating default 2x2 grid")
        return self.generate_poster_from_grid(2, 2, requirements)
