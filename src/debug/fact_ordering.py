import argparse
import logging
from service import ElectionNlgService


def main():
    # Configure logging to output everything
    formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    log = logging.getLogger('root')
    log.setLevel(logging.INFO)
    log.addHandler(handler)

    log.info("Loading pipeline")
    service = ElectionNlgService("../data", nomorphi=True, random_seed=4321)

    test_cases = [
        ("M91: 013A", "P", "91-610", "candidate"),
        ("905", "M", None, None),
        ("12", "D", "VIHR", "party"),
        ("91", "M", "KOK", "party"),
        ("fi", "C", None, None),
    ]
    for where, where_type, who, who_type in test_cases:
        log.info("Running pipeline with where={}, where_type={}, who={}, who_type={}".format(
            where, where_type, who, who_type))
        headline, body = service.run_pipeline("en", who, who_type, where, where_type)

        print("== {} ==".format(headline))
        print(body.replace("</p><p>", "</p>\n<p>"), "\n")


if __name__ == '__main__':
    parser = argparse.ArgumentParser("Test ordering of facts in a minimal pipeline")
    args = parser.parse_args()

    main()
