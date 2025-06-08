# llm_ranking_service.py

import os
import json
import re
import cohere
import requests
import base64
import logging
from typing import Any, Dict, List, Optional
from app.config import Config

logger = logging.getLogger(__name__)

class LLMBasedRankingService:
    """
    Service for ranking images using a multimodal LLM. Scores images on multiple axes and ranks them by overall score.
    """

    def __init__(self, model_name: str = "c4ai-aya-vision-8b") -> None:
        """
        Initialize the LLM-based ranking service.

        Args:
            model_name (str): The Cohere vision-capable model to call.
        Raises:
            ValueError: If the Cohere API key is not set.
        """
        api_key = Config.COHERE_API_KEY
        if not api_key:
            raise ValueError("Please set COHERE_API_KEY in your .env file")
        self.client = cohere.Client(api_key=api_key)
        self.model = model_name

    def _download_and_encode_image(self, image_url: str) -> str:
        """
        Download an image from a URL and convert it to base64.

        Args:
            image_url (str): The URL of the image to download.
        Returns:
            str: The base64-encoded image string.
        Raises:
            Exception: If the image cannot be downloaded or encoded.
        """
        try:
            response = requests.get(image_url)
            response.raise_for_status()
            image_data = response.content
            base64_image = base64.b64encode(image_data).decode('utf-8')
            return f"data:image/jpeg;base64,{base64_image}"
        except Exception as e:
            logger.error(f"Failed to download and encode image: {str(e)}", exc_info=True)
            raise Exception(f"Failed to download and encode image: {str(e)}")

    def _build_messages(self, image_url: str, description: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Build the message payload for the LLM API call.

        Args:
            image_url (str): The image URL (base64-encoded).
            description (str): The image description.
            metadata (dict): The image metadata.
        Returns:
            list: The message payload for the LLM.
        """
        system_prompt = """You are an expert photo curator and social-media strategist.
For the image and metadata I provide, evaluate each dimension on a scale from 0 (worst) to 10 (best):

  • technical (0-10): Assess image quality including:
    - Focus sharpness and clarity
    - Proper exposure and lighting
    - Low noise and grain
    - Good dynamic range between shadows and highlights
    - Image resolution and detail

  • aesthetic (0-10): Evaluate visual composition including:
    - Rule of thirds and balanced composition
    - Color harmony and palette
    - Visual flow and leading lines
    - Overall visual appeal and artistic merit
    - Professional look and feel

  • semantic (0-10): Consider content meaning:
    - Cultural relevance and context
    - Emotional impact and sentiment
    - Storytelling potential
    - Message clarity
    - Audience resonance

  • novelty (0-10): Assess uniqueness:
    - Original perspective or angle
    - Unusual or rare subject matter
    - Creative execution
    - Stands out from typical content
    - Fresh or innovative approach

  • trendy_vibe (0-10): Evaluate social media appeal:
    - Alignment with current platform trends
    - Viral potential
    - Shareability
    - Platform-specific optimization
    - Engagement likelihood

  • metadata (0-10): Consider contextual factors:
    - Recency of capture
    - Associated data quality

  • activity (0-10): ONLY if the image shows clear action:
    - Must show actual movement or action
    - Clarity of the activity being performed
    - Dynamic composition
    - Energy and motion
    - If no activity is shown, rate this 0

  • achievement (0-10): ONLY if showing a clear accomplishment:
    - Must depict a specific milestone or achievement
    - Recognition or celebration
    - Progress or success
    - If no achievement is shown, rate this 0

  • talent (0-10): ONLY if showcasing specific skills:
    - Must demonstrate a particular skill or craft
    - Technical proficiency
    - Artistic ability
    - If no talent is demonstrated, rate this 0

Then compute an overall weighted average (0-10).
Respond **only** with valid JSON, for example:
{
  "technical": 8.2,
  "aesthetic": 7.4,
  "semantic": 6.5,
  "novelty": 9.0,
  "trendy_vibe": 5.8,
  "metadata": 4.7,
  "activity": 0.0,
  "achievement": 0.0,
  "talent": 0.0,
  "overall": 6.2
}"""

        # Download and encode the image
        image_uri = self._download_and_encode_image(image_url)

        return [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Here is the image description:\n{description}\n\nAnd here is its metadata:\n{json.dumps(metadata)}"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_uri
                        }
                    }
                ]
            }
        ]

    def _get_best_quality_url(self, base_url: str) -> str:
        """
        Get the highest quality image URL from Google Photos.

        Args:
            base_url (str): The base URL of the image.
        Returns:
            str: The URL for the highest quality image.
        """
        url = base_url.split('=')[0]
        return f"{url}=d"

    def rate_image(self, item: Dict[str, Any]) -> Dict[str, float]:
        """
        Send the image and metadata to the LLM and parse the returned JSON ratings.

        Args:
            item (dict): The image item with metadata.
        Returns:
            dict: The scores for each axis and overall.
        Raises:
            Exception: If the LLM response cannot be parsed as JSON.
        """
        image_url = self._get_best_quality_url(item['baseUrl'])
        messages = self._build_messages(image_url, item['description'], item['mediaMetadata'])
        response = self.client.chat(
            model=self.model,
            messages=messages,
            max_tokens=500
        )
        content = response.message.content[0].text
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", content, re.DOTALL)
            if match:
                return json.loads(match.group())
            logger.error("Failed to parse LLM response as JSON.")
            raise

    def rank_images(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rank a list of images by their overall LLM score.

        Args:
            items (list): List of image items with metadata.
        Returns:
            list: The same list with added 'scores' and sorted by 'overall' descending.
        """
        out = []
        for it in items:
            scores = self.rate_image(it)
            it = it.copy()
            it["scores"] = scores
            it["overall"] = scores.get("overall", 0.0)
            out.append(it)
        return sorted(out, key=lambda x: x["overall"], reverse=True)
