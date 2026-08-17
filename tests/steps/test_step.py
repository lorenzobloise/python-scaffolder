"""
Tests for the abstract Step base class (python_scaffolder/steps/step.py).

Run with:
    pytest tests/steps/test_step.py
"""

import pytest
from pathlib import Path
from abc import ABC

# ---------------------------------------------------------------------------
# Concrete stub — the minimal Step implementation used across all tests
# ---------------------------------------------------------------------------

from python_scaffolder.steps.step import Step


class ConcreteStep(Step):
    """Minimal concrete implementation for testing the base class behaviour."""

    @property
    def name(self) -> str:
        return "test-step"

    def run(self, path: Path, config: dict) -> None:  # pragma: no cover
        pass


# ---------------------------------------------------------------------------
# Instantiation & interface contract
# ---------------------------------------------------------------------------


class TestStepIsAbstract:
    def test_step_cannot_be_instantiated_directly(self):
        """Step is abstract: direct instantiation must raise TypeError."""
        with pytest.raises(TypeError):
            Step()  # type: ignore[abstract]

    def test_subclass_without_name_cannot_be_instantiated(self):
        """A subclass that omits `name` must still be abstract."""
        class NoName(Step):
            def run(self, path: Path, config: dict) -> None:
                pass

        with pytest.raises(TypeError):
            NoName()

    def test_subclass_without_run_cannot_be_instantiated(self):
        """A subclass that omits `run` must still be abstract."""
        class NoRun(Step):
            @property
            def name(self) -> str:
                return "norun"

        with pytest.raises(TypeError):
            NoRun()

    def test_concrete_step_can_be_instantiated(self):
        """A fully-implemented subclass must instantiate without errors."""
        step = ConcreteStep()
        assert isinstance(step, Step)

    def test_step_is_abc(self):
        """Step must inherit from ABC."""
        assert issubclass(Step, ABC)


# ---------------------------------------------------------------------------
# `name` property
# ---------------------------------------------------------------------------


class TestNameProperty:
    def test_name_returns_correct_value(self):
        step = ConcreteStep()
        assert step.name == "test-step"

    def test_name_is_a_string(self):
        step = ConcreteStep()
        assert isinstance(step.name, str)

    def test_different_subclasses_have_independent_names(self):
        class AnotherStep(Step):
            @property
            def name(self) -> str:
                return "another"

            def run(self, path: Path, config: dict) -> None:
                pass

        assert ConcreteStep().name != AnotherStep().name


# ---------------------------------------------------------------------------
# Logging helpers — output format
# ---------------------------------------------------------------------------


class TestLogHelper:
    def test_log_prints_with_step_name_prefix(self, capsys):
        ConcreteStep().log("doing something")
        out = capsys.readouterr().out
        assert "[test-step]" in out
        assert "doing something" in out

    def test_log_ends_with_newline(self, capsys):
        ConcreteStep().log("msg")
        out = capsys.readouterr().out
        assert out.endswith("\n")

    def test_log_does_not_write_to_stderr(self, capsys):
        ConcreteStep().log("msg")
        assert capsys.readouterr().err == ""


class TestWarnHelper:
    def test_warn_prints_with_step_name_prefix(self, capsys):
        ConcreteStep().warn("something missing")
        out = capsys.readouterr().out
        assert "[test-step]" in out
        assert "something missing" in out

    def test_warn_contains_warning_indicator(self, capsys):
        ConcreteStep().warn("bad field")
        out = capsys.readouterr().out
        assert "Warning" in out or "warning" in out

    def test_warn_ends_with_newline(self, capsys):
        ConcreteStep().warn("msg")
        out = capsys.readouterr().out
        assert out.endswith("\n")

    def test_warn_does_not_write_to_stderr(self, capsys):
        ConcreteStep().warn("msg")
        assert capsys.readouterr().err == ""


class TestErrorHelper:
    def test_error_prints_with_step_name_prefix(self, capsys):
        ConcreteStep().error("something went wrong")
        out = capsys.readouterr().out
        assert "[test-step]" in out
        assert "something went wrong" in out

    def test_error_contains_error_indicator(self, capsys):
        ConcreteStep().error("boom")
        out = capsys.readouterr().out
        assert "Error" in out or "error" in out

    def test_error_ends_with_newline(self, capsys):
        ConcreteStep().error("msg")
        out = capsys.readouterr().out
        assert out.endswith("\n")

    def test_error_does_not_write_to_stderr(self, capsys):
        ConcreteStep().error("msg")
        assert capsys.readouterr().err == ""


class TestSuccessHelper:
    def test_success_prints_with_step_name_prefix(self, capsys):
        ConcreteStep().success("all done")
        out = capsys.readouterr().out
        assert "[test-step]" in out
        assert "all done" in out

    def test_success_contains_success_indicator(self, capsys):
        ConcreteStep().success("done")
        out = capsys.readouterr().out
        # accepts ✓, OK, ok, success, or similar
        assert any(tok in out for tok in ("✓", "OK", "ok", "success", "Success"))

    def test_success_ends_with_newline(self, capsys):
        ConcreteStep().success("msg")
        out = capsys.readouterr().out
        assert out.endswith("\n")

    def test_success_does_not_write_to_stderr(self, capsys):
        ConcreteStep().success("msg")
        assert capsys.readouterr().err == ""


# ---------------------------------------------------------------------------
# Helpers use `self.name` — verified by swapping out the name
# ---------------------------------------------------------------------------


class TestHelpersUseInstanceName:
    """Verify that each helper embeds the *instance's* name, not a hardcoded string."""

    @pytest.fixture()
    def custom_step(self):
        class CustomStep(Step):
            @property
            def name(self) -> str:
                return "customname"

            def run(self, path: Path, config: dict) -> None:
                pass

        return CustomStep()

    def test_log_uses_instance_name(self, custom_step, capsys):
        custom_step.log("hello")
        assert "[customname]" in capsys.readouterr().out

    def test_warn_uses_instance_name(self, custom_step, capsys):
        custom_step.warn("hello")
        assert "[customname]" in capsys.readouterr().out

    def test_error_uses_instance_name(self, custom_step, capsys):
        custom_step.error("hello")
        assert "[customname]" in capsys.readouterr().out

    def test_success_uses_instance_name(self, custom_step, capsys):
        custom_step.success("hello")
        assert "[customname]" in capsys.readouterr().out
