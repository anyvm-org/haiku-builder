# In-guest install script for haiku r1beta5 (VM_INSTALL_SCRIPT; piped into
# the guest sh by build.py with ANYVM_PKGS prepended; runs under set -e).
# Lives in conf/ (not hooks/) because it is release-scoped: the pinned
# .hpkg versions below are beta5-era, so a future r1beta6 conf must NOT
# reuse it. hooks/ is for run_hook() files that fire on every build.
#
# Upstream retired the haikuports r1beta5 repo in TWO stages, and this
# script has now had to absorb both:
#
#   2026-07  eu.hpkg.haiku-os.org/haikuports/r1beta5 began 303ing to
#            master, and master's glib2 requires haiku >= r1~beta6, which
#            is unsatisfiable on a beta5 base. sshfs_fuse + glib2 moved to
#            pinned .hpkg files here; every other package still resolved
#            from the master repo, so a repo pass remained.
#
#   2026-08  that same path now 303s to an EMPTY directory listing (HTTP
#            200, zero bytes), so the refresh itself fails: the guest logs
#            'Refreshing repository "HaikuPorts" failed' and 'Validating
#            checksum for HaikuPorts...: I/O error', after which even a
#            plain `pkgman install rsync` reports 'Name not found'.
#            Re-probed 2026-08-17 to confirm it is not a mirror glitch:
#            haikuports-repository.cdn.haiku-os.org/r1beta5/x86_64/current
#            /repo is 404, and only master/ still exists.
#
# So there is no working repo pass left for a beta5 base, and EVERY
# package now comes from the pinned snapshot below. mirrors.tnonline.net
# keeps a 2024-11 haikuports snapshot (18050 .hpkg files), which is
# beta5-era and therefore solvable against this base.
#
# NOT used, deliberately: that snapshot also serves a complete repo index
# (repo, repo.info, repo.sha256), so it looks like it could just replace
# the dead repo via add-repo. Its repo.info declares
# 'baseurl https://eu.hpkg.haiku-os.org/haikuports/master/x86_64/current'
# and the master identifier, i.e. the index is a 2024-11 snapshot while
# package fetches would go to today's master -- versions master no longer
# carries. Pinned files avoid that mismatch entirely.
PINNED_BASE="https://mirrors.tnonline.net/haiku/haikuports/x86_64/current/packages"
#
# lz4, xxhash and zstd are NOT in VM_PRE_INSTALL_PKGS -- they are rsync's
# dependencies, pinned because nothing can supply them any more once the
# repo is gone. rsync-3.2.7's own HaikuPorts recipe
# (haikuports/net-misc/rsync/rsync-3.2.7.recipe, read 2026-08-17) declares
# exactly five:
#     haiku  lib:libcrypto  lib:liblz4  lib:libxxhash  lib:libz  lib:libzstd
# libcrypto and libz come from the beta5 base -- the solver never asked for
# them. The three compression libs do not; two were proven missing by real
# builds, one per run because pkgman reports only the first problem:
#     nothing provides lib:liblz4>=1.9.4 needed by rsync-3.2.7-2
#     nothing provides lib:libxxhash>=0.8.1~git needed by rsync-3.2.7-2
# libzstd is pinned on the strength of the recipe rather than waiting for a
# third 14-minute build to name it. Deliberately NOT pinning libz/libcrypto
# on top of the base copies, which would risk a provider conflict.
PINNED_HPKGS="glib2-2.78.0-2-x86_64.hpkg
sshfs_fuse-2.10-1-x86_64.hpkg
lz4-1.9.4-1-x86_64.hpkg
xxhash-0.8.1~git-2-x86_64.hpkg
zstd-1.5.6-1-x86_64.hpkg
rsync-3.2.7-2-x86_64.hpkg
tree-1.8.0-1-x86_64.hpkg
cpio-2.14-2-x86_64.hpkg"

# Coverage assert. With no repo left to fall back on, a package named in
# VM_PRE_INSTALL_PKGS but missing from PINNED_HPKGS would simply never be
# installed, and the build would go green shipping an image without it --
# exactly the silent hole build.py's install-step check exists to stop.
# Fail loudly instead, naming the package and the fix.
for p in $ANYVM_PKGS; do
    hit=""
    for f in $PINNED_HPKGS; do
        case "$f" in
            "$p"-*) hit=yes ;;
        esac
    done
    if [ -z "$hit" ]; then
        echo "ERROR: '$p' is in VM_PRE_INSTALL_PKGS but has no pinned .hpkg." >&2
        echo "       The haikuports r1beta5 repo is gone, so every package" >&2
        echo "       must be listed in PINNED_HPKGS in this script." >&2
        exit 1
    fi
done

# Idempotent, because build.py retries the whole install step once after a
# reboot. Re-installing an already-active package aborts the transaction
# with 'Failed to change the package activation in packagefs: Name in
# use', which is what made attempt 2 fail differently from attempt 1 and
# hid the real cause. An activated package IS its file in /system/packages.
cd /tmp
TO_INSTALL=""
for f in $PINNED_HPKGS; do
    if [ -e "/system/packages/$f" ]; then
        echo "already active, skipping: $f"
        continue
    fi
    if [ ! -s "/tmp/$f" ]; then
        wget -q "$PINNED_BASE/$f" || {
            echo "ERROR: cannot fetch $PINNED_BASE/$f" >&2
            exit 1
        }
    fi
    TO_INSTALL="$TO_INSTALL /tmp/$f"
done

if [ -n "$TO_INSTALL" ]; then
    pkgman install -y $TO_INSTALL
else
    echo "all pinned packages are already active"
fi
