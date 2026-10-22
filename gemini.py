"""Asks Gemini for the data of a species.

Only used by POST /species/lookup, and only when the DB doesn't know the name.
"""

import httpx
from dotenv import load_dotenv
from fastapi import HTTPException
from google import genai
from google.genai import errors
from pydantic import BaseModel, Field, ValidationError

from schemas import SpeciesIn

# The Gemini client reads GEMINI_API_KEY from the environment, so .env must be
# loaded before the client is created below.
load_dotenv()

MODEL = "gemini-3.8-flash"
PROMPT = (
    "A user of a plant tracker typed the text below. It should name a plant, "
    "in any language. If it does not name a plant, set is_plant to false, "
    "leave the texts empty and set the numbers to 0.\n\nText: "
)

# Gemini can be slow or overloaded: give up a call after 20 s, try 3 times.
# Created once when the file loads: without GEMINI_API_KEY the app doesn't start.
client = genai.Client(
    http_options={"timeout": 20_000, "retry_options": {"attempts": 3}}
)


class GeminiSpecies(BaseModel):
    """The shape Gemini has to answer in.

    Sent to Gemini as a JSON schema; the descriptions tell it what each field means
    and which unit to use.
    """

    is_plant: bool = Field(description="false if the text does not name a plant")
    common_name: str = Field(
        description="common name in the language of the text, normally capitalized"
    )
    botanical_name: str = Field(
        description="genus and species only, no author or variety, "
        "e.g. Solanum lycopersicum"
    )
    watering_interval: int = Field(description="days between two waterings")
    min_dli: float = Field(description="lowest daily light integral in mol/m²/day")
    max_dli: float = Field(description="highest daily light integral in mol/m²/day")


def ask_gemini(name: str) -> SpeciesIn | None:
    """Returns the species data for a typed plant name, None if it is no plant."""
    print("asking gemini for", name)
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=PROMPT + name,
            config={
                # Answer as JSON in exactly the GeminiSpecies shape, not as free text.
                "response_mime_type": "application/json",
                "response_json_schema": GeminiSpecies.model_json_schema(),
                # We give it no tools to call; this just switches the feature off.
                "automatic_function_calling": {"disable": True},
            },
        )
        # Turns the JSON text into a GeminiSpecies; fails if fields are missing.
        answer = GeminiSpecies.model_validate_json(response.text)
        if not answer.is_plant:
            return None
        # Through SpeciesIn, so Gemini's data must follow the same rules as
        # hand-made species (interval > 0, min_dli <= max_dli, ...).
        return SpeciesIn(
            name=answer.common_name,
            botanical_name=answer.botanical_name,
            watering_interval=answer.watering_interval,
            min_dli=answer.min_dli,
            max_dli=answer.max_dli,
        )
    # APIError: Gemini answered with an error (e.g. 429 quota, 503 overloaded).
    # HTTPError: no connection or timeout. ValidationError: the answer broke a rule.
    # All three: Gemini is the problem, not the user, so 502 (bad gateway).
    except (errors.APIError, httpx.HTTPError, ValidationError) as error:
        print("gemini failed:", error)
        raise HTTPException(status_code=502, detail="gemini failed")
