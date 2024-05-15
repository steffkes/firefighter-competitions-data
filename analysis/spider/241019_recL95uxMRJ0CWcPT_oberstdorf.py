import scrapy
from datetime import datetime
import re
import itertools
import string
from util import JsonItemExporter, ParticipantItem, ResultItem


class Spider(scrapy.Spider):
    name = __name__
    race_date = datetime.strptime(__name__.split("_")[0], "%y%m%d").strftime("%Y-%m-%d")
    competition_id = __name__.split("_")[1]
    ident = __name__[0:24]

    race_id = "281781"
    race_key = "1a92069df75cc5903748fe12993e7e8b"

    custom_settings = {
        "FEED_EXPORTERS": {"starter": JsonItemExporter},
        "FEEDS": {
            "../data/teams/%(ident)s.json": {
                "format": "starter",
                "encoding": "utf8",
                "overwrite": True,
                "item_classes": [ParticipantItem],
            },
            "data/teams/%(name)s.jsonl": {
                "format": "jsonlines",
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
        for contest in [9026, 9027]:
            yield scrapy.FormRequest(
                method="GET",
                url="https://www.anmeldungs-service.de/module/teilnehmer/staffel_cache.php",
                formdata={
                    "wettid": str(contest),
                    "totalrows": "2000",
                },
                headers={
                    "X-Requested-With": "XMLHttpRequest",
                },
                callback=self.parse_starters,
            )

    def parse_starters(self, response):
        data = response.json()["rows"]
        for entry in data:
            yield ParticipantItem(
                competition_id=self.competition_id,
                names=sorted(entry["cell"]["name"].split("<br>")),
            )


"""
import { ofetch } from "ofetch";

const tmp = (
  await Promise.allSettled(
    [9026, 9027].map(
      async (contest) =>
        new Promise(async (resolve) => {
          const data = await ofetch(
            "https://www.anmeldungs-service.de/module/teilnehmer/staffel_cache.php",
            {
              parseResponse: JSON.parse,
              headers: {
                "X-Requested-With": "XMLHttpRequest",
              },
              query: {
                wettid: contest,
                totalrows: 2000,
              },
            }
          );
          return resolve(data.rows || []);
        })
    )
  )
)
  .flatMap(({ value }) => value)
  .map(({ cell: { name: names } }) =>
    names
      .split("<br>")
      .map((name) =>
        name
          .match(/^(.+)\s+\w\s+\d+$/)[1]
          .split(" ")
          .reverse()
          .join(" ")
          .trim()
      )
      .sort()
  );

export const teams = () => tmp.sort();
export const participants = () => teams().flat();
export const count = () => participants().length;

import { defineEventHandler } from "h3";
import data from "@/data/teams/241019_recL95uxMRJ0CWcPT.json" assert { type: "json" };

export default defineEventHandler(async (event) => data["count"]);

"""
