from reel_mind.foundation import Runtime


def test_runtime_contract_groups_foundation_components() -> None:
    runtime = Runtime(
        secrets=object(),
        supabase=object(),
        r2=object(),
        config_loader=object(),
        cost_ledger=object(),
        run_recorder=object(),
    )

    assert runtime.config_loader is not None
    assert runtime.run_recorder is not None
