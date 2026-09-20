from util import Spider, ParticipantItem, ResultItem, ResultRankItem
import scrapy


class CompetitionSpider(Spider):
    name = __name__

    def start_requests(self):
        yield scrapy.Request("data:,", dont_filter=True, callback=self.parse_starters)
        yield scrapy.Request("data:,", dont_filter=True)

    def parse_starters(self, response):
        for name in [
            "Tim Martin Speier",
            "Stefan Matheis",
            "Steve Roidl",
            "Damian Pyka",
            "Jasmin Bohun",
            "Petra Koch",
            "Philipp Döhler",
        ]:
            yield ParticipantItem(competition_id=self.competition_id, names=[name])

    def parse(self, response):
        rank_category = {"M": 1, "W": 1}
        for rank_total, (raw_duration, category, name) in enumerate(
            [
                ("00:43:19.13", "M", "Tim Martin Speier"),
                ("00:48:57.18", "M", "Stefan Matheis"),
                ("00:52:13.30", "M", "Steve Roidl"),
                ("00:57:12.13", "M", "Damian Pyka"),
                ("01:15:03.73", "W", "Jasmin Bohun"),
                ("01:23:42.87", "W", "Petra Koch"),
                ("01:47:32.91", "M", "Philipp Döhler"),
            ]
        ):
            yield ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                type="OPA",
                duration=self.fixDuration(raw_duration),
                names=[name],
                category=category,
                rank=ResultRankItem(
                    total=rank_total + 1, category=rank_category[category]
                ),
            )
            rank_category[category] += 1
