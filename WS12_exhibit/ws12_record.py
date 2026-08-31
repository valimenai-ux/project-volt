"""WS12 — record access and citation primitives.

Every number that reaches the exhibit screen as a NUMBER OF RECORD passes
through `cite()`. `cite()` opens a results file on disk, resolves an
explicit key path, formats the value with a declared format spec, and
returns a citation object carrying the raw value, the displayed string,
the file, the path and the tier badge.

The app renders `s` and nothing else. `exhibit_verify.py` re-opens the
same file with its OWN resolver and its OWN formatter and asserts the
string matches verbatim. Nothing on any screen is transcribed by hand.

Path syntax is a LIST of keys, not a dotted string: the record contains
keys such as `V1_on_VOLT-SUB`, `cold_-10C` and `CdA_5.4` that contain
dots and hyphens, and a dotted string cannot address them unambiguously.
List indices are integers in the same list.
"""

import hashlib
import json
import os

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Tiers. RECORD = on disk in a results file. DERIVED = integrated live in
# the browser from a trace file that is itself on disk. SANDBOX = the
# visitor's own inputs through a declared closed-form model.
TIER_RECORD = "RECORD"
TIER_DERIVED = "DERIVED"
TIER_SANDBOX = "SANDBOX"

# BASELINE_v7_FREEZE.md R52: every verdict keeps the status it holds at
# freeze, labelled FROZEN-<status>. These are the ONLY strings permitted
# in a badge position anywhere in the exhibit.
ALLOWED_STATUS_BADGES = (
    "FROZEN-PROVISIONAL",
    "FROZEN-KILL",
    "FROZEN-RATIFIED",
    "NOT CONVERGED",
    "NOT CUT",
)

# A bare RATIFIED or PROVISIONAL in a badge position is a build failure,
# not a style preference (CLOSEOUT.md s0.2). These are the v6-era labels.
FORBIDDEN_BADGE_TOKENS = ("RATIFIED", "PROVISIONAL")

_FILE_CACHE = {}
_SHA_CACHE = {}


def repo_path(rel):
    return os.path.join(REPO_ROOT, rel)


def load_json(rel):
    """Load a results file by repo-relative path. Read-only, cached."""
    if rel not in _FILE_CACHE:
        with open(repo_path(rel), "r", encoding="utf-8") as fh:
            _FILE_CACHE[rel] = json.load(fh)
    return _FILE_CACHE[rel]


def sha256_of(rel):
    if rel not in _SHA_CACHE:
        h = hashlib.sha256()
        with open(repo_path(rel), "rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
        _SHA_CACHE[rel] = h.hexdigest()
    return _SHA_CACHE[rel]


class PathError(KeyError):
    pass


def resolve(obj, path, where=""):
    """Resolve a key path (list of str/int) against a loaded object."""
    cur = obj
    for i, key in enumerate(path):
        try:
            if isinstance(key, int):
                cur = cur[key]
            else:
                cur = cur[key]
        except (KeyError, IndexError, TypeError) as exc:
            sofar = " -> ".join(str(k) for k in path[: i + 1])
            raise PathError(
                "%s: cannot resolve %s (failed at %r)" % (where, sofar, key)
            ) from exc
    return cur


def path_display(path):
    return " → ".join(str(k) for k in path)


def fmt_value(value, spec, pre="", suf=""):
    """Format one value. `spec` is a plain Python format spec, or `str`."""
    if spec == "str":
        body = str(value)
    else:
        body = format(value, spec)
    return pre + body + suf


def cite(file_rel, path, spec, pre="", suf="", tier=TIER_RECORD, note=None):
    """The only way a number of record reaches a screen."""
    doc = load_json(file_rel)
    value = resolve(doc, path, where=file_rel)
    if spec != "str" and not isinstance(value, (int, float)):
        raise TypeError(
            "%s -> %s is %r, not a number" % (file_rel, path_display(path),
                                              type(value).__name__)
        )
    out = {
        "v": value,
        "s": fmt_value(value, spec, pre, suf),
        "file": file_rel,
        "path": list(path),
        "pathText": path_display(path),
        "fmt": spec,
        "pre": pre,
        "suf": suf,
        "tier": tier,
    }
    if note:
        out["note"] = note
    return out


def lit(value, spec, pre="", suf="", tier=TIER_DERIVED, note=None,
        source=None):
    """A DERIVED or SANDBOX number computed by this build from record
    inputs. It is NOT a number of record; it never claims a JSON path it
    does not have. `source` names what it was derived from."""
    out = {
        "v": value,
        "s": fmt_value(value, spec, pre, suf),
        "fmt": spec,
        "pre": pre,
        "suf": suf,
        "tier": tier,
    }
    if source:
        out["derivedFrom"] = source
    if note:
        out["note"] = note
    return out


def check_badge(text):
    """Raise if `text` is a promoted status in a badge position."""
    if text in ALLOWED_STATUS_BADGES:
        return text
    upper = str(text).upper()
    for token in FORBIDDEN_BADGE_TOKENS:
        if token in upper:
            raise ValueError(
                "promoted status in a badge position: %r contains %r. "
                "BASELINE_v7_FREEZE R52 permits only %s"
                % (text, token, ", ".join(ALLOWED_STATUS_BADGES))
            )
    return text


def status_badge(text):
    """A verdict badge. Must be one of v7's five labels, exactly."""
    if text not in ALLOWED_STATUS_BADGES:
        raise ValueError(
            "%r is not one of BASELINE_v7_FREEZE's status labels: %s"
            % (text, ", ".join(ALLOWED_STATUS_BADGES))
        )
    return text
