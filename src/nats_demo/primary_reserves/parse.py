import asyncio
import json

import nats
from loguru import logger

from nats_demo.utils import upload_to_kv


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


async def _main() -> None:
    natsclient = await nats.connect(servers="localhost:4222")
    jetstream = natsclient.jetstream()
    database = await jetstream.create_key_value(bucket="DB")
    jetstream = natsclient.jetstream()
    await jetstream.add_stream(name="RAW", subjects=["raw.>"])

    subscriber = await jetstream.pull_subscribe(subject="raw.pr.>", durable="parse")
    logger.info("Ready to recieve")
    try:
        while True:
            try:
                messages = await subscriber.fetch()
            except nats.errors.TimeoutError:
                continue

            for message in messages:
                logger.info(f"Parsing message from {message.subject}")
                date = message.subject.split(".")[-1]
                await upload_to_kv(
                    database,
                    f"pr.{date}",
                    parse_statnett(json.loads(message.data.decode())),
                )
                await message.ack()
    except KeyboardInterrupt:
        await natsclient.drain()


def main() -> None:
    asyncio.run(_main())


if __name__ == "__main__":
    main()
