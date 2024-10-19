from unittest.mock import MagicMock, patch

import pytest
import requests

from jinjarope.llmfilters import (
    generate_class_schemas,
    generate_openai_schema,
    llm_analyze_image,
    llm_complete,
    llm_generate_image,
)


# Test for generate_openai_schema
def test_generate_openai_schema():
    def sample_func(param1: int, param2: str = "default"):
        """Sample function for testing.

        This is a longer description.
        """

    schema = generate_openai_schema(sample_func)
    assert schema["name"] == "sample_func"
    assert "Sample function for testing." in schema["description"]
    assert schema["parameters"]["type"] == "object"
    assert "param1" in schema["parameters"]["properties"]
    assert schema["parameters"]["properties"]["param1"]["type"] == "integer"
    assert "param2" in schema["parameters"]["properties"]
    assert schema["parameters"]["required"] == ["param1"]


def test_generate_openai_schema_no_docstring():
    def no_doc_func(param):
        pass

    with pytest.raises(ValueError, match="Function must have a docstring"):
        generate_openai_schema(no_doc_func)


def test_generate_openai_schema_no_params():
    def no_param_func():
        """This function has no parameters."""

    with pytest.raises(ValueError, match="Function must have at least one parameter"):
        generate_openai_schema(no_param_func)


# Test for generate_class_schemas
class SampleClass:
    def method1(self, param1: int):
        """Method 1."""

    def method2(self, param2: str = "default"):
        """Method 2."""

    def _private_method(self):
        """Private method."""


def test_generate_class_schemas():
    instance = SampleClass()
    schemas = generate_class_schemas(instance)
    assert len(schemas) == 2  # noqa: PLR2004
    assert any(schema["name"] == "method1" for schema in schemas)
    assert any(schema["name"] == "method2" for schema in schemas)


def test_llm_complete():
    response = llm_complete(
        model="ollama/llava",
        prompt="Test prompt",
        system_prompt="System prompt",
        context="Context",
        mock_response="Test response",
    )
    assert response == "Test response"


@patch("litellm.completion")
def test_llm_complete_error(mock_completion):
    mock_completion.side_effect = ValueError("API Error")

    with pytest.raises(ValueError, match="API Error"):
        llm_complete("Test prompt")


# Test for llm_generate_image
@patch("litellm.image_generation")
def test_llm_generate_image(mock_image_generation):
    mock_response = MagicMock()
    mock_response.data = [MagicMock(url="http://test-image.com")]
    mock_image_generation.return_value = mock_response

    result = llm_generate_image("Generate a cat")
    assert result == "http://test-image.com"
    mock_image_generation.assert_called_once()


@patch("litellm.image_generation")
def test_llm_generate_image_b64(mock_image_generation):
    mock_response = MagicMock()
    mock_response.data = [MagicMock(b64_json="base64encodedimage")]
    mock_image_generation.return_value = mock_response

    result = llm_generate_image("Generate a dog", as_b64_json=True)
    assert result == "base64encodedimage"


@patch("litellm.image_generation")
def test_llm_generate_image_no_result(mock_image_generation):
    mock_image_generation.return_value = MagicMock(data=[])

    result = llm_generate_image("Generate a bird")
    assert result is None


# Test for llm_analyze_image
@patch("requests.get")
@patch("litellm.completion")
def test_llm_analyze_image(mock_completion, mock_get):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Image analysis"))]
    mock_completion.return_value = mock_response

    mock_get.return_value.content = b"image_data"

    result = llm_analyze_image("http://test-image.com", encode_b64=True)
    assert result == "Image analysis"
    mock_completion.assert_called_once()
    mock_get.assert_called_once()


def test_llm_analyze_image_empty_url():
    with pytest.raises(ValueError, match="Image URL cannot be empty"):
        llm_analyze_image("")


@patch("requests.get")
def test_llm_analyze_image_download_error(mock_get):
    mock_get.side_effect = requests.RequestException("Download failed")

    with pytest.raises(Exception, match="Download failed"):
        llm_analyze_image("http://test-image.com", encode_b64=True)
