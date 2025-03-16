from util import RottweilSpider


class CompetitionSpider(RottweilSpider):
    name = __name__

    race_id = "233380"
    race_key = "60cc4a4284fd80a91ac2abbea60e10ed"

    custom_starter = [
        (5, "#1_{DE:Feuerwehr-Team mit PA|EN:Firefighters team with SCBA}"),
        (
            6,
            "#1_{DE:Feuerwehr-Team ohne PA|EN:Firefighters team without SCBA}",
        ),
    ]
