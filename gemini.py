"""Asks Gemini for the data of a species"""

import httpx
from dotenv import load_dotenv
from fastapi import HTTPException
from google import genai
from google.genai import errors
from pydantic import BaseModel, Field, ValidationError

from schemas import SpeciesIn

load_dotenv()

MODEL = "gemini-3.8-flash"
PROMPT = (
    "A user of a plant tracker typed the text below. It should name a plant, "
    "in any language. If it does not name a plant, set is_plant to false, "
    "leave the texts empty and set the numbers to 0.\n\nText: "
)

# Gemini can be slow or overloaded: give up a call after 20 s, try 3 times.
client = genai.Client(
    http_options={"timeout": 20_000, "retry_options": {"attempts": 3}}
)


class GeminiSpecies(BaseModel):
    """The shape Gemini has to answer in."""

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
                "response_mime_type": "application/json",
                "response_json_schema": GeminiSpecies.model_json_schema(),
                "automatic_function_calling": {"disable": True},
            },
        )
        answer = GeminiSpecies.model_validate_json(response.text)
        if not answer.is_plant:
            return None
        return SpeciesIn(
            name=answer.common_name,
            botanical_name=answer.botanical_name,
            watering_interval=answer.watering_interval,
            min_dli=answer.min_dli,
            max_dli=answer.max_dli,
        )
    except (errors.APIError, httpx.HTTPError, ValidationError) as error:
        print("gemini failed:", error)
        raise HTTPException(status_code=502, detail="gemini failed")
