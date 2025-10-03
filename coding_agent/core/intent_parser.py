"""Intent parsing module for natural language understanding."""

import json
import re
from typing import Dict, List, Optional, Any
from .models import UserIntent, IntentType, Language, CodeEdit
from ..utils.llm_client import LLMClient
from ..utils.logger import get_logger

logger = get_logger(__name__)


class IntentParser:
    """Parses natural language input into structured intents."""
    
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
        self.intent_patterns = self._build_intent_patterns()
        
    def _build_intent_patterns(self) -> Dict[IntentType, List[str]]:
        """Build regex patterns for intent detection."""
        return {
            IntentType.CREATE_FILE: [
                r"create\s+(?:a\s+)?(?:new\s+)?file",
                r"make\s+(?:a\s+)?(?:new\s+)?file",
                r"generate\s+(?:a\s+)?file",
                r"write\s+(?:a\s+)?(?:new\s+)?file"
            ],
            IntentType.EDIT_FILE: [
                r"edit\s+(\w+\.\w+)",
                r"modify\s+(\w+\.\w+)",
                r"change\s+(\w+\.\w+)",
                r"update\s+(\w+\.\w+)",
                r"add\s+(?:to\s+)?(\w+\.\w+)",
                r"remove\s+(?:from\s+)?(\w+\.\w+)"
            ],
            IntentType.EXECUTE_CODE: [
                r"run\s+(?:the\s+)?code",
                r"execute\s+(?:the\s+)?code",
                r"test\s+(?:the\s+)?code",
                r"run\s+(\w+\.\w+)",
                r"execute\s+(\w+\.\w+)"
            ],
            IntentType.ANALYZE_CODE: [
                r"analyze\s+(?:the\s+)?code",
                r"check\s+(?:the\s+)?code",
                r"review\s+(?:the\s+)?code",
                r"inspect\s+(?:the\s+)?code"
            ],
            IntentType.DEBUG_CODE: [
                r"debug\s+(?:the\s+)?code",
                r"fix\s+(?:the\s+)?(?:bug|error|issue)",
                r"troubleshoot\s+(?:the\s+)?code"
            ],
            IntentType.UNDO_CHANGES: [
                r"undo\s+(?:the\s+)?(?:last\s+)?(?:change|edit)",
                r"revert\s+(?:the\s+)?(?:last\s+)?(?:change|edit)",
                r"rollback\s+(?:the\s+)?(?:last\s+)?(?:change|edit)"
            ],
            IntentType.SHOW_STATUS: [
                r"show\s+(?:the\s+)?status",
                r"what\s+(?:is\s+)?(?:the\s+)?current\s+status",
                r"list\s+(?:the\s+)?files"
            ],
            IntentType.HELP: [
                r"help",
                r"what\s+can\s+you\s+do",
                r"show\s+(?:me\s+)?(?:the\s+)?commands"
            ]
        }
    
    def parse_intent(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> UserIntent:
        """
        Parse natural language input into structured intent.
        
        Args:
            user_input: Natural language input from user
            context: Optional context from previous interactions
            
        Returns:
            Parsed UserIntent object
        """
        logger.info(f"Parsing intent from: {user_input}")
        
        # First try pattern matching for quick classification
        intent_type = self._pattern_match_intent(user_input)
        
        # Use LLM for detailed parsing
        llm_result = self._llm_parse_intent(user_input, context)
        
        # Merge pattern and LLM results
        final_intent = self._merge_intent_results(intent_type, llm_result, user_input)
        
        logger.info(f"Parsed intent: {final_intent.intent_type} (confidence: {final_intent.confidence})")
        return final_intent
    
    def _pattern_match_intent(self, user_input: str) -> Optional[IntentType]:
        """Quick pattern-based intent classification."""
        user_input_lower = user_input.lower()
        
        for intent_type, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, user_input_lower):
                    return intent_type
        return None
    
    def _llm_parse_intent(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Use LLM for detailed intent parsing."""
        
        system_prompt = """You are an AI coding assistant that parses natural language instructions into structured intents.

Your task is to analyze user input and extract:
1. Intent type (create_file, edit_file, execute_code, analyze_code, debug_code, etc.)
2. Target files or code elements
3. Specific operations to perform
4. Programming language
5. Code content (if applicable)
6. Confidence score (0.0-1.0)

Available intent types:
- create_file: Create new files
- edit_file: Modify existing files
- delete_file: Remove files
- execute_code: Run code
- analyze_code: Review/check code
- debug_code: Fix bugs or errors
- test_code: Write/run tests
- explain_code: Explain code functionality
- refactor_code: Improve code structure
- search_code: Find code patterns
- undo_changes: Revert previous changes
- redo_changes: Reapply previous changes
- show_status: Display current state
- help: Show available commands

Respond with a JSON object containing the parsed intent."""

        context_str = ""
        if context:
            context_str = f"\nContext: {json.dumps(context, indent=2)}"
        
        prompt = f"{system_prompt}\n\nUser input: {user_input}{context_str}"
        
        try:
            response = self.llm_client.generate_response(prompt, system_prompt)
            return json.loads(response)
        except Exception as e:
            logger.error(f"LLM intent parsing failed: {e}")
            return {"intent_type": "help", "confidence": 0.5}
    
    def _merge_intent_results(self, pattern_intent: Optional[IntentType], 
                            llm_result: Dict[str, Any], user_input: str) -> UserIntent:
        """Merge pattern matching and LLM results."""
        
        # Determine final intent type
        if pattern_intent and llm_result.get("intent_type"):
            # If both agree, use LLM result (more detailed)
            final_intent_type = IntentType(llm_result["intent_type"])
            confidence = llm_result.get("confidence", 0.8)
        elif pattern_intent:
            final_intent_type = pattern_intent
            confidence = 0.7
        elif llm_result.get("intent_type"):
            final_intent_type = IntentType(llm_result["intent_type"])
            confidence = llm_result.get("confidence", 0.6)
        else:
            final_intent_type = IntentType.HELP
            confidence = 0.5
        
        # Extract parameters
        parameters = llm_result.get("parameters", {})
        
        # Determine language
        language = None
        if llm_result.get("language"):
            try:
                language = Language(llm_result["language"])
            except ValueError:
                pass
        
        # Extract target files
        target_files = llm_result.get("target_files", [])
        if not target_files and llm_result.get("target_file"):
            target_files = [llm_result["target_file"]]
        
        # Generate code edits if needed
        code_edits = self._generate_code_edits(llm_result, user_input)
        
        # Extract execution commands
        execution_commands = llm_result.get("execution_commands", [])
        
        return UserIntent(
            intent_type=final_intent_type,
            confidence=confidence,
            parameters=parameters,
            language=language,
            target_files=target_files,
            code_edits=code_edits,
            execution_commands=execution_commands,
            context=user_input,
            requires_confirmation=self._requires_confirmation(final_intent_type, parameters)
        )
    
    def _generate_code_edits(self, llm_result: Dict[str, Any], user_input: str) -> List[CodeEdit]:
        """Generate CodeEdit objects from LLM results."""
        edits = []
        
        # Handle file creation
        if llm_result.get("file_content") and llm_result.get("target_file"):
            edits.append(CodeEdit(
                file_path=llm_result["target_file"],
                content=llm_result["file_content"],
                operation="create",
                description=f"Create file from user request: {user_input[:50]}..."
            ))
        
        # Handle code modifications
        if llm_result.get("modifications"):
            for mod in llm_result["modifications"]:
                edits.append(CodeEdit(
                    file_path=mod.get("file_path", ""),
                    line_start=mod.get("line_start"),
                    line_end=mod.get("line_end"),
                    content=mod.get("content", ""),
                    operation=mod.get("operation", "replace"),
                    description=mod.get("description", "")
                ))
        
        return edits
    
    def _requires_confirmation(self, intent_type: IntentType, parameters: Dict[str, Any]) -> bool:
        """Determine if intent requires user confirmation."""
        dangerous_operations = [
            IntentType.DELETE_FILE,
            IntentType.EXECUTE_CODE,
            IntentType.UNDO_CHANGES
        ]
        
        return intent_type in dangerous_operations or parameters.get("destructive", False)
