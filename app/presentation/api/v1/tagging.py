from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from fastapi import Query
from app.database.config import get_db
from app.domain.tagging_schemas import TagTextRequest, TagTextResponse, PaginatedSentencesResponse, SentenceWithTokensResponse, UpdateSentenceRequest
from app.internal.tagging.http.controller import TaggingController
from app.shared.dependencies import get_admin_user, get_current_user
from typing import Optional, List
from fastapi import Form, Body

router = APIRouter(prefix="/tagging", tags=["tagging"])

controller = TaggingController()

@router.post("/run", response_model=TagTextResponse, dependencies=[Depends(get_admin_user)])
async def run_tagging(
    text_form: Optional[str] = Form(None),                       # text из multipart
    file: Optional[UploadFile] = File(None),                     # файл из multipart
    payload: Optional[TagTextRequest] = Body(None),              # JSON { "text": "..." }
    db: Session = Depends(get_db),
):
    text: Optional[str] = None

    # 1. Если файл загружен
    if file is not None:
        if file.content_type not in ("text/plain", "application/octet-stream") and not file.filename.endswith(".txt"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only .txt files are supported")
        content_bytes = await file.read()
        try:
            text = content_bytes.decode("utf-8")
        except UnicodeDecodeError:
            text = content_bytes.decode("cp1251", errors="ignore")

    # 2. Если пришёл текст через multipart form
    if not text and text_form:
        text = text_form

    # 3. Если пришёл JSON { "text": "..." }
    if not text and payload and payload.text:
        text = payload.text

    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide text in JSON, form-data or upload a .txt file",
        )

    # Теперь у тебя всегда есть text
    return await controller.tag_text(TagTextRequest(text=text), db)

# User routes (authenticated, not admin-only)
@router.get("/sentences", response_model=PaginatedSentencesResponse)
async def get_sentences(
    page: int = 1,
    page_size: int = 20,
    search: Optional[str] = Query(None, description="Поиск по тексту"),
    status: Optional[int] = Query(None, description="Фильтр по статусу (0 - не исправлено, 1 - исправлено)"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return await controller.list_sentences(page, page_size, search, status, db)


@router.get("/sentences/{sentence_id}", response_model=SentenceWithTokensResponse)
async def get_sentence(sentence_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return await controller.get_sentence_with_tokens(sentence_id, db)


@router.patch("/sentences/{sentence_id}", response_model=SentenceWithTokensResponse)
async def patch_sentence(sentence_id: int, payload: UpdateSentenceRequest, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return await controller.update_sentence_and_tokens(sentence_id, payload, db)
