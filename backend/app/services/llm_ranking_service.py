# llm_ranking_service.py

import os
import json
import re
import cohere
import requests
import base64
from typing import Any, Dict, List
from app.config import Config

class LLMBasedRankingService:
    """
    Uses a single multimodal LLM call to score images on multiple axes,
    then ranks them by the returned overall score.
    """

    def __init__(self, model_name: str = "c4ai-aya-vision-8b"):
        """
        :param model_name: the Cohere vision-capable model to call
        """
        api_key = Config.COHERE_API_KEY
        if not api_key:
            raise ValueError("Please set COHERE_API_KEY in your .env file")
        self.client = cohere.Client(api_key=api_key)
        self.model = model_name

    def _download_and_encode_image(self, image_url: str) -> str:
        """
        Downloads an image from a URL and converts it to base64.
        """
        try:
            response = requests.get(image_url)
            response.raise_for_status()
            image_data = response.content
            base64_image = base64.b64encode(image_data).decode('utf-8')
            return f"data:image/jpeg;base64,{base64_image}"
        except Exception as e:
            raise Exception(f"Failed to download and encode image: {str(e)}")

    def _build_messages(self, image_url: str, description: str, metadata: Dict[str, Any]):
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
        Gets the highest quality image URL from Google Photos.
        Removes any size restrictions and adds the highest quality parameter.
        """
        # Remove any existing size parameters
        url = base_url.split('=')[0]
        # Add the highest quality parameter
        return f"{url}=d"  # 'd' parameter requests the original image

    def rate_image(self, item: Dict[str, Any]) -> Dict[str, float]:
        """
        Sends the image + metadata to the LLM, parses and returns the JSON ratings.
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
            raise

    def rank_images(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        media_items: [
          {"id": "...",
           "description": "...",
           "filename": "...",
           "baseUrl": "...",
           "mediaMetadata": {"creationTime": "..."},
           ...
        ]
        Returns the same list with added 'scores' and sorted by 'overall' desc.
        """
        out = []
        for it in items:
            scores = self.rate_image(it)
            it = it.copy()
            it["scores"] = scores
            it["overall"] = scores.get("overall", 0.0)
            out.append(it)
        # sort highest overall first
        return sorted(out, key=lambda x: x["overall"], reverse=True)
