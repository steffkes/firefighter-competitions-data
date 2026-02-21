from util import FirefitSpider
import scrapy


class CompetitionSpider(FirefitSpider):
    name = __name__

    def start_requests(self):
        for contest, url in [
            (
                "Einzel",
                "https://firefit-europe.eu/en/produkt/firefit-interschutz-em-einzel-individual-monday/",
            ),
            (
                "Einzel",
                "https://firefit-europe.eu/en/produkt/firefit-interschutz-em-einzel-individual-tuesday/",
            ),
            (
                "Einzel",
                "https://firefit-europe.eu/en/produkt/firefit-interschutz-em-einzel-individual-wednesday/",
            ),
            (
                "Einzel",
                "https://firefit-europe.eu/en/produkt/firefit-interschutz-em-einzel-individual-thursday/",
            ),
            (
                "Staffel",
                "https://firefit-europe.eu/en/produkt/firefit-interschutz-em-staffel-relay-monday/",
            ),
            (
                "Staffel",
                "https://firefit-europe.eu/en/produkt/firefit-interschutz-em-staffel-relay-tuesday/",
            ),
            (
                "Staffel",
                "https://firefit-europe.eu/en/produkt/firefit-interschutz-em-staffel-relay-wednesday/",
            ),
            (
                "Staffel",
                "https://firefit-europe.eu/en/produkt/firefit-interschutz-em-staffel-relay-thursday/",
            ),
            (
                "Tandem",
                "https://firefit-europe.eu/en/produkt/firefit-interschutz-em-tandem-monday/",
            ),
            (
                "Tandem",
                "https://firefit-europe.eu/en/produkt/firefit-interschutz-em-tandem-tuesday/",
            ),
            (
                "Tandem",
                "https://firefit-europe.eu/en/produkt/firefit-interschutz-em-tandem-wednesday/",
            ),
            (
                "Tandem",
                "https://firefit-europe.eu/en/produkt/firefit-interschutz-em-tandem-thursday/",
            ),
        ]:
            yield scrapy.FormRequest(
                method="GET",
                url=url,
                callback=self.parse_slots,
                cb_kwargs={"contest": contest},
            )
