from pathlib import Path


PROMPT_FILES = [
    "system_prompt.txt",
    "user_prompt_template.txt",
    "review_checklist.txt",
]


def test_prompt_files_exist():
    for file_name in PROMPT_FILES:
        path = Path("prompts") / file_name

        assert path.exists(), f"Missing prompt file: {path}"

        content = path.read_text(encoding="utf-8")

        assert len(content) > 100, f"Prompt file too short: {path}"


def test_system_prompt_has_required_sections():
    content = Path("prompts/system_prompt.txt").read_text(encoding="utf-8")

    assert "Strict Rules" in content
    assert "Internal Review Method" in content
    assert "Output Format" in content
    assert "Approval Status" in content
    assert "Human Review Required" in content


def test_user_template_has_placeholders():
    content = Path("prompts/user_prompt_template.txt").read_text(encoding="utf-8")

    assert "{retrieved_context}" in content
    assert "{checklist}" in content
    assert "{rfc_text}" in content


def test_review_checklist_has_core_review_dimensions():
    content = Path("prompts/review_checklist.txt").read_text(encoding="utf-8")

    required_terms = [
        "Security",
        "Scalability",
        "Reliability",
        "Observability",
        "Rollback",
        "Dependencies",
        "Cost",
    ]

    for term in required_terms:
        assert term in content