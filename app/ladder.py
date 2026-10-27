"""Budget ladder: what to do at each budget threshold. Only dev projects are ever touched."""


def decide(percent: int, env: str) -> str:
    if percent >= 100:
        return "stop_resources" if env == "dev" else "page_owner"
    if percent >= 90:
        return "open_ticket"
    if percent >= 50:
        return "notify_team"
    return "none"
