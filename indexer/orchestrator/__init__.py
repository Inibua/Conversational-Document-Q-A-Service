"""
Package for the orchestrator component of the indexer.

The orchestrator coordinates the Discoverer, Collector, Processor, and Storer
components to implement the full document indexing workflow.
"""
from .base import Orchestrator
from .basic import BasicOrchestrator, create_orchestrator

__all__ = ['Orchestrator', 'BasicOrchestrator', 'create_orchestrator']

# Default imports for convenience
__all__.extend(['create_orchestrator'])