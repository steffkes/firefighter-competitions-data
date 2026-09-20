from util import Spider, ParticipantItem, ResultItem, ResultRankItem
import scrapy


class CompetitionSpider(Spider):
    name = __name__

    def start_requests(self):
        yield scrapy.Request("data:,", dont_filter=True, callback=self.parse_starters)
        yield scrapy.Request("data:,", dont_filter=True)

    def parse_starters(self, response):
        for name in [
            "Stefan Matheis",
            "Steve Roidl",
            "Jasmin Bohun",
            "Petra Koch",
            "Philipp Döhler",
        ]:
            yield ParticipantItem(competition_id=self.competition_id, names=[name])

    def parse(self, response):
        rank_category = {"M": 1, "W": 1}
        for rank_total, (raw_duration, category, name) in enumerate(
            [
                ("00:40:03.56", "M", "Stefan Matheis"),
                ("00:44:41.16", "M", "Steve Roidl"),
                ("01:08:36.36", "W", "Jasmin Bohun"),
                ("01:11:22.41", "M", "Philipp Döhler"),
                ("01:20:45.45", "W", "Petra Koch"),
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
