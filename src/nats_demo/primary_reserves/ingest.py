import asyncio
import json
import sys
import time
from datetime import UTC, datetime

import nats
import requests
from loguru import logger

from nats_demo.utils import upload_to_kv


def request_data(date: str) -> list[list[str]]:
    logger.info(f"MAKING REQUEST TO STATNETT FOR {date}")
    response = requests.get(
        f"https://driftsdata.statnett.no/restapi/Reserves/PrimaryReservesPerDay?localDateTime={date}",
        timeout=5,
    )
    response.raise_for_status()
    return response.json()


async def request_and_publish(date: str) -> None:
    natsclient = await nats.connect(servers="localhost:4222")
    jetstream = natsclient.jetstream()
    state = await jetstream.create_key_value(bucket="STATE")
    jetstream = natsclient.jetstream()
    await jetstream.add_stream(name="RAW", subjects=["raw.>"])

    response_json = request_data(date)
    if len(response_json) > 0:
        await upload_to_kv(
            state,
            f"pr.{date}.updated",
            datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        )
        await jetstream.publish(
            f"raw.pr.{date}",
            json.dumps(response_json).encode(),
        )

    await natsclient.drain()


def run(date: str) -> None:
    asyncio.run(request_and_publish(date))


def main() -> None:
    main(sys.argv[1])


if __name__ == "__main__":
    main()
