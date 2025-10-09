"""Extract test data runs."""

# TODO 1131

import databroker
import gzip
import json
from apstools.utils.misc import replay
from apstools.utils import listruns


def write_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def extract():
    db = []
    memcat = databroker.temp().v2
    print(f"{len(memcat.v2)=}")

    def receiver(k, doc):
        db.append([k, doc])

    for cname in "apstools_test usaxs_test".split():
        if cname in databroker.catalog:
            db = []
            cat = databroker.catalog[cname]
            for uid in cat.v2:
                print(f"{cat.name=}  {uid=}")
                run = cat[uid]
                replay(run, receiver)
                replay(run, memcat.v1.insert)
            print(f"documents received: {len(db)=}")
            write_json(db, f"dev_{cname}.json")

    # print(f"documents received: {len(db)=}")
    # write_json(db, f"dev_documents.json")

    print(f"{len(memcat.v2)=}")
    print(listruns(memcat.v2, num=70))


def load_catalog(path: str):
    with gzip.open(path, "rt", encoding="utf-8") as f:
        data = json.load(f)
    cat = databroker.temp().v2
    for entry in data:
        cat.v1.insert(*entry)
    # print(listruns(cat, num=len(cat.v2)))
    return cat


if __name__ == "__main__":
    # extract()

    load_catalog("resources/usaxs_test.json.gz")
    load_catalog("resources/apstools_test.json.gz")
