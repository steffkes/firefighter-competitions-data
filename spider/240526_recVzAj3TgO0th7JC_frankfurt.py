from util import Spider, ParticipantItem, ResultItem, ResultRankItem
from datetime import datetime
import scrapy
import itertools


class CompetitionSpider(Spider):
    name = __name__

    race_id = "277814"
    race_key = "0fdd4b818141191b0084fc27c0714d40"

    def start_requests(self):
        for contest in [3, 4]:
            yield scrapy.FormRequest(
                method="GET",
                url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
                formdata={
                    "key": self.race_key,
                    "listname": "Teilnehmerlisten|TN Startzeit",
                    "contest": str(contest),
                },
                callback=self.parse_starters,
            )

        for contest, competition_type, data_key in [
            (3, "OPA", "#1_messeTurm FFC FIGHTER"),
            (4, "MPA", "#1_messeTurm FFC ELITE"),
        ]:
            yield scrapy.FormRequest(
                method="GET",
                url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
                formdata={
                    "key": self.race_key,
                    "listname": "Ergebnislisten|EG ZIEL Teamwertung FF&RDC",
                    "contest": str(contest),
                },
                cb_kwargs={
                    "competition_type": competition_type,
                    "data_key": data_key,
                },
            )

    def parse_starters(self, response):
        fixName = lambda name: " ".join(reversed(list(map(str.strip, name.split(",")))))

        starters = []
        for [
            _id,
            _empty,
            bib,
            name,
            _gender,
            _category,
            _team,
            _nationality,
            _competition,
            _empty,
        ] in response.json()["data"]:
            starters.append((bib[0:-2], fixName(name)))

        for bib, items in itertools.groupby(starters, lambda item: item[0]):
            yield ParticipantItem(
                competition_id=self.competition_id,
                names=sorted(map(lambda item: item[1], items)),
            )

    def parse(self, response, data_key, competition_type):
        fixName = lambda name: " ".join(reversed(list(map(str.strip, name.split(",")))))

        data = response.json()["data"]

        groups = []
        results = []
        for team, names in data[data_key].items():
            [rank_team, team_duration] = re.match(
                r"\#\d+_(\d+)\.///.*?///(.+)", team
            ).group(1, 2)

            [
                [_id1, bib1, name1, duration1, age_group1, _nationality1],
                [_id2, bib2, name2, duration2, age_group2, _nationality2],
                [_id3, bib3, name3, duration3, age_group3, _nationality3],
            ] = names

            team_gender = list(
                set(map(lambda ag: ag[0].upper(), [age_group1, age_group2, age_group3]))
            )
            team_category = team_gender[0] if len(team_gender) == 1 else "X"

            yield ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                type=competition_type,
                duration=self.fixDuration(team_duration),
                category=team_category,
                names=sorted(map(fixName, [name1, name2, name3])),
                rank=ResultRankItem(total=int(rank_team)),
                bib=bib1.split("-")[0],
            )

            for bib, name, duration, age_group in zip(
                [bib1, bib2, bib3],
                [name1, name2, name3],
                [duration1, duration2, duration3],
                [age_group1, age_group2, age_group3],
            ):
                category = age_group[0].upper()

                result = ResultItem(
                    date=self.race_date,
                    competition_id=self.competition_id,
                    type=competition_type,
                    duration=self.fixDuration(duration),
                    category=category,
                    age_group=age_group,
                    names=[fixName(name)],
                    bib=bib,
                )
                results.append(result)
                groups.append((category, age_group))

        results = sorted(results, key=lambda result: result["duration"])

        for category, age_group in sorted(set(groups)):
            entries_type = results
            entries_category = list(
                filter(lambda result: result["category"] == category, entries_type)
            )
            entries_age_group = list(
                filter(
                    lambda result: result["age_group"] == age_group, entries_category
                )
            )

            for entry in entries_age_group:
                entry["rank"] = ResultRankItem(
                    total=entries_type.index(entry) + 1,
                    category=entries_category.index(entry) + 1,
                    age_group=entries_age_group.index(entry) + 1,
                )

                yield entry
