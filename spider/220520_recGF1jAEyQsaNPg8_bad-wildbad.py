from util import Spider, ResultItem, ResultRankItem
import scrapy

changedParticipants = {"Matheis Stefan": "Stefan Matheis"}


class CompetitionSpider(Spider):
    name = __name__

    race_id = "190046"
    race_key = "dcfc10746a9a44c2c15233d73a47d22e"

    def start_requests(self):
        yield scrapy.FormRequest(
            method="GET",
            url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
            formdata={
                "key": self.race_key,
                "listname": "Ergebnislisten|Ergebnisliste gesamt",
                "contest": "3",
            },
        )

    def parse(self, response):
        for [
            bib,
            _id1,
            rank_total,
            category,
            rank_category,
            firstname,
            lastname,
            _team,
            _yob,
            _age,
            age_group,
            rank_age_group,
            raw_duration,
            _certificate_link,
            _empty,
        ] in (response.json()["data"] or {}).get("#1_Feuerwehr-Stäffeleslauf", []):
            name = "{} {}".format(firstname, lastname)

            yield ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                type="OPA",
                duration=self.fixDuration(raw_duration),
                names=[changedParticipants.get(name, name)],
                category=category.upper(),
                age_group=age_group,
                rank=ResultRankItem(
                    total=int(rank_total[:-1]),
                    category=int(rank_category[:-1]),
                    age_group=int(rank_age_group[:-1]),
                ),
                bib=bib,
            )
