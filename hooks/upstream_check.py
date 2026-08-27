#!/usr/bin/env python3
# Print the current stable Haiku release tag, e.g. "r1beta5". Empty output
# means "nothing detected" and is not an error; a non-zero exit means
# detection itself is broken (network error, HTTP error, or a page that no
# longer matches the expected shape) and must be reported by the caller,
# never swallowed. A failure must NEVER print a plausible-but-wrong
# version -- the version is only printed after every step below has
# succeeded.
#
# Source of truth: https://www.haiku-os.org/get-haiku/
#
# conf/haiku-*.conf downloads its ISO from a third-party mirror
# (mirrors.tnonline.net) whose directory listing is not an authoritative
# upstream source (any mirror can lag or vanish), so this hook instead
# uses the project's OWN canonical "get the current release" URL, the
# same way a human visiting haiku-os.org would land on the current
# release page.
#
# Fetched and confirmed by hand (2026-07-26) with `curl -sSL -D -`:
#   GET https://www.haiku-os.org/get-haiku/  ->  HTTP/2 302
#   location: /get-haiku/r1beta5/
#   (the target then answers HTTP/2 200 for /get-haiku/r1beta5/)
# Re-run 2026-08-25 after the R1/beta6 announcement: the hook printed
# "r1beta6", i.e. the redirect had already moved on, which is the whole
# point of reading the pointer rather than a mirror listing.
# This Location header is the release tag in exactly the form
# conf/haiku-r1beta6.conf uses for VM_RELEASE ("r1beta6"). The page itself
# (https://www.haiku-os.org/get-haiku/release-notes/) also canonicalizes
# to the same release URL and carries no other release tag in its body, so
# there is no separate historical-version list to scan on this site --
# the redirect target IS the single newest version, by construction of
# the site itself (it is Haiku's own "get the latest release" pointer).
#
# stdlib only (urllib.request, re, sys, os) -- no external dependencies.

import os
import re
import sys
import urllib.request

URL = "https://www.haiku-os.org/get-haiku/"
TIMEOUT = 60
USER_AGENT = "anyvm-org-upstream-watcher/1.0"

# The redirect target is "/get-haiku/<tag>/"; the tag is always "r1..."
# (r1alpha1..r1alpha4, r1beta1..r1beta6 at fetch time), matching the exact
# string conf/*.conf uses for VM_RELEASE.
PATTERN = re.compile(r'^/get-haiku/(r1[\w.]*)/$')


def resolve_natural_key():
    """Return the engine's own natural_key, or fail loudly.

    watch.yml clones base-builder INTO the builder repo root, so at
    detection time it sits at "base-builder/" (relative to this hook's
    cwd, the builder repo root). A local checkout instead has it as a
    sibling, "../base-builder". Try both, in that order.

    There is deliberately NO local fallback copy. Ordering must be the
    single rule the engine uses -- a per-hook duplicate would have to be
    kept in sync by hand across every builder and would drift silently,
    and a hook that ranks versions differently from watch.py is worse
    than one that refuses to run. Both real contexts (CI and a local
    sibling checkout) always provide base-builder, so an ImportError here
    means the environment is wrong: report it as broken detection rather
    than guessing an order.
    """
    for candidate in ("base-builder", os.path.join("..", "base-builder")):
        if not os.path.isdir(candidate):
            continue
        path = os.path.abspath(candidate)
        if path not in sys.path:
            sys.path.insert(0, path)
        try:
            import gendata
            return gendata.natural_key
        except ImportError:
            continue
    raise ImportError(
        "base-builder/gendata.py not importable from %s; expected it at "
        "./base-builder (CI) or ../base-builder (local checkout)"
        % os.getcwd())


class _NoRedirect(urllib.request.HTTPErrorProcessor):
    """Return the raw 30x response instead of following it, so the
    Location header itself (the release tag) can be read."""

    def http_response(self, request, response):
        return response

    https_response = http_response


def fetch_redirect_target(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    opener = urllib.request.build_opener(_NoRedirect)
    with opener.open(req, timeout=TIMEOUT) as resp:
        if resp.status not in (301, 302, 303, 307, 308):
            raise ValueError("expected a redirect (30x) from %s, got "
                             "HTTP %d" % (url, resp.status))
        location = resp.headers.get("Location")
        if not location:
            raise ValueError("redirect response from %s has no Location "
                             "header" % url)
        return location


def main():
    try:
        key = resolve_natural_key()
    except ImportError as e:
        sys.stderr.write("upstream_check: %s\n" % e)
        return 1
    try:
        location = fetch_redirect_target(URL)
    except Exception as e:
        sys.stderr.write("upstream_check: fetch of %s failed: %s\n"
                         % (URL, e))
        return 1
    versions = PATTERN.findall(location)
    if not versions:
        sys.stderr.write("upstream_check: redirect target %r from %s does "
                         "not look like a release tag; page shape may "
                         "have changed\n" % (location, URL))
        return 1
    newest = sorted(set(versions), key=key)[-1]
    print(newest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
