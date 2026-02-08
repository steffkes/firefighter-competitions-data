from util import FirefitSpider
import scrapy


class CompetitionSpider(FirefitSpider):
    name = __name__

    def start_requests(self):
        yield scrapy.FormRequest(
            method="GET",
            url="https://firefit-europe.eu/produkt/firefit-luebeck-einzel-individual-friday/",
            callback=self.parse_slots,
            cb_kwargs={"contest": "Einzel"},
        )

        yield scrapy.FormRequest(
            method="GET",
            url="https://firefit-europe.eu/produkt/firefit-luebeck-tandem-saturday/",
            callback=self.parse_slots,
            cb_kwargs={"contest": "Tandem"},
        )

        yield scrapy.FormRequest(
            method="GET",
            url="https://firefit-europe.eu/produkt/firefit-luebeck-staffel-relay-saturday/",
            callback=self.parse_slots,
            cb_kwargs={"contest": "Staffel"},
        )
