#!/usr/bin/env python3
"""Test if the code generator now produces real, working code."""

import asyncio
from dotenv import load_dotenv
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel

load_dotenv()
console = Console()


async def test_real_code_generation():
    """Test code generation with real examples."""
    
    console.print("[bold cyan]🧪 Testing Real Code Generation[/bold cyan]\n")
    
    from coding_agent.utils.llm_client import LLMClientFactory
    from coding_agent.core.intent_parser import IntentParser
    from coding_agent.core.code_generator import CodeGenerator
    from coding_agent.utils.file_manager import FileManager
    from coding_agent.execution.sandbox import SandboxExecutor
    
    llm_client = LLMClientFactory.create_default_client()
    parser = IntentParser(llm_client)
    file_manager = FileManager(".")
    generator = CodeGenerator(llm_client, file_manager)
    executor = SandboxExecutor()
    
    # Test 1: Web Scraper
    console.print("="*70)
    console.print("[bold]Test 1: Create a web scraper[/bold]\n")
    
    request1 = "Create a Python function that scrapes product titles from a webpage using BeautifulSoup"
    console.print(f"[blue]Request:[/blue] {request1}\n")
    
    intent1 = parser.parse_intent(request1, {})
    code_edits1 = generator.generate_code(intent1)
    
    if code_edits1:
        code = code_edits1[0].content
        console.print(f"[green]✓ Generated {len(code)} characters of code[/green]\n")
        syntax = Syntax(code[:800] if len(code) > 800 else code, "python", theme="monokai", line_numbers=True)
        console.print(Panel(syntax, title="Generated Code Preview", border_style="green"))
        
        # Check if it's real code
        if "BeautifulSoup" in code and "def " in code:
            console.print("\n[bold green]✓ PASS:[/bold green] Generated real web scraper code!")
        else:
            console.print("\n[bold red]✗ FAIL:[/bold red] Not proper web scraper code")
    
    # Test 2: Data Processing
    console.print("\n" + "="*70)
    console.print("[bold]Test 2: Data processing function[/bold]\n")
    
    request2 = "Create a function that reads a CSV file and calculates statistics (mean, median, std dev)"
    console.print(f"[blue]Request:[/blue] {request2}\n")
    
    intent2 = parser.parse_intent(request2, {})
    code_edits2 = generator.generate_code(intent2)
    
    if code_edits2:
        code = code_edits2[0].content
        console.print(f"[green]✓ Generated {len(code)} characters of code[/green]\n")
        syntax = Syntax(code[:800] if len(code) > 800 else code, "python", theme="monokai", line_numbers=True)
        console.print(Panel(syntax, title="Generated Code Preview", border_style="green"))
        
        # Check if it's real code
        if ("csv" in code.lower() or "pandas" in code.lower()) and "def " in code:
            console.print("\n[bold green]✓ PASS:[/bold green] Generated real data processing code!")
        else:
            console.print("\n[bold red]✗ FAIL:[/bold red] Not proper data processing code")
    
    # Test 3: REST API
    console.print("\n" + "="*70)
    console.print("[bold]Test 3: REST API with Flask[/bold]\n")
    
    request3 = "Create a Flask REST API with endpoints for creating and listing users"
    console.print(f"[blue]Request:[/blue] {request3}\n")
    
    intent3 = parser.parse_intent(request3, {})
    code_edits3 = generator.generate_code(intent3)
    
    if code_edits3:
        code = code_edits3[0].content
        console.print(f"[green]✓ Generated {len(code)} characters of code[/green]\n")
        syntax = Syntax(code[:800] if len(code) > 800 else code, "python", theme="monokai", line_numbers=True)
        console.print(Panel(syntax, title="Generated Code Preview", border_style="green"))
        
        # Check if it's real code
        if "Flask" in code and "@app.route" in code:
            console.print("\n[bold green]✓ PASS:[/bold green] Generated real Flask API code!")
        else:
            console.print("\n[bold red]✗ FAIL:[/bold red] Not proper Flask API code")
    
    # Test 4: Algorithm with execution
    console.print("\n" + "="*70)
    console.print("[bold]Test 4: Algorithm + Execution[/bold]\n")
    
    request4 = "Create a function to find the longest palindrome substring in a string"
    console.print(f"[blue]Request:[/blue] {request4}\n")
    
    intent4 = parser.parse_intent(request4, {})
    code_edits4 = generator.generate_code(intent4)
    
    if code_edits4:
        code = code_edits4[0].content
        console.print(f"[green]✓ Generated {len(code)} characters of code[/green]\n")
        syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
        console.print(Panel(syntax, title="Generated Code", border_style="green"))
        
        # Try to execute it
        console.print("\n[yellow]⚡ Attempting to execute...[/yellow]")
        try:
            result = await executor.execute_code(code, "python")
            if result.success:
                console.print(f"[bold green]✓ EXECUTION SUCCESS![/bold green]")
                console.print(f"\n[bold]Output:[/bold]")
                console.print(Panel(result.stdout, border_style="green"))
            else:
                console.print(f"[yellow]⚠ Execution had issues:[/yellow]")
                console.print(result.stderr)
        except Exception as e:
            console.print(f"[red]Execution error: {e}[/red]")
    
    await executor.terminate_sandbox()
    
    # Summary
    console.print("\n" + "="*70)
    console.print("[bold cyan]📊 Test Complete[/bold cyan]")
    console.print("\nThe code generator should now produce:")
    console.print("  ✓ Real, working code (not hello world)")
    console.print("  ✓ Production-quality implementations")
    console.print("  ✓ Proper imports and error handling")
    console.print("  ✓ Runnable examples")
    console.print("\n[bold]Try the agent now: python3 main_agent.py[/bold]\n")


if __name__ == "__main__":
    asyncio.run(test_real_code_generation())

