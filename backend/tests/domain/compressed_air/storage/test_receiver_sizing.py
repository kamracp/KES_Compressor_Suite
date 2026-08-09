from decimal import Decimal

import pytest

from app.domain.compressed_air.storage.receiver_sizing import (
    InvalidReceiverSizingInputError,
    ReceiverSizingInput,
    calculate_receiver_size,
)


def test_receiver_supports_short_peak_demand() -> None:
    result = calculate_receiver_size(
        ReceiverSizingInput(
            peak_demand_nm3_per_hr=Decimal("3600"),
            available_compressor_flow_nm3_per_hr=Decimal("3000"),
            event_duration_seconds=Decimal("30"),
            receiver_high_pressure_bar_g=Decimal("7.0"),
            receiver_low_pressure_bar_g=Decimal("6.5"),
            reserve_fraction=Decimal("0.20"),
        )
    )

    assert result.flow_deficit_nm3_per_hr == Decimal("600")
    assert result.pressure_band_bar == Decimal("0.5")
    assert result.storage_required is True

    assert result.base_receiver_volume_m3 > Decimal("0")
    assert result.recommended_receiver_volume_m3 > result.base_receiver_volume_m3


def test_zero_flow_deficit_requires_no_storage() -> None:
    result = calculate_receiver_size(
        ReceiverSizingInput(
            peak_demand_nm3_per_hr=Decimal("3000"),
            available_compressor_flow_nm3_per_hr=Decimal("3200"),
            event_duration_seconds=Decimal("30"),
            receiver_high_pressure_bar_g=Decimal("7.0"),
            receiver_low_pressure_bar_g=Decimal("6.5"),
        )
    )

    assert result.flow_deficit_nm3_per_hr == Decimal("0")
    assert result.base_receiver_volume_m3 == Decimal("0")
    assert result.recommended_receiver_volume_m3 == Decimal("0")
    assert result.storage_required is False


def test_reserve_fraction_increases_receiver_volume() -> None:
    base_result = calculate_receiver_size(
        ReceiverSizingInput(
            peak_demand_nm3_per_hr=Decimal("3600"),
            available_compressor_flow_nm3_per_hr=Decimal("3000"),
            event_duration_seconds=Decimal("30"),
            receiver_high_pressure_bar_g=Decimal("7.0"),
            receiver_low_pressure_bar_g=Decimal("6.5"),
            reserve_fraction=Decimal("0"),
        )
    )

    reserve_result = calculate_receiver_size(
        ReceiverSizingInput(
            peak_demand_nm3_per_hr=Decimal("3600"),
            available_compressor_flow_nm3_per_hr=Decimal("3000"),
            event_duration_seconds=Decimal("30"),
            receiver_high_pressure_bar_g=Decimal("7.0"),
            receiver_low_pressure_bar_g=Decimal("6.5"),
            reserve_fraction=Decimal("0.25"),
        )
    )

    assert (
        reserve_result.recommended_receiver_volume_m3
        == base_result.base_receiver_volume_m3 * Decimal("1.25")
    )


def test_longer_peak_requires_larger_receiver() -> None:
    short_peak = calculate_receiver_size(
        ReceiverSizingInput(
            peak_demand_nm3_per_hr=Decimal("3600"),
            available_compressor_flow_nm3_per_hr=Decimal("3000"),
            event_duration_seconds=Decimal("15"),
            receiver_high_pressure_bar_g=Decimal("7.0"),
            receiver_low_pressure_bar_g=Decimal("6.5"),
        )
    )

    long_peak = calculate_receiver_size(
        ReceiverSizingInput(
            peak_demand_nm3_per_hr=Decimal("3600"),
            available_compressor_flow_nm3_per_hr=Decimal("3000"),
            event_duration_seconds=Decimal("60"),
            receiver_high_pressure_bar_g=Decimal("7.0"),
            receiver_low_pressure_bar_g=Decimal("6.5"),
        )
    )

    assert long_peak.base_receiver_volume_m3 > short_peak.base_receiver_volume_m3


def test_larger_pressure_band_reduces_required_receiver_volume() -> None:
    narrow_band = calculate_receiver_size(
        ReceiverSizingInput(
            peak_demand_nm3_per_hr=Decimal("3600"),
            available_compressor_flow_nm3_per_hr=Decimal("3000"),
            event_duration_seconds=Decimal("30"),
            receiver_high_pressure_bar_g=Decimal("7.0"),
            receiver_low_pressure_bar_g=Decimal("6.7"),
        )
    )

    wide_band = calculate_receiver_size(
        ReceiverSizingInput(
            peak_demand_nm3_per_hr=Decimal("3600"),
            available_compressor_flow_nm3_per_hr=Decimal("3000"),
            event_duration_seconds=Decimal("30"),
            receiver_high_pressure_bar_g=Decimal("7.0"),
            receiver_low_pressure_bar_g=Decimal("6.0"),
        )
    )

    assert wide_band.base_receiver_volume_m3 < narrow_band.base_receiver_volume_m3


def test_invalid_pressure_band_is_rejected() -> None:
    with pytest.raises(
        InvalidReceiverSizingInputError,
        match=("Receiver high pressure must be greater than receiver low pressure"),
    ):
        calculate_receiver_size(
            ReceiverSizingInput(
                peak_demand_nm3_per_hr=Decimal("3600"),
                available_compressor_flow_nm3_per_hr=Decimal("3000"),
                event_duration_seconds=Decimal("30"),
                receiver_high_pressure_bar_g=Decimal("6.5"),
                receiver_low_pressure_bar_g=Decimal("6.5"),
            )
        )


def test_zero_event_duration_is_rejected() -> None:
    with pytest.raises(
        InvalidReceiverSizingInputError,
        match="Event duration must be greater than zero",
    ):
        calculate_receiver_size(
            ReceiverSizingInput(
                peak_demand_nm3_per_hr=Decimal("3600"),
                available_compressor_flow_nm3_per_hr=Decimal("3000"),
                event_duration_seconds=Decimal("0"),
                receiver_high_pressure_bar_g=Decimal("7.0"),
                receiver_low_pressure_bar_g=Decimal("6.5"),
            )
        )


def test_invalid_reserve_fraction_is_rejected() -> None:
    with pytest.raises(
        InvalidReceiverSizingInputError,
        match="Reserve fraction must be between zero and one",
    ):
        calculate_receiver_size(
            ReceiverSizingInput(
                peak_demand_nm3_per_hr=Decimal("3600"),
                available_compressor_flow_nm3_per_hr=Decimal("3000"),
                event_duration_seconds=Decimal("30"),
                receiver_high_pressure_bar_g=Decimal("7.0"),
                receiver_low_pressure_bar_g=Decimal("6.5"),
                reserve_fraction=Decimal("1.10"),
            )
        )
