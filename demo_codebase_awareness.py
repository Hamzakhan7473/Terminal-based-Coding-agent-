#!/usr/bin/env python3
"""
Demo of Codebase Awareness Feature - Like Cursor's Project Knowledge!
"""

import asyncio
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

load_dotenv()
console = Console()


async def demo_codebase_features():
    """Demonstrate codebase awareness features."""
    
    console.print(Panel.fit(
        "[bold cyan]🧠 Codebase Awareness Demo[/bold cyan]\n"
        "[dim]Showing how AI now knows your ENTIRE project - like Cursor![/dim]",
        border_style="cyan"
    ))
    
    from coding_agent.context.codebase_indexer import CodebaseIndexer
    
    # Initialize indexer
    console.print("\n[bold]Step 1: Indexing Codebase[/bold]")
    console.print("[dim]Scanning all Python files in project...[/dim]\n")
    
    indexer = CodebaseIndexer(".")
    stats = indexer.index_codebase()
    
    console.print(f"[green]✓ Indexed {stats['total_files']} files[/green]")
    console.print(f"[green]✓ Found {stats['total_symbols']} symbols (functions, classes)[/green]")
    console.print(f"[dim]Languages: {', '.join(f'{lang} ({count})' for lang, count in stats['languages'].items())}[/dim]")
    
    # Show project summary
    console.print("\n" + "="*70)
    console.print("[bold]Step 2: Project Summary[/bold]")
    console.print("="*70 + "\n")
    
    summary = indexer.get_project_summary()
    console.print(Panel(summary, border_style="green", title="📊 Project Overview"))
    
    # Search for specific code
    console.print("\n" + "="*70)
    console.print("[bold]Step 3: Searching Codebase[/bold]")
    console.print("="*70 + "\n")
    
    search_queries = [
        "CodeGenerator",
        "execute",
        "LLM"
    ]
    
    for query in search_queries:
        console.print(f"\n[cyan]🔍 Search: '{query}'[/cyan]")
        results = indexer.search_codebase(query, limit=3)
        
        if results:
            for result in results:
                file_path = result['file']
                score = result['score']
                info = result['info']
                
                console.print(f"  [bold]→ {file_path}[/bold] [dim](score: {score})[/dim]")
                console.print(f"    [dim]{info['language']} • {info['lines']} lines[/dim]")
                
                # Show symbols
                if 'symbols' in info and info['symbols']:
                    symbols = [s['name'] for s in info['symbols'][:3]]
                    console.print(f"    [green]Contains:[/green] {', '.join(symbols)}")
        else:
            console.print("  [dim]No results[/dim]")
    
    # Find related files
    console.print("\n" + "="*70)
    console.print("[bold]Step 4: File Relationships[/bold]")
    console.print("="*70 + "\n")
    
    test_file = "coding_agent/core/code_generator.py"
    related = indexer.get_related_files(test_file, depth=1)
    
    console.print(f"[cyan]Files related to {test_file}:[/cyan]")
    if related:
        for rel_file in list(related)[:5]:
            console.print(f"  • {rel_file}")
    else:
        console.print("  [dim]No direct relationships found[/dim]")
    
    # Show what AI knows
    console.print("\n" + "="*70)
    console.print("[bold]Step 5: AI Context (What Cursor Sees)[/bold]")
    console.print("="*70 + "\n")
    
    context = indexer.get_full_context("add authentication", max_files=2)
    console.print(Panel(context[:800] + "\n...", border_style="cyan", title="🤖 AI's Knowledge"))
    
    # Save index
    indexer.save_index()
    console.print("\n[green]✓ Index saved to .codebase_index.json[/green]")
    
    # Summary
    console.print("\n" + "="*70)
    console.print("[bold green]✨ Codebase Awareness Features[/bold green]")
    console.print("="*70 + "\n")
    
    features_table = Table()
    features_table.add_column("Feature", style="cyan")
    features_table.add_column("Status", style="green")
    features_table.add_column("Benefit", style="white")
    
    features_table.add_row(
        "Project Indexing",
        "✓ Active",
        "Knows all files & symbols"
    )
    features_table.add_row(
        "Semantic Search",
        "✓ Active",
        "Find code by meaning"
    )
    features_table.add_row(
        "File Relationships",
        "✓ Active",
        "Tracks imports & dependencies"
    )
    features_table.add_row(
        "Context Injection",
        "✓ Active",
        "AI gets project context"
    )
    features_table.add_row(
        "Multi-file Awareness",
        "✓ Active",
        "Suggests related changes"
    )
    
    console.print(features_table)
    
    console.print("\n[bold cyan]🎯 What This Means:[/bold cyan]")
    console.print("  • AI knows your ENTIRE codebase")
    console.print("  • Suggests changes across multiple files")
    console.print("  • Understands your project structure")
    console.print("  • Maintains coding consistency")
    console.print("  • Finds related code automatically")
    
    console.print("\n[bold green]🚀 Just like Cursor, but in your terminal![/bold green]\n")
    
    console.print("[bold]Try these commands in main_agent.py:[/bold]")
    console.print("  • [cyan]codebase[/cyan] - Show project info")
    console.print("  • [cyan]find CodeGenerator[/cyan] - Search for code")
    console.print("  • [cyan]Add authentication to the API[/cyan] - AI uses codebase knowledge!")
    console.print()


if __name__ == "__main__":
    asyncio.run(demo_codebase_features())

