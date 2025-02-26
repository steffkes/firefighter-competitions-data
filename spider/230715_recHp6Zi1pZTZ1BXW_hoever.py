from util import FccSpider


class CompetitionSpider(FccSpider):
    name = __name__
    event_id = 13
    age_group_fallback = "M"
