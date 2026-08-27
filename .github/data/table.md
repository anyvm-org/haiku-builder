

| Release | x86_64 |
|---------|---------|
| r1beta6 | ✅ (rsync,scp,nfs,sshfs,tar) |
| r1beta5 | ✅ (rsync,scp,nfs,sshfs,tar) |

How the images are built:

Each image is built automatically in the
[anyvm-org/haiku-builder](https://github.com/anyvm-org/haiku-builder)
repo's GitHub Actions: it downloads the official Haiku anyboot ISO from
a Haiku mirror, boots it in QEMU, runs the Haiku installer unattended,
enables ssh, pre-installs the packages listed in the conf, and exports
the installed disk as a compressed qcow2 image.

Upstream install media: the official Haiku release images (download
page: https://www.haiku-os.org/get-haiku/).
