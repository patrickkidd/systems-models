import sys, logging

logging.basicConfig(
    stream=sys.stdout,
    filemode="w",
    format="%(levelname)s %(asctime)s - %(message)s",
    level=logging.INFO,
)
