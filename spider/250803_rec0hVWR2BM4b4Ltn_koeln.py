import scrapy
from util import (
    Spider,
    ParticipantItem,
    ResultItem,
    ResultRankItem,
    SlotItem,
)
import requests


class CompetitionSpider(Spider):
    name = __name__

    race_id = "323602"
    race_key = "77bdc85dcb9f1b7a137834310113b943"

    def start_requests(self):
        for contest in [5, 6]:
            yield scrapy.FormRequest(
                method="GET",
                url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
                formdata={
                    "key": self.race_key,
                    "listname": "07 - Teilnehmer|Teilnehmerliste ABC Team",
                    "contest": str(contest),
                },
                callback=self.parse_starters,
            )

        yield scrapy.FormRequest(
            method="GET",
            url="https://my.raceresult.com/%s/RRRegStart/data/config" % self.race_id,
            callback=self.parse_slots,
        )

        for contest, competition_type, data_key in [
            (5, "MPA", "#1_{DE:Feuerwehr-Team mit PA|EN:Firefighters with SCBA}"),
            (
                6,
                "OPA",
                "#1_{DE:Feuerwehr-Team ohne PA|EN:Firefighters without SCBA}",
            ),
        ]:
            r = requests.get(
                "https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
                params={
                    "key": self.race_key,
                    "listname": "01 - Detail|Details Team",
                    "contest": str(contest),
                },
            )

            yield scrapy.FormRequest(
                method="GET",
                url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
                formdata={
                    "key": self.race_key,
                    "contest": str(contest),
                    "listname": "02 - Ergebnislisten|Mannschaftswertung Ges",
                },
                cb_kwargs={
                    "competition_type": competition_type,
                    "data_key": data_key,
                    "details": dict(map(lambda row: (row[2], row), r.json()["data"])),
                },
            )

    def parse_starters(self, response):
        fixName = lambda name: " ".join(reversed(list(map(str.strip, name.split(",")))))

        data = list(response.json()["data"].values())[0]
        for [_bib, _number2, _id, _team, names, _category] in data:
            yield ParticipantItem(
                competition_id=self.competition_id,
                names=sorted(map(fixName, names.split(" / "))),
            )

    def parse_slots(self, response):
        data = response.json()

        isRegClosed = data["Now"] >= data["RegUntil"]
        if isRegClosed:
            yield SlotItem(competition_id=self.competition_id, amount=0)

    def parse(self, response, data_key, competition_type, details):
        for entry in response.json()["data"][data_key]:
            [_id1, _id2, status, bib, _team, names, age_group, raw_duration] = entry

            # sometimes contains an additional asterik at the end
            if status[0:4] == "a.k.":  # DNF / DSQ
                continue

            [category, _] = age_group.split(" ")
            names = sorted(map(str.strip, names.split("/")))
            duration = self.fixDuration(raw_duration)

            [
                _id,
                _id2,
                _bib,
                _person1,
                _person2,
                _team,
                _unknown,
                _unknown,
                _label1,
                _label2,
                _label3,
                _label4,
                _contest,
                _duration,
                _speed,
                rank_total,
                rank_category,
                rank_age_group,
            ] = details[bib]

            yield ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                duration=duration,
                type=competition_type,
                category={"MIX": "X"}.get(category, category),
                names=names,
                age_group=age_group,
                rank=ResultRankItem(
                    total=int(rank_total[:-1]),
                    category=int(rank_category[:-1]),
                    age_group=int(rank_age_group[:-1]),
                ),
                bib=bib,
            )
