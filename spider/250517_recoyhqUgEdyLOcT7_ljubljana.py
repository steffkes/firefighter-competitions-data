from util import Spider, ParticipantItem, ResultItem, ResultRankItem
import scrapy


class CompetitionSpider(Spider):
    name = __name__

    @staticmethod
    def fixName(name):
        return " ".join(
            map(lambda part: part[0].upper() + part[1:].lower(), name.split(" "))
        )

    def start_requests(self):
        yield scrapy.FormRequest(
            method="GET",
            url="https://remote.timingljubljana.si/stepup/pregledprijav.aspx",
            callback=self.parse_starters,
        )

        for contest, type, gender in [
            ("G1M", "MPA", "M"),  # single male
            ("G1Z", "MPA", "W"),  # single female
        ]:
            yield scrapy.FormRequest(
                method="GET",
                url="https://remote.timingljubljana.si/stepup/Rezultati.aspx",
                formdata={"cat": contest},
                callback=self.parse_single,
                cb_kwargs={"type": type, "gender": gender},
            )

        for contest, type in [
            ("G3", "OPA"),  # relay mixed
            ("GE", "MPA"),  # relay mixed
        ]:
            yield scrapy.FormRequest(
                method="GET",
                url="https://remote.timingljubljana.si/stepup/Rezultati.aspx",
                formdata={"cat": contest},
                callback=self.parse_relay,
                cb_kwargs={"type": type},
            )

    def parse_starters(self, response):
        for row in response.css("table tr"):
            cells = row.css("td ::text").getall()

            if len(cells) != 7:
                continue

            [lastname, firstname, _gender, _team, _bib, _unknown, group] = cells

            if not group in [
                "Step Up - Gasilci Smartwater",
                "Step Up - Ekstremna Štafeta  - Gasilci",
            ]:
                continue

            yield ParticipantItem(
                competition_id=self.competition_id,
                names=[self.fixName("%s %s" % (firstname, lastname))],
            )

    def parse_single(self, response, type, gender):
        for row in response.css("table tr")[1:]:
            [rank, name, _country, _team, duration] = row.css("td ::text").getall()

            yield ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                type=type,
                duration="0" + duration,
                names=[self.fixName(name)],
                category=gender,
                rank=ResultRankItem(category=int(rank)),
            )

    def parse_relay(self, response, type):
        for row in response.css("table tr")[1:]:
            [
                rank,
                names,
                _country,
                _team,
                duration1,
                duration2,
                duration3,
                _sum1_2,
                relay_duration,
            ] = row.css("td ::text").getall()

            yield ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                type=type,
                duration="0" + relay_duration,
                names=sorted(map(self.fixName, names.split(","))),
                category="Relay",
                rank=ResultRankItem(category=int(rank)),
            )

            for name, duration in zip(
                names.split(","), [duration1, duration2, duration3]
            ):
                yield ResultItem(
                    date=self.race_date,
                    competition_id=self.competition_id,
                    type=type,
                    duration="0" + duration,
                    names=[self.fixName(name.strip())],
                )


import pytest


@pytest.mark.parametrize(
    "input,output",
    [
        ("TOMAŽ ANŽIČ", "Tomaž Anžič"),
        ("LUKA KNEZ LAZAR", "Luka Knez Lazar"),
        ('OŽBEJ "STEROID" ŠKERBEC', 'Ožbej "steroid" Škerbec'),
    ],
)
def test_fixName(input, output):
    assert CompetitionSpider.fixName(input) == output
