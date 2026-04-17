#!/usr/bin/env python3
"""
#exonware/xwschema/src/exonware/xwschema/common/validation_rules.py
Advanced Validation Rules for XWSchema
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.4.0.17
Generation Date: 15-Nov-2025
"""

from typing import Any
from collections.abc import Callable
from exonware.xwsystem import get_logger
logger = get_logger(__name__)


class AdvancedValidationRules:
    """Advanced validation rules for schema validation."""
    @staticmethod

    def validate_email(value: Any) -> tuple[bool, str | None]:
        """
        Validate email address format.
        Args:
            value: Value to validate
        Returns:
            Tuple of (is_valid, error_message)
        """
        import re
        if not isinstance(value, str):
            return False, "Email must be a string"
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, value):
            return False, f"Invalid email format: {value}"
        return True, None
    @staticmethod

    def validate_url(value: Any) -> tuple[bool, str | None]:
        """
        Validate URL format.
        Args:
            value: Value to validate
        Returns:
            Tuple of (is_valid, error_message)
        """
        import re
        if not isinstance(value, str):
            return False, "URL must be a string"
        url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        if not re.match(url_pattern, value):
            return False, f"Invalid URL format: {value}"
        return True, None
    @staticmethod

    def validate_uuid(value: Any) -> tuple[bool, str | None]:
        """
        Validate UUID format.
        Args:
            value: Value to validate
        Returns:
            Tuple of (is_valid, error_message)
        """
        import re
        if not isinstance(value, str):
            return False, "UUID must be a string"
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        if not re.match(uuid_pattern, value, re.IGNORECASE):
            return False, f"Invalid UUID format: {value}"
        return True, None
    @staticmethod

    def validate_phone(value: Any) -> tuple[bool, str | None]:
        """
        Validate phone number format.
        Args:
            value: Value to validate
        Returns:
            Tuple of (is_valid, error_message)
        """
        import re
        if not isinstance(value, str):
            return False, "Phone number must be a string"
        # Basic phone pattern (international format)
        phone_pattern = r'^\+?[1-9]\d{1,14}$'
        if not re.match(phone_pattern, value.replace(' ', '').replace('-', '')):
            return False, f"Invalid phone number format: {value}"
        return True, None
    @staticmethod

    def validate_date(value: Any) -> tuple[bool, str | None]:
        """
        Validate date format (ISO 8601).
        Args:
            value: Value to validate
        Returns:
            Tuple of (is_valid, error_message)
        """
        from datetime import datetime
        if not isinstance(value, str):
            return False, "Date must be a string"
        try:
            datetime.fromisoformat(value.replace('Z', '+00:00'))
            return True, None
        except ValueError:
            return False, f"Invalid date format (expected ISO 8601): {value}"
    @staticmethod

    def validate_regex(value: Any, pattern: str) -> tuple[bool, str | None]:
        """
        Validate value against regex pattern.
        Args:
            value: Value to validate
            pattern: Regex pattern
        Returns:
            Tuple of (is_valid, error_message)
        """
        import re
        if not isinstance(value, str):
            return False, "Value must be a string for regex validation"
        try:
            if not re.match(pattern, value):
                return False, f"Value does not match pattern: {pattern}"
            return True, None
        except re.error as e:
            return False, f"Invalid regex pattern: {e}"
    @staticmethod

    def validate_custom(value: Any, validator: Callable[[Any], bool]) -> tuple[bool, str | None]:
        """
        Validate value using custom validator function.
        Args:
            value: Value to validate
            validator: Custom validator function
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            if not validator(value):
                return False, f"Custom validation failed for value: {value}"
            return True, None
        except Exception as e:
            return False, f"Custom validator error: {e}"
# Registry of validation rules
VALIDATION_RULES = {
    'email': AdvancedValidationRules.validate_email,
    'url': AdvancedValidationRules.validate_url,
    'uuid': AdvancedValidationRules.validate_uuid,
    'phone': AdvancedValidationRules.validate_phone,
    'date': AdvancedValidationRules.validate_date,
    'regex': AdvancedValidationRules.validate_regex,
    'custom': AdvancedValidationRules.validate_custom,
}


def get_validation_rule(rule_name: str) -> Callable | None:
    """
    Get validation rule by name.
    Args:
        rule_name: Name of the validation rule
    Returns:
        Validation rule function or None
    """
    return VALIDATION_RULES.get(rule_name)
