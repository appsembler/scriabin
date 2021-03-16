scriabin is a stopgap script that watches our nginx logs and writes
them out as text file metrics that node_exporter can read and export
to Prometheus.

Scriabin works very simply by running once per minute in a cron
job. It parses JSON formatted nginx logs (using Pygtail to track file
offsets between runs) and submits the summarized metrics to
Prometheus.

This role should be installed on edxapp servers and, with a regular
config, all the default values should work.
