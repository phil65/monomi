from uuid import UUID

from pydantic import ValidationError
import pytest

from jinjarope.llm.apicallcollection import (
    APICall,
    APICallCollection,
    ApiSource,
    BundleSource,
    ContextBundle,
    ContextSource,
    DatabaseSource,
    FileSource,
    LLMParameters,
    Prompt,
    PromptType,
    SourceType,
)


@pytest.fixture
def sample_prompt():
    return Prompt(prompt_type=PromptType.USER, content="Hello, how are you?", order=0)


@pytest.fixture
def sample_parameters():
    return LLMParameters(model="gpt-3.5-turbo", temperature=0.7, max_tokens=100)


@pytest.fixture
def sample_context_source():
    return ContextSource(source_type=SourceType.MEMORY, name="Test Source")


@pytest.fixture
def sample_bundle():
    return ContextBundle(
        name="test_bundle",
        sources=[
            FileSource(
                source_type=SourceType.FILE, name="Test File", file_path="/test.txt"
            )
        ],
    )


def test_prompt_type_enum():
    assert PromptType.SYSTEM == "system"
    assert PromptType.USER == "user"
    assert PromptType.ASSISTANT == "assistant"
    assert PromptType.FUNCTION == "function"


def test_source_type_enum():
    assert SourceType.FILE == "file"
    assert SourceType.DATABASE == "database"
    assert SourceType.API == "api"
    assert SourceType.MEMORY == "memory"


def test_context_source_creation():
    source = ContextSource(source_type=SourceType.MEMORY, name="Test Source")
    assert isinstance(source.source_id, UUID)
    assert source.source_type == SourceType.MEMORY
    assert source.name == "Test Source"
    assert source.description is None


def test_file_source_creation():
    source = FileSource(
        source_type=SourceType.FILE, name="Test File", file_path="/path/to/file.txt"
    )
    assert source.file_path == "/path/to/file.txt"
    assert source.line_start is None
    assert source.line_end is None


def test_database_source_creation():
    source = DatabaseSource(
        source_type=SourceType.DATABASE,
        name="Test DB",
        connection_string="postgresql://user:pass@localhost/db",
        query="SELECT * FROM table",
    )
    assert source.connection_string == "postgresql://user:pass@localhost/db"
    assert source.query == "SELECT * FROM table"


def test_api_source_creation():
    source = ApiSource(
        source_type=SourceType.API, name="Test API", url="https://api.example.com"
    )
    assert source.method == "GET"
    assert source.headers is None


def test_prompt_validation():
    with pytest.raises(ValidationError):
        Prompt(
            prompt_type=PromptType.USER,
            content="Test",
            order=-1,  # Should fail due to ge=0 validation
        )


def test_llm_parameters_validation():
    with pytest.raises(ValidationError):
        LLMParameters(
            model="gpt-4",
            temperature=1.5,  # Should fail due to le=1 validation
        )


def test_api_call_creation(sample_prompt, sample_parameters):
    call = APICall(
        name="Test Call",
        prompts=[sample_prompt],
        parameters=sample_parameters,
        context_sources=[],  # Fix: explicitly set empty list
    )
    assert isinstance(call.call_id, UUID)
    assert len(call.prompts) == 1
    assert call.context_sources == []


def test_api_call_collection():
    collection = APICallCollection(
        name="test",  # Fix: add required fields
        calls=[],
        context_bundles=[],
    )
    assert collection.calls == []
    assert collection.context_bundles == []


def test_full_api_call_integration(
    sample_prompt, sample_parameters, sample_context_source
):
    call = APICall(
        name="Integration Test",
        prompts=[sample_prompt],
        parameters=sample_parameters,
        context_sources=[sample_context_source],
    )
    collection = APICallCollection(name="test", calls=[call])

    assert len(collection.calls) == 1
    assert collection.calls[0].name == "Integration Test"
    assert len(collection.calls[0].prompts) == 1
    assert len(collection.calls[0].context_sources) == 1


def test_bundle_source_creation():
    source = BundleSource(
        name="Bundle Reference",
        bundle_name="test_bundle",
        source_type=SourceType.BUNDLE,  # Fix: explicitly set source type
    )
    assert source.source_type == SourceType.BUNDLE
    assert source.bundle_name == "test_bundle"


def test_context_bundle_creation(sample_bundle):
    assert sample_bundle.name == "test_bundle"
    assert len(sample_bundle.sources) == 1
    assert isinstance(sample_bundle.bundle_id, UUID)


def test_api_call_with_bundle_source(sample_prompt, sample_parameters):
    bundle_source = BundleSource(name="Bundle Ref", bundle_name="test_bundle")

    call = APICall(
        name="Test Call",
        prompts=[sample_prompt],
        parameters=sample_parameters,
        context_sources=[bundle_source],
    )

    assert len(call.context_sources) == 1
    assert isinstance(call.context_sources[0], BundleSource)


if __name__ == "__main__":
    pytest.main(["-v", __file__])
