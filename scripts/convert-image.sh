#!/usr/bin/env bash
# Turn AWS's Bottlerocket vmware-k8s OVA into the gzipped raw disk Tinkerbell
# writes to a server. The disk's contents are not changed: the raw image must
# hash to RAW_SHA256, the hash of the image the KVM lab was tested with.
#
# usage: OVA_URL=... OVA_SHA256=... RAW_SHA256=... convert-image.sh OUT.img.gz
set -euo pipefail
out=$1
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

curl -fsSL --retry 3 -o "$work/image.ova" "$OVA_URL"
echo "$OVA_SHA256  $work/image.ova" | sha256sum -c -

# An OVA is a tar file: a description, a manifest and one VMDK disk.
tar -xf "$work/image.ova" -C "$work" --wildcards '*.vmdk'
rm "$work/image.ova"
qemu-img convert -O raw "$work"/*.vmdk "$work/disk.raw"
echo "$RAW_SHA256  $work/disk.raw" | sha256sum -c -

# -n leaves out the file's name and time, so the same disk gives the same file.
gzip -n -c "$work/disk.raw" > "$out"
