"""
Schema versioning and migration support for xData framework.
"""

from typing import Any, Dict, List, Optional, Set, Union
from dataclasses import dataclass
from datetime import datetime
import logging
from enum import Enum

from src.xlib.xdata.core.exceptions import (
    SchemaError, SchemaVersionError, SchemaMigrationError
)

logger = logging.getLogger(__name__)

class MigrationType(Enum):
    """Types of schema migrations."""
    ADD = "add"
    REMOVE = "remove"
    MODIFY = "modify"
    RENAME = "rename"

@dataclass
class SchemaVersion:
    """Schema version information."""
    major: int
    minor: int
    patch: int
    date: datetime
    description: Optional[str] = None
    
    @classmethod
    def from_string(cls, version: str) -> 'SchemaVersion':
        """Create a version from a string."""
        try:
            parts = version.split('.')
            if len(parts) != 3:
                raise SchemaVersionError(f"Invalid version format: {version}")
                
            return cls(
                major=int(parts[0]),
                minor=int(parts[1]),
                patch=int(parts[2]),
                date=datetime.now()
            )
        except ValueError as e:
            raise SchemaVersionError(f"Invalid version number: {e}")
            
    def is_compatible_with(self, other: 'SchemaVersion') -> bool:
        """Check if this version is compatible with another version."""
        if self.major != other.major:
            return False
        if self.minor < other.minor:
            return False
        if self.minor == other.minor and self.patch < other.patch:
            return False
        return True
        
    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"
        
    def to_native(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'version': str(self),
            'date': self.date.isoformat(),
            'description': self.description
        }

@dataclass
class MigrationStep:
    """A single migration step."""
    type: MigrationType
    path: str
    value: Any
    old_value: Optional[Any] = None
    description: Optional[str] = None
    
    def apply(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply this migration step to data."""
        if self.type == MigrationType.ADD:
            return self._apply_add(data)
        elif self.type == MigrationType.REMOVE:
            return self._apply_remove(data)
        elif self.type == MigrationType.MODIFY:
            return self._apply_modify(data)
        elif self.type == MigrationType.RENAME:
            return self._apply_rename(data)
        else:
            raise SchemaMigrationError(f"Unknown migration type: {self.type}")
            
    def _apply_add(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply an add migration."""
        parts = self.path.split('.')
        current = data
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[parts[-1]] = self.value
        return data
        
    def _apply_remove(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply a remove migration."""
        parts = self.path.split('.')
        current = data
        for part in parts[:-1]:
            if part not in current:
                return data
            current = current[part]
        if parts[-1] in current:
            del current[parts[-1]]
        return data
        
    def _apply_modify(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply a modify migration."""
        parts = self.path.split('.')
        current = data
        for part in parts[:-1]:
            if part not in current:
                return data
            current = current[part]
        if parts[-1] in current:
            current[parts[-1]] = self.value
        return data
        
    def _apply_rename(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply a rename migration."""
        if not self.old_value:
            raise SchemaMigrationError("Old value required for rename migration")
            
        parts = self.path.split('.')
        current = data
        for part in parts[:-1]:
            if part not in current:
                return data
            current = current[part]
            
        if self.old_value in current:
            value = current[self.old_value]
            del current[self.old_value]
            current[parts[-1]] = value
            
        return data

class SchemaMigration:
    """A migration between schema versions."""
    
    def __init__(self, from_version: SchemaVersion, to_version: SchemaVersion):
        self.from_version = from_version
        self.to_version = to_version
        self.steps: List[MigrationStep] = []
        
    def add_step(self, step: MigrationStep):
        """Add a migration step."""
        self.steps.append(step)
        
    def apply(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply all migration steps to data."""
        result = data.copy()
        for step in self.steps:
            try:
                result = step.apply(result)
            except Exception as e:
                raise SchemaMigrationError(
                    f"Failed to apply migration step: {e}",
                    step=step
                )
        return result

class MigrationRegistry:
    """Registry for schema migrations."""
    
    def __init__(self):
        self._migrations: Dict[str, SchemaMigration] = {}
        
    def register(self, migration: SchemaMigration):
        """Register a migration."""
        key = f"{migration.from_version}->{migration.to_version}"
        if key in self._migrations:
            raise SchemaMigrationError(f"Migration already registered: {key}")
        self._migrations[key] = migration
        
    def get(self, from_version: SchemaVersion, to_version: SchemaVersion) -> Optional[SchemaMigration]:
        """Get a migration between versions."""
        key = f"{from_version}->{to_version}"
        return self._migrations.get(key)
        
    def find_migration_path(self, from_version: SchemaVersion, to_version: SchemaVersion) -> List[SchemaMigration]:
        """Find a path of migrations between versions."""
        if from_version == to_version:
            return []
            
        if not from_version.is_compatible_with(to_version):
            raise SchemaVersionError(
                f"Versions are not compatible: {from_version} -> {to_version}"
            )
            
        # Find direct migration
        migration = self.get(from_version, to_version)
        if migration:
            return [migration]
            
        # Find path through intermediate versions
        path = []
        current = from_version
        
        while current != to_version:
            # Try to find a migration to a newer version
            found = False
            for migration in self._migrations.values():
                if migration.from_version == current and migration.to_version.is_compatible_with(to_version):
                    path.append(migration)
                    current = migration.to_version
                    found = True
                    break
                    
            if not found:
                raise SchemaMigrationError(
                    f"No migration path found from {from_version} to {to_version}"
                )
                
        return path 