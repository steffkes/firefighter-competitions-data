import scrapy
from datetime import datetime
import requests
import re
from functools import reduce


class SlotItem(scrapy.Item):
    competition_id = scrapy.Field()
    amount = scrapy.Field()
    label = scrapy.Field()


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
        self.slots = []

        self._kwargs.setdefault("indent", 2)
        self._kwargs.setdefault("ensure_ascii", not self.encoding)
        self.encoder = ScrapyJSONEncoder(**self._kwargs)

    def finish_exporting(self):
        idMapper = lambda item: item["competition_id"]
        competition_id = next(
            iter(set(map(idMapper, self.items + self.slots))),
            None,
        )

        if not competition_id:
            return

        def slotReducer(state, slot):
            label = slot.get("label")

            if label not in state:
                state[label] = {"amount": 0}
                if label:
                    state[label]["label"] = label

            state[label]["amount"] += slot["amount"]

            return state

        slots = sorted(
            reduce(slotReducer, self.slots, {}).values(),
            key=lambda slot: slot.get("label"),
        )

        teams = sorted(
            map(lambda item: item["names"], self.items),
            key=lambda names: (len(names), list(map(lambda name: name or "", names))),
        )

        data = {
            "competition_id": competition_id,
            "slots": slots,
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
        if isinstance(item, ParticipantItem):
            self.items.append(item)
        elif isinstance(item, SlotItem):
            self.slots.append(item)
        else:
            raise "unknown type"


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
                item.get("category", ""),
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


class Spider(scrapy.Spider):
    ranks = {"category": {}, "age_group": {}}

    custom_settings = {
        "DEFAULT_REQUEST_HEADERS": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        },
        "FEED_EXPORTERS": {
            "starter": JsonItemExporter,
            "results": JsonLinesItemExporter,
        },
        "FEEDS": {
            "data/participants/%(ident)s.json": {
                "format": "starter",
                "encoding": "utf8",
                "overwrite": True,
                "item_classes": [ParticipantItem, SlotItem],
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

    def __init__(self):
        self.race_date = datetime.strptime(self.name.split("_")[0], "%y%m%d").strftime(
            "%Y-%m-%d"
        )
        self.competition_id = self.name.split("_")[1]
        self.ident = self.name[0:24]

        super().__init__()

    @staticmethod
    def fixName(name):
        return name

    @staticmethod
    def fixDuration(duration):
        return re.sub(
            r"((\d+)[:h])?(\d+)[:'](\d+)([,\.](\d)\d*)?",
            lambda match: "{0:02d}:{1:02d}:{2:02d}.{3}".format(
                *map(lambda input: int(input or 0), match.group(2, 3, 4, 6))
            ),
            duration,
        )


class FirefitSpider(Spider):

    competition_map = {
        "individual - men": ("MPA", "M individual"),
        "individual - women": ("MPA", "W individual"),
        "tandem - men": ("OPA", "M tandem"),
        "tandem - women": ("OPA", "W tandem"),
        "tandem - mixed": ("OPA", "X tandem"),
        "relay - men": ("OPA", "M relay"),
        "relay - women": ("OPA", "W relay"),
        "relay - mixed": ("OPA", "X relay"),
        "relay - women & mixed": ("OPA", "W & X relay"),
        # 'relay - elimination - men',
        # 'relay - elimination - women',
        # 'relay - elimination - mixed'
        # 'relay - elimination - women & mixed'
    }

    def parse_slots(self, response, contest):
        match = re.match(r"\d+", response.css(".stock.in-stock::text").get(default=""))
        yield SlotItem(
            competition_id=self.competition_id,
            amount=int(match.group()) if match else 0,
            label=contest,
        )

    def parse(self, response):
        tables = response.css("table.ffc-table-dark")
        buttons = response.css(".ffc-button.table-selector::text").getall()

        for (type, category), table in [
            (self.competition_map[button], tables[index])
            for (index, button) in enumerate(buttons)
            if button in self.competition_map
        ]:
            ranks = {"age_group": {}}
            age_selectors = [
                {
                    "label": item.css("::text").get(),
                    "min_age": int(item.css("::attr(data-age-min)").get()),
                    "max_age": int(item.css("::attr(data-age-max)").get()),
                }
                for item in table.css(".age-selectors div")[1:]
            ]

            for row in table.css("tbody tr.status-ok"):
                raw_duration = "".join(row.css(".result-line1 span::text").getall())

                names = [row.css(".name-line1::text").get().strip()]
                team = sorted(row.css(".member-name span::text").getall())
                if len(team):
                    names = team

                result = ResultItem(
                    date=self.race_date,
                    competition_id=self.competition_id,
                    type=type,
                    duration=self.fixDuration(raw_duration),
                    names=names,
                    category=category,
                    rank=ResultRankItem(
                        category=int(
                            row.css(".rank-val.age-overall::text").get()[0:-1]
                        ),
                    ),
                )

                if age_selectors:
                    age = int(row.css(".age::text").get())
                    age_group = next(
                        (
                            ag["label"]
                            for ag in age_selectors
                            if ag["min_age"] <= age <= ag["max_age"]
                        ),
                        None,
                    )
                    if age_group:
                        result["age_group"] = age_group
                        result["rank"]["age_group"] = ranks["age_group"].get(
                            age_group, 1
                        )
                        ranks["age_group"][age_group] = result["rank"]["age_group"] + 1

                yield result


class FccSpider(Spider):
    event_day_ids = []
    age_group_fallback = None

    @staticmethod
    def fixName(name):
        return re.sub(r"\s+", " ", name.strip())

    def start_requests(self):
        if self.event_day_ids:
            yield scrapy.FormRequest(
                method="GET",
                url="https://www.firefighter-challenge-germany.de/combat-challenge/registrierungsliste/",
                callback=self.parse_starters,
            )

        if self.get("event_id"):
            yield scrapy.FormRequest(
                method="GET",
                url="https://www.firefighter-challenge-germany.de/ergebnisse/",
            )

    def parse_starters(self, response):
        for event_day_id in self.event_day_ids:
            for row in response.css(
                "table[data-eventdayid='{}'] tr".format(event_day_id)
            ):
                entry = row.css("td:nth-child(3)::text").get()

                if not entry:
                    continue

                yield ParticipantItem(
                    competition_id=self.competition_id,
                    names=sorted(map(self.fixName, entry.split(","))),
                )

    def parse(self, response):
        yield from self.parse_single(response)
        yield from self.parse_teams(response)

    def parse_single(self, response):
        ranks = {"category": {}, "age_group": {}}
        for row in response.css(
            "div[data-targetid='overall'][data-target='results-{}'] table tbody tr".format(
                self.event_id
            )
        ):
            if row.css(".place::text").get() in ["DSQ", "DNS"]:
                continue

            age_group = row.css(".ageclass::text").get() or self.age_group_fallback
            category = "%s individual" % age_group[0].upper()

            rank_total = ranks.get("total", 1)
            rank_category = ranks["category"].get(category, 1)
            rank_age_group = ranks["age_group"].get(age_group, 1)

            yield ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                type="MPA",
                duration=self.fixDuration(row.css(".totaltime::text").get()),
                names=[self.fixName(row.css(".member::text").get())],
                category=category,
                age_group=age_group,
                rank=ResultRankItem(
                    total=rank_total,
                    category=rank_category,
                    age_group=rank_age_group,
                ),
            )

            ranks["total"] = rank_total + 1
            ranks["category"][category] = rank_category + 1
            ranks["age_group"][age_group] = rank_age_group + 1

    def parse_teams(self, response):
        for target_id, category in [
            ("TF", "W tandem"),
            ("TM", "M tandem"),
            ("TMIX", "X tandem"),
            ("RV", "relay"),
        ]:
            for row in response.css(
                "div[data-targetid='{}'][data-target='results-{}'] table tbody tr".format(
                    target_id, self.event_id
                ),
            ):
                if row.css(".place::text").get() in ["DSQ", "DNS"]:
                    continue

                yield ResultItem(
                    date=self.race_date,
                    competition_id=self.competition_id,
                    type="OPA",
                    duration=self.fixDuration(row.css(".totaltime::text").get()),
                    names=sorted(
                        filter(
                            bool,
                            map(
                                self.fixName, row.css(".member::text").get().split(",")
                            ),
                        )
                    ),
                    category=category,
                    rank=ResultRankItem(category=int(row.css(".place::text").get())),
                )


class BadWildbadSpider(Spider):
    ranks = {"category": {}}

    def start_requests(self):
        yield scrapy.FormRequest(
            method="GET",
            url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
            formdata={
                "key": self.race_key,
                "listname": "Online|Teilnehmerliste ABC",
                "contest": "3",
            },
            callback=self.parse_starters,
        )

        yield scrapy.FormRequest(
            method="GET",
            url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
            formdata={
                "key": self.race_key,
                "listname": "Online|Zieleinlaufliste",
                "contest": "3",
            },
        )

    @staticmethod
    def fixName(name):
        return name

    def parse_starters(self, response):
        fixName = lambda name: " ".join(reversed(list(map(str.strip, name.split(",")))))

        for [
            _bib,
            _bib2,
            name,
            _nationality,
            _byear,
            _gender,
            _category,
            _team,
            _empty,
        ] in (response.json()["data"] or {}).get("#1_Feuerwehr-Stäffeleslauf", []):
            yield ParticipantItem(
                competition_id=self.competition_id, names=[fixName(name)]
            )

    def parse(self, response):
        for [
            bib,
            _bib2,
            _rank,
            name,
            _nationality,
            _byear,
            category,
            _gender_full,
            team,
            raw_duration,
            _time_difference,
        ] in (response.json()["data"] or {}).get("#1_Feuerwehr-Stäffeleslauf", []):
            duration = "00:%s.0" % raw_duration

            rank_total = self.ranks.get("total", 1)
            rank_category = self.ranks["category"].get(category, 1)

            yield ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                type="OPA",
                duration=duration,
                names=[self.fixName(name)],
                category=category,
                rank=ResultRankItem(total=rank_total, category=rank_category),
                bib=bib,
            )

            self.ranks["total"] = rank_total + 1
            self.ranks["category"][category] = rank_category + 1


class RottweilSpider(Spider):
    custom_starter = None

    def start_requests(self):
        for contest, data_key in self.custom_starter or [(5, None), (6, None)]:
            yield scrapy.FormRequest(
                method="GET",
                url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
                formdata={
                    "key": self.race_key,
                    "listname": "07 - Teilnehmer - PUBLIC|Teilnehmer ABC-Team",
                    "contest": str(contest),
                },
                cb_kwargs={
                    "data_key": data_key,
                },
                callback=self.parse_starters,
            )

        for contest, competition_type, data_key in [
            (5, "MPA", "#1_{DE:Feuerwehr-Team mit PA|EN:Firefighters team with SCBA}"),
            (
                6,
                "OPA",
                "#1_{DE:Feuerwehr-Team ohne PA|EN:Firefighters team without SCBA}",
            ),
        ]:
            yield scrapy.FormRequest(
                method="GET",
                url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
                formdata={
                    "key": self.race_key,
                    "listname": "01 - Detail|Details Team",
                    "contest": str(contest),
                },
                cb_kwargs={
                    "competition_type": competition_type,
                },
            )

    def parse_starters(self, response, data_key):
        data = response.json()["data"]

        if data_key:
            data = data[data_key]

        for [_id, _id2, _bib, _team, names, _category] in data:
            yield ParticipantItem(
                competition_id=self.competition_id,
                names=sorted(names.split(" / ")),
            )

    def parse(self, response, competition_type):
        def fixName(name):
            return name.split("(")[0].strip()

        for [
            _id,
            _id2,
            bib,
            person1,
            person2,
            _team,
            _org,
            _reason_dsq,
            _label_placement,
            _label_total,
            category,
            age_group,
            _contest,
            raw_duration,
            _speed,
            rank_total,
            rank_category,
            rank_age_group,
        ] in response.json()["data"]:
            if not rank_total:
                continue

            yield ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                type=competition_type,
                duration=self.fixDuration(raw_duration.split(" ")[0]),
                names=sorted(map(fixName, [person1, person2])),
                category={"Männer": "M", "Frauen": "W", "Mixed": "X"}.get(
                    category[:-1]
                ),
                age_group=age_group[:-1],
                rank=ResultRankItem(
                    total=int(rank_total[:-1]),
                    category=int(rank_category[:-1]),
                    age_group=int(rank_age_group[:-1]),
                ),
                bib=bib,
            )


import pytest


@pytest.mark.parametrize(
    "output,input",
    [
        ("00:13:31.6", "13:31,6"),
        ("01:00:27.0", "1:00:27,0"),
        ("00:05:48.3", "5:48,34"),
        ("00:02:55.7", "2:55,70"),
        ("00:02:46.9", "2:46,96"),
        ("00:07:23.4", "00h07'23,4"),
        ("00:08:52.3", "00h08'52,3"),
        ("00:12:49.6", "00h12'49,6"),
        ("00:01:37.8", "01:37.89"),
        ("00:04:35.2", "04:35.29"),
        ("00:02:11.9", "00:02:11.9100000"),
        ("00:02:36.5", "00:02:36.5500000"),
        ("00:45:35.0", "45:35"),
    ],
)
def test_fixDuration(input, output):
    assert Spider.fixDuration(input) == output
