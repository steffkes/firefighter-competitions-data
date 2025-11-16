from util import Spider, ParticipantItem, ResultItem, ResultRankItem
import requests
import scrapy
import re


class CompetitionSpider(Spider):
    name = __name__

    race_id = "361075"
    race_key = "fd80837a7df5c6485f53ea7a3beb0f61"

    def start_requests(self):
        for contest in [10215, 10216]:
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

        for contest, type in [(1, "MPA"), (2, "OPA")]:
            yield scrapy.FormRequest(
                method="GET",
                url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
                formdata={
                    "key": self.race_key,
                    "contest": str(contest),
                    "listname": "10 Ergebnislisten|00 Ergebnisliste OA (Kategorie)",
                },
                cb_kwargs={
                    "competition_type": type,
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
        ranks = {"category": {}, "age_group": {}}

        for entry in response.json()["data"]:
            [
                bib,
                _id,
                status,
                _team,
                _nation,
                names,
                raw_age_group,
                raw_duration,
                _gap,
            ] = entry

            if status in ["DSQ", "DNF", "a.k."]:  # disqualified
                continue

            age_group = " ".join(raw_age_group.split(" ")[:-1])
            category = {
                "Burschen": "M",
                "Mannsbilder": "M",
                "Alte Knacker": "M",
                "Pärchen": "X",
                "Mädels": "W",
            }[age_group]

            rank_total = ranks.get("total", 1)
            rank_category = ranks["category"].get(category, 1)

            result = ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                type=competition_type,
                duration=self.fixDuration(raw_duration),
                category=category,
                names=sorted(map(str.strip, names.split("|"))),
                rank=ResultRankItem(total=rank_total, category=rank_category),
                bib=bib,
            )

            ranks["total"] = rank_total + 1
            ranks["category"][category] = rank_category + 1

            if category == "M":
                rank_age_group = ranks["age_group"].get(age_group, 1)

                result["age_group"] = age_group
                result["rank"]["age_group"] = rank_age_group

                ranks["age_group"][age_group] = rank_age_group + 1

            yield result
