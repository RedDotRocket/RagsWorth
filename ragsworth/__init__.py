"""
RagsWorth: An embeddable AI chatbot with RAG capabilities and multi-provider LLM support.
"""

__version__ = "0.1.0"

from .app import create_app

# Initialize app with components by default
app = create_app(init_components=True) 