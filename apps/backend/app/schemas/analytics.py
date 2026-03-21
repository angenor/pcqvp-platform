from datetime import datetime

from pydantic import BaseModel


class TrendItem(BaseModel):
    date: str
    count: int


class VisitStats(BaseModel):
    total: int
    by_page_type: dict[str, int]
    trend: list[TrendItem]


class DownloadStats(BaseModel):
    total: int
    by_format: dict[str, int]
    trend: list[TrendItem]


class DataRetentionInfo(BaseModel):
    oldest_record: datetime | None = None
    purge_eligible_count: int = 0
    purge_eligible: bool = False


class DashboardResponse(BaseModel):
    period: str
    visits: VisitStats
    downloads: DownloadStats
    data_retention: DataRetentionInfo


class PurgeResponse(BaseModel):
    purged_count: int
    message: str
