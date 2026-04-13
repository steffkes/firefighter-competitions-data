import scrapy
import itertools
from datetime import datetime
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
        yield scrapy.Request("data:,", dont_filter=True, callback=self.parse_starters)

    def parse_starters(self, response):
        starter = ["Stefan Matheis", "Damian Pyka", "Jasmin Bohun", "Nicolas Faure"]
        for names in list(map(lambda name: [name], starter)) + list(
            itertools.repeat([None], 60 - len(starter))
        ):
            yield ParticipantItem(
                competition_id=self.competition_id,
                names=names,
            )

    def parse(self, _response):
        results = [
            ("00:10:09.8", "W", "Jasmin Bohun"),
            ("00:11:05.4", "W", "Petra Koch"),
            ("00:13:01.2", "W", "Isabell Müller"),
            ("00:16:08.1", "W", "Ines Müllenschläder"),
            ("00:16:37.5", "W", "Emma Eibisch"),
            ("00:19:13.7", "W", "Nicole Tuchbreiter"),
            ("00:07:36.0", "M", "Martin Loos"),
            ("00:07:36.6", "M", "Stefan Matheis"),
            ("00:07:45.5", "M", "Andreas Maier"),
            ("00:08:02.6", "M", "Matthias Weickmann"),
            ("00:08:10.0", "M", "Fabian Schott"),
            ("00:08:12.1", "M", "Andreas Engelhardt"),
            ("00:08:42.2", "M", "Jan Abraham"),
            ("00:08:45.5", "M", "Karsten Neupert"),
            ("00:08:53.2", "M", "Steve Roidl"),
            ("00:08:53.3", "M", "Jochen Weinmann"),
            ("00:09:05.0", "M", "Johannes Pleier"),
            ("00:09:11.8", "M", "Enrico Kohl"),
            ("00:09:27.0", "M", "Fabian Blümmert"),
            ("00:09:36.2", "M", "Niclas Rösler"),
            ("00:09:48.5", "M", "Christian Mitsch"),
            ("00:09:59.6", "M", "Nicolas Faure"),
            ("00:10:04.6", "M", "Tobias Svoboda"),
            ("00:10:10.6", "M", "Max Rösel"),
            ("00:10:26.7", "M", "Michael Haas"),
            ("00:10:42.8", "M", "Florian Müllenschläder"),
            ("00:10:44.7", "M", "Olver Pander"),
            ("00:10:45.8", "M", "Alex Greis"),
            ("00:11:02.0", "M", "Erik Langenhahn"),
            ("00:11:03.2", "M", "Christian Rau"),
            ("00:11:37.4", "M", "Frank Saupe"),
            ("00:11:44.1", "M", "Andreas Kühnl"),
            ("00:11:58.0", "M", "Sebastian Hartmann"),
            ("00:12:24.3", "M", "Manfred Reppert"),
            ("00:13:19.8", "M", "Maurice Strauss"),
            ("00:13:44.2", "M", "Robin Scheuring"),
            ("00:14:09.8", "M", "Manuel Leykauf"),
            ("00:14:35.5", "M", "Mirko Döbert"),
            ("00:16:09.1", "M", "Heiko Buch"),
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
