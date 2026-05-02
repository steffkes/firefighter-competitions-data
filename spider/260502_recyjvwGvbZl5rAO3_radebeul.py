from util import Spider, ParticipantItem, ResultItem, ResultRankItem
import scrapy


class CompetitionSpider(Spider):
    name = __name__

    race_id = "393274"
    race_key = "b68addad6b48d1f289af1dff5edc6921"

    def start_requests(self):
        yield scrapy.FormRequest(
            method="GET",
            url="https://my.raceresult.com/%s/results/list" % self.race_id,
            formdata={"key": self.race_key, "listname": "Feuerwehr|Ergebnis-Online"},
        )

    def parse(self, response):
        rank_total = 1
        rank_category = {"M": 1, "X": 1, "W": 1}

        for record in response.json()["data"].values():
            [
                [_, _, _, name1, _, raw_duration, category, _],
                [_, _, _, name2, _, _, _, _],
            ] = record

            category = {"Männer-Team": "M", "Mixed-Team": "X", "Frauen-Team": "W"}[
                category
            ]

            yield ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                type="MPA",
                duration=self.fixDuration(raw_duration),
                names=sorted([name1, name2]),
                category=category,
                rank=ResultRankItem(
                    total=rank_total,
                    category=rank_category[category],
                ),
            )

            rank_total += 1
            rank_category[category] += 1
