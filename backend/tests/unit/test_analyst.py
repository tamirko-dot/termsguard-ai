from app.crew.tools.clause_classifier_tool import ClauseClassifierTool


def test_classifier_detects_red_keyword():
    tool = ClauseClassifierTool()
    result = tool._run("You waive your right to a class action lawsuit.")
    assert result.startswith("red")


def test_classifier_detects_yellow_keyword():
    tool = ClauseClassifierTool()
    result = tool._run("We may share anonymized data with affiliated companies.")
    assert result.startswith("yellow")


def test_classifier_returns_green_for_safe_text():
    tool = ClauseClassifierTool()
    result = tool._run("You can contact us at support@example.com.")
    assert result.startswith("green")


def test_classifier_red_takes_priority_over_yellow():
    tool = ClauseClassifierTool()
    result = tool._run("We may share your data and you waive arbitration rights.")
    assert result.startswith("red")
