import requests
from sqlalchemy.orm import Session
from typing import Tuple, List, Optional, Dict
from app.database.models import Sentence, Token

TAGGER_URL = "http://80.72.180.130:8040/api/tagging"

class TaggingService:
    def __init__(self, db: Session):
        self.db = db

    def _parse_conllu(self, conllu_text: str) -> List[Tuple[str, List[Dict]]]:
        """
        Парсит ответ в формате conllu. Возвращает список кортежей: (sentence_text, tokens)
        token: { token_index, form, lemma, pos, xpos, feats(dict|None) }
        """
        result = []
        current_sentence_text: Optional[str] = None
        current_tokens: List[Dict] = []

        lines = conllu_text.splitlines()
        current_index = 1
        for line in lines:
            line = line.strip()
            if not line:
                # конец предложения, если были токены — сохраняем
                if current_sentence_text is not None:
                    result.append((current_sentence_text, current_tokens))
                current_sentence_text = None
                current_tokens = []
                current_index = 1
                continue

            if line.startswith('#'):
                if line.startswith('# text = '):
                    current_sentence_text = line[len('# text = '):]
                # игнорируем остальные комментарии (# newdoc, # newpar, # sent_id, ...)
                continue

            # строки токенов: id, form, lemma, upos, xpos, feats, ... разделены табуляцией
            parts = line.split('\t')
            if len(parts) < 5:
                continue
            # parts[0] — может быть число, пропускаем составные вроде 1-2
            if '-' in parts[0]:
                continue
            try:
                int(parts[0])
            except ValueError:
                continue

            form = parts[1]
            lemma = parts[2]
            pos = parts[3]
            xpos = parts[4]
            feats_raw = parts[5] if len(parts) > 5 else '_'

            feats: Optional[Dict[str, str]] = None
            if feats_raw and feats_raw != '_' and '=' in feats_raw:
                # feats формата A=B|C=D
                feats = {}
                for item in feats_raw.split('|'):
                    if '=' in item:
                        k, v = item.split('=', 1)
                        feats[k] = v

            current_tokens.append({
                'token_index': str(current_index),
                'form': form,
                'lemma': lemma,
                'pos': pos,
                'xpos': xpos,
                'feats': feats,
            })
            current_index += 1

        # если файл не заканчивается пустой строкой, добиваем последнее предложение
        if current_sentence_text is not None:
            result.append((current_sentence_text, current_tokens))

        return result

    def tag_and_store(self, text: str) -> Tuple[int, int]:
        """Отправляет текст на теггер, парсит conllu и сохраняет в БД."""
        response = requests.post(TAGGER_URL, json={'text': text}, timeout=120)
        response.raise_for_status()
        data = response.json()
        conllu = data.get('conllu', '')

        parsed = self._parse_conllu(conllu)
        sentences_created = 0
        tokens_created = 0

        for sentence_text, tokens in parsed:
            sentence = Sentence(text=sentence_text, is_corrected=0)
            self.db.add(sentence)
            self.db.flush()  # получить sentence.id
            sentences_created += 1

            for token in tokens:
                db_token = Token(
                    token_index=token['token_index'],
                    form=token['form'],
                    lemma=token['lemma'],
                    pos=token['pos'],
                    xpos=token['xpos'],
                    feats=token['feats'],
                    sentence_id=sentence.id,
                )
                self.db.add(db_token)
                tokens_created += 1

        self.db.commit()
        return sentences_created, tokens_created
