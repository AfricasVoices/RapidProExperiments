import argparse
import time
import datetime

import pytz
from temba_client.v2 import TembaClient

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Poll RapidPro for flow runs")
    parser.add_argument("token", help="RapidPro API Token", nargs=1)
    parser.add_argument("--server", help="Address of RapidPro server. Defaults to localhost:8000.",
                        nargs="?", default="http://localhost:8000/")
    parser.add_argument("--poll_interval", help="Time to wait between polling the server, in seconds. Defaults to 5.",
                        nargs="?", default=5, type=int)

    args = parser.parse_args()
    token = args.token[0]
    server = args.server
    poll_interval = args.poll_interval

    client = TembaClient(server, token)
    last_update_time = datetime.datetime(2000, 1, 1, 0, 0, 0, 0, pytz.utc)

    while True:
        time.sleep(poll_interval)

        print("Polling")
        start = time.time()

        # Download all flow runs which have been updated since the last poll.
        runs = client.get_runs(after=last_update_time).all(retry_on_rate_exceed=True)
        # IMPORTANT: The .all() approach may not scale to flows with some as yet unquantified "large" number of runs.
        # See http://rapidpro-python.readthedocs.io/en/latest/#fetching-objects for more details.

        end = time.time()
        print("Polled")
        print("Time taken: " + str(end - start))

        # Ignore flows which are incomplete because the respondent is still working through the questions.
        runs = filter(lambda run: run.exited_on is not None, runs)

        # Ignore flows which are incomplete because the respondent stopped answering.
        runs = filter(lambda run: run.exit_type == "completed", runs)

        # Sort by ascending order of modification date
        runs.reverse()

        print("Fetched " + str(len(runs)) + " flows")

        if len(runs) == 0:
            continue

        # Print some data about the flow:
        for run in runs:
            print("Contact: " + run.contact.uuid)
            print("Update Time: " + str(run.modified_on))
            for question, answer in run.values.iteritems():
                print("  " + question)
                print("  " + "  " + answer.value)
            print("")

        # Uncomment for incremental fetching. Note that we need to check that this method is guaranteed to work.
        # last_update_time = flows[-1].modified_on + datetime.timedelta(microseconds=1)
