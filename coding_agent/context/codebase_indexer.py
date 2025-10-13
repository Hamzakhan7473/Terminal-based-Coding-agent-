"""
Codebase indexer for project-wide context awareness.
This gives the AI complete knowledge of your codebase - like Cursor!
"""

import os
import ast
import json
from pathlib import Path
from typing import Dict, List, Set, Any, Optional
from datetime import datetime
import hashlib

from ..utils.logger import get_logger

logger = get_logger(__name__)


class CodebaseIndexer:
    """Indexes entire codebase for AI context awareness."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.index: Dict[str, Any] = {}
        self.file_relationships: Dict[str, Set[str]] = {}
        self.symbols_map: Dict[str, List[str]] = {}  # symbol -> files
        self.last_indexed = None
        
        # Files/dirs to ignore
        self.ignore_patterns = {
            '__pycache__', '.git', '.venv', 'venv', 'node_modules',
            '.env', '.pyc', '.so', '.dylib', '.egg-info', 'dist',
            'build', '.DS_Store', '.pytest_cache', '.mypy_cache'
        }
        
        self.code_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp',
            '.c', '.h', '.hpp', '.cs', '.go', '.rs', '.rb', '.php',
            '.swift', '.kt', '.scala', '.sh', '.bash', '.sql'
        }
    
    def index_codebase(self) -> Dict[str, Any]:
        """
        Index entire codebase.
        Returns summary of indexed files.
        """
        logger.info(f"Indexing codebase at {self.project_root}")
        
        self.index = {}
        self.file_relationships = {}
        self.symbols_map = {}
        
        indexed_count = 0
        
        for file_path in self._walk_files():
            try:
                self._index_file(file_path)
                indexed_count += 1
            except Exception as e:
                logger.warning(f"Failed to index {file_path}: {e}")
        
        self.last_indexed = datetime.now()
        
        logger.info(f"Indexed {indexed_count} files")
        
        return {
            'total_files': indexed_count,
            'total_symbols': len(self.symbols_map),
            'languages': self._get_language_stats(),
            'last_indexed': self.last_indexed.isoformat()
        }
    
    def _walk_files(self):
        """Walk through all code files in project."""
        for root, dirs, files in os.walk(self.project_root):
            # Filter out ignored directories
            dirs[:] = [d for d in dirs if d not in self.ignore_patterns]
            
            root_path = Path(root)
            
            for file in files:
                file_path = root_path / file
                
                # Skip ignored patterns
                if any(pattern in str(file_path) for pattern in self.ignore_patterns):
                    continue
                
                # Only index code files
                if file_path.suffix in self.code_extensions:
                    yield file_path
    
    def _index_file(self, file_path: Path):
        """Index a single file."""
        relative_path = str(file_path.relative_to(self.project_root))
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.warning(f"Could not read {file_path}: {e}")
            return
        
        # Create file entry
        file_info = {
            'path': relative_path,
            'size': len(content),
            'lines': content.count('\n') + 1,
            'language': self._detect_language(file_path),
            'hash': hashlib.md5(content.encode()).hexdigest(),
            'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
        }
        
        # Extract symbols (functions, classes, etc.)
        if file_path.suffix == '.py':
            symbols = self._extract_python_symbols(content, relative_path)
            file_info['symbols'] = symbols
            
            # Build symbol map
            for symbol in symbols:
                symbol_name = symbol['name']
                if symbol_name not in self.symbols_map:
                    self.symbols_map[symbol_name] = []
                self.symbols_map[symbol_name].append(relative_path)
        
        # Extract imports/dependencies
        imports = self._extract_imports(content, file_path.suffix)
        file_info['imports'] = imports
        
        # Build file relationships
        self.file_relationships[relative_path] = set(imports)
        
        self.index[relative_path] = file_info
    
    def _detect_language(self, file_path: Path) -> str:
        """Detect programming language from file extension."""
        ext_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.go': 'go',
            '.rs': 'rust',
            '.rb': 'ruby',
            '.php': 'php',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.sh': 'bash'
        }
        return ext_map.get(file_path.suffix, 'unknown')
    
    def _extract_python_symbols(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Extract functions and classes from Python code."""
        symbols = []
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    symbols.append({
                        'type': 'function',
                        'name': node.name,
                        'line': node.lineno,
                        'docstring': ast.get_docstring(node)
                    })
                elif isinstance(node, ast.ClassDef):
                    symbols.append({
                        'type': 'class',
                        'name': node.name,
                        'line': node.lineno,
                        'docstring': ast.get_docstring(node)
                    })
        except SyntaxError:
            pass
        
        return symbols
    
    def _extract_imports(self, content: str, extension: str) -> List[str]:
        """Extract imports/dependencies from code."""
        imports = []
        
        if extension == '.py':
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports.append(node.module)
            except SyntaxError:
                pass
        elif extension in ['.js', '.ts', '.jsx', '.tsx']:
            # Simple regex-based extraction for JS/TS
            import re
            import_pattern = r'import\s+.*?\s+from\s+[\'"](.+?)[\'"]'
            imports = re.findall(import_pattern, content)
        
        return imports
    
    def _get_language_stats(self) -> Dict[str, int]:
        """Get statistics about languages in codebase."""
        stats = {}
        for file_info in self.index.values():
            lang = file_info['language']
            stats[lang] = stats.get(lang, 0) + 1
        return stats
    
    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific file."""
        return self.index.get(file_path)
    
    def find_symbol(self, symbol_name: str) -> List[str]:
        """Find which files contain a specific symbol."""
        return self.symbols_map.get(symbol_name, [])
    
    def get_related_files(self, file_path: str, depth: int = 2) -> Set[str]:
        """
        Get files related to the given file through imports.
        depth controls how many levels of relationships to traverse.
        """
        if file_path not in self.file_relationships:
            return set()
        
        related = set()
        to_explore = {file_path}
        explored = set()
        
        for _ in range(depth):
            next_level = set()
            for current_file in to_explore:
                if current_file in explored:
                    continue
                explored.add(current_file)
                
                # Add direct imports
                if current_file in self.file_relationships:
                    imports = self.file_relationships[current_file]
                    related.update(imports)
                    next_level.update(imports)
            
            to_explore = next_level
        
        return related
    
    def search_codebase(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search codebase for files/symbols matching query.
        Simple text-based search (can be enhanced with embeddings later).
        """
        results = []
        query_lower = query.lower()
        
        # Search in file paths
        for file_path, file_info in self.index.items():
            score = 0
            
            # Match in file path
            if query_lower in file_path.lower():
                score += 10
            
            # Match in symbols
            if 'symbols' in file_info:
                for symbol in file_info['symbols']:
                    if query_lower in symbol['name'].lower():
                        score += 5
                    if symbol.get('docstring') and query_lower in symbol['docstring'].lower():
                        score += 2
            
            if score > 0:
                results.append({
                    'file': file_path,
                    'score': score,
                    'info': file_info
                })
        
        # Sort by score and limit
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:limit]
    
    def get_project_summary(self) -> str:
        """Get a summary of the project for AI context."""
        if not self.index:
            return "Project not indexed yet."
        
        total_files = len(self.index)
        total_lines = sum(f['lines'] for f in self.index.values())
        lang_stats = self._get_language_stats()
        
        summary = f"""Project Structure:
- Total files: {total_files}
- Total lines: {total_lines:,}
- Languages: {', '.join(f'{lang} ({count})' for lang, count in lang_stats.items())}
- Total symbols: {len(self.symbols_map)}

Key files identified:
"""
        
        # Add top 5 largest files
        largest_files = sorted(
            self.index.items(),
            key=lambda x: x[1]['lines'],
            reverse=True
        )[:5]
        
        for file_path, info in largest_files:
            summary += f"- {file_path} ({info['lines']} lines, {info['language']})\n"
        
        return summary
    
    def get_context_for_file(self, file_path: str) -> str:
        """Get relevant context for a specific file."""
        if file_path not in self.index:
            return f"File {file_path} not found in index."
        
        file_info = self.index[file_path]
        context = f"\nFile: {file_path}\n"
        context += f"Language: {file_info['language']}\n"
        context += f"Lines: {file_info['lines']}\n"
        
        # Add symbols
        if 'symbols' in file_info and file_info['symbols']:
            context += "\nSymbols defined:\n"
            for symbol in file_info['symbols'][:10]:  # Limit to 10
                context += f"- {symbol['type']} {symbol['name']} (line {symbol['line']})\n"
        
        # Add imports
        if file_info['imports']:
            context += f"\nImports: {', '.join(file_info['imports'][:10])}\n"
        
        # Add related files
        related = self.get_related_files(file_path, depth=1)
        if related:
            context += f"\nRelated files: {', '.join(list(related)[:5])}\n"
        
        return context
    
    def get_full_context(self, query: str = "", max_files: int = 5) -> str:
        """
        Get full codebase context for AI.
        If query provided, focuses on relevant files.
        """
        context = self.get_project_summary()
        
        if query:
            # Search for relevant files
            relevant_files = self.search_codebase(query, limit=max_files)
            
            if relevant_files:
                context += "\n\nRelevant files for your query:\n"
                for result in relevant_files:
                    file_path = result['file']
                    context += f"\n{self.get_context_for_file(file_path)}"
        
        return context
    
    def save_index(self, output_file: str = ".codebase_index.json"):
        """Save index to file for faster loading."""
        index_data = {
            'index': self.index,
            'file_relationships': {k: list(v) for k, v in self.file_relationships.items()},
            'symbols_map': self.symbols_map,
            'last_indexed': self.last_indexed.isoformat() if self.last_indexed else None
        }
        
        output_path = self.project_root / output_file
        with open(output_path, 'w') as f:
            json.dump(index_data, f, indent=2)
        
        logger.info(f"Index saved to {output_path}")
    
    def load_index(self, input_file: str = ".codebase_index.json") -> bool:
        """Load index from file."""
        input_path = self.project_root / input_file
        
        if not input_path.exists():
            return False
        
        try:
            with open(input_path, 'r') as f:
                index_data = json.load(f)
            
            self.index = index_data['index']
            self.file_relationships = {k: set(v) for k, v in index_data['file_relationships'].items()}
            self.symbols_map = index_data['symbols_map']
            self.last_indexed = datetime.fromisoformat(index_data['last_indexed']) if index_data['last_indexed'] else None
            
            logger.info(f"Index loaded from {input_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load index: {e}")
            return False

