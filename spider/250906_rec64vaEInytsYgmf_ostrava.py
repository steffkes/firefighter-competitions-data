from util import FirefitSpider
import scrapy


class CompetitionSpider(FirefitSpider):
    name = __name__

    def start_requests(self):
        for contest, url in [
            (
                "Einzel",
                "https://firefit-europe.eu/en/produkt/firefit-ostrava-einzel-individual-saturday/",
            ),
            (
                "Tandem",
                "https://firefit-europe.eu/en/produkt/firefit-ostrava-tandem-sunday/",
            ),
            (
                "Staffel",
                "https://firefit-europe.eu/en/produkt/firefit-ostrava-staffel-relay-sunday/",
            ),
        ]:
            yield scrapy.FormRequest(
                method="GET",
                url=url,
                callback=self.parse_slots,
                cb_kwargs={"contest": contest},
            )
