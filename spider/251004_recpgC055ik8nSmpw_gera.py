from util import Spider, ParticipantItem, ResultItem, ResultRankItem, SlotItem
import scrapy
import re


class CompetitionSpider(Spider):
    name = __name__

    def start_requests(self):
        yield scrapy.FormRequest(
            method="GET",
            url="https://firefit-europe.eu/en/produkt/firefit-gera-einzel-individual-saturday/",
            callback=self.parse_slots,
            cb_kwargs={"contest": "Einzel"},
        )

        yield scrapy.FormRequest(
            method="GET",
            url="https://firefit-europe.eu/en/produkt/firefit-gera-tandem-sunday/",
            callback=self.parse_slots,
            cb_kwargs={"contest": "Tandem"},
        )

        yield scrapy.FormRequest(
            method="GET",
            url="https://firefit-europe.eu/en/produkt/firefit-gera-staffel-relay-sunday/",
            callback=self.parse_slots,
            cb_kwargs={"contest": "Staffel"},
        )

    def parse_slots(self, response, contest):
        match = re.match(r"\d+", response.css(".stock.in-stock::text").get(default=""))
        yield SlotItem(
            competition_id=self.competition_id,
            amount=int(match.group()) if match else 0,
            label=contest,
        )
