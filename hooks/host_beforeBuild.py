# Pick a Haiku mirror that is actually answering, before the ISO download.
#
# Haiku publishes no first-party download host: www.haiku-os.org/get-haiku
# lists only third-party mirrors, so "the official URL" does not exist and a
# conf can only ever name one of several equals. Hardcoding one is what broke
# the v2.0.3 build -- mirrors.tnonline.net started returning 502 and the
# build died two seconds in, on a release where nothing about Haiku had
# changed. Probed 2026-08-22, the same five mirrors the download page lists:
# osuosl 206, aarnet 206 (byte-identical Content-Length), rit unreachable,
# truenetwork 404, tnonline 502. Two of five.
#
# So try them in order and take the first that answers, exactly as
# freebsd-builder chooses between download.freebsd.org and archive.
# VM_ISO_LINK from the conf goes first: whatever the conf names stays the
# preferred source, and this hook only moves off it when it is down.
import os
import urllib.request
import urllib.error

_RELEASE = os.environ.get("VM_RELEASE", "r1beta6")
_ISO = "haiku-%s-x86_64-anyboot.iso" % _RELEASE

# Mirror roots, each joined with the release and the iso name. Order is the
# probe order; keep the conf's own link ahead of all of them.
_MIRRORS = [
    "https://ftp.osuosl.org/pub/haiku/%s/%s",
    "https://mirror.aarnet.edu.au/pub/haiku/%s/%s",
    "https://mirrors.rit.edu/haiku/%s/%s",
    "https://mirrors.tnonline.net/haiku/haiku-release/%s/%s",
]


def _url_ok(url):
    """True if the URL serves bytes. A 1-byte ranged GET, so this costs
    nothing even for a 1.4 GB ISO. A transient error is retried twice before
    the mirror is written off -- one blip should not push us off a mirror
    that has the file."""
    for _attempt in range(3):
        req = urllib.request.Request(url, headers={"Range": "bytes=0-0"})
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return resp.status < 400
        except urllib.error.HTTPError as exc:
            if exc.code in (404, 403, 410):
                return False
        except Exception:
            pass
    return False


candidates = []
_conf_link = os.environ.get("VM_ISO_LINK", "").strip()
if _conf_link:
    candidates.append(_conf_link)
for _m in _MIRRORS:
    _u = _m % (_RELEASE, _ISO)
    if _u not in candidates:
        candidates.append(_u)

chosen = None
for _u in candidates:
    log("Probing Haiku mirror: %s" % _u)
    if _url_ok(_u):
        chosen = _u
        break

if chosen is None:
    # Leave VM_ISO_LINK as it is: download() then fails with the real error
    # from the real server instead of this hook inventing one.
    log("WARNING: no Haiku mirror answered; keeping %s" % _conf_link)
else:
    if chosen != _conf_link:
        log("Haiku mirror %s is not answering; using %s" % (_conf_link, chosen))
    os.environ["VM_ISO_LINK"] = chosen
    globals()["VM_ISO_LINK"] = chosen
