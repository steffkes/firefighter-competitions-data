from util import Spider, ParticipantItem, ResultItem, ResultRankItem
import scrapy
import re


class CompetitionSpider(Spider):
    name = __name__

    def start_requests(self):
        yield scrapy.FormRequest(
            method="GET",
            url="https://api.fcc-slo.eu/api/races/42/runs",
        )

    def parse(self, response):
        groups = []
        entries = []

        for entry in response.json():
            if entry["disqualification"]:
                continue

            age_group = entry["application"]["assignedCategory"]["label"][1:]
            category = {"F": "W"}.get(age_group[0], age_group[0])

            groups.append((category, age_group))
            entries.append(
                ResultItem(
                    date=self.race_date,
                    competition_id=self.competition_id,
                    type="MPA",
                    duration=self.fixDuration(entry["totalTime"]),
                    names=[entry["application"]["title"]],
                    category=category,
                    age_group=age_group,
                    bib=entry["startNumber"],
                )
            )

        entries = sorted(entries, key=lambda entry: entry["duration"])

        for group in sorted(set(groups)):
            (category, age_group) = group

            entries_type = entries
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
                    age_group=entries_age_group.index(entry) + 1,
                )

                yield entry
