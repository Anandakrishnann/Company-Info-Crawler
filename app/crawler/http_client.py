import httpx


DEFAULT_TIMEOUT = 15.0


async def fetch_page(url: str) -> tuple[int, str, str]:
    """
    Fetch a webpage.

    Returns:
        status_code
        final_url
        html_content
    """

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/139.0 Safari/537.36"
        )
    }

    try:
        async with httpx.AsyncClient(
            timeout=DEFAULT_TIMEOUT,
            follow_redirects=True,
            headers=headers,
        ) as client:

            response = await client.get(url)

            content_type = response.headers.get(
                "content-type", ""
            ).lower()

            if "text/html" not in content_type:
                return response.status_code, str(response.url), ""

            return (
                response.status_code,
                str(response.url),
                response.text,
            )

    except httpx.TimeoutException:
        return 408, url, ""

    except httpx.RequestError:
        return 0, url, ""