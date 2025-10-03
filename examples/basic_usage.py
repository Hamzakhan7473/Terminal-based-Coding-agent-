#!/usr/bin/env python3
"""
Basic usage examples for the Terminal-based AI Coding Agent.

This script demonstrates how to use the coding agent programmatically.
"""

import asyncio
import os
from coding_agent import (
    IntentParser, 
    CodeGenerator, 
    SandboxExecutor, 
    SessionManager,
    CLIInterface
)
from coding_agent.utils.llm_client import LLMClientFactory
from coding_agent.utils.file_manager import FileManager


async def example_basic_usage():
    """Example of basic usage of the coding agent."""
    
    # Initialize components
    llm_client = LLMClientFactory.create_default_client()
    file_manager = FileManager()
    intent_parser = IntentParser(llm_client)
    code_generator = CodeGenerator(llm_client, file_manager)
    session_manager = SessionManager()
    
    print("🤖 Terminal-based AI Coding Agent - Basic Usage Example")
    print("=" * 60)
    
    # Example 1: Parse a natural language intent
    print("\n1. Parsing Natural Language Intent:")
    user_input = "Create a Python function for quicksort algorithm"
    intent = intent_parser.parse_intent(user_input)
    
    print(f"Input: {user_input}")
    print(f"Intent Type: {intent.intent_type}")
    print(f"Confidence: {intent.confidence:.2f}")
    print(f"Language: {intent.language}")
    
    # Example 2: Generate code
    print("\n2. Generating Code:")
    code_edits = code_generator.generate_code(intent)
    
    for i, edit in enumerate(code_edits, 1):
        print(f"Edit {i}: {edit.file_path}")
        print(f"Operation: {edit.operation}")
        print(f"Content Preview: {edit.content[:100]}...")
    
    # Example 3: Execute code in sandbox (if E2B is configured)
    if os.getenv("E2B_API_KEY"):
        print("\n3. Executing Code in Sandbox:")
        sandbox = SandboxExecutor()
        
        sample_code = """
def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)

# Test the function
test_array = [3, 6, 8, 10, 1, 2, 1]
print("Original array:", test_array)
print("Sorted array:", quicksort(test_array))
"""
        
        result = await sandbox.execute_code(sample_code, "python")
        
        print(f"Execution Success: {result.success}")
        print(f"Exit Code: {result.exit_code}")
        print(f"Execution Time: {result.execution_time:.2f}s")
        if result.stdout:
            print(f"Output: {result.stdout}")
        if result.stderr:
            print(f"Error: {result.stderr}")
        
        await sandbox.terminate_sandbox()
    else:
        print("\n3. Sandbox Execution:")
        print("⚠️  E2B_API_KEY not configured. Skipping sandbox execution.")
    
    # Example 4: Session management
    print("\n4. Session Management:")
    session_manager.update_context(intent, user_input)
    context = session_manager.get_context()
    
    print(f"Session ID: {context['session_id']}")
    print(f"Current Files: {context['current_files']}")
    print(f"Conversation History: {len(context['conversation_history'])} entries")
    
    # Example 5: File operations
    print("\n5. File Operations:")
    
    # Write a test file
    test_content = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Test the function
for i in range(10):
    print(f"fibonacci({i}) = {fibonacci(i)}")
"""
    
    success = file_manager.write_file("examples/test_fibonacci.py", test_content)
    print(f"File write success: {success}")
    
    # Read the file back
    try:
        content = file_manager.read_file("examples/test_fibonacci.py")
        print(f"File read success: {len(content)} characters")
    except Exception as e:
        print(f"File read error: {e}")
    
    print("\n✅ Basic usage example completed!")


async def example_interactive_session():
    """Example of running an interactive session."""
    
    print("\n🎮 Interactive Session Example:")
    print("=" * 40)
    
    # Initialize CLI interface
    cli = CLIInterface()
    
    # Initialize the CLI (this would normally be done in the main CLI)
    if await cli.initialize("examples/"):
        print("✅ CLI initialized successfully")
        
        # Simulate some interactions
        sample_requests = [
            "Create a simple calculator class",
            "Add error handling to the calculator",
            "Create unit tests for the calculator"
        ]
        
        for request in sample_requests:
            print(f"\n📝 Processing: {request}")
            await cli.process_request(request)
        
        await cli.cleanup()
    else:
        print("❌ Failed to initialize CLI")


if __name__ == "__main__":
    # Run the basic usage example
    asyncio.run(example_basic_usage())
    
    # Uncomment to run interactive session example
    # asyncio.run(example_interactive_session())
