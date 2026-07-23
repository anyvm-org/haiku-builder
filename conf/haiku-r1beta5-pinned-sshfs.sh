# In-guest install script for haiku r1beta5 (VM_INSTALL_SCRIPT; piped into
# the guest sh by build.py with ANYVM_PKGS prepended; runs under set -e).
# Lives in conf/ (not hooks/) because it is release-scoped: the pinned
# .hpkg versions below are beta5-era, so a future r1beta6 conf must NOT
# reuse it. hooks/ is for run_hook() files that fire on every build.
#
# Upstream retired the haikuports r1beta5 branch repo (2026-07: the
# eu.hpkg.haiku-os.org/haikuports/r1beta5 URL 303s to master), so the
# master repo's glib2 requires haiku>=r1~beta6 and `pkgman install
# sshfs_fuse` is unsolvable on a beta5 base. Install sshfs_fuse and its
# ONLY missing dependency glib2 from pinned beta5-era .hpkg files
# instead (mirrors.tnonline.net keeps a 2024-11 haikuports snapshot;
# the two files are a complete closure on the beta5 base -- verified
# 2026-07-23 in a throwaway boot: uninstall both, local-file install,
# userlandfs sshfs mount all green). The remaining packages still
# resolve fine from the live master repo.
PINNED_BASE="https://mirrors.tnonline.net/haiku/haikuports/x86_64/current/packages"
PINNED_HPKGS="glib2-2.78.0-2-x86_64.hpkg sshfs_fuse-2.10-1-x86_64.hpkg"

cd /tmp
for f in $PINNED_HPKGS; do
    wget -q "$PINNED_BASE/$f"
done
pkgman install -y $(for f in $PINNED_HPKGS; do printf '/tmp/%s ' "$f"; done)

# Repo pass for the rest; sshfs_fuse is already installed above, so strip
# it from the list (leaving it in would make the solver re-hit the broken
# glib2>=2.88 path in the master repo).
REPO_PKGS=""
for p in $ANYVM_PKGS; do
    [ "$p" = "sshfs_fuse" ] || REPO_PKGS="$REPO_PKGS $p"
done
pkgman install -y $REPO_PKGS
