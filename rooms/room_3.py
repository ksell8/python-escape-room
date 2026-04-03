import asyncio

from .base import Room


class _Response:
    def __init__(self, url, links):
        self.url = url
        self.links = links
        self.body = "x" * 100_000  # ~100 KB of simulated page content


class _Request:
    def __init__(self, url, depth=0):
        self.url = url
        self.depth = depth


async def _fake_fetch(request) -> _Response:
    await asyncio.sleep(0)
    return _Response(request.url, links=[
        request.url + "/child-1",
        request.url + "/child-2",
    ])


_LOCKED_FNS = {
    "fake_fetch": _fake_fetch,
    "Response": _Response,
    "Request": _Request,
}

ROOM = Room(
    id=3,
    title="THE SPIDER'S WEB",
    flavor=(
        "The spider crawls pages and follows child links — but it hoards every\n"
        "response in memory before yielding a single one.\n"
        "Yield each response the moment it's fetched."
    ),
    measure="memory",
    threshold=5.0,
    memory_threshold=5.0,
    broken_label="~6 MB",
    fixed_label="< 5 MB",
    expected_output="https://example.com/page-1",
    required_calls=["fake_fetch", "run_engine", "start"],
    required_yields=["start"],
    locked_fns=_LOCKED_FNS,
    hint1="Where are the child links being stored?  Can you yield them so the calling function can use it?",
    hint2="The fix is in start(): move the yield inside the while loop, right after you fetch the response. Delete all_responses entirely & it's for loop.",
    code="""\
import asyncio

# Provided — do not redefine:
#   fake_fetch(request) -> Response with .url, .links, .body (~100 KB)
#   Request(url, depth=0), Response

max_depth = 4
seed_urls = ["https://example.com/page-1", "https://example.com/page-2"]

class Spider:
    async def start(self):
        all_responses = []
        queue = [Request(url) for url in seed_urls]
        while queue:
            req = queue.pop(0)
            response = await fake_fetch(req)
            all_responses.append(response)        # hoards every response before yielding
            if req.depth < max_depth:
                for link in response.links:
                    queue.append(Request(link, req.depth + 1))
        for response in all_responses:
            yield response

async def run_engine(spider):
    async for response in spider.start():
        print(response.url)

asyncio.run(run_engine(Spider()))
""",
)
