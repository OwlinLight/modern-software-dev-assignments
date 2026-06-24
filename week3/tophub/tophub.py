from datetime import date, timedelta
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("tophub")

HUB_API_BASE = "https://api.github.com"
USER_AGENT = "tophub-app/1.0"


async def make_hub_request(
    url: str, params: dict[str, Any] | None = None
) -> dict[str, Any] | None:
    """Make a request to HUB API with proper error handling"""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None


def format_repo_summary(data: dict[str, Any], limit: int = 20) -> str:
    """
    Format key information from GitHub Search Repositories API response.

    Expected input:
    data = response.json()
    """

    repos = data.get("items", [])

    if not repos:
        return "No repositories found."

    summaries = []
    for i, repo in enumerate(repos[:limit], start=1):
        name = repo.get("full_name", "N/A")
        description = repo.get("description") or "No description"
        stars = repo.get("stargazers_count", 0)
        forks = repo.get("forks_count", 0)
        language = repo.get("language") or "Unknown"
        url = repo.get("html_url", "N/A")
        created_at = repo.get("created_at", "N/A")
        updated_at = repo.get("updated_at", "N/A")

        summaries.append(
            f"""{i}. {name}
   Description: {description}
   Language: {language}
   Stars: {stars:,} | Forks: {forks:,}
   Created: {created_at}
   Updated: {updated_at}
   URL: {url}"""
        )

    return "\n\n".join(summaries)


@mcp.tool()
async def get_tops(days: int) -> str:
    url = f"{HUB_API_BASE}/search/repositories"
    since = (date.today() - timedelta(days=days)).isoformat()
    params = {
        "q": f"created:>={since} is:public",
        "sort": "stars",
        "order": "desc",
        "per_page": 5,
    }
    data = await make_hub_request(url, params=params)

    if not data:
        return "Unable to fetch GitHub repository data."

    return format_repo_summary(data, limit=5)


def main():
    # Initialize and run the server
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
