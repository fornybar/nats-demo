import json
from copy import deepcopy

import nats
from loguru import logger

Json = list | dict | str | float | None


async def bucket_get(bucket: nats.js.kv.KeyValue, key: str) -> bytes:
    try:
        entry = await bucket.get(key)
        value = entry.value
    except nats.js.errors.KeyNotFoundError:
        logger.debug(f"Key {key} not found")
        value = b"null"

    return value


async def upload_to_kv(
    key_value_bucket: nats.js.kv.KeyValue,
    parent_key: str,
    entry: Json,
) -> None:
    if isinstance(entry, list):
        for i, element in enumerate(entry):
            await upload_to_kv(key_value_bucket, f"{parent_key}.{i}", element)
    elif isinstance(entry, dict):
        for key, value in entry.items():
            await upload_to_kv(key_value_bucket, f"{parent_key}.{key}", value)
    else:
        await key_value_bucket.put(f"{parent_key}", json.dumps(entry).encode("utf-8"))


async def populate_db_generic(
    key_value_bucket: nats.js.kv.KeyValue, input_data: Json
) -> None:
    await upload_to_kv(key_value_bucket, "gen", input_data)


async def populate_db_smart(
    key_value_bucket: nats.js.kv.KeyValue, input_data: Json
) -> None:
    data = deepcopy(input_data)
    key = "smart"
    for entry in data:
        spot_key = f"{key}.{entry.pop('SpotKey')}"
        elements = entry.pop("Elements")
        await upload_to_kv(key_value_bucket, spot_key, entry)
        for element in elements:
            element_key = f"{spot_key}.{element.pop('Date')}"
            time_spans = element.pop("TimeSpans")
            await upload_to_kv(key_value_bucket, element_key, element)
            for time_span in time_spans:
                time_span_key = f"{element_key}.{time_span.pop('TimeSpan')}"
                await upload_to_kv(key_value_bucket, time_span_key, time_span)


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
            await upload_to_kv(key_value_bucket, f"{key}.{spot_key}", row)
