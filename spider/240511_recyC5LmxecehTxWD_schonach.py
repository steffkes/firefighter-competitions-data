import scrapy
from datetime import datetime
import re
import itertools
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

        groups = []
        entries = []
        for group, teams in response.json()["data"].items():
            (contest, raw_age_group) = re.match(
                r"#\d_((Ohne|Mit) PA) / (\w+)\s", group
            ).group(1, 3)
            type = "MPA" if "Mit PA" == contest else "OPA"

            for team, names in teams.items():
                [rank_age_group, raw_duration] = re.match(
                    r"\#\d+_(\d+)\.///.*?///(.+)", team
                ).group(1, 2)
                [
                    [_id1, bib, name1, gender1, _time1],
                    [_id2, _bib2, name2, gender2, _time2],
                ] = names

                duration = "00:%s.0" % raw_duration.zfill(5)
                gender = list(set([gender1, gender2]))
                category = gender[0] if len(gender) == 1 else "X"
                age_group = raw_age_group if category == "M" else None
                groups.append((type, category, age_group))

                result = ResultItem(
                    date=self.race_date,
                    competition_id=self.competition_id,
                    type=type,
                    duration=duration,
                    names=sorted(map(fixName, [name1, name2])),
                    category=category,
                    bib=bib,
                )

                if age_group:
                    result["age_group"] = age_group

                entries.append(result)

        entries = sorted(entries, key=lambda record: record["duration"])

        for group in sorted(set(groups)):
            (type, category, age_group) = group

            entries_type = list(filter(lambda entry: entry["type"] == type, entries))
            entries_category = list(
                filter(lambda entry: entry["category"] == category, entries_type)
            )
            entries_age_group = list(
                filter(
                    lambda entry: entry.get("age_group") == age_group, entries_category
                )
            )

            for entry in entries_age_group:
                entry["rank"] = ResultRankItem(
                    total=entries_type.index(entry) + 1,
                    category=entries_category.index(entry) + 1,
                )

                if "age_group" in entry:
                    entry["rank"]["age_group"] = entries_age_group.index(entry) + 1

                yield entry
