"""Main CLI interface for the coding agent."""

import click
import asyncio
import sys
from typing import Optional, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..core.intent_parser import IntentParser
from ..core.code_generator import CodeGenerator
from ..execution.sandbox import SandboxExecutor
from ..context.session_manager import SessionManager
from ..utils.llm_client import LLMClientFactory
from ..utils.file_manager import FileManager
from ..utils.logger import get_logger, setup_rich_logging

console = Console()
logger = get_logger(__name__)


class CLIInterface:
    """Main CLI interface for the coding agent."""
    
    def __init__(self):
        self.console = console
        self.session_manager = None
        self.intent_parser = None
        self.code_generator = None
        self.sandbox_executor = None
        self.file_manager = None
        
    async def initialize(self, project_root: str = "."):
        """Initialize the CLI with all components."""
        try:
            # Setup rich logging
            setup_rich_logging()
            
            # Initialize file manager
            self.file_manager = FileManager(project_root)
            
            # Initialize LLM client
            llm_client = LLMClientFactory.create_default_client()
            
            # Initialize components
            self.intent_parser = IntentParser(llm_client)
            self.code_generator = CodeGenerator(llm_client, self.file_manager)
            self.sandbox_executor = SandboxExecutor()
            self.session_manager = SessionManager(project_root)
            
            self.console.print(Panel.fit(
                "[bold green]🤖 Terminal-based AI Coding Agent[/bold green]\n"
                "[dim]Ready to help you code with natural language![/dim]",
                border_style="green"
            ))
            
            return True
            
        except Exception as e:
            self.console.print(f"[bold red]❌ Initialization failed: {e}[/bold red]")
            return False
    
    async def run_interactive(self):
        """Run interactive CLI session."""
        if not await self.initialize():
            return
        
        self.console.print("\n[bold cyan]💡 Type your coding request in natural language...[/bold cyan]")
        self.console.print("[dim]Examples:[/dim]")
        self.console.print("  • 'Create a Python function for quicksort'")
        self.console.print("  • 'Add error handling to utils.py'")
        self.console.print("  • 'Run the code and show me the output'")
        self.console.print("  • 'Help' for available commands\n")
        
        try:
            while True:
                try:
                    # Get user input
                    user_input = Prompt.ask("\n[bold blue]You[/bold blue]")
                    
                    if user_input.lower() in ['exit', 'quit', 'bye']:
                        break
                    
                    if not user_input.strip():
                        continue
                    
                    # Process the request
                    await self.process_request(user_input)
                    
                except KeyboardInterrupt:
                    self.console.print("\n[yellow]👋 Goodbye![/yellow]")
                    break
                except Exception as e:
                    self.console.print(f"[red]❌ Error: {e}[/red]")
                    logger.error(f"Error processing request: {e}")
        
        finally:
            await self.cleanup()
    
    async def process_request(self, user_input: str):
        """Process a single user request."""
        try:
            # Show processing indicator
            with Live(self._create_processing_display(), console=self.console, refresh_per_second=4) as live:
                # Parse intent
                live.update(self._create_processing_display("Parsing intent..."))
                intent = self.intent_parser.parse_intent(user_input, self.session_manager.get_context())
                
                # Generate code if needed
                if intent.intent_type.value in ["create_file", "edit_file", "debug_code", "refactor_code"]:
                    live.update(self._create_processing_display("Generating code..."))
                    code_edits = self.code_generator.generate_code(intent)
                    intent.code_edits = code_edits
                
                # Show parsed intent
                live.stop()
                self._display_intent(intent)
                
                # Execute if needed
                if intent.intent_type.value == "execute_code":
                    await self._execute_code(intent)
                
                # Apply file changes
                if intent.code_edits:
                    await self._apply_file_changes(intent)
                
                # Update session context
                self.session_manager.update_context(intent, user_input)
                
        except Exception as e:
            self.console.print(f"[red]❌ Failed to process request: {e}[/red]")
            logger.error(f"Request processing failed: {e}")
    
    def _create_processing_display(self, message: str = "Processing...") -> Panel:
        """Create processing display."""
        return Panel(
            f"[yellow]{message}[/yellow]\n"
            "[dim]Please wait while I understand your request...[/dim]",
            title="🤖 AI Agent",
            border_style="yellow"
        )
    
    def _display_intent(self, intent):
        """Display parsed intent to user."""
        table = Table(title="📋 Parsed Intent")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Intent Type", intent.intent_type.value)
        table.add_row("Confidence", f"{intent.confidence:.2f}")
        table.add_row("Language", intent.language.value if intent.language else "Not specified")
        table.add_row("Target Files", ", ".join(intent.target_files) if intent.target_files else "None")
        table.add_row("Requires Confirmation", "Yes" if intent.requires_confirmation else "No")
        
        if intent.parameters:
            table.add_row("Parameters", str(intent.parameters))
        
        self.console.print(table)
        
        # Show code edits if any
        if intent.code_edits:
            self.console.print("\n[bold green]📝 Generated Code Changes:[/bold green]")
            for i, edit in enumerate(intent.code_edits, 1):
                self.console.print(f"\n[bold]Edit {i}:[/bold] {edit.file_path}")
                self.console.print(f"[dim]Operation: {edit.operation}[/dim]")
                if edit.description:
                    self.console.print(f"[dim]Description: {edit.description}[/dim]")
                
                # Show code preview
                if edit.content:
                    preview = edit.content[:200] + "..." if len(edit.content) > 200 else edit.content
                    self.console.print(Panel(preview, title="Code Preview", border_style="blue"))
    
    async def _execute_code(self, intent):
        """Execute code in sandbox."""
        try:
            self.console.print("\n[bold yellow]🚀 Executing code in sandbox...[/bold yellow]")
            
            # Determine code to execute
            code = intent.parameters.get("code", "")
            language = intent.language.value if intent.language else "python"
            
            if not code and intent.code_edits:
                # Use the first code edit
                code = intent.code_edits[0].content
            
            if not code:
                self.console.print("[red]❌ No code to execute[/red]")
                return
            
            # Execute in sandbox
            result = await self.sandbox_executor.execute_code(code, language)
            
            # Display results
            self._display_execution_result(result)
            
        except Exception as e:
            self.console.print(f"[red]❌ Execution failed: {e}[/red]")
    
    def _display_execution_result(self, result):
        """Display code execution results."""
        table = Table(title="📊 Execution Results")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Success", "✅ Yes" if result.success else "❌ No")
        table.add_row("Exit Code", str(result.exit_code))
        table.add_row("Execution Time", f"{result.execution_time:.2f}s")
        
        self.console.print(table)
        
        if result.stdout:
            self.console.print("\n[bold green]📤 Output:[/bold green]")
            self.console.print(Panel(result.stdout, border_style="green"))
        
        if result.stderr:
            self.console.print("\n[bold red]📥 Error Output:[/bold red]")
            self.console.print(Panel(result.stderr, border_style="red"))
    
    async def _apply_file_changes(self, intent):
        """Apply file changes to the filesystem."""
        if not intent.code_edits:
            return
        
        # Show confirmation if required
        if intent.requires_confirmation:
            if not Confirm.ask("\n[bold yellow]⚠️  Apply these changes?"):
                self.console.print("[yellow]Changes cancelled by user[/yellow]")
                return
        
        self.console.print("\n[bold green]💾 Applying file changes...[/bold green]")
        
        for edit in intent.code_edits:
            try:
                if edit.operation == "create":
                    success = self.file_manager.write_file(edit.file_path, edit.content)
                elif edit.operation == "replace":
                    success = self.file_manager.write_file(edit.file_path, edit.content)
                elif edit.operation == "delete":
                    success = self.file_manager.delete_file(edit.file_path)
                else:
                    self.console.print(f"[yellow]⚠️  Unknown operation: {edit.operation}[/yellow]")
                    continue
                
                if success:
                    self.console.print(f"[green]✅ {edit.operation.capitalize()}d: {edit.file_path}[/green]")
                else:
                    self.console.print(f"[red]❌ Failed to {edit.operation}: {edit.file_path}[/red]")
                    
            except Exception as e:
                self.console.print(f"[red]❌ Error with {edit.file_path}: {e}[/red]")
    
    async def cleanup(self):
        """Cleanup resources."""
        try:
            if self.sandbox_executor:
                await self.sandbox_executor.terminate_sandbox()
            
            if self.session_manager:
                await self.session_manager.save_session()
            
            self.console.print("[dim]Cleaned up resources[/dim]")
            
        except Exception as e:
            logger.error(f"Cleanup error: {e}")


def main():
    """Main entry point for CLI."""
    cli = CLIInterface()
    
    try:
        asyncio.run(cli.run_interactive())
    except KeyboardInterrupt:
        console.print("\n[yellow]👋 Goodbye![/yellow]")
    except Exception as e:
        console.print(f"[red]❌ Fatal error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
