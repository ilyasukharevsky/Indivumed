import argparse
import logging
import sys
from json import JSONDecodeError
from data_extractor import DataExtractor, FatalError


def parse_arguments():
    parser = argparse.ArgumentParser(description="DataExtractor",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     fromfile_prefix_chars="@")
    parser.add_argument("ijson", type=str, help="input JSON file")
    parser.add_argument("ojson", type=str, help="output JSON file")
    parser.parse_args()

    try:
        options = parser.parse_args()
    except IndexError:
        logging.error("Failed to read arguments. When using arguments from a file, "
                      "please ensure that no empty lines are present.", file=sys.stderr)
        return None
    return options


def setup_logging(logdebug):
    if logdebug:
        level = logging.DEBUG
    else:
        level = logging.INFO
    logformat = '%(levelname)s: %(message)s'
    logging.basicConfig(level=level, format=logformat)


def main():
    """
    Main function parses the command line arguments and starts the process.
    Return 0 upon success and 1 upon failure.
    """
    try:
        options = parse_arguments()
        data_extractor = DataExtractor(options.ijson, options.ojson)
        data_extractor.run()

    except (IOError, OSError) as exc:
        logging.error("Input/Output error: " + str(exc))
        return 1
    except JSONDecodeError as exc:
        logging.error("Input JSON file cannot be decoded: " + str(exc))
        return 1
    except FatalError as exc:
        logging.error("Fatal error: " + str(exc))
        return 1
    finally:
        logging.shutdown()


if __name__ == '__main__':
    main()
