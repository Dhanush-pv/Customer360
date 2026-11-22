import sys

import pytest

from customer360 import cli


def test_generate_command_writes_five_extracts(tmp_path, monkeypatch, capsys):
    out = tmp_path / "out"
    argv = ["customer360", "generate", "--output", str(out), "--customers", "20", "--orders", "30"]
    monkeypatch.setattr(sys, "argv", argv)
    cli.main()
    assert len(list(out.glob("*.csv"))) == 5
    assert "commerce_customers: 20" in capsys.readouterr().out


def test_command_is_required(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["customer360"])
    with pytest.raises(SystemExit):
        cli.main()
