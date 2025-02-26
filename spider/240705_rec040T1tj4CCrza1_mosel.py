from util import Spider, ParticipantItem, ResultItem, ResultRankItem
import scrapy
import re


class CompetitionSpider(Spider):
    name = __name__

    @staticmethod
    def fixName(name):
        return re.sub(r"\s+", " ", name.strip())

    def start_requests(self):
        yield scrapy.FormRequest(
            method="GET",
            url="https://www.firefighter-challenge-germany.de/combat-challenge/registrierungsliste/",
            callback=self.parse_starters,
        )

        yield scrapy.FormRequest(
            method="GET",
            url="https://www.firefighter-challenge-germany.de/ergebnisse/",
        )

    def parse_starters(self, response):
        for row in response.css("table[data-eventdayid='34'] tr"):
            entry = row.css("td:nth-child(3)::text").get()

            if not entry:
                continue

            yield ParticipantItem(
                competition_id=self.competition_id,
                names=sorted(map(self.fixName, entry.split(","))),
            )

        for row in response.css("table[data-eventdayid='35'] tr"):
            entry = row.css("td:nth-child(3)::text").get()

            if not entry:
                continue

            yield ParticipantItem(
                competition_id=self.competition_id,
                names=sorted(map(self.fixName, entry.split(","))),
            )

        for row in response.css("table[data-eventdayid='36'] tr"):
            entry = row.css("td:nth-child(3)::text").get()

            if not entry:
                continue

            yield ParticipantItem(
                competition_id=self.competition_id,
                names=sorted(map(self.fixName, entry.split(","))),
            )

    def parse(self, response):
        ranks = {"category": {}, "age_group": {}}
        for row in response.css(
            "div[data-targetid='overall'][data-target='results-17'] table tbody tr"
        ):
            if row.css(".place::text").get() in ["DSQ", "DNS"]:
                continue

            age_group = row.css(".ageclass::text").get()
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

        for row in response.css(
            "div[data-targetid='TF'][data-target='results-17'] table tbody tr"
        ):
            if row.css(".place::text").get() in ["DSQ", "DNS"]:
                continue

            yield ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                type="OPA",
                duration=self.fixDuration(row.css(".totaltime::text").get()),
                names=sorted(
                    map(self.fixName, row.css(".member::text").get().split(","))
                ),
                category="W tandem",
                rank=ResultRankItem(category=int(row.css(".place::text").get())),
            )

        for row in response.css(
            "div[data-targetid='TM'][data-target='results-17'] table tbody tr"
        ):
            if row.css(".place::text").get() in ["DSQ", "DNS"]:
                continue

            yield ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                type="OPA",
                duration=self.fixDuration(row.css(".totaltime::text").get()),
                names=sorted(
                    map(self.fixName, row.css(".member::text").get().split(","))
                ),
                category="M tandem",
                rank=ResultRankItem(category=int(row.css(".place::text").get())),
            )

        for row in response.css(
            "div[data-targetid='RV'][data-target='results-17'] table tbody tr"
        ):
            if row.css(".place::text").get() in ["DSQ", "DNS"]:
                continue

            yield ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                type="OPA",
                duration=self.fixDuration(row.css(".totaltime::text").get()),
                names=sorted(
                    map(self.fixName, row.css(".member::text").get().split(","))
                ),
                category="relay",
                rank=ResultRankItem(category=int(row.css(".place::text").get())),
            )
