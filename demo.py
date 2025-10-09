#!/usr/bin/env python3
"""
Demo script for the Terminal-based AI Coding Agent.

This script demonstrates the core functionality without requiring installation.
"""

import sys
import os
import asyncio
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Now we can import our modules
from coding_agent.core.models import IntentType, Language, UserIntent
from coding_agent.core.intent_parser import IntentParser
from coding_agent.core.code_generator import CodeGenerator
from coding_agent.utils.llm_client import LLMClientFactory
from coding_agent.utils.file_manager import FileManager
from coding_agent.utils.logger import get_logger

logger = get_logger(__name__)


def print_banner():
    """Print the demo banner."""
    print("🤖 Terminal-based AI Coding Agent - DEMO")
    print("=" * 50)
    print("This demo showcases the core functionality of the AI coding agent.")
    print("Note: This demo runs in simulation mode without API calls.")
    print("=" * 50)


def simulate_intent_parsing():
    """Simulate intent parsing without LLM calls."""
    print("\n📋 1. Intent Parsing Demo")
    print("-" * 30)
    
    sample_inputs = [
        "Create a Python function for quicksort algorithm",
        "Add error handling to utils.py",
        "Run the code and show me the output",
        "Fix the bug in my sorting function"
    ]
    
    for user_input in sample_inputs:
        print(f"\n🔍 Input: '{user_input}'")
        
        # Simulate intent parsing
        if "create" in user_input.lower() or "make" in user_input.lower():
            intent_type = IntentType.CREATE_FILE
            confidence = 0.85
            language = Language.PYTHON
        elif "add" in user_input.lower() or "edit" in user_input.lower():
            intent_type = IntentType.EDIT_FILE
            confidence = 0.90
            language = Language.PYTHON
        elif "run" in user_input.lower() or "execute" in user_input.lower():
            intent_type = IntentType.EXECUTE_CODE
            confidence = 0.80
            language = Language.PYTHON
        elif "fix" in user_input.lower() or "debug" in user_input.lower():
            intent_type = IntentType.DEBUG_CODE
            confidence = 0.75
            language = Language.PYTHON
        else:
            intent_type = IntentType.HELP
            confidence = 0.50
            language = None
        
        print(f"   Intent Type: {intent_type.value}")
        print(f"   Confidence: {confidence:.2f}")
        print(f"   Language: {language.value if language else 'Not specified'}")
        
        # Extract target files if mentioned
        if "utils.py" in user_input:
            print(f"   Target Files: ['utils.py']")
        elif "sorting" in user_input:
            print(f"   Target Files: ['sorting_function.py']")


def simulate_code_generation():
    """Simulate code generation."""
    print("\n💻 2. Code Generation Demo")
    print("-" * 30)
    
    # Simulate generating a quicksort function
    print("\n🔧 Generating Python quicksort function...")
    
    sample_code = '''def quicksort(arr):
    """
    Sort an array using the quicksort algorithm.
    
    Args:
        arr: List of comparable elements
        
    Returns:
        Sorted list
    """
    if len(arr) <= 1:
        return arr
    
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    return quicksort(left) + middle + quicksort(right)


def test_quicksort():
    """Test the quicksort function with sample data."""
    test_cases = [
        [3, 6, 8, 10, 1, 2, 1],
        [64, 34, 25, 12, 22, 11, 90],
        [5, 2, 8, 1, 9],
        [],
        [1],
        [2, 1]
    ]
    
    print("Testing quicksort function:")
    for i, test_case in enumerate(test_cases):
        result = quicksort(test_case.copy())
        print(f"Test {i+1}: {test_case} -> {result}")


if __name__ == "__main__":
    test_quicksort()'''
    
    print("✅ Generated quicksort.py")
    print("📝 Code Preview:")
    print("-" * 20)
    preview = sample_code[:300] + "..." if len(sample_code) > 300 else sample_code
    print(preview)


def simulate_execution():
    """Simulate code execution."""
    print("\n🚀 3. Code Execution Demo")
    print("-" * 30)
    
    print("\n🔧 Executing quicksort function in sandbox...")
    print("📊 Execution Results:")
    print("   Success: ✅ Yes")
    print("   Exit Code: 0")
    print("   Execution Time: 0.05s")
    print("   Memory Usage: 2.1MB")
    
    print("\n📤 Output:")
    print("-" * 10)
    print("Testing quicksort function:")
    print("Test 1: [3, 6, 8, 10, 1, 2, 1] -> [1, 1, 2, 3, 6, 8, 10]")
    print("Test 2: [64, 34, 25, 12, 22, 11, 90] -> [11, 12, 22, 25, 34, 64, 90]")
    print("Test 3: [5, 2, 8, 1, 9] -> [1, 2, 5, 8, 9]")
    print("Test 4: [] -> []")
    print("Test 5: [1] -> [1]")
    print("Test 6: [2, 1] -> [1, 2]")


def simulate_file_management():
    """Simulate file management operations."""
    print("\n📁 4. File Management Demo")
    print("-" * 30)
    
    print("\n💾 File Operations:")
    print("   ✅ Created: quicksort.py")
    print("   ✅ Created backup: .coding_agent_backups/20250127_120000_quicksort.py")
    print("   ✅ Git commit: 'Add quicksort implementation'")
    
    print("\n📋 Current Project Files:")
    print("   - quicksort.py (new)")
    print("   - README.md")
    print("   - requirements.txt")


def simulate_session_management():
    """Simulate session management."""
    print("\n🧠 5. Session Management Demo")
    print("-" * 30)
    
    print("\n📊 Session State:")
    print("   Session ID: session_20250127_120000")
    print("   Duration: 00:02:15")
    print("   Total Interactions: 4")
    print("   Files Modified: 1")
    print("   Total Edits: 1")
    
    print("\n💬 Conversation History:")
    print("   1. 'Create a Python function for quicksort algorithm'")
    print("   2. 'Add test cases to the function'")
    print("   3. 'Run the code and show me the output'")
    print("   4. 'Create a backup of the file'")


def main():
    """Main demo function."""
    print_banner()
    
    try:
        # Run all demo sections
        simulate_intent_parsing()
        simulate_code_generation()
        simulate_execution()
        simulate_file_management()
        simulate_session_management()
        
        print("\n" + "=" * 50)
        print("🎉 Demo completed successfully!")
        print("=" * 50)
        
        print("\n📋 What you've seen:")
        print("   ✅ Natural language intent parsing")
        print("   ✅ Code generation with best practices")
        print("   ✅ Sandboxed execution simulation")
        print("   ✅ File management with versioning")
        print("   ✅ Context-aware session management")
        
        print("\n🚀 To use the full agent:")
        print("   1. Set up your API keys in .env file")
        print("   2. Install dependencies: pip install -r requirements.txt")
        print("   3. Run: python3 -m coding_agent.cli")
        
        print("\n📚 Resources:")
        print("   - GitHub: https://github.com/Hamzakhan7473/Terminal-based-Coding-agent-")
        print("   - Email: hamzakhan@taxora.ai")
        print("   - LinkedIn: https://www.linkedin.com/in/abuhamzakhan/")
        
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        logger.error(f"Demo failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())



