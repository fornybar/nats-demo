import asyncio
import json
from copy import deepcopy
from pathlib import Path

import nats

servers = "nats://localhost:4222"

Json = list | dict | str | float | None


async def get_attribute(
    key_value_bucket: nats.js.kv.KeyValue, attributes: list[str]
) -> bytes:
    try:
        entry = await key_value_bucket.get(".".join(attributes))
        value = entry.value
    except nats.js.errors.KeyNotFoundError:
        value = b"null"

    return value


async def upload_to_db(
    key_value_bucket: nats.js.kv.KeyValue,
    parent_key: str,
    entry: Json,
) -> None:
    if isinstance(entry, list):
        for i, element in enumerate(entry):
            await upload_to_db(key_value_bucket, f"{parent_key}.{i}", element)
    elif isinstance(entry, dict):
        for key, value in entry.items():
            await upload_to_db(key_value_bucket, f"{parent_key}.{key}", value)
    else:
        print(f"Uploading {entry} to {parent_key}")
        await key_value_bucket.put(f"{parent_key}", json.dumps(entry).encode("utf-8"))


async def populate_db_generic(
    key_value_bucket: nats.js.kv.KeyValue, input_data: Json
) -> None:
    await upload_to_db(key_value_bucket, "gen", input_data)


async def populate_db_smart(
    key_value_bucket: nats.js.kv.KeyValue, input_data: Json
) -> None:
    data = deepcopy(input_data)
    key = "smart"
    for entry in data:
        spot_key = f"{key}.{entry.pop('SpotKey')}"
        elements = entry.pop("Elements")
        await upload_to_db(key_value_bucket, spot_key, entry)
        for element in elements:
            element_key = f"{spot_key}.{element.pop('Date')}"
            time_spans = element.pop("TimeSpans")
            await upload_to_db(key_value_bucket, element_key, element)
            for time_span in time_spans:
                time_span_key = f"{element_key}.{time_span.pop('TimeSpan')}"
                await upload_to_db(key_value_bucket, time_span_key, time_span)


async def populate_db_flat(
    key_value_bucket: nats.js.kv.KeyValue, input_data: Json
) -> None:
    key = "flat"
    for e in input_data:
        spot_key = e["SpotKey"]
        for row in [
            {k: v for k, v in entry.items() if k != "Elements"}
            | {k: v for k, v in element.items() if k != "TimeSpans"}
            | time_span
            for entry in input_data
            for element in entry["Elements"]
            for time_span in element["TimeSpans"]
        ]:
            await upload_to_db(key_value_bucket, f"{key}.{spot_key}", row)


async def main() -> None:
    natsclient = await nats.connect(servers=servers)
    jetstream = natsclient.jetstream()
    key_value_bucket = await jetstream.create_key_value(bucket="DB")

    # input_data = json.load((Path(__file__).parents[2] / "spot.json").open())
    # await populate_db_generic(key_value_bucket, input_data)
    # await populate_db_smart(key_value_bucket, input_data)
    # await populate_db_flat(key_value_bucket, input_data)

    subscriber = await natsclient.subscribe("get.>")
    print("Subscriber starter")
    try:
        while True:
            response = b"null"
            try:
                msg = await subscriber.next_msg()
            except nats.errors.TimeoutError:
                continue
            verb, *attributes = msg.subject.split(".")
            if verb == "get":
                response = await get_attribute(key_value_bucket, attributes)

            await msg.respond(response)
    except KeyboardInterrupt:
        await natsclient.drain()


if __name__ == "__main__":
    asyncio.run(main())
