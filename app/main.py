from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl

from app.crawler.http_client import fetch_page
from app.extraction.company import extract_company_info
from app.models.schemas import (
    CompanyInfo,
    ContactInfo,
    CrawlResult,
    CrawlStats,
    PageResult,
)


app = FastAPI(
    title="Company Information Crawler",
    description=(
        "A system for crawling company websites "
        "and extracting useful information."
    ),
    version="1.0.0",
)


class CrawlRequest(BaseModel):
    url: HttpUrl


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/")
async def root():
    return {
        "message": "Company Information Crawler API"
    }


@app.post("/crawl", response_model=CrawlResult)
async def crawl_company(request: CrawlRequest):

    url = str(request.url)

    status_code, final_url, html = await fetch_page(url)

    if not html:
        raise HTTPException(
            status_code=502,
            detail=f"Unable to process website: {url}",
        )

    company_data = extract_company_info(
        html,
        final_url,
    )

    company = CompanyInfo(
        name=company_data["name"],
        website=company_data["website"],
        description=company_data["description"],
    )

    page = PageResult(
        url=final_url,
        title=company_data["name"],
        category="home",
        status_code=status_code,
        processed=True,
        extraction_result=company_data,
    )

    result = CrawlResult(
        company=company,
        contact=ContactInfo(),
        pages=[page],
        crawl_stats=CrawlStats(
            discovered=1,
            crawled=1,
            skipped=0,
            failed=0,
        ),
    )

    return result