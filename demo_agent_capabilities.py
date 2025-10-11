#!/usr/bin/env python3
"""
Demo showing what the AI Coding Assistant can do - Like Cursor for Terminal
"""

import asyncio
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.syntax import Syntax

load_dotenv()
console = Console()


async def demo():
    """Demonstrate agent capabilities."""
    
    console.print(Panel.fit(
        "[bold cyan]🤖 AI Coding Assistant - Capabilities Demo[/bold cyan]\n"
        "[dim]Showing what the assistant can do - Like Cursor for Terminal[/dim]",
        border_style="cyan"
    ))
    
    from coding_agent.utils.llm_client import LLMClientFactory
    from coding_agent.core.intent_parser import IntentParser
    from coding_agent.core.code_generator import CodeGenerator
    from coding_agent.execution.sandbox import SandboxExecutor
    from coding_agent.utils.file_manager import FileManager
    
    llm_client = LLMClientFactory.create_default_client()
    parser = IntentParser(llm_client)
    file_manager = FileManager(".")
    generator = CodeGenerator(llm_client, file_manager)
    executor = SandboxExecutor()
    
    # Demo 1: Code Generation
    console.print("\n" + "="*70)
    console.print("[bold cyan]Demo 1: AI Code Generation[/bold cyan]")
    console.print("="*70)
    
    request1 = "Create a Python function to calculate fibonacci numbers recursively"
    console.print(f"\n[bold blue]You:[/bold blue] {request1}")
    console.print("[dim]🤔 Understanding request...[/dim]")
    
    intent1 = parser.parse_intent(request1, {})
    console.print(f"[green]✓ Intent:[/green] {intent1.intent_type.value}")
    
    console.print("[cyan]💻 Generating code...[/cyan]")
    code_edits1 = generator.generate_code(intent1)
    
    if code_edits1:
        for edit in code_edits1:
            console.print(f"\n[bold green]✓ Generated:[/bold green] [cyan]{edit.file_path}[/cyan]")
            syntax = Syntax(edit.content, "python", theme="monokai", line_numbers=True)
            console.print(Panel(syntax, border_style="green", title="📄 Generated Code"))
    
    # Demo 2: Code Execution
    console.print("\n" + "="*70)
    console.print("[bold cyan]Demo 2: Code Execution in Sandbox[/bold cyan]")
    console.print("="*70)
    
    test_code = """
# Calculate factorial
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

# Test it
for i in range(1, 8):
    print(f"factorial({i}) = {factorial(i)}")
"""
    
    console.print("\n[bold blue]You:[/bold blue] Run this factorial code")
    syntax2 = Syntax(test_code, "python", theme="monokai", line_numbers=True)
    console.print(Panel(syntax2, border_style="blue", title="📝 Code to Execute"))
    
    console.print("\n[cyan]⚡ Executing in secure sandbox...[/cyan]")
    result = await executor.execute_code(test_code, "python")
    
    console.print(f"\n[bold green]✓ Execution Completed[/bold green]")
    console.print(f"[dim]Time: {result.execution_time:.2f}s[/dim]")
    console.print(f"\n[bold green]📤 Output:[/bold green]")
    console.print(Panel(result.stdout, border_style="green"))
    
    # Demo 3: AI Explanation
    console.print("\n" + "="*70)
    console.print("[bold cyan]Demo 3: Code Explanation[/bold cyan]")
    console.print("="*70)
    
    request3 = "Explain how the quicksort algorithm works"
    console.print(f"\n[bold blue]You:[/bold blue] {request3}")
    console.print("[cyan]🤖 AI Assistant responding...[/cyan]\n")
    
    explanation_prompt = """Explain quicksort algorithm concisely:
1. How it works
2. Time complexity
3. Simple example

Keep it under 200 words."""
    
    explanation = llm_client.generate_response(explanation_prompt)
    md = Markdown(explanation)
    console.print(Panel(md, border_style="cyan", title="💡 AI Explanation"))
    
    # Demo 4: Complex Code Generation
    console.print("\n" + "="*70)
    console.print("[bold cyan]Demo 4: Complex Task - REST API[/bold cyan]")
    console.print("="*70)
    
    request4 = "Create a simple Flask REST API with GET and POST endpoints"
    console.print(f"\n[bold blue]You:[/bold blue] {request4}")
    console.print("[dim]🤔 Understanding request...[/dim]")
    
    intent4 = parser.parse_intent(request4, {})
    console.print(f"[green]✓ Intent:[/green] {intent4.intent_type.value}")
    
    console.print("[cyan]💻 Generating Flask API code...[/cyan]")
    code_edits4 = generator.generate_code(intent4)
    
    if code_edits4:
        for edit in code_edits4:
            console.print(f"\n[bold green]✓ Generated:[/bold green] [cyan]{edit.file_path}[/cyan]")
            syntax4 = Syntax(edit.content[:500] + "\n..." if len(edit.content) > 500 else edit.content, 
                           "python", theme="monokai", line_numbers=True)
            console.print(Panel(syntax4, border_style="green", title="📄 Flask API Code"))
    
    # Cleanup
    await executor.terminate_sandbox()
    
    # Summary
    console.print("\n" + "="*70)
    console.print("[bold green]✨ Agent Capabilities Summary[/bold green]")
    console.print("="*70)
    
    capabilities = """
# 🤖 AI Coding Assistant - Like Cursor for Terminal

## What It Can Do:

✅ **Intelligent Code Generation**
   - Understands natural language requests
   - Generates production-quality code
   - Supports multiple languages (Python, JavaScript, etc.)

✅ **Secure Code Execution**
   - Runs code in E2B sandbox
   - Real-time output display
   - Error handling and debugging

✅ **AI-Powered Assistance**
   - Code explanations
   - Debugging help
   - Best practices suggestions
   - Context-aware responses

✅ **File Management**
   - Create, edit, save files
   - Version control integration
   - Project organization

## To Use Interactively:

Run in your terminal:
```bash
python3 main_agent.py
```

Then ask questions like:
- "Create a web scraper with BeautifulSoup"
- "Write a function to process CSV files"
- "Build a REST API with authentication"
- "Explain how decorators work"
- "Debug this code: [paste your code]"

**It's like having Cursor's AI in your terminal!** 🚀
"""
    
    md_summary = Markdown(capabilities)
    console.print(Panel(md_summary, border_style="cyan", title="📖 Full Capabilities"))
    
    console.print("\n[bold cyan]💡 Ready to try it yourself?[/bold cyan]")
    console.print("[dim]Run:[/dim] [bold]python3 main_agent.py[/bold]\n")


if __name__ == "__main__":
    asyncio.run(demo())

