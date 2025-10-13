"""
Enhanced Terminal UI - Makes the terminal experience more like an IDE.
Provides split-screen, file browser, diffs, and better visuals.
"""

import os
from pathlib import Path
from typing import List, Optional, Tuple
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.tree import Tree
from rich.table import Table
from rich.syntax import Syntax
from rich.text import Text
from rich.live import Live
from difflib import unified_diff

from ..utils.logger import get_logger

logger = get_logger(__name__)


class EnhancedUI:
    """Enhanced terminal UI with IDE-like features."""
    
    def __init__(self, console: Console):
        self.console = console
        self.current_file = None
        self.file_content = None
        self.ignore_patterns = {
            '__pycache__', '.git', '.venv', 'venv', 'node_modules',
            '.env', '.DS_Store', '.pytest_cache'
        }
    
    def create_split_layout(self) -> Layout:
        """Create split-screen layout."""
        layout = Layout()
        
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=3)
        )
        
        layout["main"].split_row(
            Layout(name="sidebar", ratio=1),
            Layout(name="content", ratio=3)
        )
        
        return layout
    
    def render_file_browser(self, root_path: str = ".", current_file: Optional[str] = None) -> Tree:
        """Render file browser tree."""
        root = Path(root_path)
        tree = Tree(
            f"📁 [bold cyan]{root.name or 'Project'}[/bold cyan]",
            guide_style="dim"
        )
        
        self._build_tree(tree, root, current_file, max_depth=3)
        return tree
    
    def _build_tree(self, tree: Tree, path: Path, current_file: Optional[str], 
                    max_depth: int, current_depth: int = 0):
        """Recursively build file tree."""
        if current_depth >= max_depth:
            return
        
        try:
            items = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name))
        except PermissionError:
            return
        
        for item in items:
            # Skip ignored patterns
            if any(pattern in str(item) for pattern in self.ignore_patterns):
                continue
            
            # Determine icon and style
            if item.is_dir():
                icon = "📁"
                style = "bold blue"
                branch = tree.add(f"{icon} [{style}]{item.name}[/{style}]")
                self._build_tree(branch, item, current_file, max_depth, current_depth + 1)
            else:
                # File icon based on extension
                icon = self._get_file_icon(item.suffix)
                style = "cyan" if str(item) == current_file else "white"
                marker = "→ " if str(item) == current_file else ""
                tree.add(f"{marker}{icon} [{style}]{item.name}[/{style}]")
    
    def _get_file_icon(self, extension: str) -> str:
        """Get icon for file type."""
        icons = {
            '.py': '🐍',
            '.js': '📜',
            '.ts': '📘',
            '.html': '🌐',
            '.css': '🎨',
            '.json': '📋',
            '.md': '📝',
            '.yml': '⚙️',
            '.yaml': '⚙️',
            '.txt': '📄',
            '.sh': '⚡',
        }
        return icons.get(extension, '📄')
    
    def render_file_content(self, file_path: str, highlight_lines: Optional[List[int]] = None) -> Panel:
        """Render file content with syntax highlighting."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Detect language from extension
            ext = Path(file_path).suffix
            lang_map = {
                '.py': 'python',
                '.js': 'javascript',
                '.ts': 'typescript',
                '.html': 'html',
                '.css': 'css',
                '.json': 'json',
                '.md': 'markdown',
                '.sh': 'bash',
                '.yml': 'yaml',
                '.yaml': 'yaml'
            }
            language = lang_map.get(ext, 'text')
            
            # Create syntax highlighted content
            syntax = Syntax(
                content,
                language,
                theme="monokai",
                line_numbers=True,
                word_wrap=False,
                highlight_lines=set(highlight_lines) if highlight_lines else None
            )
            
            return Panel(
                syntax,
                title=f"[bold cyan]FILE: {file_path}",
                border_style="cyan",
                subtitle=f"[dim]{len(content)} chars | {content.count(chr(10)) + 1} lines | {language}[/dim]"
            )
        except Exception as e:
            return Panel(
                f"[red]Error reading file: {e}[/red]",
                title=f"[bold red]ERROR: {file_path}",
                border_style="red"
            )
    
    def render_diff(self, old_content: str, new_content: str, file_path: str) -> Panel:
        """Render side-by-side diff with colors."""
        old_lines = old_content.splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)
        
        diff = list(unified_diff(
            old_lines,
            new_lines,
            fromfile=f"{file_path} (original)",
            tofile=f"{file_path} (modified)",
            lineterm=''
        ))
        
        # Colorize diff
        colored_diff = []
        for line in diff:
            if line.startswith('+++') or line.startswith('---'):
                colored_diff.append(f"[bold cyan]{line}[/bold cyan]")
            elif line.startswith('@@'):
                colored_diff.append(f"[bold blue]{line}[/bold blue]")
            elif line.startswith('+'):
                colored_diff.append(f"[green]{line}[/green]")
            elif line.startswith('-'):
                colored_diff.append(f"[red]{line}[/red]")
            else:
                colored_diff.append(f"[dim]{line}[/dim]")
        
        diff_text = '\n'.join(colored_diff)
        
        return Panel(
            diff_text,
            title=f"[bold yellow]DIFF: {file_path}",
            border_style="yellow",
            subtitle="[green]+[/green] additions | [red]-[/red] deletions"
        )
    
    def render_side_by_side_diff(self, old_content: str, new_content: str) -> Table:
        """Render side-by-side comparison."""
        old_lines = old_content.splitlines()
        new_lines = new_content.splitlines()
        
        table = Table(show_header=True, header_style="bold cyan", expand=True)
        table.add_column("Original", style="dim", width=50)
        table.add_column("Modified", style="white", width=50)
        
        max_lines = max(len(old_lines), len(new_lines))
        
        for i in range(min(max_lines, 20)):  # Limit to 20 lines for display
            old_line = old_lines[i] if i < len(old_lines) else ""
            new_line = new_lines[i] if i < len(new_lines) else ""
            
            # Highlight differences
            if old_line != new_line:
                if old_line:
                    old_style = "[red]"
                else:
                    old_style = "[dim]"
                if new_line:
                    new_style = "[green]"
                else:
                    new_style = "[dim]"
            else:
                old_style = "[dim]"
                new_style = "[dim]"
            
            table.add_row(
                f"{old_style}{old_line[:80]}...[/]" if len(old_line) > 80 else f"{old_style}{old_line}[/]",
                f"{new_style}{new_line[:80]}...[/]" if len(new_line) > 80 else f"{new_style}{new_line}[/]"
            )
        
        if max_lines > 20:
            table.add_row("[dim]...[/dim]", f"[dim]... ({max_lines - 20} more lines)[/dim]")
        
        return table
    
    def render_file_list(self, files: List[str], current_index: int = 0) -> Table:
        """Render selectable file list."""
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("File", style="white")
        
        for i, file_path in enumerate(files):
            icon = self._get_file_icon(Path(file_path).suffix)
            if i == current_index:
                table.add_row(f"→ {icon} [bold cyan]{file_path}[/bold cyan]")
            else:
                table.add_row(f"  {icon} [dim]{file_path}[/dim]")
        
        return Panel(table, title="📁 Files", border_style="blue")
    
    def render_command_palette(self, commands: List[Tuple[str, str]]) -> Panel:
        """Render command palette with shortcuts."""
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Key", style="bold cyan", width=15)
        table.add_column("Command", style="white")
        
        for key, command in commands:
            table.add_row(key, command)
        
        return Panel(
            table,
            title="⌨️  Commands",
            border_style="cyan",
            subtitle="[dim]Press key to execute[/dim]"
        )
    
    def render_status_bar(self, info: dict) -> Panel:
        """Render status bar with session info."""
        status_text = Text()
        
        # Session info
        status_text.append("Session: ", style="cyan")
        status_text.append(f"{info.get('session_id', 'N/A')[:12]}", style="dim")
        status_text.append(" | ", style="dim")
        
        # File info
        if info.get('current_file'):
            status_text.append("File: ", style="cyan")
            status_text.append(info['current_file'], style="white")
            status_text.append(" | ", style="dim")
        
        # Messages
        status_text.append("Messages: ", style="cyan")
        status_text.append(f"{info.get('messages', 0)}", style="dim")
        status_text.append(" | ", style="dim")
        
        # Codebase
        if info.get('indexed_files'):
            status_text.append("Indexed: ", style="cyan")
            status_text.append(f"{info['indexed_files']} files", style="dim")
        
        return Panel(
            status_text,
            border_style="blue",
            height=3
        )
    
    def render_loading_spinner(self, message: str = "Processing...") -> Panel:
        """Render loading animation."""
        return Panel(
            f"[yellow]⏳ {message}[/yellow]\n[dim]Please wait...[/dim]",
            border_style="yellow"
        )
    
    def show_notification(self, message: str, style: str = "info"):
        """Show toast-like notification."""
        styles = {
            'info': ('cyan', 'ℹ️'),
            'success': ('green', '✓'),
            'warning': ('yellow', '⚠️'),
            'error': ('red', '✗')
        }
        
        color, icon = styles.get(style, styles['info'])
        
        self.console.print(
            Panel(
                f"{icon} {message}",
                border_style=color,
                padding=(0, 2)
            )
        )
    
    def render_code_preview_panel(self, code: str, language: str = "python") -> Panel:
        """Render live code preview as AI generates."""
        syntax = Syntax(
            code,
            language,
            theme="monokai",
            line_numbers=True
        )
        
        return Panel(
            syntax,
            title="[bold green]>> AI GENERATED CODE",
            border_style="green",
            subtitle="[dim]Ready to save[/dim]"
        )
    
    def clear_screen(self):
        """Clear terminal screen."""
        self.console.clear()
    
    def render_help_sidebar(self) -> Panel:
        """Render help sidebar with tips."""
        help_text = """
