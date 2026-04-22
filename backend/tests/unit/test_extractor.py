from unittest.mock import MagicMock, patch

from app.crew.tasks.extract_task import build_extract_task


def test_build_extract_task_contains_raw_text():
    agent = MagicMock()
    raw_text = "You agree to binding arbitration. We may share your data."
    task = build_extract_task(agent, raw_text)
    assert raw_text[:100] in task.description


def test_build_extract_task_truncates_long_text():
    agent = MagicMock()
    raw_text = "x" * 10_000
    task = build_extract_task(agent, raw_text)
    # Only first 8000 chars should appear in the description
    assert "x" * 8000 in task.description
    assert "x" * 8001 not in task.description


def test_build_extract_task_assigns_correct_agent():
    agent = MagicMock()
    task = build_extract_task(agent, "some text")
    assert task.agent is agent
