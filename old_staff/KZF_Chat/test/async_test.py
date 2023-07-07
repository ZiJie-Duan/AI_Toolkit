import asyncio

async def hello():
    print("Hello ...")
    await asyncio.sleep(1)
    print("... World!")


def main():
    loop = asyncio.get_event_loop()
    tasks = [hello(), hello(), hello()]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()

main()