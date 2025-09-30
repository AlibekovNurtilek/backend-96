from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from app.database.config import get_db
from app.database.models import Sentence, Token
from app.domain.tagging_schemas import (
    TagTextRequest,
    TagTextResponse,
    PaginatedSentencesResponse,
    PageMeta,
    SentenceResponse,
    SentenceWithTokensResponse,
    UpdateSentenceRequest,
)
from app.internal.tagging.service import TaggingService


class TaggingController:
    def __init__(self):
        pass

    async def tag_text(self, payload: TagTextRequest, db: Session = Depends(get_db)) -> TagTextResponse:
        service = TaggingService(db)
        s_count, t_count = service.tag_and_store(payload.text)
        return TagTextResponse(message="Теггинг выполнен", sentences_created=s_count, tokens_created=t_count)

    async def list_sentences(
    self,
    page: int,
    page_size: int,
    search: Optional[str],
    status: Optional[int],
    db: Session = Depends(get_db)
) -> PaginatedSentencesResponse:
        if page < 1 or page_size < 1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="page and page_size must be >= 1")

        query = db.query(Sentence)

        # Фильтр по статусу
        if status is not None:
            query = query.filter(Sentence.is_corrected == status)

        # Поиск по тексту
        if search:
            query = query.filter(Sentence.text.ilike(f"%{search}%"))

        total_items = query.count()
        total_pages = (total_items + page_size - 1) // page_size
        if total_pages == 0:
            total_pages = 1
        if page > total_pages and total_items > 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page out of range")

        offset = (page - 1) * page_size
        sentences = (
            query.order_by(Sentence.id.asc())
            .limit(page_size)
            .offset(offset)
            .all()
        )

        items = [SentenceResponse.model_validate(s) for s in sentences]

        return PaginatedSentencesResponse(
            meta=PageMeta(
                current_page=page,
                page_size=page_size,
                total_pages=total_pages,
                total_items=total_items
            ),
            items=items,
        )


    async def get_sentence_with_tokens(self, sentence_id: int, db: Session = Depends(get_db)) -> SentenceWithTokensResponse:
        sentence = db.query(Sentence).filter(Sentence.id == sentence_id).first()
        if not sentence:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sentence not found")
        # ensure tokens are loaded
        _ = sentence.tokens  # access relationship
        return SentenceWithTokensResponse(
            id=sentence.id,
            text=sentence.text,
            is_corrected=sentence.is_corrected,
            tokens=[
                {
                    "id": t.id,
                    "token_index": t.token_index,
                    "form": t.form,
                    "lemma": t.lemma,
                    "pos": t.pos,
                    "xpos": t.xpos,
                    "feats": t.feats,
                }
                for t in sentence.tokens
            ],
        )

    async def update_sentence_and_tokens(self, sentence_id: int, payload: UpdateSentenceRequest, db: Session = Depends(get_db)) -> SentenceWithTokensResponse:
        sentence = db.query(Sentence).filter(Sentence.id == sentence_id).first()
        if not sentence:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sentence not found")

        if payload.sentence_text is not None:
            sentence.text = payload.sentence_text
        if payload.is_corrected is not None:
            sentence.is_corrected = payload.is_corrected

        if payload.tokens:
            # Update provided tokens by id
            token_ids = [t.id for t in payload.tokens]
            db_tokens = db.query(Token).filter(Token.id.in_(token_ids), Token.sentence_id == sentence.id).all()
            db_tokens_by_id = {t.id: t for t in db_tokens}
            for t_update in payload.tokens:
                db_t = db_tokens_by_id.get(t_update.id)
                if not db_t:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Token id {t_update.id} not found for sentence")
                if t_update.token_index is not None:
                    db_t.token_index = t_update.token_index
                if t_update.form is not None:
                    db_t.form = t_update.form
                if t_update.lemma is not None:
                    db_t.lemma = t_update.lemma
                if t_update.pos is not None:
                    db_t.pos = t_update.pos
                if t_update.xpos is not None:
                    db_t.xpos = t_update.xpos
                if t_update.feats is not None:
                    db_t.feats = t_update.feats

        db.commit()
        db.refresh(sentence)
        _ = sentence.tokens
        return await self.get_sentence_with_tokens(sentence.id, db)
