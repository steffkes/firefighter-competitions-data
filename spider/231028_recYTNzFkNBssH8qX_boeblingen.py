from util import FccSpider


class CompetitionSpider(FccSpider):
    name = __name__
    event_id = 15
    age_group_fallback = "M"  # not sure why this is even needed
