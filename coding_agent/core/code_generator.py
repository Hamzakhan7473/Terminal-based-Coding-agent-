"""Code generation module for creating and modifying code."""

import os
import ast
from typing import Dict, List, Optional, Any, Tuple
from .models import UserIntent, CodeEdit, Language
from ..utils.llm_client import LLMClient
from ..utils.logger import get_logger
from ..utils.file_manager import FileManager

logger = get_logger(__name__)


class CodeGenerator:
    """Generates and modifies code based on user intents."""
    
    def __init__(self, llm_client: LLMClient, file_manager: FileManager):
        self.llm_client = llm_client
        self.file_manager = file_manager
        self.code_templates = self._load_code_templates()
    
    def _load_code_templates(self) -> Dict[str, Dict[str, str]]:
        """Load code templates for different languages and patterns."""
        return {
            "python": {
                "function": "def {name}({params}):\n    \"\"\"{docstring}\"\"\"\n    {body}\n",
                "class": "class {name}:\n    \"\"\"{docstring}\"\"\"\n    \n    def __init__(self{params}):\n        {init_body}\n",
                "main": "if __name__ == \"__main__\":\n    {body}\n",
                "import": "import {module}\n",
                "test": "import unittest\n\nclass Test{name}(unittest.TestCase):\n    def test_{method}(self):\n        {body}\n"
            },
            "javascript": {
                "function": "function {name}({params}) {{\n    {body}\n}}\n",
                "class": "class {name} {{\n    constructor({params}) {{\n        {init_body}\n    }}\n}}\n",
                "async_function": "async function {name}({params}) {{\n    {body}\n}}\n",
                "arrow_function": "const {name} = ({params}) => {{\n    {body}\n}};\n"
            },
            "typescript": {
                "interface": "interface {name} {{\n    {properties}\n}}\n",
                "type": "type {name} = {{\n    {properties}\n}};\n",
                "function": "function {name}({params}): {return_type} {{\n    {body}\n}}\n",
                "class": "class {name} {{\n    {properties}\n    \n    constructor({params}) {{\n        {init_body}\n    }}\n}}\n"
            }
        }
    
    def generate_code(self, intent: UserIntent) -> List[CodeEdit]:
        """
        Generate code based on user intent.
        
        Args:
            intent: Parsed user intent
            
        Returns:
            List of CodeEdit objects
        """
        logger.info(f"Generating code for intent: {intent.intent_type}")
        
        if intent.intent_type.value == "create_file":
            return self._generate_file_creation(intent)
        elif intent.intent_type.value == "edit_file":
            return self._generate_file_edit(intent)
        elif intent.intent_type.value == "execute_code":
            return self._generate_execution_wrapper(intent)
        elif intent.intent_type.value == "debug_code":
            return self._generate_debug_code(intent)
        elif intent.intent_type.value == "test_code":
            return self._generate_test_code(intent)
        elif intent.intent_type.value == "refactor_code":
            return self._generate_refactor_code(intent)
        else:
            logger.warning(f"Unsupported intent type for code generation: {intent.intent_type}")
            return []
    
    def _generate_file_creation(self, intent: UserIntent) -> List[CodeEdit]:
        """Generate code for file creation."""
        edits = []
        
        # Determine target file
        target_file = intent.parameters.get("filename", "new_file.py")
        if not target_file:
            target_file = self._suggest_filename(intent)
        
        # Determine language
        language = intent.language or self._detect_language_from_filename(target_file)
        
        # Generate content using LLM
        content = self._llm_generate_content(intent, language, target_file)
        
        # Create code edit
        edits.append(CodeEdit(
            file_path=target_file,
            content=content,
            operation="create",
            description=f"Create {target_file} based on user request"
        ))
        
        return edits
    
    def _generate_file_edit(self, intent: UserIntent) -> List[CodeEdit]:
        """Generate code edits for file modification."""
        edits = []
        
        target_files = intent.target_files
        if not target_files:
            # Try to extract from parameters
            target_files = [intent.parameters.get("target_file", "")]
        
        for target_file in target_files:
            if not target_file or not os.path.exists(target_file):
                logger.warning(f"Target file not found: {target_file}")
                continue
            
            # Read existing content
            try:
                existing_content = self.file_manager.read_file(target_file)
            except Exception as e:
                logger.error(f"Failed to read file {target_file}: {e}")
                continue
            
            # Generate modifications using LLM
            modifications = self._llm_generate_modifications(
                intent, existing_content, target_file
            )
            
            edits.extend(modifications)
        
        return edits
    
    def _generate_execution_wrapper(self, intent: UserIntent) -> List[CodeEdit]:
        """Generate execution wrapper code."""
        edits = []
        
        # Create a temporary execution script
        script_content = self._create_execution_script(intent)
        
        edits.append(CodeEdit(
            file_path="temp_execution.py",
            content=script_content,
            operation="create",
            description="Temporary execution script"
        ))
        
        return edits
    
    def _generate_debug_code(self, intent: UserIntent) -> List[CodeEdit]:
        """Generate debugging code."""
        edits = []
        
        target_files = intent.target_files
        if not target_files:
            return edits
        
        for target_file in target_files:
            try:
                existing_content = self.file_manager.read_file(target_file)
            except Exception as e:
                logger.error(f"Failed to read file {target_file}: {e}")
                continue
            
            # Analyze code for potential issues
            issues = self._analyze_code_issues(existing_content, target_file)
            
            # Generate fixes
            fixes = self._llm_generate_debug_fixes(intent, existing_content, issues)
            
            edits.extend(fixes)
        
        return edits
    
    def _generate_test_code(self, intent: UserIntent) -> List[CodeEdit]:
        """Generate test code."""
        edits = []
        
        target_files = intent.target_files
        if not target_files:
            return edits
        
        for target_file in target_files:
            try:
                existing_content = self.file_manager.read_file(target_file)
            except Exception as e:
                logger.error(f"Failed to read file {target_file}: {e}")
                continue
            
            # Generate test file name
            test_file = self._generate_test_filename(target_file)
            
            # Generate test content
            test_content = self._llm_generate_test_content(intent, existing_content, target_file)
            
            edits.append(CodeEdit(
                file_path=test_file,
                content=test_content,
                operation="create",
                description=f"Generate tests for {target_file}"
            ))
        
        return edits
    
    def _generate_refactor_code(self, intent: UserIntent) -> List[CodeEdit]:
        """Generate refactored code."""
        edits = []
        
        target_files = intent.target_files
        if not target_files:
            return edits
        
        for target_file in target_files:
            try:
                existing_content = self.file_manager.read_file(target_file)
            except Exception as e:
                logger.error(f"Failed to read file {target_file}: {e}")
                continue
            
            # Generate refactored content
            refactored_content = self._llm_generate_refactored_content(intent, existing_content)
            
            edits.append(CodeEdit(
                file_path=target_file,
                content=refactored_content,
                operation="replace",
                description=f"Refactor {target_file}"
            ))
        
        return edits
    
    def _llm_generate_content(self, intent: UserIntent, language: Language, filename: str) -> str:
        """Use LLM to generate code content."""
        
        system_prompt = f"""You are an expert {language.value} programmer. Generate clean, well-documented code based on the user's request.

Guidelines:
- Write production-ready code with proper error handling
- Include appropriate comments and docstrings
- Follow language-specific best practices
- Make code modular and reusable
- Include necessary imports

Generate only the code content, no explanations or markdown formatting."""

        user_prompt = f"""
Create a {language.value} file named {filename} with the following requirements:
{intent.context}

Additional parameters: {intent.parameters}
"""

        try:
            response = self.llm_client.generate_response(user_prompt, system_prompt)
            return response.strip()
        except Exception as e:
            logger.error(f"LLM content generation failed: {e}")
            return self._fallback_content_generation(intent, language)
    
    def _llm_generate_modifications(self, intent: UserIntent, existing_content: str, filename: str) -> List[CodeEdit]:
        """Use LLM to generate code modifications."""
        
        system_prompt = """You are an expert programmer. Analyze the existing code and generate specific modifications based on the user's request.

Return a JSON array of modifications with this structure:
[
    {
        "line_start": <int>,
        "line_end": <int>,
        "content": "<new_content>",
        "operation": "insert|replace|delete",
        "description": "<description>"
    }
]

If no modifications are needed, return an empty array."""

        user_prompt = f"""
File: {filename}
Request: {intent.context}

Existing code:
```
{existing_content}
```

Generate the necessary modifications."""

        try:
            response = self.llm_client.generate_response(user_prompt, system_prompt)
            modifications = self._parse_modifications_response(response)
            
            edits = []
            for mod in modifications:
                edits.append(CodeEdit(
                    file_path=filename,
                    line_start=mod.get("line_start"),
                    line_end=mod.get("line_end"),
                    content=mod.get("content", ""),
                    operation=mod.get("operation", "replace"),
                    description=mod.get("description", "")
                ))
            
            return edits
            
        except Exception as e:
            logger.error(f"LLM modification generation failed: {e}")
            return []
    
    def _parse_modifications_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse LLM response for modifications."""
        import json
        
        try:
            # Try to extract JSON from response
            json_start = response.find('[')
            json_end = response.rfind(']') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            else:
                return []
        except Exception as e:
            logger.error(f"Failed to parse modifications response: {e}")
            return []
    
    def _suggest_filename(self, intent: UserIntent) -> str:
        """Suggest a filename based on intent."""
        language = intent.language or Language.PYTHON
        
        if "function" in intent.context.lower():
            return f"function_{intent.parameters.get('name', 'new')}.{language.value}"
        elif "class" in intent.context.lower():
            return f"{intent.parameters.get('name', 'NewClass')}.{language.value}"
        elif "test" in intent.context.lower():
            return f"test_{intent.parameters.get('name', 'code')}.{language.value}"
        else:
            return f"new_file.{language.value}"
    
    def _detect_language_from_filename(self, filename: str) -> Language:
        """Detect language from filename extension."""
        ext = filename.split('.')[-1].lower()
        
        language_map = {
            'py': Language.PYTHON,
            'js': Language.JAVASCRIPT,
            'ts': Language.TYPESCRIPT,
            'java': Language.JAVA,
            'cpp': Language.CPP,
            'cc': Language.CPP,
            'cxx': Language.CPP,
            'cs': Language.CSHARP,
            'rs': Language.RUST,
            'go': Language.GO,
            'html': Language.HTML,
            'css': Language.CSS,
            'sql': Language.SQL,
            'sh': Language.BASH,
            'bash': Language.BASH
        }
        
        return language_map.get(ext, Language.PYTHON)
    
    def _fallback_content_generation(self, intent: UserIntent, language: Language) -> str:
        """Fallback content generation when LLM fails."""
        if language == Language.PYTHON:
            return f'''# Generated code based on: {intent.context}

def main():
    """Main function."""
    pass

if __name__ == "__main__":
    main()
'''
        else:
            return f"// Generated code based on: {intent.context}\n"
    
    def _create_execution_script(self, intent: UserIntent) -> str:
        """Create a temporary execution script."""
        return f'''#!/usr/bin/env python3
# Temporary execution script

import sys
import os

# Add current directory to path
sys.path.insert(0, os.getcwd())

# Execution logic based on intent
{intent.context}

if __name__ == "__main__":
    try:
        # Execute the requested code
        pass
    except Exception as e:
        print(f"Execution error: {{e}}")
        sys.exit(1)
'''
    
    def _analyze_code_issues(self, content: str, filename: str) -> List[Dict[str, Any]]:
        """Analyze code for potential issues."""
        issues = []
        
        # Basic syntax checking for Python
        if filename.endswith('.py'):
            try:
                ast.parse(content)
            except SyntaxError as e:
                issues.append({
                    "type": "syntax_error",
                    "message": str(e),
                    "line": e.lineno,
                    "severity": "error"
                })
        
        # Add more analysis as needed
        return issues
    
    def _llm_generate_debug_fixes(self, intent: UserIntent, content: str, issues: List[Dict[str, Any]]) -> List[CodeEdit]:
        """Generate debug fixes using LLM."""
        # Implementation for LLM-based debugging
        return []
    
    def _generate_test_filename(self, target_file: str) -> str:
        """Generate test filename from target file."""
        name = os.path.splitext(target_file)[0]
        ext = os.path.splitext(target_file)[1]
        return f"test_{name}{ext}"
    
    def _llm_generate_test_content(self, intent: UserIntent, content: str, target_file: str) -> str:
        """Generate test content using LLM."""
        # Implementation for LLM-based test generation
        return f"# Tests for {target_file}\n# Generated based on: {intent.context}\n"
    
    def _llm_generate_refactored_content(self, intent: UserIntent, content: str) -> str:
        """Generate refactored content using LLM."""
        # Implementation for LLM-based refactoring
        return content
