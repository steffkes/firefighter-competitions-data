from util import Spider, ParticipantItem, ResultItem, ResultRankItem
import scrapy


class CompetitionSpider(Spider):
    name = __name__

    def start_requests(self):
        for params, callback in [
            ({"id": "85", "Itemid": "107"}, self.parse_starters_single),
            ({"id": "86", "Itemid": "742"}, self.parse_starters_tandem),
            ({"id": "87", "Itemid": "743"}, self.parse_starters_relay),
        ]:
            yield scrapy.FormRequest(
                method="GET",
                url="https://www.fcc-team-austria.at/index.php",
                formdata={"option": "com_content", "view": "article", **params},
                callback=callback,
            )

    def parse_starters_single(self, response):
        for row in response.css(".item-page table")[0].css("tr")[1:]:
            yield ParticipantItem(
                competition_id=self.competition_id,
                names=[row.css("td::text").get()],
            )

    def parse_starters_tandem(self, response):
        for row in response.css(".item-page table")[0].css("tr")[1:]:
            yield ParticipantItem(
                competition_id=self.competition_id,
                names=sorted(row.css("td::text").getall()[1:3]),
            )

    def parse_starters_relay(self, response):
        for row in response.css(".item-page table")[0].css("tr")[1:]:
            yield ParticipantItem(
                competition_id=self.competition_id,
                names=sorted(row.css("td::text").getall()[1:-1]),
            )
