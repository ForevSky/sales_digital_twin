import pytest

from sales_digital_twin.cli.app import (
    DEMO_SAMPLES,
    _has_cli_input,
    build_parser,
    load_sample_text,
)


def test_demo_flag_parses_without_other_input() -> None:
    args = build_parser().parse_args(["--demo"])
    assert args.demo is True


def test_demo_is_mutually_exclusive_with_text() -> None:
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["--demo", "--text", "hello"])


def test_no_args_means_interactive_mode() -> None:
    args = build_parser().parse_args([])
    assert _has_cli_input(args) is False


def test_demo_samples_match_example_files() -> None:
    for _, filename in DEMO_SAMPLES:
        text = load_sample_text(filename)
        assert len(text) > 0