[bold cyan]Quick Commands:[/bold cyan]

[bold]File Operations:[/bold]
• [cyan]edit <file>[/cyan] - Open file
• [cyan]save[/cyan] - Save changes
• [cyan]close[/cyan] - Close file

[bold]Navigation:[/bold]
• [cyan]find <query>[/cyan] - Search
• [cyan]codebase[/cyan] - Browse
• [cyan]back[/cyan] - Previous view

[bold]AI:[/bold]
• Just type your request!
• [cyan]help[/cyan] - Show help
• [cyan]exit[/cyan] - Quit

[dim]Tip: Use tab for completion[/dim]
"""
        return Panel(
            help_text,
            title="💡 Help",
            border_style="cyan"
        )
    
    def get_file_list(self, directory: str = ".") -> List[str]:
        """Get list of files in directory."""
        files = []
        root = Path(directory)
        
        for item in root.rglob("*"):
            if item.is_file():
                # Skip ignored patterns
                if any(pattern in str(item) for pattern in self.ignore_patterns):
                    continue
                files.append(str(item.relative_to(root)))
        
        return sorted(files)
    
    def render_context_panel(self, context: dict) -> Panel:
        """Render current context information."""
        table = Table(show_header=False, box=None)
        table.add_column("Key", style="cyan")
        table.add_column("Value", style="white")
        
        for key, value in context.items():
            if isinstance(value, (list, dict)):
                value = str(len(value)) + " items"
            table.add_row(key, str(value))
        
        return Panel(
            table,
            title="🔍 Context",
            border_style="blue"
        )

