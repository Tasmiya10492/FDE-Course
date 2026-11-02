from pydantic import BaseModel, ConfigDict, Field


class WorkExperience(BaseModel):
    """Represents one job held by the candidate."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    job_title: str = Field(min_length=1)
    company: str = Field(min_length=1)
    start_year: int | None = None
    end_year: int | None = None


class Education(BaseModel):
    """Represents the candidate's education."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    degree: str = Field(min_length=1)
    graduation_year: int | None = None


class CVData(BaseModel):
    """Structured information extracted from a CV."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    full_name: str = Field(min_length=1)
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    summary: str | None = None
    skills: list[str] = Field(default_factory=list)
    experience: list[WorkExperience] = Field(default_factory=list)
    education: Education | None = None
