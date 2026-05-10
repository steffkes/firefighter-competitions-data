from util import Spider, ParticipantItem, ResultItem, ResultRankItem
import scrapy
import json
import re


class CompetitionSpider(Spider):
    name = __name__

    def start_requests(self):
        yield scrapy.FormRequest(
            method="GET",
            url="https://event.endu.net/events/event/entrants-json",
            formdata={"idevento": "100485", "rows": "200", "page": "1"},
            callback=self.parse_starters,
        )

        yield scrapy.FormRequest(
            method="GET",
            url="https://egs-eventi.s3.amazonaws.com/00000000/00100000/00100400/00100485/results/jsonp/615003_5GHUV40FU7.jsonp",
        )

    @staticmethod
    def loads_jsonp(text):
        text = text.strip()

        # remove optional comment prefix
        text = re.sub(r"^/\*\*/", "", text)

        start = text.find("(")
        end = text.rfind(")")

        if start == -1 or end == -1:
            raise ValueError("Invalid JSONP")

        payload = text[start + 1 : end]

        return json.loads(payload)

    def parse_starters(self, response):
        for entry in response.json()["rows"]:
            [
                _empty,
                firstname,
                lastname,
                _year,
                _nation,
                _team,
                _empty2,
                _competiton,
            ] = entry["cell"]
            yield ParticipantItem(
                competition_id=self.competition_id,
                names=["%s %s" % (firstname, lastname)],
            )

    def parse(self, response):
        results = []

        for row in self.loads_jsonp(response.text)["rows"]:
            category = {"M": "M", "F": "W"}[row["sx"]]
            duration = self.fixDuration(row["tu"])

            results.append(
                ResultItem(
                    date=self.race_date,
                    competition_id=self.competition_id,
                    type="OPA",
                    duration=duration,
                    names=["%s %s" % (row["nn"], row["nc"])],
                    category=category,
                    rank=ResultRankItem(
                        total=None,
                        category=None,
                    ),
                )
            )

        for result in results:
            yield result
