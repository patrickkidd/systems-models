import sys
import optparse
import logging
import multiprocessing as mp

from models.mythematical import server

log = logging.getLogger(__name__)

parser = optparse.OptionParser()
parser.add_option(
    "-m",
    "--models",
    dest="models",
    help="Which models to run, separated by commas, e.g. -m=calhoun,bowen",
)
parser.add_option(
    "-q",
    "--quiet",
    action="store_false",
    dest="verbose",
    default=True,
    help="don't print status messages to stdout",
)

(options, args) = parser.parse_args()

import models.bowen
import models.mythematical

MODELS = {"mythematical": models.mythematical, "bowen": models.mythematical}


def ports():
    return iter([port for port in range(5001, 5030)])


if options.models is None:
    raise Exception("--models is required")


BASE_PORT = 5001


def go(server, port):
    log.info(f"Running server {server} on port {port}.")
    server.port = int(port)
    server.verbose = options.verbose
    server.launch()


model_names = [name for name in options.models.split(",") if name in MODELS]

if __name__ == "__main__":

    log.info(f"Starting {len(model_names)} processes.")
    manager = mp.Manager()
    with mp.Pool(processes=len(model_names)) as pool:
        pool.starmap(
            go,
            [
                (MODELS.get(name).server, BASE_PORT + i)
                for i, name in enumerate(model_names)
            ],
        )
