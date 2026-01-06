from util import Spider, ParticipantItem, ResultItem, ResultRankItem
import scrapy


class CompetitionSpider(Spider):
    name = __name__

    def requestHelper(self, raceId, page=1):
        return scrapy.http.JsonRequest(
            method="POST",
            url="https://tracey-prod-6b98eac1c8fad5e7fa6493b8d82e4fc3.traceysport.com/api/public/competitors/find",
            data={
                "pages": {"pageSize": 51, "page": page},
                "filter": {"eventId": 2841, "raceId": raceId},
            },
            cb_kwargs={"raceId": raceId, "page": page},
            callback=self.parse_starters,
        )

    def start_requests(self):
        for raceId in [8052, 8053]:
            yield self.requestHelper(raceId)

    def parse_starters(self, response, raceId, page):
        records = response.json()["result"]

        if not records:
            return

        for record in records:
            yield ParticipantItem(
                competition_id=self.competition_id,
                names=[record["fullName"].strip()],
            )
        yield self.requestHelper(raceId, page + 1)
