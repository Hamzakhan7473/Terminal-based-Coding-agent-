"""File management utilities for the coding agent."""

import os
import shutil
import tempfile
from typing import List, Dict, Optional, Any
from datetime import datetime
import git
from ..utils.logger import get_logger

logger = get_logger(__name__)


class FileManager:
    """Manages file operations with versioning and rollback capabilities."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = os.path.abspath(project_root)
        self.backup_dir = os.path.join(self.project_root, ".coding_agent_backups")
        self._ensure_backup_dir()
        self.git_repo = self._init_git_repo()
    
    def _ensure_backup_dir(self) -> None:
        """Ensure backup directory exists."""
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def _init_git_repo(self) -> Optional[git.Repo]:
        """Initialize or get existing Git repository."""
        try:
            return git.Repo(self.project_root)
        except git.InvalidGitRepositoryError:
            try:
                return git.Repo.init(self.project_root)
            except Exception as e:
                logger.warning(f"Could not initialize Git repository: {e}")
                return None
    
    def read_file(self, file_path: str) -> str:
        """Read file content with error handling."""
        full_path = os.path.join(self.project_root, file_path)
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            raise
    
    def write_file(self, file_path: str, content: str, create_backup: bool = True) -> bool:
        """Write file content with backup creation."""
        full_path = os.path.join(self.project_root, file_path)
        
        try:
            # Create backup if file exists
            if create_backup and os.path.exists(full_path):
                self._create_backup(file_path)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            # Write file
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Successfully wrote file: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to write file {file_path}: {e}")
            return False
    
    def delete_file(self, file_path: str, create_backup: bool = True) -> bool:
        """Delete file with optional backup."""
        full_path = os.path.join(self.project_root, file_path)
        
        try:
            if not os.path.exists(full_path):
                logger.warning(f"File does not exist: {file_path}")
                return False
            
            # Create backup before deletion
            if create_backup:
                self._create_backup(file_path)
            
            os.remove(full_path)
            logger.info(f"Successfully deleted file: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {e}")
            return False
    
    def _create_backup(self, file_path: str) -> None:
        """Create backup of file."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{timestamp}_{os.path.basename(file_path)}"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            full_path = os.path.join(self.project_root, file_path)
            shutil.copy2(full_path, backup_path)
            
            logger.info(f"Created backup: {backup_path}")
            
        except Exception as e:
            logger.error(f"Failed to create backup for {file_path}: {e}")
    
    def list_files(self, pattern: str = "*", recursive: bool = True) -> List[str]:
        """List files matching pattern."""
        import glob
        
        search_pattern = os.path.join(self.project_root, "**", pattern) if recursive else os.path.join(self.project_root, pattern)
        
        try:
            files = glob.glob(search_pattern, recursive=recursive)
            # Convert to relative paths
            return [os.path.relpath(f, self.project_root) for f in files]
        except Exception as e:
            logger.error(f"Failed to list files with pattern {pattern}: {e}")
            return []
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get file information."""
        full_path = os.path.join(self.project_root, file_path)
        
        try:
            stat = os.stat(full_path)
            return {
                "path": file_path,
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime),
                "created": datetime.fromtimestamp(stat.st_ctime),
                "is_file": os.path.isfile(full_path),
                "is_directory": os.path.isdir(full_path)
            }
        except Exception as e:
            logger.error(f"Failed to get file info for {file_path}: {e}")
            return {}
    
    def rollback_file(self, file_path: str, backup_timestamp: Optional[str] = None) -> bool:
        """Rollback file to previous version."""
        try:
            if backup_timestamp:
                backup_filename = f"{backup_timestamp}_{os.path.basename(file_path)}"
                backup_path = os.path.join(self.backup_dir, backup_filename)
            else:
                # Find most recent backup
                backups = [f for f in os.listdir(self.backup_dir) if f.endswith(f"_{os.path.basename(file_path)}")]
                if not backups:
                    logger.error(f"No backups found for {file_path}")
                    return False
                
                backups.sort(reverse=True)
                backup_path = os.path.join(self.backup_dir, backups[0])
            
            if not os.path.exists(backup_path):
                logger.error(f"Backup not found: {backup_path}")
                return False
            
            full_path = os.path.join(self.project_root, file_path)
            shutil.copy2(backup_path, full_path)
            
            logger.info(f"Successfully rolled back file: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to rollback file {file_path}: {e}")
            return False
    
    def commit_changes(self, message: str = "Auto-commit from coding agent") -> bool:
        """Commit changes to Git repository."""
        if not self.git_repo:
            logger.warning("Git repository not available")
            return False
        
        try:
            # Add all changes
            self.git_repo.git.add(A=True)
            
            # Check if there are changes to commit
            if not self.git_repo.is_dirty() and not self.git_repo.untracked_files:
                logger.info("No changes to commit")
                return True
            
            # Commit changes
            self.git_repo.index.commit(message)
            
            logger.info(f"Successfully committed changes: {message}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to commit changes: {e}")
            return False
    
    def get_changes(self) -> Dict[str, Any]:
        """Get current Git changes."""
        if not self.git_repo:
            return {"error": "Git repository not available"}
        
        try:
            return {
                "modified": [item.a_path for item in self.git_repo.index.diff(None)],
                "staged": [item.a_path for item in self.git_repo.index.diff("HEAD")],
                "untracked": self.git_repo.untracked_files,
                "is_dirty": self.git_repo.is_dirty()
            }
        except Exception as e:
            logger.error(f"Failed to get changes: {e}")
            return {"error": str(e)}
    
    def create_temp_file(self, content: str, suffix: str = ".tmp") -> str:
        """Create temporary file with content."""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False) as f:
                f.write(content)
                return f.name
        except Exception as e:
            logger.error(f"Failed to create temp file: {e}")
            raise
