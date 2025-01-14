import scrapy
from datetime import datetime
from util import (
    JsonItemExporter,
    JsonLinesItemExporter,
    ParticipantItem,
    ResultItem,
    ResultRankItem,
)


class Spider(scrapy.Spider):
    name = __name__
    race_date = datetime.strptime(__name__.split("_")[0], "%y%m%d").strftime("%Y-%m-%d")
    competition_id = __name__.split("_")[1]
    ident = __name__[0:24]

    custom_settings = {
        "FEED_EXPORTERS": {
            "starter": JsonItemExporter,
            "results": JsonLinesItemExporter,
        },
        "FEEDS": {
            "data/participants/%(ident)s.json": {
                "format": "starter",
                "encoding": "utf8",
                "overwrite": True,
                "item_classes": [ParticipantItem],
            },
            "data/results/%(name)s.jsonl": {
                "format": "results",
                "encoding": "utf8",
                "overwrite": True,
                "item_classes": [ResultItem],
            },
        },
        "EXTENSIONS": {
            "scrapy.extensions.telnet.TelnetConsole": None,
        },
    }

    def start_requests(self):
        for contest, type, _ in [
            (6014, "MPA", "STRONG"),
            (6015, "MPA", "OPEN"),
            (6016, "OPA", "LIGHT"),
        ]:
            yield scrapy.FormRequest(
                method="GET",
                url="https://www.stotinka.hr/eng/race/%d/registered_list" % contest,
                callback=self.parse_starters,
            )

            yield scrapy.FormRequest(
                method="GET",
                url="https://www.stotinka.hr/eng/race/%d/total_rank" % contest,
                cb_kwargs={"type": type},
            )

    def parse_starters(self, response):
        for entry in response.css("table tbody tr"):
            [_, lastname, firstname] = [
                cell.css("::text").get() for cell in entry.css("td")
            ][0:3]

            yield ParticipantItem(
                competition_id=self.competition_id,
                names=["%s %s" % (firstname, lastname)],
            )

        yield from response.follow_all(
            response.css(".pagination li:not([class~='disabled']) a::attr(href)"),
            callback=self.parse_starters,
        )

    def parse(self, response, type):

        for entry in response.css("table tbody tr"):
            cells = entry.css("td")
            [
                total_rank,
                bib,
                name,
                category,
                _country,
                _status,
                _passed,
                duration,
                _pace,
                _speed,
                _rank,
            ] = [cell.css("::text").get() for cell in cells]
            [
                _category,
                category_rank,
                age_group_info,
            ] = (
                cells[10].css("span::text").getall()
            )

            [
                _category,
                category_rank,
                age_group_info,
            ] = [subcell.css("::text").get() for subcell in cells[10].css("span")]

            [age_group_rank, age_group] = age_group_info.split(" - ")

            yield ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                type=type,
                category={"F": "W"}.get(category, category),
                duration="00:" + (("0" + duration)[-9:])[:7],
                names=[name],
                bib=bib.strip(),
                age_group=age_group.replace("Ž", "W"),
                rank=ResultRankItem(
                    total=int(total_rank),
                    category=int(category_rank),
                    age_group=int(age_group_rank),
                ),
            )
