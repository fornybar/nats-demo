import asyncio
import json
from datetime import UTC, datetime

import nats
import requests


def request_data(date: str) -> list[list[str]]:
    print("MAKING REQUEST TO STATNETT FOR", date)
    response = requests.get(
        f"https://driftsdata.statnett.no/restapi/Reserves/PrimaryReservesPerDay?localDateTime={date}",
        timeout=5,
    )
    response.raise_for_status()
    return response.json()


def parse_statnett(response_json: list[list[str]]) -> dict[int, dict[str, float]]:
    statnett_columns = {
        0: "no1_fcrn_pris",
        1: "no1_fcrn_vol",
        2: "no1_fcrd_opp_pris",
        3: "no1_fcrd_opp_vol",
        6: "no2_fcrn_pris",
        7: "no2_fcrn_vol",
        8: "no2_fcrd_opp_pris",
        9: "no2_fcrd_opp_vol",
        12: "no3_fcrn_pris",
        13: "no3_fcrn_vol",
        14: "no3_fcrd_opp_pris",
        15: "no3_fcrd_opp_vol",
        18: "no4_fcrn_pris",
        19: "no4_fcrn_vol",
        20: "no4_fcrd_opp_pris",
        21: "no4_fcrd_opp_vol",
        24: "no5_fcrn_pris",
        25: "no5_fcrn_vol",
        26: "no5_fcrd_opp_pris",
        27: "no5_fcrd_opp_vol",
    }
    data = {}
    for _hour, *values in response_json:
        hour = int(_hour)
        data[hour] = {}
        for idx, column in statnett_columns.items():
            data[hour][column] = float(values[idx].replace(",", "."))
    return data


async def upload_to_db(
    key_value_bucket: nats.js.kv.KeyValue,
    parent_key: str,
    entry: dict,
) -> None:
    if isinstance(entry, list):
        for i, element in enumerate(entry):
            await upload_to_db(key_value_bucket, f"{parent_key}.{i}", element)
    elif isinstance(entry, dict):
        for key, value in entry.items():
            await upload_to_db(key_value_bucket, f"{parent_key}.{key}", value)
    else:
        await key_value_bucket.put(f"{parent_key}", json.dumps(entry).encode("utf-8"))


async def get_attribute(
    key_value_bucket: nats.js.kv.KeyValue, attributes: list[str]
) -> bytes:
    try:
        entry = await key_value_bucket.get(".".join(attributes))
        value = entry.value
    except nats.js.errors.KeyNotFoundError:
        value = b"null"

    return value


async def main() -> None:
    natsclient = await nats.connect(servers="localhost:4222")
    jetstream = natsclient.jetstream()
    await jetstream.delete_key_value(bucket="DB")
    key_value_bucket = await jetstream.create_key_value(bucket="DB")
    subscriber = await natsclient.subscribe("get.>")

    print("Subscriber starter")
    try:
        while True:
            response = b"null"
            try:
                msg = await subscriber.next_msg()
            except nats.errors.TimeoutError:
                continue
            verb, db, date, *attributes = msg.subject.split(".")
            if verb == "get":
                if (
                    attributes != ["updated"]
                    and await get_attribute(key_value_bucket, ["pr", date, "updated"])
                    == b"null"
                ):
                    await upload_to_db(
                        key_value_bucket,
                        "pr",
                        {
                            date: {
                                "updated": datetime.now(tz=UTC).strftime(
                                    "%Y-%m-%dT%H:%M:%SZ"
                                )
                            }
                            | parse_statnett(request_data(date))
                        },
                    )
                response = await get_attribute(
                    key_value_bucket, ["pr", date, *attributes]
                )

            await msg.respond(response)
    except KeyboardInterrupt:
        await natsclient.drain()


if __name__ == "__main__":
    asyncio.run(main())
