from util import BadWildbadSpider, ParticipantItem
import re


class CompetitionSpider(BadWildbadSpider):
    name = __name__

    race_id = "309460"
    race_key = "56a60c6e165f85306496963612462b2f"

    @staticmethod
    def fixName(name):
        return re.sub(r"\s\(\d+\)$", "", name)

    def parse_starters(self, response):
        fixName = lambda name: " ".join(reversed(list(map(str.strip, name.split(",")))))

        for [
            _bib,
            _number2,
            name,
            _nationality,
            _byear,
            _gender,
            _category,
            _team,
            _empty,
        ] in (response.json()["data"] or {}).get("#1_Feuerwehr-Stäffeleslauf", []):
            yield ParticipantItem(
                competition_id=self.competition_id, names=[fixName(name)]
            )


import pytest


@pytest.mark.parametrize(
    "input,output",
    [
        ("Anna Lena Steurer (464)", "Anna Lena Steurer"),
        ("Hanna Lena Knack (421)", "Hanna Lena Knack"),
        ("Fabian Missfelder (406)", "Fabian Missfelder"),
        ("Sascha Unsöld (413)", "Sascha Unsöld"),
    ],
)
def test_fixName(input, output):
    assert CompetitionSpider.fixName(input) == output
