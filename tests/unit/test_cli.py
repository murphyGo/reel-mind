from reel_mind.cli.main import main


class FakeConfigLoader:
    def list_active_channels(self) -> list[str]:
        return ["ko-shorts-tech"]

    def load_channel_config(self, channel_id: str) -> object:
        class Config:
            version_hash = f"hash-{channel_id}"

        return Config()


class FakeRuntime:
    config_loader = FakeConfigLoader()


def test_cli_lists_active_channels(capsys) -> None:
    assert main(["list-active-channels"], runtime=FakeRuntime()) == 0

    assert capsys.readouterr().out == "ko-shorts-tech\n"


def test_cli_validates_channel_config(capsys) -> None:
    assert main(["validate-channel-config", "ko-shorts-tech"], runtime=FakeRuntime()) == 0

    assert capsys.readouterr().out == "hash-ko-shorts-tech\n"
