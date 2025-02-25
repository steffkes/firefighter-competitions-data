from util import Spider, ParticipantItem, ResultItem, ResultRankItem
import requests
import scrapy
import re


class CompetitionSpider(Spider):
    name = __name__

    race_id = "313822"
    race_key = "6c9e34b3e68526be8ae12fdaa2a5158c"

    @staticmethod
    def matchNames(input, template):
        replacerFn = lambda name: re.sub(
            r"^(.+)\s+(" + "|".join(map(re.escape, template)) + ")$",
            r"\2 \1",
            name,
        )
        work = list(map(replacerFn, input))

        return sorted(work) if len(set(input) & set(work)) == 0 else None

    def start_requests(self):
        for contest in [9026, 9027]:
            yield scrapy.FormRequest(
                method="GET",
                url="https://www.anmeldungs-service.de/module/teilnehmer/staffel_cache.php",
                formdata={
                    "wettid": str(contest),
                    "totalrows": "2000",
                },
                headers={
                    "X-Requested-With": "XMLHttpRequest",
                },
                callback=self.parse_starters,
            )

        fixName = lambda name: re.match(r"^(.+)\s+\w\s+\d+$", name).group(1).strip()

        for contest, type, participant_contest in [(1, "OPA", 9026), (2, "MPA", 9027)]:
            r = requests.post(
                "https://www.anmeldungs-service.de/module/teilnehmer/staffel_cache.php",
                params={
                    "wettid": str(participant_contest),
                    "totalrows": "2000",
                },
                headers={
                    "X-Requested-With": "XMLHttpRequest",
                },
            )

            yield scrapy.FormRequest(
                method="GET",
                url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
                formdata={
                    "key": self.race_key,
                    "contest": str(contest),
                    "listname": "10 Ergebnislisten|00 Ergebnisliste OA (Kategorie)",
                },
                cb_kwargs={
                    "competition_type": type,
                    "allParticipants": dict(
                        map(
                            lambda row: (
                                row["cell"]["stnr"],
                                list(map(fixName, row["cell"]["name"].split("<br>"))),
                            ),
                            r.json()["rows"],
                        )
                    ),
                },
            )

    def parse_starters(self, response):
        reverseName = lambda name: " ".join(
            reversed(list(map(str.strip, name.split(" "))))
        )
        fixName = lambda name: reverseName(
            re.match(r"^(.+)\s+\w\s+\d+$", name).group(1).strip()
        )

        data = response.json()["rows"]
        for entry in data:
            yield ParticipantItem(
                competition_id=self.competition_id,
                names=sorted(map(fixName, entry["cell"]["name"].split("<br>"))),
            )

    def parse(self, response, competition_type, allParticipants):
        ranks = {"category": {}, "age_group": {}}

        for entry in response.json()["data"]:
            [_, status, bib, _, _, names, raw_age_group, raw_duration, _] = entry

            if status in ["DSQ", "DNF", "a.k."]:  # disqualified
                continue

            # BIB is not registered as participant
            participants = allParticipants.get(bib)
            if not participants:
                continue

            names = sorted(map(str.strip, names.split("|")))
            age_group = " ".join(raw_age_group.split(" ")[:-1])
            category = {
                "Burschen": "M",
                "Mannsbilder": "M",
                "Alte Knacker": "M",
                "Pärchen": "X",
                "Mädels": "W",
            }[age_group]

            # matches between starter & finisher don't match
            matchedNames = self.matchNames(participants, names)

            rank_total = ranks.get("total", 1)
            rank_category = ranks["category"].get(category, 1)

            result = ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                type=competition_type,
                duration=self.fixDuration(raw_duration),
                category=category,
                names=matchedNames,
                rank=ResultRankItem(total=rank_total, category=rank_category),
                bib=bib,
            )

            ranks["total"] = rank_total + 1
            ranks["category"][category] = rank_category + 1

            if category == "M":
                rank_age_group = ranks["age_group"].get(age_group, 1)

                result["age_group"] = age_group
                result["rank"]["age_group"] = rank_age_group

                ranks["age_group"][age_group] = rank_age_group + 1

            # we need to pass late, to ensure that all rank calc is done properly
            # we skip the participants, but the rank needs to continue
            if not matchedNames:
                continue

            yield result


import pytest


@pytest.mark.parametrize(
    "input,template,output",
    [
        (
            ["Missfelder Fabian", "Ruf Juliane"],
            ["Juliane", "Fabian"],
            ["Fabian Missfelder", "Juliane Ruf"],
        ),  # BIB  712
        (
            ["Albrecht Nils", "Kohrs Karsten Kala"],
            ["Karsten Kala", "Vincent"],
            None,
        ),  # BIB  307
        (
            ["Chech-Madak Boris", "Dohrmann Rocky"],
            ["Rocky", "Boris"],
            ["Boris Chech-Madak", "Rocky Dohrmann"],
        ),  # BIB  711
        (
            ["Di Palma Fabio", "Sonsalla Finn"],
            ["Fabio", "Finn"],
            ["Fabio Di Palma", "Finn Sonsalla"],
        ),  # BIB 1313
    ],
)
def test_matchNames(input, template, output):
    assert CompetitionSpider.matchNames(input, template) == output
