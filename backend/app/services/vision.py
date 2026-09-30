"""
Vision step: caption an incident photo and flag visible hazards
(fire, smoke, structural damage, visible injuries, hazmat signage).

Uses a Groq-hosted vision-capable Llama model. In MOCK_MODE, returns a
canned caption so the pipeline can be demoed without an API key or a
real photo.
"""

import base64

from app.config import settings

_MOCK_CAPTION = (
    "Photo shows a two-car collision on a paved road. Visible smoke near "
    "the front of one vehicle. No visible fire. One person appears to be "
    "seated on the curb, no other bystanders visible."
)


def _encode_image(image_path: str) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def caption_photo(image_path: str) -> str:
    if settings.MOCK_MODE:
        return _MOCK_CAPTION

    from groq import Groq  # imported lazily so MOCK_MODE needs no SDK

    client = Groq(api_key=settings.GROQ_API_KEY)
    b64_image = _encode_image(image_path)

    response = client.chat.completions.create(
        model=settings.GROQ_VISION_MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "You are assisting emergency dispatch. Describe this "
                            "incident scene photo factually in 2-3 sentences. "
                            "Explicitly mention any visible fire, smoke, structural "
                            "damage, hazardous materials signage, or visible injuries. "
                            "Do not speculate beyond what is visible."
                        ),
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"},
                    },
                ],
            }
        ],
        temperature=0.1,
        max_tokens=200,
    )
    return response.choices[0].message.content.strip()
