#!/usr/bin/env python3
"""
Enhanced AI Coding Agent with Beautiful Terminal UI
Features: Split-screen, file browser, diffs, live preview
"""

import asyncio
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live

load_dotenv()
console = Console()


class EnhancedCodingAgent:
    """Enhanced agent with beautiful terminal UI."""
    
    def __init__(self):
        self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.conversation_history = []
        self.context = {}
        self.current_file = None
        self.ui = None
        
        # Components
        self.llm_client = None
        self.parser = None
        self.generator = None
        self.executor = None
        self.file_manager = None
        self.codebase_indexer = None
        
    async def initialize(self):
        """Initialize all components."""
        try:
            from coding_agent.utils.llm_client import LLMClientFactory
            from coding_agent.core.intent_parser import IntentParser
            from coding_agent.core.code_generator import CodeGenerator
            from coding_agent.execution.sandbox import SandboxExecutor
            from coding_agent.utils.file_manager import FileManager
            from coding_agent.context.codebase_indexer import CodebaseIndexer
            from coding_agent.cli.enhanced_ui import EnhancedUI
            
            # Initialize UI
            self.ui = EnhancedUI(console)
            
            # Show loading
            console.print("[dim]>> Initializing AI Coding Agent...[/dim]")
            
            # Initialize components
            self.llm_client = LLMClientFactory.create_default_client()
            self.parser = IntentParser(self.llm_client)
            self.file_manager = FileManager(".")
            self.generator = CodeGenerator(self.llm_client, self.file_manager)
            self.executor = SandboxExecutor()
            
            # Index codebase
            console.print("[dim]>> Indexing codebase...[/dim]", end=" ")
            self.codebase_indexer = CodebaseIndexer(".")
            
            if not self.codebase_indexer.load_index():
                stats = self.codebase_indexer.index_codebase()
                self.codebase_indexer.save_index()
                console.print(f"[green]DONE[/green] ({stats['total_files']} files)")
            else:
                console.print("[green]LOADED[/green] (cached)")
            
            console.print("[bold green]>> All systems operational[/bold green]")
            
            return True
            
        except Exception as e:
            console.print(f"[red]✗ Initialization failed: {e}[/red]")
            return False
    
    def print_welcome(self):
        """Print beautiful welcome screen."""
        welcome = Panel.fit(
            "[bold cyan]AI CODING ASSISTANT[/bold cyan]\n\n"
            "[bold]Features:[/bold]\n"
            "  > File browser with tree view\n"
            "  > Visual diffs with colors\n"
            "  > Live code preview\n"
            "  > Complete codebase awareness\n"
            "  > AI-powered code generation\n\n"
            "[dim]Powered by GPT-4 | E2B Sandbox | Production Ready[/dim]",
            border_style="cyan"
        )
        console.print(welcome)
        
        console.print("\n[bold]What can I help you code today?[/bold]")
        console.print("[bold green]> AI has indexed your entire codebase[/bold green]\n")
        
        # Show commands
        commands = [
            ("[cyan]browse[/cyan]", "Show file browser"),
            ("[cyan]edit <file>[/cyan]", "Open and edit file"),
            ("[cyan]diff[/cyan]", "Show changes"),
            ("[cyan]find <query>[/cyan]", "Search codebase"),
            ("[cyan]codebase[/cyan]", "Project overview"),
        ]
        
        console.print("[dim]Quick Commands:[/dim]")
        for cmd, desc in commands:
            console.print(f"  {cmd} - {desc}")
        console.print()
    
    async def handle_browse_command(self):
        """Show file browser."""
        tree = self.ui.render_file_browser(".", self.current_file)
        console.print(Panel(tree, title="[bold cyan]PROJECT FILES", border_style="cyan"))
        
        # Show stats
        files = self.ui.get_file_list(".")
        console.print(f"\n[dim]>> Total: {len(files)} files in project[/dim]")
    
    async def handle_edit_command(self, file_path: str):
        """Open file for editing."""
        if not Path(file_path).exists():
            self.ui.show_notification(f"File not found: {file_path}", "error")
            return
        
        self.current_file = file_path
        
        # Show file content
        content_panel = self.ui.render_file_content(file_path)
        console.print(content_panel)
        
        # Get context
        if self.codebase_indexer:
            context = self.codebase_indexer.get_context_for_file(file_path)
            console.print(Panel(context, title="[bold blue]FILE CONTEXT", border_style="blue", expand=False))
        
        console.print(f"[green]>> Opened: {file_path}[/green]")
    
    async def handle_diff_command(self, old_content: str, new_content: str, file_path: str):
        """Show diff between versions."""
        # Unified diff
        diff_panel = self.ui.render_diff(old_content, new_content, file_path)
        console.print(diff_panel)
        
        # Ask if user wants side-by-side
        show_side = Prompt.ask("\nShow side-by-side comparison?", choices=["y", "n"], default="n")
        if show_side == "y":
            table = self.ui.render_side_by_side_diff(old_content, new_content)
            console.print("\n")
            console.print(table)
    
    async def handle_code_generation(self, user_input: str):
        """Handle code generation with live preview."""
        console.print("[cyan]>> AI is generating code...[/cyan]")
        
        # Parse intent
        intent = self.parser.parse_intent(user_input, self.context)
        
        # Get codebase context
        codebase_context = ""
        if self.codebase_indexer:
            codebase_context = self.codebase_indexer.get_full_context(user_input, max_files=3)
        
        # Generate code
        code_edits = self.generator.generate_code(intent)
        
        if not code_edits:
            console.print("[yellow]WARNING: Could not generate code[/yellow]")
            return
        
        for edit in code_edits:
            # Show live preview
            console.print("\n[bold green]AI GENERATED CODE:[/bold green]")
            preview = self.ui.render_code_preview_panel(edit.content, intent.language.value if intent.language else "python")
            console.print("\n")
            console.print(preview)
            
            # Show related files if any
            if self.codebase_indexer and edit.file_path in self.codebase_indexer.index:
                related = self.codebase_indexer.get_related_files(edit.file_path, depth=1)
                if related:
                    console.print(f"\n[dim]>> Related files: {', '.join(list(related)[:3])}[/dim]")
            
            # Ask to save
            save = Prompt.ask(
                f"\n[bold]Save to {edit.file_path}?[/bold]",
                choices=["y", "n", "d"],
                default="y"
            )
            
            if save == "d":
                # Show diff if file exists
                if Path(edit.file_path).exists():
                    with open(edit.file_path, 'r') as f:
                        old_content = f.read()
                    await self.handle_diff_command(old_content, edit.content, edit.file_path)
                    save = Prompt.ask("[bold]Apply changes?[/bold]", choices=["y", "n"], default="y")
            
            if save == "y":
                success = self.file_manager.write_file(edit.file_path, edit.content)
                if success:
                    console.print(f"[bold green]>> SAVED: {edit.file_path}[/bold green]")
                    self.current_file = edit.file_path
                    
                    # Ask to execute if Python
                    if edit.file_path.endswith('.py'):
                        execute = Prompt.ask("[bold]Execute this code?[/bold]", choices=["y", "n"], default="n")
                        if execute == "y":
                            await self.execute_code(edit.content)
                else:
                    console.print(f"[bold red]>> ERROR: Failed to save {edit.file_path}[/bold red]")
    
    async def execute_code(self, code: str):
        """Execute code with nice output."""
        console.print("\n[cyan]>> Executing in secure sandbox...[/cyan]")
        
        result = await self.executor.execute_code(code, "python")
        
        # Show results
        if result.success:
            console.print(f"\n[bold green]>> EXECUTION COMPLETED[/bold green] [dim]({result.execution_time:.2f}s)[/dim]")
        else:
            console.print(f"\n[bold red]>> EXECUTION FAILED[/bold red] [dim]({result.execution_time:.2f}s)[/dim]")
        
        if result.stdout:
            console.print(Panel(result.stdout, title="[bold green]OUTPUT", border_style="green"))
        
        if result.stderr:
            console.print(Panel(result.stderr, title="[bold red]ERRORS", border_style="red"))
    
    def get_status_info(self) -> dict:
        """Get current status information."""
        indexed_files = len(self.codebase_indexer.index) if self.codebase_indexer else 0
        
        return {
            'session_id': self.session_id,
            'current_file': self.current_file,
            'messages': len(self.conversation_history),
            'indexed_files': indexed_files
        }
    
    async def run(self):
        """Main run loop with enhanced UI."""
        if not await self.initialize():
            return
        
        self.print_welcome()
        
        try:
            while True:
                try:
                    # Show status bar
                    status = self.ui.render_status_bar(self.get_status_info())
                    console.print(status)
                    
                    # Get user input
                    user_input = Prompt.ask("\n[bold blue]You[/bold blue]").strip()
                    
                    if not user_input:
                        continue
                    
                    # Handle commands
                    if user_input.lower() in ['exit', 'quit', 'bye']:
                        self.ui.show_notification("Thanks for using Enhanced AI Agent!", "info")
                        break
                    
                    if user_input.lower() == 'clear':
                        self.ui.clear_screen()
                        self.print_welcome()
                        continue
                    
                    if user_input.lower() == 'browse':
                        await self.handle_browse_command()
                        continue
                    
                    if user_input.lower().startswith('edit '):
                        file_path = user_input[5:].strip()
                        await self.handle_edit_command(file_path)
                        continue
                    
                    if user_input.lower() == 'codebase':
                        if self.codebase_indexer:
                            summary = self.codebase_indexer.get_project_summary()
                            console.print(Panel(summary, title="[bold cyan]CODEBASE OVERVIEW", border_style="cyan"))
                        continue
                    
                    if user_input.lower().startswith('find '):
                        query = user_input[5:].strip()
                        if self.codebase_indexer:
                            results = self.codebase_indexer.search_codebase(query, limit=10)
                            if results:
                                console.print(f"\n[cyan]>> Search results for '{query}': {len(results)} found[/cyan]\n")
                                for i, result in enumerate(results, 1):
                                    console.print(f"{i}. [bold]{result['file']}[/bold] [dim](relevance: {result['score']})[/dim]")
                            else:
                                console.print("[yellow]>> No results found[/yellow]")
                        continue
                    
                    if user_input.lower() == 'help':
                        help_panel = self.ui.render_help_sidebar()
                        console.print(help_panel)
                        continue
                    
                    # Handle as code generation request
                    await self.handle_code_generation(user_input)
                    
                except KeyboardInterrupt:
                    console.print("\n[yellow]Interrupted[/yellow]")
                    continue
                    
        except Exception as e:
            console.print(f"\n[red]✗ Fatal error: {e}[/red]")
        finally:
            # Cleanup
            if self.executor:
                await self.executor.terminate_sandbox()


async def main():
    """Entry point."""
    agent = EnhancedCodingAgent()
    await agent.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Goodbye![/yellow]")

