from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.config import get_db
from app.domain.tagging_schemas import TagTextRequest, TagTextResponse
from app.internal.tagging.http.controller import TaggingController
from app.shared.dependencies import get_admin_user

router = APIRouter(prefix="/tagging", tags=["tagging"])

controller = TaggingController()

@router.post("/run", response_model=TagTextResponse, dependencies=[Depends(get_admin_user)])
async def run_tagging(payload: TagTextRequest, db: Session = Depends(get_db)):
    return await controller.tag_text(payload, db)
