#!/usr/bin/env python3
"""Write the bundle override and controller manifest for the patched controller.

Takes EKS Anywhere's own bundle and eksa-components.yaml and changes only:
  - the cluster controller image, and its digest, in both
  - the bundle's link to eksa-components.yaml, so it points at the edited copy

Text replacement rather than a YAML round trip, so everything else stays
byte-for-byte as AWS published it. Each replacement checks how many places it
changed, and fails if AWS's files don't look as expected.

usage: make-bundle.py BUNDLE COMPONENTS OUT_DIR --image REF --digest SHA256 --components-url URL
"""
import argparse
import pathlib

OLD_IMAGE = "public.ecr.aws/eks-anywhere/cluster-controller:v0.26.4-eks-a-128"
OLD_DIGEST = "sha256:b9df8e8fc3fe5decb2e4e0a7e9ce341e9a699ba4e8fec717d2667c60eee70ff5"
OLD_COMPONENTS = (
    "https://anywhere-assets.eks.amazonaws.com/releases/bundles/128/artifacts/"
    "eks-anywhere/manifests/cluster-controller/v0.26.4/eksa-components.yaml"
)


def replace(text, old, new, expected, what):
    n = text.count(old)
    if n != expected:
        raise SystemExit(f"{what}: expected {expected} occurrences of {old!r}, found {n}")
    return text.replace(old, new)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("bundle")
    p.add_argument("components")
    p.add_argument("out_dir")
    p.add_argument("--image", required=True)
    p.add_argument("--digest", required=True)
    p.add_argument("--components-url", required=True)
    a = p.parse_args()
    out = pathlib.Path(a.out_dir)

    # One controller per Kubernetes version the bundle covers.
    b = pathlib.Path(a.bundle).read_text()
    b = replace(b, OLD_IMAGE, a.image, 7, "bundle image")
    b = replace(b, OLD_DIGEST, a.digest, 7, "bundle digest")
    b = replace(b, OLD_COMPONENTS, a.components_url, 7, "bundle components")
    (out / "bundle-128-br.yaml").write_text(b)

    c = pathlib.Path(a.components).read_text()
    c = replace(c, f"image: {OLD_IMAGE}\n", f"image: {a.image}\n", 1, "components image")
    (out / "eksa-components-br.yaml").write_text(c)


if __name__ == "__main__":
    main()
