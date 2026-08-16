from app.domain.compressed_air.skid.skid_assessment import assess_air_skid
from app.schemas.compressed_air_skid import (
    AirSkidAssessmentRequest,
    AirSkidAssessmentResponse,
)


class CompressedAirSkidService:
    """Application service for compressed-air skid assessment."""

    def assess(
        self,
        request: AirSkidAssessmentRequest,
    ) -> AirSkidAssessmentResponse:
        result = assess_air_skid(request.to_domain())

        return AirSkidAssessmentResponse.from_domain(result)


compressed_air_skid_service = CompressedAirSkidService()
