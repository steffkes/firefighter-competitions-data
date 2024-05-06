import scrapy
from datetime import datetime


class ParticipantItem(scrapy.Item):
    competition_id = scrapy.Field()
    names = scrapy.Field()


class ResultItem(scrapy.Item):
    date = scrapy.Field()
    competition_id = scrapy.Field()
    bib = scrapy.Field()
    type = scrapy.Field()
    duration = scrapy.Field()
    category = scrapy.Field()
    names = scrapy.Field()


from scrapy.utils.python import to_bytes
from scrapy.exporters import BaseItemExporter
from scrapy.utils.serialize import ScrapyJSONEncoder
import itertools


class JsonItemExporter(BaseItemExporter):
    def __init__(self, file, **kwargs):
        super().__init__(dont_fail=True, **kwargs)

        self.file = file
        self.items = []

        self._kwargs.setdefault("indent", 2)
        self._kwargs.setdefault("ensure_ascii", not self.encoding)
        self.encoder = ScrapyJSONEncoder(**self._kwargs)

    def finish_exporting(self):
        teams = sorted(
            map(lambda item: item["names"], self.items),
            key=lambda entry: (len(entry), entry),
        )
        data = {
            "date": datetime.now().isoformat(),
            "competition_id": self.items[0]["competition_id"],
            "count": len(list(itertools.chain.from_iterable(teams))),
            "teams": teams,
        }

        self.file.write(
            to_bytes(
                self.encoder.encode(data) + "\n",
                self.encoding,
            )
        )

    def export_item(self, item):
        self.items.append(item)
