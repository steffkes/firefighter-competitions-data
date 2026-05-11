from util import QuintoSpider
import scrapy


class CompetitionSpider(QuintoSpider):
    name = __name__

    def start_requests(self):
        yield scrapy.FormRequest(
            method="GET",
            url="https://event.endu.net/events/event/entrants-json",
            formdata={"idevento": "100485", "rows": "200", "page": "1"},
            callback=self.parse_starters,
        )

        yield scrapy.FormRequest(
            method="GET",
            url="https://egs-eventi.s3.amazonaws.com/00000000/00100000/00100400/00100485/results/jsonp/615003_5GHUV40FU7.jsonp",
        )
