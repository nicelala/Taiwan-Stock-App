from app.db.base import Base
from app.db.session import engine

# 重要：要 import model，metadata 才會知道有哪些表
from app.models.stock_basic import StockBasic  # noqa: F401
from app.models.dividend_history import DividendHistory  # noqa: F401


def init_db() -> None:
    Base.metadata.create_all(bind=engine)