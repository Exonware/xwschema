#!/usr/bin/env python3
"""
#exonware/xwschema/src/exonware/xwschema/errors.py

XWSchema Error Classes

This module defines all error classes for the xwschema library,
providing rich error context and actionable error messages.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.2
Generation Date: 09-Nov-2025
"""

from typing import Any, Optional


# ==============================================================================
# BASE ERROR
# ==============================================================================

class XWSchemaError(Exception):
    """
    Base exception for all xwschema errors.
    
    Provides rich error context with actionable suggestions.
    """
    
    def __init__(
        self,
        message: str,
        *,
        operation: Optional[str] = None,
        path: Optional[str] = None,
        format: Optional[str] = None,
        context: Optional[dict[str, Any]] = None,
        suggestion: Optional[str] = None
    ):
        """
        Initialize xwschema error with rich context.
        
        Args:
            message: Error message
            operation: Operation being performed
            path: Schema path (if applicable)
            format: Schema format (if applicable)
            context: Additional context
            suggestion: Actionable suggestion for fixing
        """
        self.message = message
        self.operation = operation
        self.path = path
        self.format = format
        self.context = context or {}
        self.suggestion = suggestion
        
        # Build detailed error message
        parts = [message]
        
        if operation:
            parts.append(f"Operation: {operation}")
        if path:
            parts.append(f"Path: {path}")
        if format:
            parts.append(f"Format: {format}")
        if context:
            context_str = ", ".join(f"{k}={v}" for k, v in context.items())
            parts.append(f"Context: {context_str}")
        if suggestion:
            parts.append(f"Suggestion: {suggestion}")
        
        full_message = " | ".join(parts)
        super().__init__(full_message)


# ==============================================================================
# VALIDATION ERRORS
# ==============================================================================

class XWSchemaValidationError(XWSchemaError):
    """Raised when data fails schema validation."""
    
    def __init__(self, message: str, field: Optional[str] = None, **kwargs):
        if 'suggestion' not in kwargs:
            kwargs['suggestion'] = "Check the data structure against the schema definition"
        if field:
            kwargs['path'] = field
        super().__init__(message, operation='validation', **kwargs)


class XWSchemaTypeError(XWSchemaValidationError):
    """Raised when data type doesn't match schema."""
    
    def __init__(self, message: str, expected_type: str, actual_type: str, **kwargs):
        kwargs['context'] = kwargs.get('context', {})
        kwargs['context'].update({
            'expected_type': expected_type,
            'actual_type': actual_type
        })
        if 'suggestion' not in kwargs:
            kwargs['suggestion'] = f"Expected type '{expected_type}', got '{actual_type}'"
        super().__init__(message, **kwargs)


class XWSchemaConstraintError(XWSchemaValidationError):
    """Raised when a constraint is violated."""
    
    def __init__(self, message: str, constraint: str, **kwargs):
        kwargs['context'] = kwargs.get('context', {})
        kwargs['context']['constraint'] = constraint
        if 'suggestion' not in kwargs:
            kwargs['suggestion'] = f"Constraint '{constraint}' was violated"
        super().__init__(message, **kwargs)


# ==============================================================================
# SCHEMA ERRORS
# ==============================================================================

class XWSchemaParseError(XWSchemaError):
    """Raised when schema cannot be parsed."""
    
    def __init__(self, message: str, **kwargs):
        if 'suggestion' not in kwargs:
            kwargs['suggestion'] = "Check schema syntax and format compatibility"
        super().__init__(message, operation='parse', **kwargs)


class XWSchemaFormatError(XWSchemaError):
    """Raised when schema format is invalid or unsupported."""
    
    def __init__(self, message: str, format: str, **kwargs):
        if 'suggestion' not in kwargs:
            kwargs['suggestion'] = f"Ensure schema format '{format}' is supported and correctly formatted"
        super().__init__(message, format=format, **kwargs)


class XWSchemaReferenceError(XWSchemaError):
    """Raised when schema reference cannot be resolved."""
    
    def __init__(self, message: str, ref: str, **kwargs):
        kwargs['context'] = kwargs.get('context', {})
        kwargs['context']['reference'] = ref
        if 'suggestion' not in kwargs:
            kwargs['suggestion'] = f"Check that reference '{ref}' exists and is accessible"
        super().__init__(message, operation='reference_resolution', **kwargs)


# ==============================================================================
# GENERATION ERRORS
# ==============================================================================

class XWSchemaGenerationError(XWSchemaError):
    """Raised when schema generation fails."""
    
    def __init__(self, message: str, **kwargs):
        if 'suggestion' not in kwargs:
            kwargs['suggestion'] = "Check input data structure and generation options"
        super().__init__(message, operation='generation', **kwargs)

