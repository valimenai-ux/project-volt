"""WS12 — determinism gate. Build twice, diff every artifact.

    ../.venv/bin/python3 check_determinism_ws12.py [--with-app]

Hashes every emitted artifact, re-runs `build_exhibit_data.py`, hashes
again, and asserts every file is byte-identical. With `--with-app` it
also runs `npm run build` twice and compares the emitted bundle.

Written to `determinism_check.txt`, the same pattern WS5 and WS11 use.
"""

import hashlib
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PUBLIC = os.path.join(HERE, "app", "public")
APP = os.path.join(HERE, "app")
PY = os.path.join(HERE, "..", ".venv", "bin", "python3")
WATCH = ("data", "traces", "maps")

# `verify_summary.json` is written by the VERIFIER, not the builder, and
# the builder clears the data directory. It is not a build artifact and is
# not part of this comparison.
SKIP = {"verify_summary.json"}


def snapshot(root, subdirs):
    out = {}
    for sub in subdirs:
        base = os.path.join(root, sub)
        if not os.path.isdir(base):
            continue
        for d, _, names in os.walk(base):
            for n in sorted(names):
                if n in SKIP:
                    continue
                p = os.path.join(d, n)
                h = hashlib.sha256()
                with open(p, "rb") as fh:
                    for chunk in iter(lambda: fh.read(1 << 20), b""):
                        h.update(chunk)
                out[os.path.relpath(p, root)] = (os.path.getsize(p),
                                                 h.hexdigest())
    return out


def compare(a, b, label, log):
    only_a = sorted(set(a) - set(b))
    only_b = sorted(set(b) - set(a))
    diff = sorted(k for k in set(a) & set(b) if a[k] != b[k])
    log.append("%-28s %5d files, %5d differing, %d only-before, "
               "%d only-after"
               % (label, len(set(a) | set(b)), len(diff), len(only_a),
                  len(only_b)))
    for k in only_a[:10]:
        log.append("    ONLY BEFORE  " + k)
    for k in only_b[:10]:
        log.append("    ONLY AFTER   " + k)
    for k in diff[:10]:
        log.append("    DIFFERS      %s  %s -> %s" % (k, a[k][1][:12],
                                                      b[k][1][:12]))
    return not (only_a or only_b or diff)


def main():
    with_app = "--with-app" in sys.argv
    log = ["WS12 DETERMINISM CHECK", "=" * 68]

    before = snapshot(PUBLIC, WATCH)
    log.append("pass 1 snapshot: %d artifacts" % len(before))
    r = subprocess.run([PY, os.path.join(HERE, "build_exhibit_data.py")],
                       cwd=HERE, capture_output=True, text=True)
    log.append("build_exhibit_data.py exit %d" % r.returncode)
    for line in r.stdout.strip().splitlines():
        log.append("    " + line)
    if r.returncode != 0:
        log.append(r.stderr.strip()[-2000:])
    after = snapshot(PUBLIC, WATCH)
    ok = compare(before, after, "data + traces + maps", log) \
        and r.returncode == 0

    if with_app:
        # Each build writes into a CLEAN dist. Building over an existing
        # one lets the platform's directory-copy leave empty " 2" siblings
        # beside `dist/traces`, which are cruft rather than output, and it
        # also makes the comparison a from-scratch one rather than an
        # overwrite.
        def fresh_build():
            shutil.rmtree(os.path.join(APP, "dist"), ignore_errors=True)
            return subprocess.run(["npm", "run", "build"], cwd=APP,
                                  capture_output=True, text=True)

        r1 = fresh_build()
        b1 = snapshot(APP, ("dist",))
        r2 = fresh_build()
        b2 = snapshot(APP, ("dist",))
        log.append("npm run build exits: %d, %d" % (r1.returncode,
                                                    r2.returncode))
        ok = compare(b1, b2, "app bundle", log) and ok \
            and r1.returncode == 0 and r2.returncode == 0

    log.append("=" * 68)
    log.append("RESULT: " + ("PASS - every artifact byte-identical"
                             if ok else "FAIL"))
    text = "\n".join(log) + "\n"
    with open(os.path.join(HERE, "determinism_check.txt"), "w",
              encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    print(text)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
