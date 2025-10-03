"""Data models for the coding agent system."""

from enum import Enum
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime


class IntentType(str, Enum):
    """Types of user intents."""
    CREATE_FILE = "create_file"
    EDIT_FILE = "edit_file"
    DELETE_FILE = "delete_file"
    EXECUTE_CODE = "execute_code"
    ANALYZE_CODE = "analyze_code"
    DEBUG_CODE = "debug_code"
    TEST_CODE = "test_code"
    EXPLAIN_CODE = "explain_code"
    REFACTOR_CODE = "refactor_code"
    SEARCH_CODE = "search_code"
    UNDO_CHANGES = "undo_changes"
    REDO_CHANGES = "redo_changes"
    SHOW_STATUS = "show_status"
    HELP = "help"


class Language(str, Enum):
    """Supported programming languages."""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CPP = "cpp"
    CSHARP = "csharp"
    RUST = "rust"
    GO = "go"
    HTML = "html"
    CSS = "css"
    SQL = "sql"
    BASH = "bash"
    SHELL = "shell"


class CodeEdit(BaseModel):
    """Represents a code edit operation."""
    file_path: str
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    content: str
    operation: str = Field(..., description="insert, replace, delete")
    description: Optional[str] = None


class ExecutionResult(BaseModel):
    """Result of code execution."""
    success: bool
    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0
    execution_time: float = 0.0
    memory_usage: Optional[float] = None
    error_details: Optional[Dict[str, Any]] = None


class UserIntent(BaseModel):
    """Parsed user intent with structured information."""
    intent_type: IntentType
    confidence: float = Field(..., ge=0.0, le=1.0)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    language: Optional[Language] = None
    target_files: List[str] = Field(default_factory=list)
    code_edits: List[CodeEdit] = Field(default_factory=list)
    execution_commands: List[str] = Field(default_factory=list)
    context: Optional[str] = None
    requires_confirmation: bool = False


class SessionState(BaseModel):
    """Current session state."""
    session_id: str
    project_root: str
    current_files: List[str] = Field(default_factory=list)
    recent_edits: List[CodeEdit] = Field(default_factory=list)
    execution_history: List[ExecutionResult] = Field(default_factory=list)
    context_memory: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    last_activity: datetime = Field(default_factory=datetime.now)


class AgentResponse(BaseModel):
    """Agent's response to user input."""
    intent: UserIntent
    generated_code: Optional[str] = None
    execution_result: Optional[ExecutionResult] = None
    file_changes: List[CodeEdit] = Field(default_factory=list)
    messages: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    requires_confirmation: bool = False


class SafetyCheck(BaseModel):
    """Safety validation for code execution."""
    is_safe: bool
    warnings: List[str] = Field(default_factory=list)
    blocked_operations: List[str] = Field(default_factory=list)
    resource_limits: Dict[str, Any] = Field(default_factory=dict)
    security_concerns: List[str] = Field(default_factory=list)
