"""
EduShield AI — Module Xác thực Giám thị dùng chung (Shared-Secret Token Auth)

Tách riêng từ main.py để cả API module Giám sát (violations) và module Đề thi (exams)
đều dùng chung 1 cơ chế xác thực, không lặp code và tránh import vòng giữa các router.
"""

import logging
import os
import secrets
from typing import Optional

from fastapi import Header, HTTPException, Query

logger = logging.getLogger("edushield.auth")

# Token cố định dùng để xác thực Giám thị. ƯU TIÊN lấy từ biến môi trường
# PROCTOR_API_TOKEN; nếu không có, sinh 1 token ngẫu nhiên MỖI LẦN khởi động
# (an toàn hơn dùng giá trị mặc định cố định) và in ra log để giám thị copy dùng.
PROCTOR_API_TOKEN = os.environ.get("PROCTOR_API_TOKEN")
USING_GENERATED_TOKEN = False
if not PROCTOR_API_TOKEN:
    PROCTOR_API_TOKEN = secrets.token_urlsafe(24)
    USING_GENERATED_TOKEN = True


def verify_proctor_token(
    x_proctor_token: Optional[str] = Header(default=None, alias="X-Proctor-Token"),
    token: Optional[str] = Query(default=None, description="Token giám thị (dùng cho ảnh <img>)"),
) -> None:
    """
    Dependency xác thực Giám thị bằng shared-secret token — dùng chung cho MỌI API
    yêu cầu quyền giám thị, bao gồm cả module Giám sát (violations) và module Đề thi (exams).

    Chấp nhận token qua:
      - Header "X-Proctor-Token" (dùng cho các lệnh gọi fetch() JSON từ dashboard)
      - Query string "?token=" (dùng cho thẻ <img src="..."> vì không set được header)

    So sánh bằng secrets.compare_digest để chống timing attack cơ bản.
    """
    supplied = x_proctor_token or token
    if not supplied or not secrets.compare_digest(supplied, PROCTOR_API_TOKEN):
        raise HTTPException(
            status_code=401,
            detail="Yêu cầu token giám thị hợp lệ (header X-Proctor-Token hoặc ?token=)",
        )
