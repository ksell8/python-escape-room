from .base import Room

ROOM = Room(
    id=4,
    title="THE FINAL LOCK",
    flavor=(
        "This is how Scrapy actually works — it runs on Twisted under the hood.\n"
        "Twisted wraps around an async runner (like asyncio) to schedule jobs.\n"
        "Scrapy uses a DeferredQueue: spiders put requests in, workers pull them out.\n"
        "Right now there's one worker, so pages fetch one at a time (~2s).\n"
        "Spawn all workers at once with gatherResults() to unlock the door."
    ),
    measure="time",
    threshold=1.0,
    broken_label="~2.0s",
    fixed_label="< 1.0s",
    hint1="gatherResults() is Twisted's asyncio.gather() — pass it a list of Deferreds and they run concurrently.",
    hint2=(
        "Replace the for loop with:\n"
        "  workers = [worker(queue, results) for _ in range(5)]\n"
        "  yield gatherResults(workers)"
    ),
    required_calls=["gatherResults", "worker", "run_engine"],
    expected_output="fetched 5 pages",
    code="""\
import asyncio
from twisted.internet import defer
from twisted.internet.defer import DeferredQueue, inlineCallbacks, gatherResults


def fetch(request):
    \"\"\"Simulate an HTTP fetch — takes 0.4 seconds.\"\"\"
    loop = asyncio.get_running_loop()
    future = loop.create_future()
    loop.call_later(0.4, future.set_result, f"200 OK: {request.url}")
    return defer.Deferred.fromFuture(future)


@inlineCallbacks
def worker(queue, results):
    request = yield queue.get()
    result = yield fetch(request)
    results.append(result)


@inlineCallbacks
def run_engine(spider):
    queue = DeferredQueue()
    for req in spider.start_requests():
        queue.put(req)

    results = []
    # TODO: one worker processes requests one at a time — fix this
    for _ in range(5):
        yield worker(queue, results)

    return results


class Request:
    def __init__(self, url): self.url = url
    def __repr__(self): return f"Request({self.url!r})"


class ScrapySpider:
    def start_requests(self):
        for i in range(5):
            yield Request(f"https://example.com/page/{i}")


async def main():
    d = run_engine(ScrapySpider())
    results = await d.asFuture(asyncio.get_event_loop())
    print(f"fetched {len(results)} pages")


asyncio.run(main())
""",
)
