from typing import List, Optional
from pydantic import BaseModel


class CompanyInfo(BaseModel):
    name: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    headquarters: Optional[str] = None
    locations: List[str] = []
    products: List[str] = []
    services: List[str] = []
    solutions: List[str] = []
    industries: List[str] = []


class ContactInfo(BaseModel):
    emails: List[str] = []
    phones: List[str] = []
    address: Optional[str] = None
    contact_page: Optional[str] = None
    social_profiles: List[str] = []


class PageResult(BaseModel):
    url: str
    title: Optional[str] = None
    category: Optional[str] = None
    status_code: Optional[int] = None
    processed: bool = False
    extraction_result: dict = {}


class CrawlStats(BaseModel):
    discovered: int = 0
    crawled: int = 0
    skipped: int = 0
    failed: int = 0


class CrawlResult(BaseModel):
    company: CompanyInfo
    contact: ContactInfo
    pages: List[PageResult]
    crawl_stats: CrawlStats