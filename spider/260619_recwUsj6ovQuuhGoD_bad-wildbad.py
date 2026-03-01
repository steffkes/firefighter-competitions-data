from util import BadWildbadSpider, ParticipantItem


class CompetitionSpider(BadWildbadSpider):
    name = __name__

    race_id = "342979"
    race_key = "9522fa0db23d64ba7c0aba8100851fe2"

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
        ] in (response.json()["data"] or {}).get(
            "#1_Gollmer & Hummel Feuerwehrlauf", []
        ):
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
