import pytest
from final import extract_identifier


def test_simple():
    assert extract_identifier("CICU6332694P") == "CICU6332694"


def test_with_spaces():
    assert extract_identifier("CI CU 6332694 P") == "CICU6332694"


def test_extra_letter():
    assert extract_identifier("CICUA6332694P") == "CICU6332694"


def test_parentheses():
    assert extract_identifier("(CI-CU-6332694-P)") == "CICU6332694"


def test_no_match():
    assert extract_identifier("no id here") == ""
