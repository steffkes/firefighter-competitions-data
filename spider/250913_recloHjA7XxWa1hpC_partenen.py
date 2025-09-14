from util import Spider, ParticipantItem, ResultItem, ResultRankItem
import scrapy


class CompetitionSpider(Spider):
    name = __name__

    def start_requests(self):
        # dont_filter is needed, because otherwise the
        # second request is treated as duplicate for
        # the first one ..

        yield scrapy.Request(
            "data:,",
            dont_filter=True,
            callback=self.parse_starters,
        )

        yield scrapy.Request("data:,", dont_filter=True)

    def parse_starters(self, response):
        for name in ["Nicolas Faure", "Stefan Matheis", "Elias Vogt", "Marcel König"]:
            yield ParticipantItem(
                competition_id=self.competition_id,
                names=[name],
            )

    def parse(self, response):
        for total_rank, raw_duration, name in [
            (1, "1:07:11.29", "Stefan Matheis"),
            (2, "1:12:47.09", "Marcel König"),
            (3, "1:23:29.81", "Nicolas Faure"),
        ]:
            yield ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                type="OPA",
                duration=self.fixDuration(raw_duration),
                names=[name],
                category="M",
                age_group=None,
                bib=None,
                rank=ResultRankItem(total=total_rank),
            )
