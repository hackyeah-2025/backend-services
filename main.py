from fastapi import FastAPI, Body
import json

app = FastAPI()


# import base64
# import os
# from google import genai
# from google.genai import types
# from pydantic import BaseModel

# def generateForSpicy(Input):
#     client = genai.Client(
#         api_key="AIzaSyCKkntn5yb8dAQZaFlxkoPzCd0O9p01LEI",
#     )

#     model = "gemini-flash-latest"
#     contents = [
#         types.Content(
#             role="user",
#             parts=[
#                 types.Part.from_text(text=Input),
#             ],
#         ),
#     ]
#     # tools = [
#     #     types.Tool(googleSearch=types.GoogleSearch(
#     #     )),
#     # ]
#     generate_content_config = types.GenerateContentConfig(
#         thinking_config = types.ThinkingConfig(
#             thinking_budget=-1,
#         ),
#         media_resolution="MEDIA_RESOLUTION_UNSPECIFIED",
#         # tools=tools,
#         system_instruction=[
#             types.Part.from_text(text="""You are an expert AI Travel Planner whose sole purpose is to efficiently modify and re-balance an existing travel itinerary based on user requests. You must strictly adhere to the following steps: 1. Acknowledge the user's constraint. 2. Access the 'EXISTING_TRAVEL_PLAN_JSON' data provided. 3. Propose specific, itemized changes to the Itinerary, Budget, and/or Transport sections, ensuring all suggested changes are consistent across the entire plan. 4. Present the proposed changes clearly and ask for confirmation. """),
#         ],
#     )

#     response = client.models.generate_content(
#         model=model,
#         contents=contents,
#         config=generate_content_config,
#     )
#     return response.text



import base64
import os
from google import genai
from google.genai import types


def generateFromScratch(data: str):
    client = genai.Client(
        api_key="AIzaSyCKkntn5yb8dAQZaFlxkoPzCd0O9p01LEI",
    )

    model = "gemini-flash-latest"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=data),
            ],
        ),
    ]
    # tools = [
    #     types.Tool(googleSearch=types.GoogleSearch(
    #     )),
    # ]
    generate_content_config = types.GenerateContentConfig(
        thinking_config = types.ThinkingConfig(
            thinking_budget=-1,
        ),
        # tools=tools,

         # 1. Force JSON output
        response_mime_type="application/json",
        # 2. Pass the main Pydantic model (your schema)
        response_schema=TravelPlan,
        system_instruction=[
            types.Part.from_text(text="""You are a **Data Localization Engine** that updates travel itineraries from one destination to another while maintaining data integrity.

You are a highly advanced **Dynamic Itinerary Relocalizer**. Your function is to take an existing travel plan, maintain its internal structure, and translate the entire itinerary to a randomly selected, plausible new destination.

**Input Constraint:**
The input will be a complete trip plan JSON object with existing timestamps, and tasks. You must parse and process this raw JSON input.

**Your Goal:**
Generate a single, complete JSON object that represents a logically consistent itinerary for a new destination, while strictly adhering to all preservation rules.

**Decision Rule (Random Destination Selection):**
Before generating the output, you **MUST** randomly select a major, non-European world city (e.g., Seoul, Tokyo, Buenos Aires, Sydney, or Cairo) as the new destination for the itinerary.

**Execution Constraints (The Golden Rules):**
1.  **Pure JSON Output:** Your **ONLY** output must be the raw JSON object, starting with `{` and ending with `}`. **DO NOT** include any conversational text, explanations, or code block delimiters (```json).
2.  **Preservation Rule (Mandatory):** For all objects in the entire JSON structure, you **MUST RETAIN** the original values for the following administrative and structural fields. Do not attempt to generate or update timestamps unless absolutely required by a date change:
    * `createdAt`
    * `updatedAt`
    * `orderIndex`
    * `isCompleted`
    * `type`, `category` (preserve these unless the activity must be fundamentally changed)

3.  **Localization Rule (Mandatory Update):** You **MUST UPDATE** all content and location-specific fields to logically reflect the **newly selected destination** (e.g., Tokyo):
    * The **trip's title** (e.g., "Kyoto Cultural Immersion").
    * The **destination** (`destination`, `continent`, etc.) fields.
    * All **task titles** and **descriptions** to relevant landmarks and activities in the new city.
    * All **locations** (`locations[...].location` fields) to valid, real-world addresses in the new city.
    * All **transport details** (`transportDetails` object) to correctly route flights, taxis, and public transit to/from the new city's main international airport (e.g., Narita or Haneda for Tokyo).."""),
        ],
    )

    results = client.models.generate_content(
        model=model,
        contents=contents,
        config=generate_content_config,
    )
    return results.text





    



# class UserPromptJSON(BaseModel):
#     prompt: str



from pydantic import BaseModel, Field
from typing import List, Optional
# from uuid import UUID
from datetime import datetime

# --- Nested Models (Innermost to Outermost) ---

class Location(BaseModel):
    """Represents a specific geographic point in a task."""
    # id: UUID
    location: str
    locationType: str = Field(description="e.g., 'origin', 'waypoint', 'destination'")
    orderIndex: int

class TransportDetails(BaseModel):
    """Details specific to transportation tasks."""
    # id: UUID
    transportMode: str = Field(description="e.g., 'uber', 'flight', 'taxi', 'subway'")
    fromLocation: str
    toLocation: str
    estimatedDurationMinutes: int
    bookingReference: Optional[str] = None
    notes: Optional[str] = None
    departureTime: datetime # Matches ISO 8601 format with 'Z'
    arrivalTime: datetime   # Matches ISO 8601 format with 'Z'

class Task(BaseModel):
    """Represents a single step or item in the travel plan."""
    # id: UUID
    type: str = Field(description="e.g., 'activity', 'simple', 'transport', 'accommodation'")
    title: str
    description: str
    dueDate: datetime  # Use datetime for the ISO 8601 timestamp
    isCompleted: bool
    orderIndex: int
    category: str = Field(description="e.g., 'activity', 'lodging', 'transport', 'packing'")
    createdAt: datetime
    updatedAt: datetime
    # This field is null for simple/activity tasks, so it's optional
    transportDetails: Optional[TransportDetails] = None 
    locations: List[Location]

# ----------------------------------------------------------------------
# --- Main Object ---

class TravelPlan(BaseModel):
    """The main object representing the entire travel itinerary."""
    # id: UUID
    title: str
    duration: int = Field(description="Trip length in days")
    category: str = Field(description="e.g., 'Leisure', 'Business'")
    budget: float  # Use float/decimal for currency, or int if only whole numbers
    continent: str
    destination: str
    highRisk: bool = Field(description="Flag for high-risk travel (e.g., political unrest)")
    kidsFriendly: bool
    participants: int
    details: str
    # The 'tasks' array contains a list of the nested Task models
    tasks: List[Task]







#
@app.post("/ai/generateIteary")
async def returnIteary(data: dict = Body(..., media_type="application/json")):
    datastr = json.dumps(data)
    genresponse = generateFromScratch(datastr)
    


    genresponseJSON = json.loads(genresponse)
    return genresponseJSON

#send the last ai response that was liked, and make it return a ready json schema
# @app.post("/ai/FinalizeSpicy")
#     async def returnCompleteSpicy():
#     genresponse = 

