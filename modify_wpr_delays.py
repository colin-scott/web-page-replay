#!/usr/bin/env python

# TODO(cs): make cache hit ratio tunable.
# TODO(cs): two analyses: perfect cachability at proxy, and perfect
# cachability in browser. Use CC: private vs. CC: public to make distinction.
# TODO(cs): don't assume that cache is co-located with browser, i.e. insert
# delays between browser and perfect cache.
# TODO(cs): account for performance cost of conditional GETs
# TODO(cs): show a CDF of fraction of response bytes that are cacheable per
# site.
from httparchive import HttpArchive
import glob
import re
import optparse

# Modified archive.
def assume_perfect_cache(archive):
  for request in archive:
    response = archive[request]
    if is_cacheable(response):
      # Set all delays to zero:
      response.delays = None
      response.fix_delays()

def is_cacheable(response):
  # We use an array to handle the case where there are redundant headers. The
  # most restrictive caching header wins.
  cc_headers = []
  expires_headers = []
  for (name, value) in response.headers:
    if re.match("cache-control", name, re.IGNORECASE):
      cc_headers.append(value)
    if re.match("expires", name, re.IGNORECASE):
      expires_headers.append(value)

  # N.B. we consider undefined as cacheable.
  # WHEN LENGTH(resp_cache_control) = 0
  #   AND LENGTH(resp_expires) = 0
  #   THEN "undefined"
  if cc_headers == [] and expires_headers == []:
    return True

  # WHEN resp_cache_control CONTAINS "no-store"
  #   OR resp_cache_control CONTAINS "no-cache"
  #   OR resp_cache_control CONTAINS "max-age=0"
  #   OR resp_expires = "-1"
  #   THEN "non-cacheable"
  for cc_header in cc_headers:
    if (re.match("no-store", cc_header, re.IGNORECASE) or
        re.match("no-cache", cc_header, re.IGNORECASE) or
        re.match("max-age=0", cc_header, re.IGNORECASE)):
      return False

  for expires_header in expires_headers:
    if re.match("-1", expires_header, re.IGNORECASE):
      return False

  # ELSE "cacheable"
  return True

if __name__ == '__main__':
  option_parser = optparse.OptionParser(
      usage='%prog <directory containing wpr files>')

  options, args = option_parser.parse_args()

  if len(args) < 1:
    print 'args: %s' % args
    option_parser.error('Must specify a directory containing wpr files')

  for wpr in glob.iglob(args[0] + "/*.wpr"):
    archive = HttpArchive.Load(wpr)
    assume_perfect_cache(archive)
    output_file = re.sub('.wpr$', '.pc.har', wpr)
    archive.Persist(output_file)
