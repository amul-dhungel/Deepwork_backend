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
        Parse user query to extract layout requirements
        
        Args:
            query: User's layout description
            
        Returns:
            Dictionary with parsed requirements
        """
        requirements = {
            'columns': None,
            'rows': None,
            'sections': None,
            'images': None,
            'grid': False
        }
        
        # Extract columns
        col_match = re.search(r'(\d+)\s*column', query.lower())
        if col_match:
            requirements['columns'] = int(col_match.group(1))
            requirements['grid'] = True
            
        # Extract rows
        row_match = re.search(r'(\d+)\s*row', query.lower())
        if row_match:
            requirements['rows'] = int(row_match.group(1))
            requirements['grid'] = True
            
        # Extract number of sections
        section_match = re.search(r'(\d+)\s*section', query.lower())
        if section_match:
            requirements['sections'] = int(section_match.group(1))
            
        # Extract number of images
        image_match = re.search(r'(\d+)\s*image', query.lower())
        if image_match:
            requirements['images'] = int(image_match.group(1))
            
        return requirements
    
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
        
        # Add padding
        padding = 10
        cell_width = (width - (cols + 1) * padding) / cols
        cell_height = (height - (rows + 1) * padding) / rows
        
        positions = []
        section_id = 0
        
        for row in range(rows):
            for col in range(cols):
                x = padding + col * (cell_width + padding)
                y = padding + row * (cell_height + padding)
                
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
            cols: Number of columns
            rows: Number of rows
            requirements: Additional requirements (images, sections, etc.)
            
        Returns:
            Poster JSON
        """
        positions = self.calculate_grid_positions(cols, rows)
        
        # Determine section categories
        total_sections = len(positions)
        categories = self._assign_categories(total_sections, requirements)
        
        poster_json = {"section": {}}
        
        for i, pos in enumerate(positions):
            poster_json["section"][str(i)] = {
                "category": categories[i],
                "title": f"{categories[i].capitalize()} content",
                "xy": [pos['x'], pos['y'], pos['width'], pos['height']]
            }
            
        return poster_json
    
    def _assign_categories(self, total: int, requirements: Dict = None) -> List[str]:
        """Assign section categories based on requirements"""
        categories = []
        
        # First section is always title
        categories.append("title")
        remaining = total - 1
        
        # Determine image vs text sections
        num_images = 0
        if requirements and requirements.get('images'):
            num_images = min(requirements['images'], remaining)
        else:
            # Default: 40% images
            num_images = int(remaining * 0.4)
            
        # Add image sections
        for _ in range(num_images):
            categories.append("image")
            
        # Fill remaining with text sections
        text_categories = ["introduction", "methods", "results", "conclusion", "references"]
        remaining_text = remaining - num_images
        
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
