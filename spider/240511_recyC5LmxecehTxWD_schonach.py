from util import Spider, ParticipantItem, ResultItem, ResultRankItem
import scrapy
import re
import itertools


class CompetitionSpider(Spider):
    name = __name__

    race_id = "279564"
    race_key = "0b390ff34ee4d88a57b036f1dc1fbf9e"

    @staticmethod
    def fixName(name):
        return re.sub(
            r"(([A-ZÄÜÖß]+[-\s])?([A-ZÄÜÖß]+))\s(.+)",
            lambda match: " ".join(
                [
                    match.group(4),
                    "".join(
                        map(
                            lambda str: str[0] + str[1:].lower(),
                            filter(None, match.group(2, 3)),
                        )
                    ),
                ]
            ),
            name,
        )

    def start_requests(self):
        yield scrapy.FormRequest(
            method="GET",
            url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
            formdata={
                "key": self.race_key,
                "listname": "02_Teilnehmerlisten|Teilnehmer_Schanzenlauf",
                "contest": "1",
            },
            callback=self.parse_starters,
        )

        yield scrapy.FormRequest(
            method="GET",
            url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
            formdata={
                "key": self.race_key,
                "listname": "01_Feuerwehr|Ergebnisliste_Feuerwehr_Wertungen",
                "contest": "1",
            },
        )

    def parse_starters(self, response):
        for [_bib1, name1, _gender1, _competition1, _birthyear1, _category1, _rand1], [
            _bib2,
            name2,
            _gender2,
            _competition2,
            _birthyear2,
            _category2,
            _rand2,
        ] in itertools.batched(response.json()["data"], 2):
            yield ParticipantItem(
                competition_id=self.competition_id,
                names=sorted([self.fixName(name1), self.fixName(name2)]),
            )

    def parse(self, response):
        groups = []
        entries = []
        for group, teams in response.json()["data"].items():
            (contest, raw_age_group) = re.match(
                r"#\d_((Ohne|Mit) PA) / (\w+)\s", group
            ).group(1, 3)
            type = "MPA" if "Mit PA" == contest else "OPA"

            for team, names in teams.items():
                [rank_age_group, raw_duration] = re.match(
                    r"\#\d+_(\d+)\.///.*?///(.+)", team
                ).group(1, 2)
                [
                    [_id1, bib, name1, gender1, _time1],
                    [_id2, _bib2, name2, gender2, _time2],
                ] = names

                duration = "00:%s.0" % raw_duration.zfill(5)
                gender = list(set([gender1, gender2]))
                category = gender[0] if len(gender) == 1 else "X"
                age_group = raw_age_group if category == "M" else None
                groups.append((type, category, age_group))

                result = ResultItem(
                    date=self.race_date,
                    competition_id=self.competition_id,
                    type=type,
                    duration=duration,
                    names=sorted([self.fixName(name1), self.fixName(name2)]),
                    category=category,
                    bib=bib,
                )

                if age_group:
                    result["age_group"] = age_group

                entries.append(result)

        entries = sorted(entries, key=lambda record: record["duration"])

        for group in sorted(set(groups)):
            (type, category, age_group) = group

            entries_type = list(filter(lambda entry: entry["type"] == type, entries))
            entries_category = list(
                filter(lambda entry: entry["category"] == category, entries_type)
            )
            entries_age_group = list(
                filter(
                    lambda entry: entry.get("age_group") == age_group, entries_category
                )
            )

            for entry in entries_age_group:
                entry["rank"] = ResultRankItem(
                    total=entries_type.index(entry) + 1,
                    category=entries_category.index(entry) + 1,
                )

                if "age_group" in entry:
                    entry["rank"]["age_group"] = entries_age_group.index(entry) + 1

                yield entry


import pytest


@pytest.mark.parametrize(
    "input,output",
    [
        ("ZIMMERMANN Lukas", "Lukas Zimmermann"),
        ("BOGENSCHÜTZ Jörg", "Jörg Bogenschütz"),
        ("CECH-MEDAK Boris", "Boris Cech-Medak"),
        ("TO Han Kiet", "Han Kiet To"),
        ("MENZL Marc Michael", "Marc Michael Menzl"),
    ],
)
def test_fixName(input, output):
    assert CompetitionSpider.fixName(input) == output
