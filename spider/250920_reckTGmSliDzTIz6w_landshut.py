from util import FirefitSpider
import scrapy


class CompetitionSpider(FirefitSpider):
    name = __name__

    def start_requests(self):
        for contest, url in [
            (
                "Einzel",
                "https://firefit-europe.eu/en/produkt/firefit-landshut-einzel-individual/",
            ),
            (
                "Tandem",
                "https://firefit-europe.eu/en/produkt/firefit-landshut-tandem-sunday/",
            ),
            (
                "Staffel",
                "https://firefit-europe.eu/en/produkt/firefit-landshut-staffel-relay-sunday/",
            ),
        ]:
            yield scrapy.FormRequest(
                method="GET",
                url=url,
                callback=self.parse_slots,
                cb_kwargs={"contest": contest},
            )
