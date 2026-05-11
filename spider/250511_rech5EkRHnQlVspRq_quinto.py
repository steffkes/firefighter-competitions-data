from util import QuintoSpider
import scrapy


class CompetitionSpider(QuintoSpider):
    name = __name__

    def start_requests(self):
        yield scrapy.FormRequest(
            method="GET",
            url="https://event.endu.net/events/event/entrants-json",
            formdata={"idevento": "93312", "rows": "200", "page": "1"},
            callback=self.parse_starters,
        )

        yield scrapy.FormRequest(
            method="GET",
            url="https://egs-eventi.s3.amazonaws.com/00000000/00090000/00093300/00093312/results/jsonp/542524_YBX3V486Q8.jsonp",
        )
