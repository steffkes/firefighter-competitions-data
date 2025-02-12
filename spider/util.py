import scrapy
from datetime import datetime


class ParticipantItem(scrapy.Item):
    competition_id = scrapy.Field()
    names = scrapy.Field()


class ResultRankItem(scrapy.Item):
    total = scrapy.Field()
    category = scrapy.Field()
    age_group = scrapy.Field()


class ResultItem(scrapy.Item):
    date = scrapy.Field()
    competition_id = scrapy.Field()
    duration = scrapy.Field()
    type = scrapy.Field()
    category = scrapy.Field()
    names = scrapy.Field()
    bib = scrapy.Field()
    age_group = scrapy.Field()
    rank = scrapy.Field()


from scrapy.utils.python import to_bytes
from scrapy.exporters import (
    BaseItemExporter,
    JsonLinesItemExporter as BaseJsonLinesItemExporter,
)
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
        if not len(self.items):
            return

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


class JsonLinesItemExporter(BaseJsonLinesItemExporter):
    def __init__(self, file, **kwargs):
        super().__init__(file, **kwargs)

        self.items = []

    def export_item(self, item):
        self.items.append(item)

    def finish_exporting(self):
        results = sorted(
            self.items,
            key=lambda item: (
                item["duration"],
                item["type"],
                item.get("category"),
                item.get("age_group"),
                item.get("bib"),
            ),
        )

        self.file.write(
            to_bytes(
                "\n".join(map(self.encoder.encode, results)) + "\n",
                self.encoding,
            )
        )
