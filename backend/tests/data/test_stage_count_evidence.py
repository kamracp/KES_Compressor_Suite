from app.data.evidence.loader import bound_envelope, get_evidence


def test_centrifugal_stage_limit_set_loads_with_its_registry_entry():
    data = get_evidence("MFR-CENTRIFUGAL-STAGE-LIMITS-2026-09")
    assert data["kind"] == "manufacturer_evidence"
    assert {s["id"] for s in data["sources"]} == {"SRC-SE-IGC", "SRC-TMI-CONFIG"}


def test_stage_count_envelopes_match_the_schema_constants():
    from app.schemas._bounds import MAX_CENTRIFUGAL_IMPELLER_STAGES, MAX_RECIP_STAGES

    assert bound_envelope("centrifugal_impeller_stages") == (1, MAX_CENTRIFUGAL_IMPELLER_STAGES)
    assert bound_envelope("recip_cylinders_per_frame")[1] == MAX_RECIP_STAGES
