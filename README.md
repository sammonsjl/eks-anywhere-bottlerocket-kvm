# EKS Anywhere with Bottlerocket on KVM

Prebuilt pieces for running Amazon EKS Anywhere's Bare Metal provider with **Bottlerocket** nodes on KVM virtual machines, so a lab doesn't have to build anything:

| Release asset | What it is |
|---|---|
| `eksctl-anywhere-<tag>-linux-amd64.tar.gz` | EKS Anywhere v0.26.4's CLI, with the patch in `patches/` |
| `ghcr.io/sammonsjl/eks-anywhere-bottlerocket-kvm/cluster-controller:<tag>` | EKS Anywhere v0.26.4's own controller image, with its `manager` binary rebuilt from the patched source |
| `bundle-128-br.yaml`, `eksa-components-br.yaml` | EKS Anywhere's bundle 128 and controller manifest, pointing at that image. For `--bundles-override` |
| `bottlerocket-vmware-k8s-1-35-x86_64-v1.68.0.img.gz` | AWS's Bottlerocket `vmware-k8s-1.35` image from bundle 128, converted from OVA to a raw disk with no other change |
| `SHA256SUMS` | Hashes of all of the above |

> **AWS doesn't support any of this.** It's for learning how EKS Anywhere works, in a lab. Don't use it for anything that matters.

## Why it's needed

EKS Anywhere's Bare Metal provider refuses Bottlerocket on Kubernetes 1.29 and later, because AWS stopped publishing Bottlerocket bare metal images after 1.28. AWS does still publish Bottlerocket images for VMware, and the `vmware-k8s` image boots on KVM with a few settings, which the lab's Tinkerbell template writes.

The check runs in two places, the CLI and the controller, so both are rebuilt. The patch only removes the check. Nothing else in EKS Anywhere changes.

## How it's built

`.github/workflows/release.yml` runs when a tag is pushed. Everything it fetches from AWS is pinned by hash, and it fails if anything differs:

1. Clones aws/eks-anywhere at `v0.26.4`, checks the commit, applies `patches/`, and runs the Tinkerbell provider's tests
2. Builds the CLI and the controller manager, with the same version and key settings as AWS's release builds
3. Builds the controller image `FROM` AWS's image, by digest, replacing only `manager`
4. Writes the bundle override with `scripts/make-bundle.py`, which changes only the controller image, its digest, and the link to the controller manifest
5. Converts the OVA with `scripts/convert-image.sh`, and checks the raw disk's hash against the image the lab was tested with
6. Publishes the release

To make a new release, push a tag such as `v0.26.4-br.2`.

## Licence

Apache 2.0, the same as EKS Anywhere. See `LICENSE` and `NOTICE`. Bottlerocket is AWS's, under its own open source licences, and is redistributed unchanged.
