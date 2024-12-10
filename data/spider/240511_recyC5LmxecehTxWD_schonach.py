import scrapy
from datetime import datetime
import re
import itertools
from util import JsonItemExporter, JsonLinesItemExporter, ParticipantItem, ResultItem


class Spider(scrapy.Spider):
    name = __name__
    race_date = datetime.strptime(__name__.split("_")[0], "%y%m%d").strftime("%Y-%m-%d")
    competition_id = __name__.split("_")[1]
    ident = __name__[0:24]

    race_id = "279564"
    race_key = "0b390ff34ee4d88a57b036f1dc1fbf9e"

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
            method="GET",
            url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
            formdata={
                "key": self.race_key,
                "listname": "02_Teilnehmerlisten|Teilnehmer_Schanzenlauf",
                "contest": "1",
            },
            callback=self.parse_starters,
        )

        yield scrapy.FormRequest(
            method="GET",
            url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
            formdata={
                "key": self.race_key,
                "listname": "01_Feuerwehr|Ergebnisliste_Feuerwehr_Wertungen",
                "contest": "1",
            },
        )

    def parse_starters(self, response):
        fixName = lambda name: re.sub(
            r"^(.+)\s(.+)$",
            lambda match: "%s %s"
            % (
                match.group(2),
                re.sub(
                    r"^(.)(.+)$",
                    lambda match: "%s%s" % (match.group(1), match.group(2).lower()),
                    match.group(1),
                ),
            ),
            name.strip(),
        )

        for [_bib1, name1, _gender1, _competition1, _birthyear1, _category1], [
            _bib2,
            name2,
            _gender2,
            _competition2,
            _birthyear2,
            _category2,
        ] in itertools.batched(response.json()["data"], 2):
            yield ParticipantItem(
                competition_id=self.competition_id,
                names=sorted(map(fixName, [name1, name2])),
            )

    def parse(self, response):
        fixName = lambda name: re.sub(
            r"^(.+)\s(.+)$",
            lambda match: "%s %s"
            % (
                match.group(2),
                re.sub(
                    r"^(.)(.+)$",
                    lambda match: "%s%s" % (match.group(1), match.group(2).lower()),
                    match.group(1),
                ),
            ),
            name.strip(),
        )

        for category, teams in response.json()["data"].items():
            is_mpa = "Mit PA" in category
            for team, names in teams.items():
                duration = "00:%s.0" % team.split("///").pop().zfill(5)
                [
                    [_id1, bib, name1, gender1, _time1],
                    [_id2, _bib2, name2, gender2, _time2],
                ] = names
                yield ResultItem(
                    date=self.race_date,
                    competition_id=self.competition_id,
                    bib=bib,
                    type="MPA" if is_mpa else "OPA",
                    duration=duration,
                    category=None,
                    names=sorted(map(fixName, [name1, name2])),
                )
