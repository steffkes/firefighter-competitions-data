from util import Spider, ParticipantItem, ResultItem, ResultRankItem
import scrapy


class CompetitionSpider(Spider):
    name = __name__

    def start_requests(self):
        yield scrapy.FormRequest(
            method="POST",
            url="https://www.berlin-timing.de/Hochhauslauf/Startliste",
            formdata={"StartlisteStrecke": "Einsatzkräfte"},
            callback=self.parse_starters,
        )

        yield scrapy.FormRequest(
            method="GET",
            url="https://www.berlin-timing.de/Hochhauslauf/Ergebnis/2026-04-29/Einsatzkraefte",
        )

    def parse_starters(self, response):
        for row in response.css("table tbody tr"):
            [_, _, _, firstname, lastname, _, _] = row.css("td::text").getall()
            if firstname.lower() != "cop":
                yield ParticipantItem(
                    competition_id=self.competition_id,
                    names=["{} {}".format(firstname.strip(), lastname.strip())],
                )

    def parse(self, response):
        rank_total = 1
        rank_category = {"M": 1, "W": 1}
        rank_age_group = {}

        for row in response.css("table tbody tr"):
            [_, _, _, name, _, age_group, _, duration] = row.css("td::text").getall()

            if not name.lower().startswith("cop"):
                category = age_group[0].upper()
                yield ResultItem(
                    date=self.race_date,
                    competition_id=self.competition_id,
                    type="MPA",
                    duration=self.fixDuration(duration),
                    names=[name],
                    category=category,
                    age_group=age_group,
                    rank=ResultRankItem(
                        total=rank_total,
                        category=rank_category[category],
                        age_group=rank_age_group.get(age_group, 1),
                    ),
                )

                rank_total += 1
                rank_category[category] += 1
                rank_age_group[age_group] = rank_age_group.get(age_group, 1) + 1
