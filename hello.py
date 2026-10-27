import logging

logger = logging.getLogger(__name__)


def greet(name: str) -> str:
    return f"Hello, {name}!"


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger.info("%s", greet("FieldReady"))
