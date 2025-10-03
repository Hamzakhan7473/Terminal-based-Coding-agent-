"""
Terminal-based AI Coding Agent

A comprehensive AI-powered coding assistant that accepts natural language instructions,
interprets them into structured code generation commands, and manages an interactive
development workflow with sandboxed execution.
"""

__version__ = "0.1.0"
__author__ = "AI Coding Agent"

from .core.intent_parser import IntentParser
from .core.code_generator import CodeGenerator
from .execution.sandbox import SandboxExecutor
from .context.session_manager import SessionManager
from .cli.interface import CLIInterface

__all__ = [
    "IntentParser",
    "CodeGenerator", 
    "SandboxExecutor",
    "SessionManager",
    "CLIInterface",
]
