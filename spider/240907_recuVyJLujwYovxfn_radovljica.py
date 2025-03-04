from util import Spider, ParticipantItem, ResultItem, ResultRankItem
import scrapy
import re


class CompetitionSpider(Spider):
    name = __name__

    def start_requests(self):
        def categoryAgeGroupTandem(entry):
            raw_age_group = entry["application"]["assignedCategory"]["label"][1:]
            category = "%s tandem" % {"F": "W", "MX": "X"}.get(
                raw_age_group, raw_age_group[0]
            )
            age_group = raw_age_group if category == "M tandem" else None
            return (category, age_group)

        def categoryAgeGroupRelay(entry):
            return ("relay", None)

        yield scrapy.FormRequest(
            method="GET",
            url="https://api.fcc-slo.eu/api/races/42/runs",
            callback=self.parse_single,
        )

        yield scrapy.FormRequest(
            method="GET",
            url="https://api.fcc-slo.eu/api/races/43/runs",
            callback=self.parse_teams,
            cb_kwargs={"categoryAgeGroupMapper": categoryAgeGroupTandem},
        )

        yield scrapy.FormRequest(
            method="GET",
            url="https://api.fcc-slo.eu/api/races/44/runs",
            callback=self.parse_teams,
            cb_kwargs={"categoryAgeGroupMapper": categoryAgeGroupRelay},
        )

    def parse_single(self, response):
        groups = []
        entries = []

        for entry in response.json():
            if entry["disqualification"]:
                continue

            age_group = entry["application"]["assignedCategory"]["label"][1:]
            category = "%s individual" % {"F": "W"}.get(age_group[0], age_group[0])

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

    def parse_teams(self, response, categoryAgeGroupMapper):
        groups = []
        entries = []

        for entry in response.json():
            if entry["disqualification"]:
                continue

            (category, age_group) = categoryAgeGroupMapper(entry)

            result = ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                type="OPA",
                duration=self.fixDuration(entry["totalTime"]),
                names=sorted(
                    map(
                        lambda item: "{firstName} {lastName}".format(
                            **item["competitor"]
                        ),
                        entry["application"]["applicationCompetitors"],
                    )
                ),
                category=category,
                bib=entry["startNumber"],
            )

            if age_group:
                result["age_group"] = age_group

            groups.append((category, age_group))
            entries.append(result)

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
                )

                if "age_group" in entry:
                    entry["rank"]["age_group"] = entries_age_group.index(entry) + 1

                yield entry
