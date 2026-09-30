# Notice

Independent security research on a consumer product the author purchased. Not affiliated
with, endorsed by, or sponsored by Quadzilla, Cummins, Chrysler/Stellantis or Bosch. All
product names and marks belong to their owners.

## What is and is not in this repository

| Included | Not included |
|---|---|
| Original tools, tests and written analysis (MIT, see LICENSE) | Vendor installers, firmware images, libraries, APKs, `.qz`/`.Smt` files |
| Decompiler output and extracted metadata, for analysis and protocol documentation | Vendor documentation |
| Vehicle profile JSON served publicly by the vendor's update server | Any credential, VIN or personal data |

`.gitignore` keeps vendor binaries out of the tree. The 8-byte password/key pair that appears
in the docs and test vectors is the static value that ships in the vendor's public installer.

## Responsible use

The work is static analysis of an installer, an Android app and a firmware image the author
obtained legitimately, plus the vendor's publicly served profile JSON. Device interaction is
limited to the read-only USB queries in `tools/quadzilla_tool.py`. No modified firmware has
been flashed to a device (see "Not tested" in docs/SECURITY_ASSESSMENT.md). If you are the
rights holder and want something removed, open an issue.

Changing fuel or timing on a diesel can destroy an engine and may be illegal for road use in
your jurisdiction. Nothing here is a tuning guide.
