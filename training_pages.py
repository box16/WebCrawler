from mymod import d2v
import logging
import os

if __name__ == "__main__":
    log_file = os.environ.get("LOGFILE")
    logging.basicConfig(filename=log_file, level=logging.WARNING)
    _d2v = d2v.D2V()
    print("training")
    _d2v.training()
    print("training Done")
