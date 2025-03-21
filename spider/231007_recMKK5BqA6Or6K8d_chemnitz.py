from util import Spider, ParticipantItem, ResultItem, ResultRankItem
import scrapy


class CompetitionSpider(Spider):
    name = __name__

    def start_requests(self):
        yield scrapy.FormRequest(
            method="GET",
            url="https://events.lauf-kultour.de/zeitmessung/results.php",
            formdata={
                "eventID": "88",
                "cat": "ff",
            },
        )

    def parse(self, response):
        for entry in response.json()["results"]:
            if entry["time"] in ["DNS", "DNF"]:
                continue

            [minutes, seconds] = entry["time"] // 60, entry["time"] % 60
            age_group = (
                {"Männer": "M", "Frauen": "W"}.get(entry["AK"], entry["AK"]).upper()
            )
            category = age_group[0]

            yield ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                duration="00:%02d:%02d.0" % (minutes, seconds),
                type="MPA",
                names=["%s %s" % (entry["forename"].strip(), entry["surname"].strip())],
                category=category,
                age_group=age_group,
                rank=ResultRankItem(
                    total=entry["position"],
                    category=entry["MW"],
                    age_group=entry["AKP"],
                ),
                bib=entry["bib"],
            )
