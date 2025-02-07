import asyncio

import services.push_consumer as push_consumer
from fastapi import FastAPI
from websockets_item import router as ws_router

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(
        push_consumer.consume_push_notifications(
            queue_name="notification_queue",
        )
    )


app.include_router(ws_router, prefix="")
