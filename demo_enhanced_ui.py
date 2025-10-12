#!/usr/bin/env python3
"""
Demo of Enhanced Terminal UI Features
Shows: File browser, diffs, live preview, split-screen
"""

import asyncio
from rich.console import Console
from rich.panel import Panel
from pathlib import Path

console = Console()


async def demo_enhanced_ui():
    """Demonstrate all enhanced UI features."""
    
    console.print(Panel.fit(
        "[bold cyan]🎨 Enhanced Terminal UI Demo[/bold cyan]\n"
        "[dim]Showcasing IDE-like features in terminal[/dim]",
        border_style="cyan"
    ))
    
    from coding_agent.cli.enhanced_ui import EnhancedUI
    
    ui = EnhancedUI(console)
    
    # Demo 1: File Browser
    console.print("\n" + "="*70)
    console.print("[bold]Demo 1: File Browser with Tree View[/bold]")
    console.print("="*70 + "\n")
    
    tree = ui.render_file_browser(".", current_file="main_agent.py")
    console.print(Panel(tree, title="📁 Project Explorer", border_style="cyan"))
    
    ui.show_notification("File browser shows project structure!", "info")
    await asyncio.sleep(1)
    
    # Demo 2: File Content Viewer
    console.print("\n" + "="*70)
    console.print("[bold]Demo 2: Syntax Highlighted File Viewer[/bold]")
    console.print("="*70 + "\n")
    
    test_file = "coding_agent/__init__.py"
    if Path(test_file).exists():
        content_panel = ui.render_file_content(test_file)
        console.print(content_panel)
    
    ui.show_notification(f"Opened: {test_file}", "success")
    await asyncio.sleep(1)
    
    # Demo 3: Diff View
    console.print("\n" + "="*70)
    console.print("[bold]Demo 3: Visual Diff with Colors[/bold]")
    console.print("="*70 + "\n")
    
    old_code = """def hello():
    print("Hello")
    return True"""
    
    new_code = """def hello(name="World"):
    \"\"\"Greet someone by name.\"\"\"
    print(f"Hello, {name}!")
    return True"""
    
    diff_panel = ui.render_diff(old_code, new_code, "example.py")
    console.print(diff_panel)
    
    ui.show_notification("Diff shows changes clearly!", "info")
    await asyncio.sleep(1)
    
    # Demo 4: Side-by-Side Comparison
    console.print("\n" + "="*70)
    console.print("[bold]Demo 4: Side-by-Side Comparison[/bold]")
    console.print("="*70 + "\n")
    
    table = ui.render_side_by_side_diff(old_code, new_code)
    console.print(table)
    
    await asyncio.sleep(1)
    
    # Demo 5: Live Code Preview
    console.print("\n" + "="*70)
    console.print("[bold]Demo 5: Live Code Preview (as AI generates)[/bold]")
    console.print("="*70 + "\n")
    
    generated_code = """import requests
from bs4 import BeautifulSoup

def scrape_titles(url):
    \"\"\"Scrape product titles from a webpage.\"\"\"
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        titles = soup.find_all('h2', class_='product-title')
        return [title.text.strip() for title in titles]
    
    except Exception as e:
        print(f"Error: {e}")
        return []

if __name__ == "__main__":
    url = "https://example.com/products"
    titles = scrape_titles(url)
    for i, title in enumerate(titles, 1):
        print(f"{i}. {title}")"""
    
    preview = ui.render_code_preview_panel(generated_code, "python")
    console.print(preview)
    
    ui.show_notification("Live preview as AI generates!", "success")
    await asyncio.sleep(1)
    
    # Demo 6: Command Palette
    console.print("\n" + "="*70)
    console.print("[bold]Demo 6: Command Palette[/bold]")
    console.print("="*70 + "\n")
    
    commands = [
        ("Ctrl+P", "Quick open file"),
        ("Ctrl+Shift+F", "Search in files"),
        ("Ctrl+B", "Toggle file browser"),
        ("Ctrl+`", "Toggle terminal"),
        ("Ctrl+G", "Go to line"),
    ]
    
    palette = ui.render_command_palette(commands)
    console.print(palette)
    
    await asyncio.sleep(1)
    
    # Demo 7: Status Bar
    console.print("\n" + "="*70)
    console.print("[bold]Demo 7: Status Bar[/bold]")
    console.print("="*70 + "\n")
    
    status_info = {
        'session_id': 'session_20241012_123456',
        'current_file': 'main_agent.py',
        'messages': 42,
        'indexed_files': 28
    }
    
    status_bar = ui.render_status_bar(status_info)
    console.print(status_bar)
    
    await asyncio.sleep(1)
    
    # Demo 8: File List
    console.print("\n" + "="*70)
    console.print("[bold]Demo 8: Selectable File List[/bold]")
    console.print("="*70 + "\n")
    
    files = ui.get_file_list(".")
    file_list = ui.render_file_list(files[:10], current_index=3)
    console.print(file_list)
    
    await asyncio.sleep(1)
    
    # Demo 9: Notifications
    console.print("\n" + "="*70)
    console.print("[bold]Demo 9: Toast Notifications[/bold]")
    console.print("="*70 + "\n")
    
    ui.show_notification("This is an info notification", "info")
    await asyncio.sleep(0.5)
    ui.show_notification("Success! Code saved", "success")
    await asyncio.sleep(0.5)
    ui.show_notification("Warning: Large file detected", "warning")
    await asyncio.sleep(0.5)
    ui.show_notification("Error: File not found", "error")
    
    await asyncio.sleep(1)
    
    # Demo 10: Help Sidebar
    console.print("\n" + "="*70)
    console.print("[bold]Demo 10: Help Sidebar[/bold]")
    console.print("="*70 + "\n")
    
    help_panel = ui.render_help_sidebar()
    console.print(help_panel)
    
    # Summary
    console.print("\n" + "="*70)
    console.print("[bold green]✨ Enhanced UI Features Summary[/bold green]")
    console.print("="*70 + "\n")
    
    features = [
        ("📁 File Browser", "Tree view with icons, current file highlighting"),
        ("🎨 Syntax Highlighting", "Beautiful code display with line numbers"),
        ("🔄 Visual Diffs", "Colored unified and side-by-side diffs"),
        ("💻 Live Preview", "Real-time code preview as AI generates"),
        ("⌨️  Command Palette", "Quick access to all commands"),
        ("📊 Status Bar", "Session info, file stats, codebase size"),
        ("📋 File Lists", "Selectable, navigable file lists"),
        ("🔔 Notifications", "Toast-style status messages"),
        ("💡 Help Sidebar", "Context-sensitive help"),
        ("🎯 Context Panels", "Show relevant file and project info")
    ]
    
    for feature, desc in features:
        console.print(f"  {feature}")
        console.print(f"    [dim]{desc}[/dim]")
    
    console.print("\n[bold cyan]🎯 What This Means:[/bold cyan]")
    console.print("  • Professional IDE-like experience in terminal")
    console.print("  • Visual feedback for all operations")
    console.print("  • Easy navigation and file management")
    console.print("  • Clear diff visualization")
    console.print("  • Live code preview")
    
    console.print("\n[bold green]🚀 Much better than basic terminal![/bold green]\n")
    
    console.print("[bold]Try the enhanced agent:[/bold]")
    console.print("  [cyan]python3 enhanced_agent.py[/cyan]")
    console.print()
    
    console.print("[dim]Commands to try:[/dim]")
    console.print("  • [cyan]browse[/cyan] - See file tree")
    console.print("  • [cyan]edit main_agent.py[/cyan] - View file with syntax highlighting")
    console.print("  • [cyan]Create a web scraper[/cyan] - See live code preview")
    console.print("  • [cyan]diff[/cyan] - View changes with colors")
    console.print()


if __name__ == "__main__":
    asyncio.run(demo_enhanced_ui())

