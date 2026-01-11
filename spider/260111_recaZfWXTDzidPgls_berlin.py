import scrapy
from datetime import datetime
from util import (
    JsonItemExporter,
    JsonLinesItemExporter,
    ParticipantItem,
    ResultItem,
    ResultRankItem,
)


class Spider(scrapy.Spider):
    name = __name__
    race_date = datetime.strptime(__name__.split("_")[0], "%y%m%d").strftime("%Y-%m-%d")
    competition_id = __name__.split("_")[1]
    ident = __name__[0:24]

    race_id = "1728"

    custom_settings = {
        "FEED_EXPORTERS": {
            "starter": JsonItemExporter,
            "results": JsonLinesItemExporter,
        },
        "FEEDS": {
            "data/participants/%(ident)s.json": {
                "format": "starter",
                "encoding": "utf8",
                "overwrite": True,
                "item_classes": [ParticipantItem],
            },
            "data/results/%(name)s.jsonl": {
                "format": "results",
                "encoding": "utf8",
                "overwrite": True,
                "item_classes": [ResultItem],
            },
        },
        "EXTENSIONS": {
            "scrapy.extensions.telnet.TelnetConsole": None,
        },
    }

    def start_requests(self):
        yield scrapy.FormRequest(
            url="https://ziel-zeit.de/suche.php",
            formdata={
                "action": "list",
                "lauf_id": self.race_id,
                "name_tabelle": "erg_1_" + self.race_id,
                "strecke": "Feuerwehr-Lauf",
            },
            cb_kwargs={
                "competition_type": "MPA",
            },
        )

    def parse(self, response, competition_type):
        for row in response.css('[class^="LineContainer"]'):
            name = fixName(row.css('[name="sp4"]::text').get().strip())
            raw_duration = row.css('[name="sp9"]::text').get().strip().split(" ")[0]
            age_group = row.css('[name="sp5"]::text').get().strip()

            yield ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                type=competition_type,
                category=age_group[0],
                duration="00:%s.0" % ("0" + raw_duration)[-5:],
                names=[name],
                age_group=age_group,
                rank=ResultRankItem(
                    total=int(row.css('[name="sp1"]::text').get().strip()),
                    category=int(
                        row.css('[name="sp2"]::text').get().strip()
                        or row.css('[name="sp3"]::text').get().strip()
                    ),
                    age_group=int(row.css('[name="sp6"]::text').get().strip()),
                ),
            )


def fixName(name):
    return " ".join(reversed(name.split(","))).strip()


import pytest


@pytest.mark.parametrize(
    "input,output",
    [
        ("Fröhlich, Tobias", "Tobias Fröhlich"),
        ("de Vries, Bjarne", "Bjarne de Vries"),
        ("Walter, Kilian Alexander", "Kilian Alexander Walter"),
    ],
)
def test_fixName(input, output):
    assert fixName(input) == output
