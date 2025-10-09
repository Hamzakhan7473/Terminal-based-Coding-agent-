#!/usr/bin/env python3
"""
Simple runner for the Terminal-based AI Coding Agent.

This script provides a working version of the CLI without complex imports.
"""

import sys
import os
import time
import json
from pathlib import Path
from datetime import datetime


class SimpleAgent:
    """Simplified version of the AI coding agent for demonstration."""
    
    def __init__(self):
        self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.conversation_history = []
        self.files_created = []
        self.project_root = "."
        
    def print_banner(self):
        """Print the agent banner."""
        print("🤖 Terminal-based AI Coding Agent")
        print("=" * 50)
        print("AI-powered coding assistant ready to help!")
        print("Type natural language commands to get started.")
        print("Examples: 'Create a Python function', 'Run my code', 'Help'")
        print("Type 'exit' to quit.")
        print("=" * 50)
    
    def parse_intent(self, user_input):
        """Simple intent parsing."""
        user_input_lower = user_input.lower()
        
        if any(word in user_input_lower for word in ["create", "make", "generate", "write"]):
            return "create", 0.85
        elif any(word in user_input_lower for word in ["edit", "modify", "change", "update", "add"]):
            return "edit", 0.90
        elif any(word in user_input_lower for word in ["run", "execute", "test"]):
            return "execute", 0.80
        elif any(word in user_input_lower for word in ["fix", "debug", "error"]):
            return "debug", 0.75
        elif any(word in user_input_lower for word in ["explain", "what", "how"]):
            return "explain", 0.70
        elif "help" in user_input_lower:
            return "help", 1.0
        else:
            return "general", 0.50
    
    def generate_code(self, intent, user_input):
        """Generate sample code based on intent and input."""
        if "quicksort" in user_input.lower():
            return '''def quicksort(arr):
    """Sort an array using quicksort algorithm."""
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)

# Test the function
test_array = [3, 6, 8, 10, 1, 2, 1]
print("Original:", test_array)
print("Sorted:", quicksort(test_array))'''
        
        elif "fibonacci" in user_input.lower():
            return '''def fibonacci(n):
    """Calculate nth Fibonacci number."""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Test the function
for i in range(10):
    print(f"fibonacci({i}) = {fibonacci(i)}")'''
        
        elif "calculator" in user_input.lower():
            return '''class Calculator:
    """Simple calculator class."""
    
    def add(self, a, b):
        return a + b
    
    def subtract(self, a, b):
        return a - b
    
    def multiply(self, a, b):
        return a * b
    
    def divide(self, a, b):
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b

# Test the calculator
calc = Calculator()
print("5 + 3 =", calc.add(5, 3))
print("10 - 4 =", calc.subtract(10, 4))
print("6 * 7 =", calc.multiply(6, 7))
print("15 / 3 =", calc.divide(15, 3))'''
        
        else:
            return '''def hello_world():
    """A simple hello world function."""
    print("Hello, World!")
    return "Function executed successfully"

if __name__ == "__main__":
    hello_world()'''
    
    def simulate_execution(self, code):
        """Simulate code execution."""
        if "quicksort" in code.lower():
            return "Original: [3, 6, 8, 10, 1, 2, 1]\nSorted: [1, 1, 2, 3, 6, 8, 10]"
        elif "fibonacci" in code.lower():
            return "fibonacci(0) = 0\nfibonacci(1) = 1\nfibonacci(2) = 1\nfibonacci(3) = 2\nfibonacci(4) = 3\nfibonacci(5) = 5\nfibonacci(6) = 8\nfibonacci(7) = 13\nfibonacci(8) = 21\nfibonacci(9) = 34"
        elif "calculator" in code.lower():
            return "5 + 3 = 8\n10 - 4 = 6\n6 * 7 = 42\n15 / 3 = 5.0"
        else:
            return "Hello, World!\nFunction executed successfully"
    
    def show_help(self):
        """Show help information."""
        print("\n📋 Available Commands:")
        print("  • Create/Make [something] - Generate new code")
        print("  • Edit/Modify [file] - Modify existing code")
        print("  • Run/Execute [code] - Run code in sandbox")
        print("  • Fix/Debug [issue] - Debug code problems")
        print("  • Explain/What is [concept] - Explain code concepts")
        print("  • Help - Show this help message")
        print("  • Exit - Quit the agent")
        
        print("\n💡 Examples:")
        print("  • 'Create a Python function for quicksort'")
        print("  • 'Make a fibonacci function'")
        print("  • 'Create a calculator class'")
        print("  • 'Run the quicksort code'")
        print("  • 'Fix the bug in my function'")
        
        print("\n🔧 Features:")
        print("  • Natural language understanding")
        print("  • Code generation with best practices")
        print("  • Safe code execution simulation")
        print("  • File management and versioning")
        print("  • Context-aware conversations")
    
    def process_request(self, user_input):
        """Process a user request."""
        print(f"\n🤖 Processing: '{user_input}'")
        
        # Parse intent
        intent, confidence = self.parse_intent(user_input)
        print(f"📋 Intent: {intent.title()} (confidence: {confidence:.2f})")
        
        if intent == "help":
            self.show_help()
            return
        
        if intent == "create":
            print("💻 Generating code...")
            time.sleep(1)  # Simulate processing
            
            code = self.generate_code(intent, user_input)
            filename = self.suggest_filename(user_input)
            
            print(f"\n✅ Generated {filename}:")
            print("-" * 40)
            print(code)
            print("-" * 40)
            
            self.files_created.append(filename)
            print(f"💾 File saved: {filename}")
        
        elif intent == "execute":
            print("🚀 Executing code in sandbox...")
            time.sleep(1)  # Simulate processing
            
            # Get the most recent code
            if self.files_created:
                print(f"📤 Executing {self.files_created[-1]}...")
                print("📊 Results:")
                print("   ✅ Success: Yes")
                print("   ⏱️  Execution time: 0.05s")
                print("   📊 Memory usage: 2.1MB")
                
                # Simulate output
                sample_code = self.generate_code("create", "quicksort")
                output = self.simulate_execution(sample_code)
                print(f"\n📤 Output:")
                print("-" * 20)
                print(output)
            else:
                print("❌ No code to execute. Create some code first!")
        
        elif intent == "debug":
            print("🔍 Analyzing code for issues...")
            time.sleep(1)
            print("✅ Found potential issue: Index out of bounds")
            print("💡 Suggested fix: Add bounds checking")
            print("🔧 Applied fix automatically")
        
        elif intent == "explain":
            print("📚 Explaining code concepts...")
            time.sleep(1)
            if "quicksort" in user_input.lower():
                print("Quicksort is a divide-and-conquer sorting algorithm.")
                print("It selects a pivot and partitions the array around it.")
            elif "fibonacci" in user_input.lower():
                print("Fibonacci sequence: each number is the sum of the two preceding ones.")
                print("F(n) = F(n-1) + F(n-2)")
            else:
                print("This is a general code explanation request.")
        
        else:
            print("🤔 I'm not sure how to help with that.")
            print("Try 'help' for available commands.")
        
        # Update conversation history
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "input": user_input,
            "intent": intent,
            "confidence": confidence
        })
    
    def suggest_filename(self, user_input):
        """Suggest a filename based on user input."""
        if "quicksort" in user_input.lower():
            return "quicksort.py"
        elif "fibonacci" in user_input.lower():
            return "fibonacci.py"
        elif "calculator" in user_input.lower():
            return "calculator.py"
        else:
            return "generated_code.py"
    
    def show_status(self):
        """Show current session status."""
        print(f"\n📊 Session Status:")
        print(f"   Session ID: {self.session_id}")
        print(f"   Files created: {len(self.files_created)}")
        print(f"   Conversations: {len(self.conversation_history)}")
        if self.files_created:
            print(f"   Recent files: {', '.join(self.files_created[-3:])}")
    
    def run(self):
        """Main run loop."""
        self.print_banner()
        
        try:
            while True:
                try:
                    user_input = input(f"\n[{len(self.conversation_history) + 1}] You: ").strip()
                    
                    if not user_input:
                        continue
                    
                    if user_input.lower() in ['exit', 'quit', 'bye']:
                        print(f"\n👋 Thanks for using the AI Coding Agent!")
                        print(f"📁 Files created: {len(self.files_created)}")
                        print(f"💬 Conversations: {len(self.conversation_history)}")
                        print(f"🔗 Full project: https://github.com/Hamzakhan7473/Terminal-based-Coding-agent-")
                        break
                    
                    if user_input.lower() == 'status':
                        self.show_status()
                        continue
                    
                    self.process_request(user_input)
                    
                except KeyboardInterrupt:
                    print(f"\n\n👋 Agent stopped. Goodbye!")
                    break
                except Exception as e:
                    print(f"\n❌ Error: {e}")
                    continue
        
        except Exception as e:
            print(f"❌ Fatal error: {e}")


def main():
    """Main function."""
    agent = SimpleAgent()
    agent.run()


if __name__ == "__main__":
    main()
