from util import Spider, ParticipantItem, ResultItem, ResultRankItem
import scrapy


class CompetitionSpider(Spider):
    name = __name__

    def start_requests(self):
        yield scrapy.FormRequest(
            method="GET",
            url="https://www.1-sv-gera.de/etl-meldeliste.html",
            callback=self.parse_starters,
            dont_filter=True,
        )

        yield scrapy.Request("data:,", dont_filter=True)

    def parse_starters(self, response):
        for table in response.css("table[summary*='TreppenlaufFeuerwehr']"):
            for rows in table.css("tbody tr"):
                row = rows.css("td::text").getall()
                yield ParticipantItem(
                    competition_id=self.competition_id,
                    names=["{} {}".format(row[1], row[0])],
                )

    def parse(self, response):
        for rank_total, (
            duration,
            (category, rank_category),
            (age_group, rank_age_group),
            name,
        ) in enumerate(
            [
                ("00:15:54,8", ("M", 1), ("M40", 1), "Stefan Matheis"),
                ("00:15:55,8", ("M", 2), ("M35", 1), "Tobias Diedrigkeit"),
                ("00:19:00.1", ("M", 3), ("M45", 1), "Karsten Neupert"),
                ("00:19:18.9", ("M", 4), ("M20", 1), "Florian Wedel"),
                ("00:20:18.4", ("M", 5), ("M35", 2), "Max Zschach"),
                ("00:23:07.4", ("W", 1), ("W35", 1), "Jasmin Bohun"),
                ("00:23:07.9", ("M", 6), ("M20", 2), "Erik Langenhahn"),
                ("00:25:13.7", ("M", 7), ("M20", 3), "Lucas Kröning"),
                ("00:25:16.4", ("M", 8), ("M20", 4), "Colin Zeißner"),
            ]
        ):
            yield ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                type="MPA",
                duration=duration,
                names=[name],
                rank=ResultRankItem(
                    total=rank_total + 1,
                    category=rank_category,
                    age_group=rank_age_group,
                ),
            )
