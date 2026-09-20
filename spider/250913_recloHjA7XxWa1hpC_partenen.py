from util import Spider, ParticipantItem, ResultItem, ResultRankItem
import scrapy


class CompetitionSpider(Spider):
    name = __name__

    def start_requests(self):
        yield scrapy.Request("data:,", dont_filter=True, callback=self.parse_starters)
        yield scrapy.Request("data:,", dont_filter=True)

    def parse_starters(self, response):
        for name in ["Stefan Matheis", "Nicolas Faure", "Marcel König", "Elias Vogt"]:
            yield ParticipantItem(competition_id=self.competition_id, names=[name])

    def parse(self, response):
        rank_category = {"M": 1, "W": 1}
        for rank_total, (raw_duration, category, name) in enumerate(
            [
                ("01:07:11.29", "M", "Stefan Matheis"),
                ("01:23:29.81", "M", "Marcel König"),
                ("01:12:47.09", "M", "Nicolas Faure"),
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
