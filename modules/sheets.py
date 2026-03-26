from __future__ import annotations

import json
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
HEADER = ["프리셋명", "키워드", "분류기준"]


def _get_sheet():
    """Google Sheets 워크시트 연결"""
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES,
    )
    client = gspread.authorize(creds)
    sheet = client.open_by_key(st.secrets["GOOGLE_SHEET_ID"])

    # '프리셋' 시트가 없으면 생성
    try:
        ws = sheet.worksheet("프리셋")
    except gspread.WorksheetNotFound:
        ws = sheet.add_worksheet(title="프리셋", rows=100, cols=3)
        ws.append_row(HEADER)

    # 헤더가 없으면 추가
    if ws.row_values(1) != HEADER:
        ws.insert_row(HEADER, 1)

    return ws


def load_presets() -> dict[str, dict]:
    """
    저장된 프리셋 목록을 반환합니다.
    반환값: {"프리셋명": {"keywords": "...", "categories": {...}}, ...}
    """
    try:
        ws = _get_sheet()
        rows = ws.get_all_records()
        presets = {}
        for row in rows:
            name = str(row.get("프리셋명", "")).strip()
            if not name:
                continue
            try:
                categories = json.loads(row.get("분류기준", "{}"))
            except Exception:
                categories = {}
            presets[name] = {
                "keywords": str(row.get("키워드", "")),
                "categories": categories,
            }
        return presets
    except Exception as e:
        st.warning(f"프리셋 불러오기 실패: {e}")
        return {}


def save_preset(name: str, keywords: str, categories: dict) -> bool:
    """
    프리셋을 저장합니다. 같은 이름이 있으면 덮어씁니다.
    """
    try:
        ws = _get_sheet()
        rows = ws.get_all_values()

        new_row = [name, keywords, json.dumps(categories, ensure_ascii=False)]

        # 같은 이름 행이 있으면 업데이트
        for i, row in enumerate(rows[1:], start=2):  # 헤더 제외
            if row and str(row[0]).strip() == name:
                ws.update(f"A{i}:C{i}", [new_row])
                return True

        # 없으면 새 행 추가
        ws.append_row(new_row)
        return True

    except Exception as e:
        st.warning(f"프리셋 저장 실패: {e}")
        return False


def delete_preset(name: str) -> bool:
    """프리셋을 삭제합니다."""
    try:
        ws = _get_sheet()
        rows = ws.get_all_values()

        for i, row in enumerate(rows[1:], start=2):
            if row and str(row[0]).strip() == name:
                ws.delete_rows(i)
                return True
        return False

    except Exception as e:
        st.warning(f"프리셋 삭제 실패: {e}")
        return False
