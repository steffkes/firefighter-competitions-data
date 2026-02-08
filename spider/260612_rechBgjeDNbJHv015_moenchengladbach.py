from util import Spider, SlotItem
import scrapy


class CompetitionSpider(Spider):
    name = __name__

    def start_requests(self):
        yield scrapy.FormRequest(
            method="GET",
            url="https://tfa-registrierung.sdserv.de/staffel/checkKontingent",
            cb_kwargs={"contest": "Staffel"},
            callback=self.parse_slots,
        )

        yield scrapy.FormRequest(
            method="GET",
            url="https://tfa-registrierung.sdserv.de/einzelstarter/checkKontingent",
            cb_kwargs={"contest": "Einzel"},
            callback=self.parse_slots,
        )

    def parse_slots(self, response, contest):
        yield SlotItem(
            competition_id=self.competition_id,
            amount=response.json()[0]["Kontingent"],
            label=contest,
        )
