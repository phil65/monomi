from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv

# import litellm
from jinjarope import htmlfilters, lazylitellm


load_dotenv()


litellm = lazylitellm.LazyLiteLLM()


def llm_complete(
    prompt: str,
    system_prompt: str | None = None,
    context: str | None = None,
    model: str | None = None,
    token: str | None = None,
    base_url: str | None = None,
    **kwargs: Any,
) -> str:
    """Complete a prompt using the LLM API.

    Args:
        prompt: The prompt to complete.
        system_prompt: The system prompt to set context for the model.
        context: Additional context for the prompt.
        model: The model to use.
        token: The API token.
        base_url: The base URL of the API.
        kwargs: Additional keyword arguments passed to litellm.completion.

    Returns:
        The completed text from the LLM.

    Raises:
        ValueError: If the API response is invalid or missing expected data.
    """
    messages: list[dict[str, str]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    if context:
        messages.append({"role": "user", "content": context})
    messages.append({"role": "user", "content": prompt})

    response = litellm.completion(
        model=model or os.getenv("OPENAI_MODEL", ""),
        api_key=token or os.getenv("OPENAI_API_TOKEN"),
        api_base=base_url or os.getenv("OPENAI_API_BASE"),
        messages=messages,
        **kwargs,
    )
    if not response.choices or not response.choices[0].message:
        msg = "Invalid API response: missing choices or message"
        raise ValueError(msg)
    return response.choices[0].message.content or ""


def llm_generate_image(
    prompt: str,
    model: str | None = None,
    token: str | None = None,
    base_url: str | None = None,
    size: str = "1024x1024",
    quality: str = "standard",
    as_b64_json: bool = False,
    **kwargs: Any,
) -> str | None:
    """Generate an image using the LLM API and returns the URL.

    Args:
        prompt: The prompt to generate an image from.
        model: The model to use. Defaults to None.
        token: The API token. Defaults to None.
        base_url: The base URL of the API. Defaults to None.
        size: The size of the generated image. Defaults to "1024x1024".
        quality: The quality of the generated image. Defaults to "standard".
        as_b64_json: Return b64-encoded image instead of URL.
        kwargs: Additional keyword arguments passed to litellm.image_generation.

    Returns:
        The generated image response.
    """
    response = litellm.image_generation(
        prompt=prompt,
        model=model or os.getenv("OPENAI_IMAGE_MODEL"),
        api_key=token or os.getenv("OPENAI_API_TOKEN"),
        api_base=base_url,
        size=size,
        quality=quality,
        response_format="b64_json" if as_b64_json else "url",
        **kwargs,
    )
    # Check if the API result is valid
    if response and response.data and len(response.data) > 0:
        # TODO: <img src="data:image/png;base64,iVBORw0KG..." />
        return response.data[0].b64_json if as_b64_json else response.data[0].url
    return None


def llm_analyze_image(
    image_url: str,
    prompt: str | None = None,
    model: str = "gpt-4-vision-preview",
    token: str | None = None,
    base_url: str | None = None,
    encode_b64: bool = False,
    **kwargs: Any,
) -> str:
    """Analyze an image using an LLM vision model and return the analysis as a string.

    Args:
        image_url: The URL of the image to analyze.
        prompt: A prompt to guide the image analysis. If None, use a default prompt.
        model: The name of the model to use. Defaults to "gpt-4-vision-preview".
        token: The API token (key) for authentication.
               If None, it will use the OPENAI_API_KEY environment variable.
        base_url: The base URL for the API endpoint.
                  If None, the default URL for the model will be used.
        encode_b64: Whether to encode the image to base64 before sending it to the API.
                    (required for some models)
        kwargs: Additional keyword arguments passed to litellm.completion.

    Returns:
        The analysis of the image as a string.

    Raises:
        ValueError: If the image_url is empty or invalid.
        requests.RequestException: If there's an error downloading the image.
        Exception: If there's an error in making the API call or processing the response.
    """
    if not image_url or not image_url.strip():
        msg = "Image URL cannot be empty"
        raise ValueError(msg)

    prompt = prompt or "Analyze this image and describe what you see in detail."
    image_str = htmlfilters.url_to_b64(image_url) if encode_b64 else image_url
    completion_kwargs: dict[str, Any] = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_str,
                        },
                    },
                ],
            },
        ],
        "max_tokens": 300,  # Default max tokens
    }

    if token:
        completion_kwargs["api_key"] = token
    if base_url:
        completion_kwargs["api_base"] = base_url
    response = litellm.completion(**completion_kwargs, **kwargs)
    return response.choices[0].message.content.strip()


if __name__ == "__main__":
    response = llm_analyze_image(
        image_url="https://picsum.photos/200/300",
        model="ollama/llava",
    )
    print(response)
    print(response)
