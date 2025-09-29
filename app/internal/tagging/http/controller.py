from fastapi import Depends
from sqlalchemy.orm import Session
from app.database.config import get_db
from app.domain.tagging_schemas import TagTextRequest, TagTextResponse
from app.internal.tagging.service import TaggingService

class TaggingController:
    def __init__(self):
        pass

    async def tag_text(self, payload: TagTextRequest, db: Session = Depends(get_db)) -> TagTextResponse:
        service = TaggingService(db)
        s_count, t_count = service.tag_and_store(payload.text)
        return TagTextResponse(message="Теггинг выполнен", sentences_created=s_count, tokens_created=t_count)
