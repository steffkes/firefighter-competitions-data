from util import FirefitSpider
import scrapy


class CompetitionSpider(FirefitSpider):
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
