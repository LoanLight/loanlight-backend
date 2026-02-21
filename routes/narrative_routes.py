from fastapi import APIRouter
import json
from pathlib import Path

router = APIRouter(prefix="/narrative", tags=["narrative"])

@router.get("")
def narrative():
    p = Path("assets/narrative.json")
    if p.exists():
        return json.loads(p.read_text())
    return {"cards": []}