scriabin is a stopgap script that watches our nginx logs and pushes
the metrics to prometheus via a pushgateway.

We would prefer a pull-based approach (see
https://appsembler.atlassian.net/wiki/spaces/ED/pages/43614296/Getting+Data+into+Prometheus)
but we don't have that set up yet.

Scriabin works very simply by running once per minute in a cron
job. It parses JSON formatted nginx logs (using Pygtail to track file
offsets between runs) and submits the summarized metrics to
Prometheus.

This role should be installed on edxapp servers and, with a regular
config, all the default values should work.
