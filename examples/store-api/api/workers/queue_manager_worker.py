import logging
from chronoqueue.client import ChronoqueueClient
from chronoqueue.utils import QueueOptions, QueueType
from config.settings import QUEUE_NAME_STORE_CART, QUEUE_NAME_CHECKOUT_CART, CHECKOUT_QUEUE_EXCLUSIVE_KEY

# Initialize logging
logging.basicConfig(level=logging.INFO)


async def create_store_cart_queue(client: ChronoqueueClient):
    try:
        queue_options = QueueOptions(
            type=QueueType.SIMPLE,
            exclusivity_key="",
            max_attempts=2,
            lease_duration="1m",
            invisibility_duration="3s",
        )

        response = client.create_queue(name=QUEUE_NAME_STORE_CART, options=queue_options).to_dict()
        logging.info("Create STORE Queue returned: ")
        logging.info(response)
    except Exception as e:
        logging.error(f"===== STORE ERROR: occurred in create_store_cart_queue: {e} ==== ")


async def create_checkout_cart_queue(client: ChronoqueueClient):
    try:
        queue_options = QueueOptions(
            type=QueueType.EXCLUSIVE,
            exclusivity_key=CHECKOUT_QUEUE_EXCLUSIVE_KEY,
            max_attempts=-1,  # Unlimited attempts
            lease_duration="5m",
            invisibility_duration="2s",
        )

        response = client.create_queue(name=QUEUE_NAME_CHECKOUT_CART, options=queue_options).to_proto()
        logging.info("Create CHECKOUT Queue returned: ")
        logging.info(response)
    except Exception as e:
        logging.error(f"===== CHECKOUT ERROR: occurred in create_checkout_cart_queue: {e} ==== ")
