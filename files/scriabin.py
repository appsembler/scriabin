#!/usr/bin/env python3
import json
import os
import socket
from datetime import datetime, timedelta
from dateutil import parser, tz
from pygtail import Pygtail

from prometheus_client import CollectorRegistry, write_to_textfile
from prometheus_client import Gauge, Histogram

# gather up environment variables

LOG_FILE = os.environ.get("SCRIABIN_LOG_FILE",
                          "/edx/var/log/nginx/access_json.log")
SLOW_THRESHOLD = float(os.environ.get("SCRIABIN_SLOW_THRESHOLD",
                                      "0.4"))  # seconds
PROJECT = os.environ["SCRIABIN_PROJECT"]
APP = os.environ["SCRIABIN_APP"]
SKIP_PATHS = os.environ.get(
    "SCRIABIN_SKIP_PATHS",
    "/static/,/admin/,/hijack/,/favicon.ico").split(",")

INSTANCE = socket.gethostname()
OFFSET_FILE = "/tmp/scriabin-{}-{}.offset".format(PROJECT, APP)

# prepare Prometheus metrics
registry = CollectorRegistry()
requests_counter = Gauge("nginx_requests", "HTTP Requests",
                         ["app", "status"],
                         registry=registry)
# make sure a few are always set, rather than have missing values
requests_counter.labels(app=APP, status=200).set(0)
requests_counter.labels(app=APP, status=201).set(0)
requests_counter.labels(app=APP, status=204).set(0)
requests_counter.labels(app=APP, status=206).set(0)
requests_counter.labels(app=APP, status=301).set(0)
requests_counter.labels(app=APP, status=302).set(0)
requests_counter.labels(app=APP, status=304).set(0)
requests_counter.labels(app=APP, status=400).set(0)
requests_counter.labels(app=APP, status=403).set(0)
requests_counter.labels(app=APP, status=404).set(0)
requests_counter.labels(app=APP, status=499).set(0)
requests_counter.labels(app=APP, status=500).set(0)
requests_counter.labels(app=APP, status=502).set(0)

response_time = Histogram("nginx_response_time", "HTTP Response Time (s)",
                          ["app"],
                          buckets=[.01, 0.02, 0.04, 0.1, 0.2, 0.4, 1.0,
                                   2.0, 4.0, 10.0, 20.0, 40.0,
                                   float("inf")],
                          registry=registry)

apdex_score = Gauge("apdex_score", "Apdex", ["app"], registry=registry)
parse_errors = Gauge("parse_errors", "Nginx log parse errors", ["app"],
                     registry=registry)


def log_entries(now=None, window_minutes=1):
    """ returns the log entries that we are interested in

    ie, within our time window, and not in the skip list """
    if now is None:
        now = datetime.now(tz.tzlocal())
    start = now - timedelta(minutes=window_minutes)
    errors = 0
    entries = []
    for line in Pygtail(LOG_FILE, offset_file=OFFSET_FILE):
        try:
            d = json.loads(line)
            ts = parser.parse(d['time_local'])
            if ts < start:
                # ignore entries that are too old
                # with pygtail, this should mostly only happen on the first run
                continue
            entries.append(d)
        except Exception as e:
            print(e)
            errors += 1
    return entries, errors


def main():
    total_requests = 0
    failed_requests = 0
    slow_requests = 0

    entries, errors = log_entries()
    for d in entries:
        total_requests += 1
        requests_counter.labels(app=APP, status=d['status']).inc()
        if d['status'].startswith('5'):
            failed_requests += 1
        rt = float(d['request_time'])
        response_time.labels(app=APP).observe(rt)
        if rt > SLOW_THRESHOLD:
            slow_requests += 1

    apdex_score.labels(app=APP).set(1)
    if total_requests > 0:
        satisfied = total_requests - (failed_requests + slow_requests)
        apdex_score.labels(
            app=APP).set((satisfied + (slow_requests / 2)) / total_requests)

    parse_errors.labels(app=APP).set(errors)

    print("total_requests:", total_requests)
    print("failed:", failed_requests)
    print("slow:", slow_requests)

    write_to_textfile(
        "/var/lib/node_exporter/nginx_{}.prom".format(APP), registry)


if __name__ == "__main__":
    main()
