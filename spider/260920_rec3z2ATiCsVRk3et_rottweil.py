from util import RottweilSpider, ParticipantItem
import itertools


class CompetitionSpider(RottweilSpider):
    name = __name__

    race_id = "382555"
    race_key = "5b0be9067a35f8d840dcc9a45c9bbd0d"

    custom_starter = [(5, "#1_5"), (6, "#1_6")]
    listname = "07-TEILNEHMER-PUBLIC|Teilnehmer ABC"

    @staticmethod
    def fixName(name):
        return " ".join(reversed(name.split(","))).strip()

    def parse_starters(self, response, data_key):
        data = response.json()["data"]

        participants = []
        for [_id1, _id2, _bib, name, _competition, _gender, team] in data[data_key]:
            participants.append((team, self.fixName(name)))

        for team, participants in itertools.groupby(
            sorted(participants), lambda p: p[0]
        ):
            yield ParticipantItem(
                competition_id=self.competition_id,
                names=sorted(map(lambda p: p[1], participants)),
            )


import pytest


@pytest.mark.parametrize(
    "input,output",
    [
        ("Delitzsch, Sven", "Sven Delitzsch"),
        ("Garcia Marin, Shelem", "Shelem Garcia Marin"),
        ("Hügle, Eliana", "Eliana Hügle"),
        ("Hügle, Thoma", "Thoma Hügle"),
        ("Schultheiß, Peter", "Peter Schultheiß"),
        ("Weh, David", "David Weh"),
    ],
)
def test_fixName(input, output):
    assert CompetitionSpider.fixName(input) == output
