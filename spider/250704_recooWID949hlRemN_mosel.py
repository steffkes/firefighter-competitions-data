from util import FccSpider


class CompetitionSpider(FccSpider):
    name = __name__
    event_day_ids = [42, 43, 44]
