from util import FccSpider


class CompetitionSpider(FccSpider):
    name = __name__
    event_id = 19
    event_day_ids = [39, 40]
