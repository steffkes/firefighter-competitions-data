from util import BadWildbadSpider, ParticipantItem


class CompetitionSpider(BadWildbadSpider):
    name = __name__

    race_id = "309460"
    race_key = "56a60c6e165f85306496963612462b2f"

    def parse_starters(self, response):
        fixName = lambda name: " ".join(reversed(list(map(str.strip, name.split(",")))))

        for [_bib, name, _nationality, _byear, _gender, _category, _team, _empty] in (
            response.json()["data"] or {}
        ).get("#1_Feuerwehr-Stäffeleslauf", []):
            yield ParticipantItem(
                competition_id=self.competition_id, names=[fixName(name)]
            )
