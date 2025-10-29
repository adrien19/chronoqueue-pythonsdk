from fastapi import FastAPI, Depends, HTTPException
import asyncio
import logging
import os
from chronoqueue.client import ChronoqueueClient
from chronoqueue.utils import TlsConfig

from .routes import store
from config.settings import CHRONOQUEUE_HOST, CHRONOQUEUE_PORT
from .workers.process_store_cart_worker import process_store_cart, process_checkout_cart
from .workers.queue_manager_worker import create_store_cart_queue, create_checkout_cart_queue

app = FastAPI()

# Initialize client as None, will be created on startup
client = None

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def heartbeat_error_handler(error_info: dict):
    """
    Custom error handler for heartbeat failures.
    This demonstrates how to monitor and react to heartbeat issues.
    """
    logger.error(
        f"⚠️ HEARTBEAT ERROR - Message: {error_info['message_id']}, "
        f"Queue: {error_info['queue_name']}, "
        f"Error: {error_info.get('error_details', 'Unknown')}, "
        f"Retry Count: {error_info.get('retry_count', 0)}, "
        f"Heartbeats Sent: {error_info.get('heartbeats_sent', 0)}"
    )


def get_client():
    """Get or create ChronoQueue client with TLS if certificates exist."""
    global client
    if client is None:
        # Check if TLS certs exist
        ca_path = "./certs/ca.crt"
        client_crt_path = "./certs/client.crt"
        client_key_path = "./certs/client.key"

        use_tls = all(os.path.exists(p) for p in [ca_path, client_crt_path, client_key_path])

        if use_tls:
            client = ChronoqueueClient(
                host=CHRONOQUEUE_HOST,
                port=CHRONOQUEUE_PORT,
                use_tls=False,
                tls_config=TlsConfig(ca_path=ca_path, client_crt_path=client_crt_path, client_key_path=client_key_path),
                # New heartbeat configuration parameters
                heartbeat_max_duration=120,  # 2 minutes max for this example
                heartbeat_max_count=500,
                heartbeat_thread_pool_size=10,
                heartbeat_error_callback=heartbeat_error_handler,
            )
            logger.info("✅ ChronoQueue client initialized with TLS and enhanced heartbeat management")
        else:
            # Use insecure connection for testing/development with enhanced heartbeat
            client = ChronoqueueClient(
                host=CHRONOQUEUE_HOST,
                port=CHRONOQUEUE_PORT,
                use_tls=False,
                # New heartbeat configuration parameters
                heartbeat_max_duration=120,  # 2 minutes max for demo (normally would be higher)
                heartbeat_max_count=500,
                heartbeat_thread_pool_size=10,
                heartbeat_error_callback=heartbeat_error_handler,
            )
            logger.info("✅ ChronoQueue client initialized (no TLS) with enhanced heartbeat management")
            logger.info(f"   - Max heartbeat duration: 120s")
            logger.info(f"   - Max heartbeat count: 500")
            logger.info(f"   - Thread pool size: 10")
    return client


@app.on_event("startup")
async def startup_event():
    global client
    client = get_client()
    asyncio.create_task(create_store_cart_queue(client))
    asyncio.create_task(create_checkout_cart_queue(client))
    asyncio.create_task(process_store_cart(client))
    asyncio.create_task(process_checkout_cart(client))
    # Add heartbeat monitoring task to demonstrate observability
    asyncio.create_task(monitor_heartbeats(client))


async def monitor_heartbeats(client: ChronoqueueClient):
    """
    Background task to monitor active heartbeats.
    This demonstrates the new observability features.
    """
    await asyncio.sleep(5)  # Wait for workers to start

    while True:
        try:
            active_count = client.get_active_heartbeat_count()

            if active_count > 0:
                logger.info(f"💓 Active heartbeats: {active_count}")

                # Get detailed info about active heartbeats
                active_hb = client.get_active_heartbeats()
                for msg_id, info in active_hb.items():
                    logger.info(
                        f"   📨 Message {msg_id[:8]}... on queue '{info['queue_name']}' "
                        f"(running for {info['duration']:.1f}s, freq: {info['heartbeat_frequency']}s)"
                    )

                # Get statistics
                stats = client.get_heartbeat_stats()
                for msg_id, metric in stats.items():
                    if msg_id in active_hb:  # Only log active ones
                        logger.info(
                            f"   📊 Stats: {metric['heartbeats_sent']} sent, " f"{metric['heartbeats_failed']} failed"
                        )

            await asyncio.sleep(10)  # Check every 10 seconds
        except Exception as e:
            logger.error(f"Error in heartbeat monitor: {e}")
            await asyncio.sleep(10)


@app.on_event("shutdown")
def shutdown_event():
    if client:
        logger.info("🛑 Shutting down ChronoQueue client...")
        # Show final heartbeat stats before closing
        active_count = client.get_active_heartbeat_count()
        if active_count > 0:
            logger.warning(f"⚠️ Closing with {active_count} active heartbeat(s)")

        client.close(timeout=30.0)
        logger.info("✅ ChronoQueue client closed successfully")


app.include_router(store.router, prefix="/store", tags=["store"])
