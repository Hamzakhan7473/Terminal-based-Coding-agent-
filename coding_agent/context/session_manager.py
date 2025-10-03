"""Session manager for maintaining context across interactions."""

import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from ..core.models import UserIntent, SessionState, AgentResponse
from ..utils.logger import get_logger

logger = get_logger(__name__)


class SessionManager:
    """Manages session state and context for multi-turn conversations."""
    
    def __init__(self, project_root: str = ".", max_context_length: int = 10):
        self.project_root = project_root
        self.max_context_length = max_context_length
        self.session_state = SessionState(
            session_id=self._generate_session_id(),
            project_root=project_root
        )
        self.conversation_history = []
        self.context_memory = {}
        self.session_file = os.path.join(project_root, ".coding_agent_session.json")
        self._load_session()
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID."""
        return f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def _load_session(self) -> None:
        """Load existing session from file."""
        try:
            if os.path.exists(self.session_file):
                with open(self.session_file, 'r') as f:
                    data = json.load(f)
                
                # Restore session state
                self.session_state.current_files = data.get("current_files", [])
                self.session_state.recent_edits = data.get("recent_edits", [])
                self.session_state.context_memory = data.get("context_memory", {})
                self.conversation_history = data.get("conversation_history", [])
                
                logger.info(f"Loaded existing session: {self.session_state.session_id}")
            else:
                logger.info(f"Starting new session: {self.session_state.session_id}")
                
        except Exception as e:
            logger.error(f"Failed to load session: {e}")
    
    async def save_session(self) -> None:
        """Save current session to file."""
        try:
            session_data = {
                "session_id": self.session_state.session_id,
                "project_root": self.session_state.project_root,
                "current_files": self.session_state.current_files,
                "recent_edits": [edit.dict() for edit in self.session_state.recent_edits],
                "execution_history": [result.dict() for result in self.session_state.execution_history],
                "context_memory": self.session_state.context_memory,
                "conversation_history": self.conversation_history,
                "created_at": self.session_state.created_at.isoformat(),
                "last_activity": datetime.now().isoformat()
            }
            
            with open(self.session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
            
            logger.info("Session saved successfully")
            
        except Exception as e:
            logger.error(f"Failed to save session: {e}")
    
    def update_context(self, intent: UserIntent, user_input: str) -> None:
        """Update session context with new intent and user input."""
        # Add to conversation history
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "intent_type": intent.intent_type.value,
            "confidence": intent.confidence,
            "parameters": intent.parameters
        })
        
        # Keep only recent history
        if len(self.conversation_history) > self.max_context_length:
            self.conversation_history = self.conversation_history[-self.max_context_length:]
        
        # Update recent edits
        if intent.code_edits:
            self.session_state.recent_edits.extend(intent.code_edits)
            # Keep only recent edits
            if len(self.session_state.recent_edits) > 20:
                self.session_state.recent_edits = self.session_state.recent_edits[-20:]
        
        # Update current files
        for file_path in intent.target_files:
            if file_path not in self.session_state.current_files:
                self.session_state.current_files.append(file_path)
        
        # Update context memory
        self._update_context_memory(intent, user_input)
        
        # Update last activity
        self.session_state.last_activity = datetime.now()
    
    def _update_context_memory(self, intent: UserIntent, user_input: str) -> None:
        """Update context memory with relevant information."""
        # Extract key information from intent
        if intent.language:
            self.context_memory["current_language"] = intent.language.value
        
        if intent.target_files:
            self.context_memory["working_files"] = intent.target_files
        
        if "function" in user_input.lower():
            # Extract function name if mentioned
            import re
            func_match = re.search(r'(?:function|def)\s+(\w+)', user_input, re.IGNORECASE)
            if func_match:
                self.context_memory["current_function"] = func_match.group(1)
        
        if "class" in user_input.lower():
            # Extract class name if mentioned
            import re
            class_match = re.search(r'class\s+(\w+)', user_input, re.IGNORECASE)
            if class_match:
                self.context_memory["current_class"] = class_match.group(1)
        
        # Store project-specific context
        if "project" in user_input.lower() or "app" in user_input.lower():
            self.context_memory["project_context"] = user_input
    
    def get_context(self) -> Dict[str, Any]:
        """Get current session context for LLM."""
        return {
            "session_id": self.session_state.session_id,
            "project_root": self.session_state.project_root,
            "current_files": self.session_state.current_files,
            "recent_edits": [edit.dict() for edit in self.session_state.recent_edits[-5:]],
            "conversation_history": self.conversation_history[-3:],
            "context_memory": self.context_memory,
            "session_duration": str(datetime.now() - self.session_state.created_at)
        }
    
    def get_recent_context(self, turns: int = 3) -> List[Dict[str, Any]]:
        """Get recent conversation context."""
        return self.conversation_history[-turns:] if self.conversation_history else []
    
    def clear_context(self) -> None:
        """Clear session context."""
        self.conversation_history = []
        self.context_memory = {}
        self.session_state.recent_edits = []
        self.session_state.current_files = []
        logger.info("Session context cleared")
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get session summary information."""
        return {
            "session_id": self.session_state.session_id,
            "created_at": self.session_state.created_at.isoformat(),
            "last_activity": self.session_state.last_activity.isoformat(),
            "duration": str(datetime.now() - self.session_state.created_at),
            "total_interactions": len(self.conversation_history),
            "files_modified": len(self.session_state.current_files),
            "total_edits": len(self.session_state.recent_edits),
            "executions": len(self.session_state.execution_history)
        }
    
    def add_execution_result(self, result) -> None:
        """Add execution result to session history."""
        self.session_state.execution_history.append(result)
        # Keep only recent executions
        if len(self.session_state.execution_history) > 10:
            self.session_state.execution_history = self.session_state.execution_history[-10:]
    
    def get_working_files(self) -> List[str]:
        """Get list of files currently being worked on."""
        return self.session_state.current_files.copy()
    
    def set_working_files(self, files: List[str]) -> None:
        """Set the list of working files."""
        self.session_state.current_files = files.copy()
    
    def get_recent_edits(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent edits with limit."""
        return [edit.dict() for edit in self.session_state.recent_edits[-limit:]]
    
    def is_session_expired(self, max_duration_hours: int = 24) -> bool:
        """Check if session has expired."""
        max_duration = timedelta(hours=max_duration_hours)
        return datetime.now() - self.session_state.created_at > max_duration
