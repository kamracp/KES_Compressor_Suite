from app.domain.compressed_air.allied.allied_analysis import (
    analyze_allied_equipment,
)
from app.schemas.compressed_air_allied import (
    AlliedEquipmentAnalysisRequest,
    AlliedEquipmentAnalysisResponse,
)


class CompressedAirAlliedService:
    """Application service for compressed-air allied-equipment analysis."""

    def analyze(
        self,
        request: AlliedEquipmentAnalysisRequest,
    ) -> AlliedEquipmentAnalysisResponse:
        result = analyze_allied_equipment(request.to_domain())

        return AlliedEquipmentAnalysisResponse.from_domain(result)


compressed_air_allied_service = CompressedAirAlliedService()
