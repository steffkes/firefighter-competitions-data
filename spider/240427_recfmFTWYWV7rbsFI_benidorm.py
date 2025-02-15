from util import Spider, ResultItem, ResultRankItem
import scrapy
import re


class CompetitionSpider(Spider):
    name = __name__

    def start_requests(self):
        yield scrapy.FormRequest(
            method="GET",
            url="https://cronorunner.com/resultados.php?ref=441-1821-2651",
        )

    def fixName(self, name):
        def mapper(arg):
            (sep, name) = arg
            return sep + name[0].upper() + name[1:].lower()

        return "".join(map(mapper, re.findall(r"([- ])?(\w+)", name)))

    def parse(self, response):
        for row in response.css(
            "#clasificados .table-clasificacion.table-desktop tbody tr"
        ):
            age_group = row.css(".campo-categoria::text").get()
            category = {"F": "W"}.get(age_group[-1], age_group[-1])

            category_rank = self.ranks["category"].get(category, 1)
            age_group_rank = self.ranks["age_group"].get(age_group, 1)

            yield ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                type="MPA",
                duration="%s.0" % row.css(".campo-tiempo::text").get(),
                names=[self.fixName(row.css(".nombre-corredor::text").get())],
                category=category,
                age_group=age_group,
                bib=row.css(".campo-dorsal::text").get(),
                rank=ResultRankItem(
                    total=int(row.css(".campo-posicion::text").get()),
                    category=category_rank,
                    age_group=age_group_rank,
                ),
            )

            self.ranks["category"][category] = category_rank + 1
            self.ranks["age_group"][age_group] = age_group_rank + 1


import pytest


@pytest.mark.parametrize(
    "input,output",
    [
        ("ÁLVARO  GARCÍA PASTOR ", "Álvaro García Pastor"),
        ("JUAN CARLOS PASTOR ROSADO", "Juan Carlos Pastor Rosado"),
        ("JOSÉ GONZALO PASTOR SIGÜENZA", "José Gonzalo Pastor Sigüenza"),
        ("GUSTAVO JOSÉ  GARCÍA IBÁÑEZ ", "Gustavo José García Ibáñez"),
        ("INÉS SUÁREZ ALONSO -CORTÉS ", "Inés Suárez Alonso-Cortés"),
    ],
)
def test_fixName(input, output):
    assert CompetitionSpider.fixName(input) == output
