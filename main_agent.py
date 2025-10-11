#!/usr/bin/env python3
"""
Enhanced Terminal-based AI Coding Agent - Like Cursor for Terminal
Full-featured AI assistant with code generation, execution, and intelligent responses.
"""

import asyncio
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.prompt import Prompt

# Load environment
load_dotenv()

console = Console()


class CursorLikeAgent:
    """Advanced AI Coding Agent with Cursor-like capabilities."""
    
    def __init__(self):
        self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.conversation_history = []
        self.context = {}
        self.llm_client = None
        self.parser = None
        self.generator = None
        self.executor = None
        self.file_manager = None
        
    async def initialize(self):
        """Initialize all components."""
        try:
            from coding_agent.utils.llm_client import LLMClientFactory
            from coding_agent.core.intent_parser import IntentParser
            from coding_agent.core.code_generator import CodeGenerator
            from coding_agent.execution.sandbox import SandboxExecutor
            from coding_agent.utils.file_manager import FileManager
            
            # Initialize components
            self.llm_client = LLMClientFactory.create_default_client()
            self.parser = IntentParser(self.llm_client)
            self.file_manager = FileManager(".")
            self.generator = CodeGenerator(self.llm_client, self.file_manager)
            self.executor = SandboxExecutor()
            
            console.print(Panel.fit(
                "[bold cyan]🤖 AI Coding Assistant[/bold cyan]\n"
                "[dim]Powered by GPT-4, E2B Sandbox - Like Cursor for Terminal[/dim]\n"
                "[green]✓[/green] All systems operational",
                border_style="cyan"
            ))
            
            return True
            
        except Exception as e:
            console.print(f"[red]✗ Initialization failed: {e}[/red]")
            return False
    
    def print_banner(self):
        """Print welcome banner."""
        console.print("\n[bold]What can I help you code today?[/bold]")
        console.print("[dim]Examples:[/dim]")
        console.print("  • Create a REST API with Flask")
        console.print("  • Write a function to scrape a website")
        console.print("  • Build a data processing pipeline")
        console.print("  • Implement quicksort algorithm")
        console.print("  • Debug my code / Explain this function")
        console.print("\n[dim]Type 'exit' to quit, 'help' for more info[/dim]\n")
    
    async def process_request(self, user_input: str):
        """Process user request with AI capabilities."""
        
        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })
        
        try:
            # Parse intent
            console.print("\n[dim]🤔 Understanding your request...[/dim]")
            intent = self.parser.parse_intent(user_input, self.context)
            
            # Update context
            self.context['last_intent'] = intent.intent_type.value
            self.context['last_language'] = intent.language.value if intent.language else None
            
            # Handle different intent types
            if intent.intent_type.value == "create_file":
                await self.handle_create_file(user_input, intent)
                
            elif intent.intent_type.value == "execute_code":
                await self.handle_execute_code(user_input, intent)
                
            elif intent.intent_type.value == "edit_file":
                await self.handle_edit_file(user_input, intent)
                
            elif intent.intent_type.value == "debug_code":
                await self.handle_debug_code(user_input, intent)
                
            elif intent.intent_type.value == "explain_code":
                await self.handle_explain_code(user_input, intent)
                
            elif intent.intent_type.value == "help":
                self.show_help()
                
            else:
                # General AI response
                await self.handle_general_query(user_input)
                
        except Exception as e:
            console.print(f"\n[red]✗ Error: {e}[/red]")
            console.print("[yellow]💡 Tip: Try rephrasing your request or use 'help' for guidance[/yellow]")
    
    async def handle_create_file(self, user_input: str, intent):
        """Handle file creation requests."""
        console.print("[cyan]💻 Generating code...[/cyan]")
        
        try:
            # Generate code using AI
            code_edits = self.generator.generate_code(intent)
            
            if not code_edits:
                console.print("[yellow]⚠ Could not generate code. Let me help you differently.[/yellow]")
                await self.handle_general_query(user_input)
                return
            
            for edit in code_edits:
                # Display generated code
                console.print(f"\n[bold green]✓ Generated:[/bold green] [cyan]{edit.file_path}[/cyan]")
                
                if edit.description:
                    console.print(f"[dim]{edit.description}[/dim]\n")
                
                # Show code with syntax highlighting
                language = intent.language.value if intent.language else "python"
                syntax = Syntax(edit.content, language, theme="monokai", line_numbers=True)
                console.print(Panel(syntax, border_style="green", title=f"📄 {edit.file_path}"))
                
                # Ask if user wants to save
                save = Prompt.ask(
                    "\n[bold]Save this file?[/bold]",
                    choices=["y", "n", "e"],
                    default="y"
                )
                
                if save == "y":
                    success = self.file_manager.write_file(edit.file_path, edit.content)
                    if success:
                        console.print(f"[green]✓ Saved to {edit.file_path}[/green]")
                        
                        # Ask if user wants to execute
                        if language == "python":
                            execute = Prompt.ask(
                                "[bold]Run this code?[/bold]",
                                choices=["y", "n"],
                                default="y"
                            )
                            if execute == "y":
                                await self.execute_code_content(edit.content, language)
                    else:
                        console.print(f"[red]✗ Failed to save {edit.file_path}[/red]")
                        
                elif save == "e":
                    console.print("[yellow]Edit mode coming soon. For now, I'll regenerate with modifications.[/yellow]")
                else:
                    console.print("[yellow]File not saved[/yellow]")
                    
        except Exception as e:
            console.print(f"[red]✗ Generation failed: {e}[/red]")
    
    async def handle_execute_code(self, user_input: str, intent):
        """Handle code execution requests."""
        console.print("[cyan]🚀 Preparing to execute...[/cyan]")
        
        # Check if there's code in the intent parameters
        code = intent.parameters.get("code")
        language = intent.language.value if intent.language else "python"
        
        if code:
            await self.execute_code_content(code, language)
        else:
            # Check if there are recent files to execute
            if self.context.get('last_file'):
                file_path = self.context['last_file']
                console.print(f"[dim]Executing {file_path}...[/dim]")
                # Read and execute
                content = self.file_manager.read_file(file_path)
                if content:
                    await self.execute_code_content(content, language)
            else:
                console.print("[yellow]⚠ No code to execute. Please create a file first or provide code.[/yellow]")
    
    async def execute_code_content(self, code: str, language: str = "python"):
        """Execute code content in sandbox."""
        try:
            console.print("\n[cyan]⚡ Executing in secure sandbox...[/cyan]")
            result = await self.executor.execute_code(code, language)
            
            # Display results
            console.print(f"\n[bold]{'✓' if result.success else '✗'} Execution {'Completed' if result.success else 'Failed'}[/bold]")
            console.print(f"[dim]Time: {result.execution_time:.2f}s[/dim]")
            
            if result.stdout:
                console.print(f"\n[bold green]📤 Output:[/bold green]")
                console.print(Panel(result.stdout, border_style="green"))
            
            if result.stderr:
                console.print(f"\n[bold red]📥 Errors:[/bold red]")
                console.print(Panel(result.stderr, border_style="red"))
                
        except Exception as e:
            console.print(f"[red]✗ Execution error: {e}[/red]")
    
    async def handle_edit_file(self, user_input: str, intent):
        """Handle file editing requests."""
        console.print("[cyan]✏️  Editing file...[/cyan]")
        console.print("[yellow]💡 Advanced editing coming soon![/yellow]")
    
    async def handle_debug_code(self, user_input: str, intent):
        """Handle debugging requests."""
        console.print("[cyan]🔍 Analyzing code for issues...[/cyan]")
        
        # Use LLM to analyze and suggest fixes
        prompt = f"""You are an expert debugger. Analyze this request and provide:
1. What the issue likely is
2. How to fix it
3. Corrected code if applicable

User request: {user_input}

Provide a clear, concise response with code examples if needed."""

        response = self.llm_client.generate_response(prompt)
        
        console.print("\n[bold cyan]🔧 Debug Analysis:[/bold cyan]")
        md = Markdown(response)
        console.print(Panel(md, border_style="cyan"))
    
    async def handle_explain_code(self, user_input: str, intent):
        """Handle code explanation requests."""
        console.print("[cyan]📚 Explaining...[/cyan]")
        
        prompt = f"""Explain this code or concept clearly and concisely:

{user_input}

Provide:
1. What it does
2. How it works
3. Key concepts
4. Example usage if relevant"""

        response = self.llm_client.generate_response(prompt)
        
        console.print("\n[bold cyan]💡 Explanation:[/bold cyan]")
        md = Markdown(response)
        console.print(Panel(md, border_style="cyan"))
    
    async def handle_general_query(self, user_input: str):
        """Handle general coding queries with AI."""
        console.print("[cyan]🤖 AI Assistant responding...[/cyan]")
        
        # Build context-aware prompt
        context_str = ""
        if self.context.get('last_language'):
            context_str += f"Working with {self.context['last_language']}. "
        
        prompt = f"""You are an expert coding assistant. Help with this request:

{user_input}

{context_str}

Provide clear, actionable code and explanations. Use markdown formatting."""

        response = self.llm_client.generate_response(prompt)
        
        console.print("\n[bold cyan]🤖 Assistant:[/bold cyan]")
        md = Markdown(response)
        console.print(Panel(md, border_style="cyan"))
    
    def show_help(self):
        """Show help information."""
        help_text = """
# 🤖 AI Coding Assistant Help

## What I Can Do

**Code Generation**
- "Create a REST API with Flask"
- "Write a binary search function"
- "Build a web scraper"

**Code Execution**
- "Run this code"
- "Execute the file"
- "Test this function"

**Debugging**
- "Fix the bug in my code"
- "Why is this throwing an error?"
- "Debug this function"

**Code Explanation**
- "Explain how quicksort works"
- "What does this code do?"
- "How does recursion work?"

**General Help**
- "How do I connect to a database?"
- "Best way to handle errors in Python"
- "Explain async/await"

## Tips
- Be specific about what you want
- Mention the programming language if not Python
- I maintain context across our conversation
- All code runs in a secure sandbox

## Commands
- `help` - Show this help
- `status` - Show session info  
- `clear` - Clear screen
- `exit` - Quit assistant
"""
        md = Markdown(help_text)
        console.print(Panel(md, border_style="cyan", title="📖 Help"))
    
    def show_status(self):
        """Show session status."""
        console.print(f"\n[bold cyan]📊 Session Status[/bold cyan]")
        console.print(f"Session ID: [dim]{self.session_id}[/dim]")
        console.print(f"Messages: [dim]{len(self.conversation_history)}[/dim]")
        if self.context.get('last_language'):
            console.print(f"Working with: [dim]{self.context['last_language']}[/dim]")
        console.print()
    
    async def run(self):
        """Main run loop."""
        if not await self.initialize():
            return
        
        self.print_banner()
        
        try:
            while True:
                try:
                    # Get user input
                    user_input = Prompt.ask("\n[bold blue]You[/bold blue]").strip()
                    
                    if not user_input:
                        continue
                    
                    # Handle special commands
                    if user_input.lower() in ['exit', 'quit', 'bye']:
                        console.print("\n[cyan]👋 Thanks for using AI Coding Assistant![/cyan]")
                        console.print(f"[dim]Session: {len(self.conversation_history)} messages[/dim]\n")
                        break
                    
                    if user_input.lower() == 'clear':
                        console.clear()
                        self.print_banner()
                        continue
                    
                    if user_input.lower() == 'status':
                        self.show_status()
                        continue
                    
                    if user_input.lower() == 'help':
                        self.show_help()
                        continue
                    
                    # Process the request
                    await self.process_request(user_input)
                    
                except KeyboardInterrupt:
                    console.print("\n\n[yellow]⚠ Interrupted. Type 'exit' to quit.[/yellow]")
                    continue
                    
        except Exception as e:
            console.print(f"\n[red]✗ Fatal error: {e}[/red]")
        finally:
            # Cleanup
            if self.executor:
                await self.executor.terminate_sandbox()


async def main():
    """Entry point."""
    agent = CursorLikeAgent()
    await agent.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Goodbye![/yellow]")

