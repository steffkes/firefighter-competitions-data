from util import FirefitSpider
import scrapy


class CompetitionSpider(FirefitSpider):
    name = __name__

    def start_requests(self):
        for contest, url in [
            (
                "Einzel",
                "https://firefit-europe.eu/en/produkt/firefit-em-szolnok-individual-qualification-friday/",
            ),
            (
                "Einzel",
                "https://firefit-europe.eu/en/produkt/firefit-em-szolnok-individual-qualification-thursday/",
            ),
            (
                "Tandem",
                "https://firefit-europe.eu/en/produkt/firefit-em-szolnok-tandem-qualification-friday/",
            ),
            (
                "Tandem",
                "https://firefit-europe.eu/en/produkt/firefit-em-szolnok-tandem-qualification-thursday/",
            ),
            (
                "Staffel",
                "https://firefit-europe.eu/en/produkt/firefit-em-szolnok-relay-qualification-friday/",
            ),
            (
                "Staffel",
                "https://firefit-europe.eu/en/produkt/firefit-em-szolnok-relay-qualification-thursday/",
            ),
        ]:
            yield scrapy.FormRequest(
                method="GET",
                url=url,
                callback=self.parse_slots,
                cb_kwargs={"contest": contest},
            )
