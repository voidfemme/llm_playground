# src/chatbots/tools/tools.py

from datetime import datetime
import requests
import os
import openai


# Example tool: get_current_time
def get_current_time() -> str:
    """
    Returns the current date and time in the format: YYYY-MM-DD HH:MM:SS.
    This tool does not require any input parameters.
    Use this tool when you need to know the exact current time.
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_weather(
    location: str, unit: str = "celsius", api_key: str | None = None
) -> str:
    """
    Retrieves the current weather for a given location.
    The location should be provided as a string in the format "City, Country Code" (e.g., "London, UK").
    The unit parameter is optional and defaults to "celsius". It can be set to "fahrenheit" to get the temperature in Fahrenheit.
    This tool should be used when the user asks about the current weather conditions in a specific location.
    It will return a string with the current temperature and weather description.
    Note: This tool relies on an external API and requires an internet connection and a valid API key.
    """

    if not api_key:
        return "API key is missing. Please provide a valid API key."

    base_url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units={'imperial' if unit == 'fahrenheit' else 'metric'}"

    try:
        response = requests.get(base_url)
        response.raise_for_status()
        data = response.json()
        temperature = data["main"]["temp"]
        description = data["weather"][0]["description"]
        return f"The current weather in {location} is {description} with a temperature of {temperature}°{'F' if unit == 'fahrenheit' else 'C'}."
    except requests.exceptions.RequestException:
        return "Error occurred while fetching weather data."


def generate_image(
    model: str,
    prompt: str,
    size: str = "1024x1024",
    quality: str = "standard",
    n: int = 1,
) -> str:
    """
    Generates an image based on the given text prompt using the specified DALL·E model.
    The model parameter specifies the DALL·E model to use, either "dall-e-2" or "dall-e-3".
    The prompt should describe the desired image in detail.
    The size parameter specifies the dimensions of the generated image and defaults to "1024x1024".
    Other supported sizes are "1024x1792" and "1792x1024".
    The quality parameter indicates the quality of the generated image and defaults to "standard".
    For DALL·E 3, you can set quality to "hd" for enhanced detail.
    The n parameter indicates the number of images to generate and defaults to 1.
    This tool is useful when the user requests a specific image to be created from a textual description.
    It will return the URL of the generated image.
    Note: This tool requires the OpenAI Python library to be installed and properly authenticated.
    """

    client = openai.OpenAI()
    try:
        response = client.images.generate(
            model=model,
            prompt=prompt,
            size=size,  # type: ignore
            quality=quality,  # type: ignore
            n=n,
        )
        image_url = response.data[0].url
        if image_url:
            return image_url
        else:
            return "Error occurred while generating image."
    except openai.OpenAIError as e:
        return f"Error occurred while generating image: {str(e)}"
