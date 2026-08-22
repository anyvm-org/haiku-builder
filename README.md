

[![Build](https://github.com/anyvm-org/haiku-builder/actions/workflows/build.yml/badge.svg)](https://github.com/anyvm-org/haiku-builder/actions/workflows/build.yml)

Latest: v2.0.2


The image builder for `haiku`


All the supported releases are here:



| Release | x86_64 |
|---------|---------|
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




How to build:

1. Use the [manual.yml](.github/workflows/manual.yml) to build manually.
   
    Run the workflow manually, you will get a view-only webconsole from the output of the workflow, just open the link in your web browser.
   
    You will also get an interactive VNC connection port from the output, you can connect to the vm by any vnc client.

2. Run the builder locally on your Ubuntu machine.

    Just clone the repo. and run:
    ```bash
    python3 build.py conf/haiku-r1beta5.conf
    ```
   
