import pytest

from cv_extractor.extractor import (
    ExtractionError,
    extract_cv,
)
from llm_client.models import LLMResponse

CV_FILE = "sample_data/cvs/cv_01.txt"


VALID_CV_JSON = """
{
    "full_name": "Asha Alder",
    "email": "asha.alder@example.com",
    "phone": "+00 555 588 8287",
    "location": "Kochi",
    "summary": "Analyst with 1 years of experience.",
    "skills": ["JavaScript", "SQL", "Git"],
    "experience": [
        {
            "job_title": "Backend Developer",
            "company": "Stonebridge Software",
            "start_year": 2024,
            "end_year": 2025
        }
    ],
    "education": {
        "degree": "B.Sc Mathematics",
        "graduation_year": 2022
    }
}
"""


class FakeLLMClient:
    """A fake LLM client that returns predefined responses."""

    def __init__(self, responses):
        self.responses = responses
        self.call_count = 0

    def chat(
        self,
        messages,
        temperature=0.0,
        seed=None,
    ):
        response = self.responses[self.call_count]
        self.call_count += 1
        return LLMResponse(content=response, model="test-model")


def test_successful_extraction():
    client = FakeLLMClient([VALID_CV_JSON])

    result = extract_cv(CV_FILE, client=client)

    assert result.full_name == "Asha Alder"
    assert result.email == "asha.alder@example.com"
    assert result.location == "Kochi"
    assert result.skills == ["JavaScript", "SQL", "Git"]
    assert client.call_count == 1


def test_invalid_response_is_repaired():
    client = FakeLLMClient(
        [
            '{"full_name": 123}',
            VALID_CV_JSON,
        ]
    )

    result = extract_cv(CV_FILE, client=client)

    assert result.full_name == "Asha Alder"
    assert client.call_count == 2


def test_extraction_fails_after_one_repair():
    client = FakeLLMClient(
        [
            '{"full_name": 123}',
            '{"full_name": 123}',
        ]
    )

    with pytest.raises(ExtractionError):
        extract_cv(CV_FILE, client=client)

    assert client.call_count == 2
