"""Enumerations for data models"""

from enum import Enum


class ObservationType(str, Enum):
    """Types of observations in a trace"""
    
    SPAN = "SPAN"              # Generic execution span
    GENERATION = "GENERATION"  # LLM generation
    EVENT = "EVENT"           # Single point event
    TOOL = "TOOL"             # Tool call
    AGENT = "AGENT"           # Agent execution
