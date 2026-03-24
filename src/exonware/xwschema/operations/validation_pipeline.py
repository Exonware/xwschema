#!/usr/bin/env python3
"""
#exonware/xwschema/src/exonware/xwschema/operations/validation_pipeline.py
Schema Validation Pipeline (Optional BaaS Feature)
Provides multi-stage validation pipelines for complex validation workflows.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.4.0.3
Generation Date: 26-Jan-2026
NOTE: This is an OPTIONAL module for BaaS platform integration.
"""

from __future__ import annotations
from typing import Any
from collections.abc import Callable
from dataclasses import dataclass, field
from exonware.xwsystem import get_logger
from exonware.xwsystem.validation.contracts import ISchemaProvider
from ..defs import ValidationMode
from ..errors import XWSchemaError, XWSchemaValidationError
from ..engine import XWSchemaEngine
from ..facade import XWSchema
logger = get_logger(__name__)
@dataclass

class ValidationResult:
    """Result of a validation operation."""
    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    stage_name: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
@dataclass

class PipelineStage:
    """
    Individual validation stage in a pipeline.
    Attributes:
        name: Stage name/identifier
        validator: Validation function or validator instance
        mode: Validation mode
        required: Whether this stage must pass for pipeline to succeed
        description: Optional description of the stage
    """
    name: str
    validator: Callable | ISchemaProvider
    mode: ValidationMode = ValidationMode.STRICT
    required: bool = True
    description: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class ValidationPipeline:
    """
    Multi-step validation pipeline.
    Provides support for complex validation workflows with multiple stages.
    This is an optional BaaS feature.
    """

    def __init__(self, name: str | None = None):
        """
        Initialize validation pipeline.
        Args:
            name: Optional pipeline name
        """
        self._name = name or "ValidationPipeline"
        self._stages: list[PipelineStage] = []
        self._engine = XWSchemaEngine()
        self._default_provider: ISchemaProvider | None = None

    def add_stage(
        self,
        name: str,
        validator: Callable | ISchemaProvider,
        mode: ValidationMode = ValidationMode.STRICT,
        required: bool = True,
        description: str | None = None,
        **metadata
    ) -> ValidationPipeline:
        """
        Add validation stage to pipeline.
        Args:
            name: Stage name
            validator: Validator function or validator instance
            mode: Validation mode
            required: Whether this stage must pass
            description: Optional stage description
            **metadata: Additional stage metadata
        Returns:
            Self for chaining
        """
        stage = PipelineStage(
            name=name,
            validator=validator,
            mode=mode,
            required=required,
            description=description,
            metadata=metadata
        )
        self._stages.append(stage)
        return self

    async def validate(
        self,
        data: Any,
        schema: dict[str, Any],
        **opts
    ) -> ValidationResult:
        """
        Execute validation pipeline on data.
        Args:
            data: Data to validate
            schema: Schema definition
            **opts: Additional validation options
        Returns:
            Aggregated validation result
        """
        all_errors: list[str] = []
        all_warnings: list[str] = []
        stage_results: list[ValidationResult] = []
        for stage in self._stages:
            try:
                # Execute stage validation
                if isinstance(stage.validator, ISchemaProvider):
                    is_valid, errors = stage.validator.validate_schema(data, schema)
                elif callable(stage.validator):
                    # Custom validator function
                    result = await stage.validator(data, schema, **opts)
                    if isinstance(result, tuple):
                        is_valid, errors = result
                    elif isinstance(result, ValidationResult):
                        is_valid = result.is_valid
                        errors = result.errors
                    else:
                        is_valid = bool(result)
                        errors = []
                else:
                    # Use default schema provider
                    provider = self._ensure_default_provider()
                    is_valid, errors = provider.validate_schema(data, schema)
                # Create stage result
                stage_result = ValidationResult(
                    is_valid=is_valid,
                    errors=errors if isinstance(errors, list) else [str(errors)] if errors else [],
                    stage_name=stage.name,
                    metadata=stage.metadata
                )
                stage_results.append(stage_result)
                # Collect errors and warnings
                if not is_valid:
                    all_errors.extend(stage_result.errors)
                    if stage.required:
                        # Stop on required stage failure
                        break
                else:
                    # Stage passed, continue
                    pass
            except Exception as e:
                logger.error(f"Validation stage '{stage.name}' failed with exception: {e}")
                error_msg = f"Stage '{stage.name}' validation error: {str(e)}"
                all_errors.append(error_msg)
                stage_results.append(ValidationResult(
                    is_valid=False,
                    errors=[error_msg],
                    stage_name=stage.name
                ))
                if stage.required:
                    break
        # Aggregate results
        overall_valid = len(all_errors) == 0
        result = ValidationResult(
            is_valid=overall_valid,
            errors=all_errors,
            warnings=all_warnings,
            metadata={
                'stage_count': len(self._stages),
                'stages_executed': len(stage_results),
                'stage_results': [r.stage_name for r in stage_results]
            }
        )
        return result

    def clear_stages(self) -> ValidationPipeline:
        """
        Clear all pipeline stages.
        Returns:
            Self for chaining
        """
        self._stages.clear()
        return self

    def _ensure_default_provider(self) -> ISchemaProvider:
        """Ensure default schema provider (XWSchema) is initialized."""
        if self._default_provider is None:
            self._default_provider = XWSchema({})
        return self._default_provider
__all__ = ['ValidationPipeline', 'PipelineStage', 'ValidationResult']
