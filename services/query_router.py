"""
Intelligent Query Router - Routes questions to appropriate processing system.

Simple queries → /dd command (fast, direct)
Complex investigations → agentic system (thorough, analytical)
"""
import re
from typing import Tuple, Dict, Any
from enum import Enum


class QueryType(Enum):
    SIMPLE = "simple"
    COMPLEX = "complex"
    AMBIGUOUS = "ambiguous"


class QueryRouter:
    """
    Intelligent router that determines whether a question needs simple data retrieval
    or complex agentic investigation.
    """
    
    def __init__(self):
        # Patterns that indicate simple, direct queries
        self.simple_patterns = [
            # Direct data requests
            r'\b(show|list|display|get)\s+(?:me\s+)?(the\s+)?',
            r'\btop\s+\d+',
            r'\bbottom\s+\d+', 
            r'\bfirst\s+\d+',
            r'\blast\s+\d+',
            r'\bhow\s+many',
            r'\bcount\s+(?:of\s+)?',
            r'\bsum\s+(?:of\s+)?',
            r'\baverage\s+(?:of\s+)?',
            r'\bmax(?:imum)?\s+',
            r'\bmin(?:imum)?\s+',
            
            # Specific data lookups
            r'\bwhat\s+(?:is|are)\s+the\s+(?:name|title|value|amount)',
            r'\bwhich\s+(?:driver|team|customer|product|user)',
            r'\bwho\s+(?:won|has|is)',
            r'\bwhen\s+(?:did|was)',
            r'\bwhere\s+(?:is|are|did)',
            
            # Simple aggregations
            r'\btotal\s+(?:sales|revenue|orders|count)',
            r'\ball\s+(?:customers|products|orders|users)',
            
            # Simple comparisons
            r'\bcompare\s+\w+\s+(?:and|vs|versus)\s+\w+',
        ]
        
        # Patterns that indicate complex analytical questions
        self.complex_patterns = [
            # Why questions (root cause analysis)
            r'\bwhy\s+(?:did|is|are|has|have)',
            r'\bwhat\s+(?:caused|drove|contributed|led\s+to)',
            r'\bwhat\s+(?:factors|reasons|causes)',
            
            # Analysis and investigation
            r'\b(?:analyze|analyse|investigate|examine|explore)\b',
            r'\bwhat\s+patterns?\b',
            r'\bwhat\s+trends?\b',
            r'\bwhat\s+insights?\b',
            r'\bwhat\s+should\s+I\s+know',
            r'\btell\s+me\s+about\s+(?:the\s+)?(?:data|dataset|performance|business)',
            r'\bexplain\s+(?:the\s+)?(?:data|dataset|trends|patterns)',
            
            # Business intelligence
            r'\bhow\s+(?:is|are)\s+(?:we|our|the\s+business|performance)',
            r'\bwhat\s+(?:drives|affects|influences|impacts)',
            r'\bhow\s+(?:can|should|do)\s+(?:we|I)\s+improve',
            r'\boptimize|optimization',
            r'\bstrategy|strategic',
            
            # Multi-dimensional analysis
            r'\brelationship\s+between',
            r'\bcorrelation\s+(?:between|with)',
            r'\bimpact\s+of\s+\w+\s+on',
            r'\b(?:predict|forecast|project)',
            
            # Comparative analysis
            r'\bbetter\s+(?:than|performing)',
            r'\bworst\s+performing',
            r'\bbest\s+performing',
            r'\bperformance\s+(?:analysis|comparison)',
            
            # Vague/open-ended questions
            r'\bwhat\s+(?:else|other|more)',
            r'\banything\s+(?:else|interesting|unusual)',
            r'\bsurprising|unexpected|anomal',
        ]
        
        # Keywords that suggest simple queries even if patterns don't match
        self.simple_keywords = {
            'list', 'show', 'display', 'count', 'total', 'sum', 'average', 'max', 'min',
            'first', 'last', 'top', 'bottom', 'all', 'latest', 'recent', 'name', 'title'
        }
        
        # Keywords that suggest complex analysis
        self.complex_keywords = {
            'why', 'analyze', 'investigate', 'pattern', 'trend', 'factor', 'cause',
            'insight', 'understand', 'explain', 'explore', 'relationship', 'impact',
            'performance', 'optimize', 'strategy', 'improve', 'predict', 'forecast'
        }
    
    def route_question(self, question: str) -> Tuple[QueryType, Dict[str, Any]]:
        """
        Analyze question and determine routing strategy.
        
        Args:
            question: User's natural language question
            
        Returns:
            Tuple of (QueryType, routing_metadata)
        """
        question_lower = question.lower().strip()
        
        # Calculate pattern scores
        simple_score = self._calculate_pattern_score(question_lower, self.simple_patterns)
        complex_score = self._calculate_pattern_score(question_lower, self.complex_patterns)
        
        # Calculate keyword scores
        simple_keyword_score = self._calculate_keyword_score(question_lower, self.simple_keywords)
        complex_keyword_score = self._calculate_keyword_score(question_lower, self.complex_keywords)
        
        # Combine scores
        total_simple_score = simple_score + simple_keyword_score
        total_complex_score = complex_score + complex_keyword_score
        
        # Additional heuristics
        question_length = len(question.split())
        has_question_words = any(word in question_lower for word in ['why', 'how', 'what', 'when', 'where', 'who'])
        
        # Decision logic
        routing_metadata = {
            'simple_score': total_simple_score,
            'complex_score': total_complex_score,
            'question_length': question_length,
            'confidence': 0.0,
            'reasoning': ''
        }
        
        # Strong simple indicators
        if total_simple_score >= 3 and total_complex_score <= 1:
            routing_metadata['confidence'] = 0.9
            routing_metadata['reasoning'] = 'Strong simple query patterns detected'
            return QueryType.SIMPLE, routing_metadata
        
        # Strong complex indicators  
        if total_complex_score >= 3 and total_simple_score <= 1:
            routing_metadata['confidence'] = 0.9
            routing_metadata['reasoning'] = 'Strong complex analysis patterns detected'
            return QueryType.COMPLEX, routing_metadata
        
        # Length-based heuristics
        if question_length <= 5 and total_simple_score > 0:
            routing_metadata['confidence'] = 0.8
            routing_metadata['reasoning'] = 'Short question with simple patterns'
            return QueryType.SIMPLE, routing_metadata
        
        if question_length >= 10 and has_question_words:
            routing_metadata['confidence'] = 0.7
            routing_metadata['reasoning'] = 'Long analytical question'
            return QueryType.COMPLEX, routing_metadata
        
        # Edge case handling
        if total_simple_score > total_complex_score:
            routing_metadata['confidence'] = 0.6
            routing_metadata['reasoning'] = 'Simple score higher than complex'
            return QueryType.SIMPLE, routing_metadata
        elif total_complex_score > total_simple_score:
            routing_metadata['confidence'] = 0.6  
            routing_metadata['reasoning'] = 'Complex score higher than simple'
            return QueryType.COMPLEX, routing_metadata
        else:
            # Ambiguous case
            routing_metadata['confidence'] = 0.5
            routing_metadata['reasoning'] = 'Ambiguous question - defaulting to simple'
            return QueryType.SIMPLE, routing_metadata  # Default to simple for efficiency
    
    def _calculate_pattern_score(self, question: str, patterns: list) -> float:
        """Calculate score based on regex pattern matches."""
        score = 0
        for pattern in patterns:
            if re.search(pattern, question, re.IGNORECASE):
                score += 1
        return score
    
    def _calculate_keyword_score(self, question: str, keywords: set) -> float:
        """Calculate score based on keyword presence."""
        question_words = set(question.split())
        matching_keywords = question_words.intersection(keywords)
        return len(matching_keywords)
    
    def should_use_agentic(self, question: str, confidence_threshold: float = 0.7) -> Tuple[bool, str]:
        """
        Simple boolean check if question should use agentic analysis.
        
        Args:
            question: User's question
            confidence_threshold: Minimum confidence to use agentic system
            
        Returns:
            Tuple of (use_agentic, explanation)
        """
        query_type, metadata = self.route_question(question)
        
        if query_type == QueryType.COMPLEX and metadata['confidence'] >= confidence_threshold:
            return True, f"Complex analytical question (confidence: {metadata['confidence']:.1%})"
        elif query_type == QueryType.COMPLEX:
            return True, f"Likely complex question (confidence: {metadata['confidence']:.1%})"
        else:
            return False, f"Simple data query (confidence: {metadata['confidence']:.1%})"


# Global router instance
query_router = QueryRouter()