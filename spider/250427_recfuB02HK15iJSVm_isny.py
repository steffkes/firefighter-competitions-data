from util import Spider, ParticipantItem, ResultItem, ResultRankItem
import scrapy


class CompetitionSpider(Spider):
    name = __name__

    def start_requests(self):
        yield scrapy.Request("data:,", dont_filter=True)

    def parse(self, response):
        for raw_duration, rank, name in [
            ("2:12.1", 1, "Jan Kösler"),
            ("2:17.1", 2, "Stefan Matheis"),
            ("2:32.1", 3, "Matthias Hefele"),
            ("3:36.4", 4, "Elias Vogt"),
            ("3:37.6", 5, "Benjamin Weber"),
            ("4:00.4", 6, "Markus Weber"),
            ("5:21.0", 7, "Jasmin Bohun"),
            ("1:44.9", 1, "Jan Kösler"),
            ("1:51.4", 2, "Stefan Matheis"),
            ("1:57.1", 3, "Matthias Hefele"),
            ("3:04.2", 4, "Elias Vogt"),
            ("3:51.2", 5, "Jasmin Bohun"),
        ]:
            yield ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                type="OPA",
                duration=self.fixDuration(raw_duration),
                names=[name],
                rank=ResultRankItem(
                    total=rank,
                ),
            )
