from pydantic import BaseModel

from app.schemas.calculation_execution import CalculationExecutionMetadata
from app.schemas.compressor_calculation import (
    CentrifugalCalculationRequest,
    CompressionCalculationRequest,
    CompressorSelectionRequest,
    ReciprocatingCalculationRequest,
    RotaryScrewCalculationRequest,
)


class CompressionExecutionRequest(BaseModel):
    """Combined compression calculation and persistence request."""

    calculation: CompressionCalculationRequest
    execution: CalculationExecutionMetadata = CalculationExecutionMetadata()


class ReciprocatingExecutionRequest(BaseModel):
    """Combined reciprocating calculation and persistence request."""

    calculation: ReciprocatingCalculationRequest
    execution: CalculationExecutionMetadata = CalculationExecutionMetadata()


class CentrifugalExecutionRequest(BaseModel):
    """Combined centrifugal calculation and persistence request."""

    calculation: CentrifugalCalculationRequest
    execution: CalculationExecutionMetadata = CalculationExecutionMetadata()


class SelectionExecutionRequest(BaseModel):
    """Combined compressor selection and persistence request."""

    calculation: CompressorSelectionRequest
    execution: CalculationExecutionMetadata = CalculationExecutionMetadata()


class RotaryScrewExecutionRequest(BaseModel):
    """Combined rotary screw calculation and persistence request."""

    calculation: RotaryScrewCalculationRequest
    execution: CalculationExecutionMetadata = CalculationExecutionMetadata()
