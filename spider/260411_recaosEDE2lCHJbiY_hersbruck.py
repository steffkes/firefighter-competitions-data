import scrapy
from util import (
    Spider,
    ResultItem,
    ResultRankItem,
)


class CompetitionSpider(Spider):
    name = __name__

    def start_requests(self):
        yield scrapy.Request("data:,")

    def parse(self, _response):
        results = [
            ("00:10:22.9", "W", "Simone Türmer"),
            ("00:10:38.8", "W", "Petra Koch"),
            ("00:13:09.6", "W", "Nina Groth"),
            ("00:15:34.2", "W", "Emma Eibisch"),
            ("00:16:07.6", "W", "Isabell Müller"),
            ("00:16:54.2", "W", "Ines Müllenschläder"),
            ("00:06:56.3", "M", "Christian Brandmann"),
            ("00:07:10.3", "M", "Stefan Matheis"),
            ("00:07:29.4", "M", "Tobias Diedrigkeit"),
            ("00:07:44.4", "M", "Markus Albersdorfer"),
            ("00:07:44.5", "M", "Fabian Schott"),
            ("00:07:45.8", "M", "Matthias Weickmann"),
            ("00:07:51:0", "M", "Andreas Engelhardt"),
            ("00:07:52.7", "M", "Julius Betz"),
            ("00:07:54.6", "M", "Andreas Maier"),
            ("00:08:04.2", "M", "Sebastian Tiefel"),
            ("00:08:06.9", "M", "Thomas Daubitz"),
            ("00:08:15.4", "M", "Tobias Orlet"),
            ("00:08:24.0", "M", "Johannes Schüll"),
            ("00:08:37.1", "M", "Niklas Blöchinger"),
            ("00:08:37.5", "M", "Christian Leuchner"),
            ("00:08:43.5", "M", "Johannes Pleier"),
            ("00:08:48.7", "M", "Damian Pyka"),
            ("00:08:56.4", "M", "Tobias Rösch"),
            ("00:08:57.2", "M", "Steve Roidl"),
            ("00:08:57.3", "M", "Enrico Kohl"),
            ("00:08:57.4", "M", "Sebastian Berner"),
            ("00:08:58.7", "M", "Tobias Halgasch"),
            ("00:09:04.7", "M", "Fabian Pokorny"),
            ("00:09:15.5", "M", "Andreas Sperber"),
            ("00:09:21.0", "M", "Hannes Leikauf"),
            ("00:09:24.1", "M", "Christian Quoika"),
            ("00:09:24.3", "M", "Christian Mitsch"),
            ("00:09:26.7", "M", "Maximilian Schellermann"),
            ("00:09:26.8", "M", "Manuel Schuler"),
            ("00:09:28.5", "M", "Christian Rau"),
            ("00:09:35.4", "M", "Felix Pfister"),
            ("00:09:42.5", "M", "Patrick Bauer"),
            ("00:09:46.2", "M", "Max Rösel"),
            ("00:09:48.3", "M", "Martin Franke"),
            ("00:09:53.6", "M", "Philip Rögner"),
            ("00:09:57.9", "M", "Max Oberhäuser"),
            ("00:09:58.9", "M", "Carsten Scheckelmann"),
            ("00:10:05.6", "M", "Timo Kirzdörfer"),
            ("00:10:07.1", "M", "Tom Rebhan"),
            ("00:10:29.1", "M", "Erik Langenhahn"),
            ("00:10:41.2", "M", "Tino Leidel"),
            ("00:10:56.2", "M", "Felix Platzmann"),
            ("00:11:09.5", "M", "Johannes Rögner"),
            ("00:11:10.9", "M", "David Stilper"),
            ("00:11:21.3", "M", "Peter Wälzlein"),
            ("00:11:21.5", "M", "Frank Saupe"),
            ("00:11:28.6", "M", "Heiko Baier"),
            ("00:11:35.3", "M", "Nikolas Gil Eckert"),
            ("00:11:57.2", "M", "Andreas Kühnl"),
            ("00:12:13.7", "M", "Markus Kirzdörfer"),
            ("00:12:47.7", "M", "Zacharias Raum"),
            ("00:12:52.5", "M", "Manfred Reppert"),
            ("00:13:45.5", "M", "Steffen Schaefer"),
            ("00:14:25.8", "M", "Marcel Huck"),
            ("00:14:38.7", "M", "Heiko Gorny"),
            ("00:14:54.2", "M", "Robin Scheuring"),
            ("00:16:12.0", "M", "Mikro Döbert"),
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
