from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ValidationError
import json
import logging

class RoboticsTaskSchema(BaseModel):
    tasks: List[str] = Field(..., description="List of high-level tasks to be performed")
    objects: List[str] = Field(..., description="List of objects involved in the environment")
    initial_state: List[str] = Field(default_factory=list, description="List of PDDL-style initial state predicates")
    constraints: List[str] = Field(..., description="List of operational or safety constraints")
    robots: List[str] = Field(..., description="List of robot agents involved")
    goal_predicates: List[str] = Field(..., description="List of PDDL-style goal predicates")

def validate_json_response(content: str) -> Optional[Dict[str, Any]]:
    """
    Validates a string content against the RoboticsTaskSchema.
    Returns the parsed dictionary if valid, None otherwise.
    """
    try:
        # Attempt to find JSON block if wrapped in markdown
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        data = json.loads(content)
        RoboticsTaskSchema(**data)
        return data
    except (json.JSONDecodeError, ValidationError) as e:
        logging.error(f"Validation failed: {e}")
        return None

def get_empty_schema() -> Dict[str, Any]:
    return {
        "tasks": [],
        "objects": [],
        "initial_state": [],
        "constraints": [],
        "robots": [],
        "goal_predicates": []
    }
