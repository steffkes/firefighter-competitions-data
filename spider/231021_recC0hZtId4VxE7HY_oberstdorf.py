import scrapy
from datetime import datetime
import re
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

    race_id = 266311
    race_key = "bac6b526cf62ea3cc99afd4f707ac0cc"

    ranks = {"category": {}, "age_group": {}}

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
        for contest in [8152, 8153]:
            yield scrapy.FormRequest(
                method="GET",
                url="https://www.anmeldungs-service.de/module/teilnehmer/staffel_cache.php",
                formdata={
                    "wettid": str(contest),
                    "totalrows": "2000",
                },
                headers={
                    "X-Requested-With": "XMLHttpRequest",
                },
                callback=self.parse_starters,
            )

        yield scrapy.FormRequest(
            method="GET",
            url="https://my.raceresult.com/%d/RRPublish/data/list" % self.race_id,
            formdata={
                "key": self.race_key,
                "contest": "1",
                "listname": "10 Ergebnislisten|00 Ergebnisliste OA (Kategorie)",
            },
            cb_kwargs={
                "competition_type": "MPA",
            },
        )

        yield scrapy.FormRequest(
            method="GET",
            url="https://my.raceresult.com/%d/RRPublish/data/list" % self.race_id,
            formdata={
                "key": self.race_key,
                "contest": "2",
                "listname": "10 Ergebnislisten|00 Ergebnisliste OA (Kategorie)",
            },
            cb_kwargs={
                "competition_type": "OPA",
            },
        )

    def parse_starters(self, response):
        reverseName = lambda name: " ".join(
            reversed(list(map(str.strip, name.split(" "))))
        )
        fixName = lambda name: reverseName(
            re.match(r"^(.+)\s+\w\s+\d+$", name).group(1).strip()
        )

        data = response.json()["rows"]
        for entry in data:
            yield ParticipantItem(
                competition_id=self.competition_id,
                names=sorted(map(fixName, entry["cell"]["name"].split("<br>"))),
            )

    def parse(self, response, competition_type):
        for entry in response.json()["data"]:
            [_, status, bib, _, _, names, raw_age_group, raw_duration, _] = entry

            if status == "DSQ":  # disqualified
                continue

            names = sorted(map(str.strip, names.split("|")))
            duration = "00:" + raw_duration.replace(",", ".")
            age_group = " ".join(raw_age_group.split(" ")[:-1])
            category = {
                "Burschen": "M",
                "Mannsbilder": "M",
                "Alte Knacker": "M",
                "Pärchen": "X",
                "Mädels": "W",
            }[age_group]

            rank_total = self.ranks.get("total", 1)
            rank_category = self.ranks["category"].get(category, 1)

            result = ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                type=competition_type,
                duration=duration,
                category=category,
                names=names,
                rank=ResultRankItem(total=rank_total, category=rank_category),
                bib=bib,
            )

            self.ranks["total"] = rank_total + 1
            self.ranks["category"][category] = rank_category + 1

            if category == "M":
                rank_age_group = self.ranks["age_group"].get(age_group, 1)

                result["age_group"] = age_group
                result["rank"]["age_group"] = rank_age_group

                self.ranks["age_group"][age_group] = rank_age_group + 1

            yield result
