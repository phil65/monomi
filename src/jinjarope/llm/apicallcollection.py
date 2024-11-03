from __future__ import annotations

from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, HttpUrl


class PromptType(str, Enum):
    SYSTEM = "system"
    """System-level prompts that set behavior and context"""

    USER = "user"
    """User input prompts"""

    ASSISTANT = "assistant"
    """Assistant responses in conversation history"""

    FUNCTION = "function"
    """Function calls and their responses"""


class SourceType(str, Enum):
    FILE = "file"
    """Local file system source"""

    DATABASE = "database"
    """Database query source"""

    API = "api"
    """External API endpoint source"""

    MEMORY = "memory"
    """In-memory cached source"""

    BUNDLE = "bundle"
    """Reference to a context bundle"""


class ContextSource(BaseModel):
    source_id: UUID = Field(default_factory=uuid4)
    """Unique identifier for the context source"""

    source_type: SourceType
    """Type of the context source (file/db/api/memory)"""

    name: str
    """Human readable name for the context source"""

    description: str | None = None
    """Optional description of what this source provides"""


class FileSource(ContextSource):
    file_path: str
    """Path to the source file, absolute or relative"""

    line_start: int | None = None
    """Starting line number for partial file reads"""

    line_end: int | None = None
    """Ending line number for partial file reads"""


class DatabaseSource(ContextSource):
    connection_string: str
    """Database connection string with credentials"""

    query: str
    """SQL query to execute for retrieving context"""


class ApiSource(ContextSource):
    url: HttpUrl
    """API endpoint URL"""

    headers: dict[str, str] | None = None
    """Optional HTTP headers for the API request"""

    method: str = "GET"
    """HTTP method to use (GET/POST/etc)"""


class BundleSource(ContextSource):
    """References a context bundle to include its sources."""

    bundle_name: str
    """Name of the bundle to reference"""

    source_type: SourceType = SourceType.BUNDLE
    """Always BUNDLE for this source type"""


class Prompt(BaseModel):
    prompt_type: PromptType
    """Type of the prompt (system/user/assistant/function)"""

    content: str
    """Actual prompt text content"""

    order: int = Field(ge=0)
    """Order in which prompts should be applied (0-based)"""


class LLMParameters(BaseModel):
    model: str
    """Name/ID of the LLM model to use"""

    temperature: float = Field(default=0.7, ge=0, le=1)
    """Sampling temperature (0-1) controlling randomness"""

    max_tokens: int | None = None
    """Maximum tokens in response"""

    top_p: float | None = None
    """Nucleus sampling parameter"""

    presence_penalty: float | None = None
    """Penalty for new token presence"""

    frequency_penalty: float | None = None
    """Penalty for token frequency"""


class APICall(BaseModel):
    call_id: UUID = Field(default_factory=uuid4)
    """Unique identifier for this API call"""

    name: str
    """Human readable name for the API call"""

    description: str | None = None
    """Optional description of the call's purpose"""

    prompts: list[Prompt]
    """Ordered list of prompts to send"""

    parameters: LLMParameters
    """LLM-specific parameters for this call"""

    context_sources: list[ContextSource] = []
    """Optional list of context sources to include"""

    # def get_expanded_sources(
    #     self, manager: APICallCollectionManager
    # ) -> list[ContextSource]:
    #     """Get all context sources with bundles expanded."""
    #     sources = []
    #     for source in self.context_sources:
    #         print(source)
    #         if isinstance(source, BundleSource):
    #             bundle = manager.get_bundle(source.bundle_name)
    #             if bundle:
    #                 sources.extend(bundle.sources)
    #         else:
    #             sources.append(source)
    #     return sources


class ContextBundle(BaseModel):
    """A named bundle of context sources that can be reused across API calls."""

    bundle_id: UUID = Field(default_factory=uuid4)
    name: str
    description: str | None = None
    sources: list[ContextSource]


class APICallCollection(BaseModel):
    name: str
    description: str | None = None
    calls: list[APICall]
    context_bundles: list[ContextBundle] = Field(default_factory=list)


if __name__ == "__main__":
    # Create a simple test case
    test_call = APICall(
        name="Test Greeting",
        description="A basic test of the API call system",
        prompts=[
            Prompt(
                prompt_type=PromptType.SYSTEM,
                content="You are a helpful assistant.",
                order=0,
            ),
            Prompt(
                prompt_type=PromptType.USER,
                content="Say hello to the world.",
                order=1,
            ),
        ],
        parameters=LLMParameters(
            model="gpt-3.5-turbo",
            temperature=0.7,
            max_tokens=100,
        ),
        context_sources=[
            FileSource(
                source_type=SourceType.FILE,
                name="Greeting Config",
                file_path="greetings.txt",
            ),
        ],
    )
    test_call.get_expanded_sources()
    print(test_call.model_dump_json(indent=2))
