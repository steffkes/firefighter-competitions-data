from util import FirefitSpider
import scrapy


class CompetitionSpider(FirefitSpider):
    name = __name__

    def start_requests(self):
        for contest, url in [
            (
                "Einzel",
                "https://firefit-europe.eu/en/produkt/firefit-kassel-einzel-individual-saturday-26/",
            ),
            (
                "Staffel",
                "https://firefit-europe.eu/en/produkt/firefit-kassel-staffel-relay-sunday-26/",
            ),
            (
                "Tandem",
                "https://firefit-europe.eu/en/produkt/firefit-kassel-tandem-sunday-26/",
            ),
        ]:
            yield scrapy.FormRequest(
                method="GET",
                url=url,
                callback=self.parse_slots,
                cb_kwargs={"contest": contest},
            )
