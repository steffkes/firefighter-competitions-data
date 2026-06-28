import scrapy
from util import (
    Spider,
    ParticipantItem,
    ResultItem,
    ResultRankItem,
    SlotItem,
)
import requests
import itertools


class CompetitionSpider(Spider):
    name = __name__

    race_id = "375344"
    race_key = "8909e64154c10a08ec9249ea496c7d02"

    def start_requests(self):
        for contest in [5, 6]:
            yield scrapy.FormRequest(
                method="GET",
                url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
                formdata={
                    "key": self.race_key,
                    "listname": "07-TEILNEHMER|Teilnehmerliste ABC",
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
            yield scrapy.FormRequest(
                method="GET",
                url="https://my.raceresult.com/%s/results/list" % self.race_id,
                formdata={
                    "key": self.race_key,
                    "contest": str(contest),
                    "listname": "02-ERGEBNISSE|Mannschaftswertung Ges",
                },
                cb_kwargs={
                    "competition_type": competition_type,
                    "data_key": data_key,
                },
            )

    def parse_starters(self, response):
        fixName = lambda name: " ".join(reversed(list(map(str.strip, name.split(",")))))

        data = list(response.json()["data"].values())[0]

        teamGetter = lambda row: row[6]
        teams = itertools.groupby(sorted(data, key=teamGetter), key=teamGetter)
        for _key, team in teams:
            yield ParticipantItem(
                competition_id=self.competition_id,
                names=sorted(map(lambda row: fixName(row[3]), team)),
            )

    def parse_slots(self, response):
        data = response.json()

        isRegClosed = data["Now"] >= data["RegUntil"]
        if isRegClosed:
            yield SlotItem(competition_id=self.competition_id, amount=0)

    def parse(self, response, data_key, competition_type):
        for entry in response.json()["data"][data_key]:
            [
                _id1,
                pid,
                _rank_total,
                _bib,
                _team,
                raw_names,
                _age_group,
                _raw_duration,
            ] = entry

            yield scrapy.FormRequest(
                method="GET",
                url="https://my.raceresult.com/%s/details/view" % self.race_id,
                formdata={"lang": "en", "standalone": "false", "pid": str(pid)},
                callback=self.parse_detail,
                cb_kwargs={
                    "competition_type": competition_type,
                    "names": raw_names.split(" / "),
                },
            )

    def parse_detail(self, response, competition_type, names):
        data = response.json()
        elementKeys = dict(
            map(
                lambda record: (record[1]["ID"], record[0]), enumerate(data["Elements"])
            )
        )
        ranking = data["Elements"][elementKeys["3uDykg"]]["Children"][0]["Children"]

        yield ResultItem(
            date=self.race_date,
            competition_id=self.competition_id,
            duration=self.fixDuration(
                data["Elements"][elementKeys["2f5s2P"]]["Children"][0]["Children"][0][
                    "Config"
                ]["Field"]
            ),
            type=competition_type,
            category={"Männer": "M", "Mixed": "X", "Frauen": "W"}[
                ranking[1]["Config"]["Title"]
            ],
            names=sorted(names),
            age_group=ranking[2]["Config"]["Title"],
            rank=ResultRankItem(
                total=int(ranking[0]["Config"]["Field"][:-1]),
                category=int(ranking[1]["Config"]["Field"][:-1]),
                age_group=int(ranking[2]["Config"]["Field"][:-1]),
            ),
        )
