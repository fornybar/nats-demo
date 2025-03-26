import asyncio
import json

import nats
from loguru import logger

from nats_demo.primary_reserves.ingest import request_and_publish
from nats_demo.utils import bucket_get


async def _main() -> None:
    natsclient = await nats.connect(servers="localhost:4222")
    jetstream = natsclient.jetstream()
    database = await jetstream.create_key_value(bucket="DB")
    state = await jetstream.create_key_value(bucket="STATE")
    jetstream = natsclient.jetstream()
    await jetstream.add_stream(name="RAW", subjects=["raw.>"])

    subscribe_pattern = "get.pr.>"
    subscriber = await natsclient.subscribe(subscribe_pattern)
    logger.info(f"Subscriber startet listening to {subscribe_pattern}")
    try:
        while True:
            try:
                msg = await subscriber.next_msg()
            except nats.errors.TimeoutError:
                continue

            msg_data = json.loads(msg.data.decode())
            logger.info(
                f"HERE WE COULD DO SOMETHING WITH DATA FROM REQUEST: {msg_data}"
            )
            response = b"null"
            verb, target_database, date, *attributes = msg.subject.split(".")
            if verb == "get" and target_database == "pr":
                for _ in range(3):
                    if (
                        attributes != ["updated"]
                        and await bucket_get(state, f"pr.{date}.updated") == b"null"
                    ):
                        logger.info("Missing data. Please wait while we request it...")
                        await request_and_publish(date)
                        await asyncio.sleep(1)
                    else:
                        break
                response = await bucket_get(
                    database, f"pr.{date}.{'.'.join(attributes)}"
                )

            await msg.respond(response)
    except KeyboardInterrupt:
        await natsclient.drain()


def main() -> None:
    asyncio.run(_main())


if __name__ == "__main__":
    main()
