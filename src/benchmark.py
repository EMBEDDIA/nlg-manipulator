from service import CrimeNlgService
import os
import sys
import time

import logging
formatter = logging.Formatter(fmt='\33[2K\r%(asctime)s - %(levelname)s - %(module)s - %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
log = logging.getLogger('root')
log.setLevel(logging.ERROR)
log.addHandler(handler)


def print_progress(iteration, total, decimals=1):
    """
    MODIFIED FROM https://gist.github.com/aubricus/f91fb55dc6ba5557fbab06119420dd6a
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
    """
    percents = "{0:.1f}".format(100 * (iteration / total))
    filled_length = int(round(100 * iteration / total))
    bar = '█' * filled_length + '-' * (100 - filled_length)
    sys.stdout.write('\r |%s| %s%s' % (bar, percents, '%')),
    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()


def benchmark():
    print("Initializing ", end="")
    service = CrimeNlgService(
        random_seed = 4551546,
        force_cache_refresh=False,
        #nomorphi=True, # Remove to use omorphi
    )
    print(".", end="")

    municipalities = service.registry.get('geodata-lookup')["fi"]['M'].keys()
    print(".", end="")
    
    total = 1 + len(municipalities)
    print(" done.")

    print("\nRunning benchmark with {} generations".format(total))
    start = time.perf_counter()

    i = 1
    service.run_pipeline(language='fi', where="fi", where_type="C")
    print_progress(i, total)

    for m in municipalities:
        i += 1
        service.run_pipeline(language='fi', where=m, where_type="M")
        print_progress(i, total)

    delta = time.perf_counter() - start

    print("\nEstimating overhead")
    overhead_start = time.perf_counter()
    for j in range(1, i+1):
        print_progress(j, i)
    overhead_delta = time.perf_counter() - overhead_start
    print("Estimated overhead at {} seconds".format(overhead_delta))

    print("Benchmark complete.")
    print("\tTotal time: {} seconds".format(delta))
    print("\tTotal time w\o overhead: {} seconds".format(delta - overhead_delta))
    print("\tTime per generation: {} seconds".format(delta / total))
    print("\tTime per generation w\o overhead: {} seconds".format((delta - overhead_delta) / total))

    
if __name__ == "__main__":
    benchmark()
