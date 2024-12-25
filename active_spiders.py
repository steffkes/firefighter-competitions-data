from pathlib import Path
from datetime import date, datetime
import re

today = date.today()

spiders = list(
    filter(
        lambda path: datetime.strptime(re.match(r"^\d+", path.name)[0], "%y%m%d").date()
        >= today,
        sorted(Path("spider/").glob("*rec*.py")),
    )
)

if __name__ == "__main__":
    print("\n".join(map(str, spiders)))
