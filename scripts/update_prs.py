import json
import os
import re
import urllib.parse
import urllib.request

USER = os.environ.get("GH_USER", "darskkaa")
QUERY = f"is:pr author:{USER} is:merged -user:{USER}"
START, END = "<!-- PRS:START -->", "<!-- PRS:END -->"

url = "https://api.github.com/search/issues?" + urllib.parse.urlencode(
    {"q": QUERY, "sort": "updated", "order": "desc", "per_page": 20}
)
req = urllib.request.Request(
    url,
    headers={
        "Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
        "Accept": "application/vnd.github+json",
    },
)
items = json.load(urllib.request.urlopen(req))["items"]

prs = []
for it in items:
    repo = it["repository_url"].split("/repos/", 1)[1]
    merged = (it["pull_request"].get("merged_at") or it["closed_at"])[:10]
    prs.append((merged, repo, it["number"], it["title"], it["html_url"]))
prs.sort(reverse=True)

lines = [
    f"- `{merged}` **[{repo}#{num}]({link})**: {title}"
    for merged, repo, num, title, link in prs[:6]
]
block = START + "\n" + "\n".join(lines) + "\n" + END

with open("README.md", encoding="utf-8") as f:
    readme = f.read()
new = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _: block, readme, flags=re.S)
if new != readme:
    with open("README.md", "w", encoding="utf-8", newline="\n") as f:
        f.write(new)
