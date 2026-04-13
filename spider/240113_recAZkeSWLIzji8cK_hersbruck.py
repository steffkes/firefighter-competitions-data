import scrapy
from util import (
    Spider,
    ParticipantItem,
    ResultItem,
    ResultRankItem,
)


class CompetitionSpider(Spider):
    name = __name__

    def start_requests(self):
        yield scrapy.Request("data:,", dont_filter=True)

    def parse(self, _response):
        results = [
            ("00:10:26.7", "W", "Jasmin Bohun"),
            ("00:15:51.8", "W", "Nicole Tuchbreiter"),
            ("00:07:45.2", "M", "Lukas Loos"),
            ("00:07:45.6", "M", "Stefan Matheis"),
            ("00:07:54.0", "M", "Andreas Maier"),
            ("00:08:13.3", "M", "Matthias Weickmann"),
            ("00:08:40.7", "M", "Jochen Weinmann"),
            ("00:08:42.4", "M", "Fabian Blümmert"),
            ("00:08:52.7", "M", "Steve Roidl"),
            ("00:09:01.4", "M", "Sean O'Reilly"),
            ("00:09:03.1", "M", "Fabian Schott"),
            ("00:09:07.9", "M", "Niklas Blöchinger"),
            ("00:09:17.4", "M", "Hannes Albert"),
            ("00:09:18.9", "M", "Enrico Kohl"),
            ("00:09:28.0", "M", "Jan Abraham"),
            ("00:09:33.0", "M", "Christian Mitsch"),
            ("00:09:41.1", "M", "Tobias Rösch"),
            ("00:09:49.0", "M", "Alexander Eberhard"),
            ("00:09:50.6", "M", "Tim Leimberger"),
            ("00:09:51.4", "M", "Johannes Schüll"),
            ("00:10:01.1", "M", "Johannes Pleier"),
            ("00:10:15.0", "M", "Christoph Örtel"),
            ("00:10:29.8", "M", "Florian Fischer"),
            ("00:10:32.9", "M", "Helmut Rupprecht"),
            ("00:10:36.9", "M", "Frank Bayer"),
            ("00:10:55.4", "M", "Simon Mangels"),
            ("00:11:00.6", "M", "Oliver Pander"),
            ("00:11:05.5", "M", "Erik Langenhahn"),
            ("00:11:12.3", "M", "Alex Greis"),
            ("00:11:21.2", "M", "Sebastian Hartmann"),
            ("00:11:25.7", "M", "Thomas Wunderlich"),
            ("00:11:31.4", "M", "Max Rösel"),
            ("00:11:37.0", "M", "Markus Leuthel"),
            ("00:11:51.3", "M", "Timo Bachhiesl"),
            ("00:12:21.4", "M", "Sebastian Berner"),
            ("00:12:53.2", "M", "Frank Saupe"),
            ("00:13:03.5", "M", "Peter Singer"),
            ("00:13:08.0", "M", "Daniel Hammerand"),
            ("00:13:19.0", "M", "Adrian Günther"),
            ("00:13:21.8", "M", "Jens Dienstühler"),
            ("00:13:23.4", "M", "Harald Wunderlich"),
            ("00:15:55.6", "M", "Markus Kerling"),
            ("00:16:32.6", "M", "Marco Schwarz"),
            ("00:16:36.6", "M", "Heiko Buch"),
        ]
        rank_category = {"M": 1, "W": 1}
        for total_rank, (duration, sex, name) in enumerate(sorted(results)):
            yield ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                type="MPA",
                duration=duration,
                names=[name],
                category=sex,
                rank=ResultRankItem(
                    total=total_rank + 1,
                    category=rank_category.get(sex),
                ),
            )
            rank_category[sex] += 1
