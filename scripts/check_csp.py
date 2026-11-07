#!/usr/bin/env python3
"""Check, or fix, the script fingerprint in index.html's security policy.

index.html carries a Content-Security-Policy that lets only its own inline
script run. The policy names that script by its SHA-256 hash, so any edit to
the script changes the hash, and the browser then refuses to run it: the page
loads but nothing works.

    python3 scripts/check_csp.py          check; exits 1 if the policy is stale
    python3 scripts/check_csp.py --fix    write the current hash into the policy

Uses only the Python standard library (3.8 or later).
"""
import base64
import hashlib
import html
import re
import sys
from pathlib import Path

PAGE = Path(__file__).resolve().parent.parent / "index.html"

# Used by --fix only when the page has no policy at all.
COMMENT = (
    "<!-- Security policy: only the script at the bottom of this page may run, and the\n"
    "     page can't load or send anything over the network. The sha256 value is a\n"
    "     fingerprint of that script. If you change the script, update it or the page\n"
    "     stops working: run  python3 scripts/check_csp.py --fix  -->\n"
)
DEFAULT_POLICY = (
    "default-src 'none'; script-src {hashes}; style-src 'unsafe-inline'; "
    "img-src data:; base-uri 'none'"
)

META_RE = re.compile(r"<meta\b[^>]*>", re.I)
SCRIPT_RE = re.compile(r"<script\b([^>]*)>(.*?)</script\s*>", re.I | re.S)
HASH_RE = re.compile(r"'sha256-[A-Za-z0-9+/]+={0,2}'")

# Script types the browser runs, so the policy has to allow them. Anything
# else (such as application/json) is a data block and is never run.
RUN_TYPES = {
    "", "module", "importmap",
    "application/ecmascript", "application/javascript", "application/x-ecmascript",
    "application/x-javascript", "text/ecmascript", "text/javascript",
    "text/javascript1.0", "text/javascript1.1", "text/javascript1.2",
    "text/javascript1.3", "text/javascript1.4", "text/javascript1.5",
    "text/jscript", "text/livescript", "text/x-ecmascript", "text/x-javascript",
}


def find_attr(tag, name):
    """Return (value, start, end, quote) for attribute `name` in `tag`, or None."""
    m = re.search(
        r"(?:^|\s){}\s*=\s*(?:\"([^\"]*)\"|'([^']*)'|([^\s\"'>]+))".format(name), tag, re.I
    )
    if not m:
        return None
    for group, quote in ((1, '"'), (2, "'"), (3, "")):
        if m.group(group) is not None:
            return m.group(group), m.start(group), m.end(group), quote
    return None


def attr(tag, name):
    found = find_attr(tag, name)
    return None if found is None else found[0]


def line_of(text, pos):
    return text.count("\n", 0, pos) + 1


def sha256_source(script):
    # Browsers hash the script text after the HTML parser turns CRLF and CR
    # line endings into LF, encoded as UTF-8.
    script = script.replace("\r\n", "\n").replace("\r", "\n")
    digest = hashlib.sha256(script.encode("utf-8")).digest()
    return "'sha256-" + base64.b64encode(digest).decode("ascii") + "'"


def inline_scripts(text):
    """Return ([(line, hash)] for each inline script the browser runs, [problems])."""
    found, problems = [], []
    for m in SCRIPT_RE.finditer(text):
        attrs, body = m.group(1), m.group(2)
        kind = (attr(attrs, "type") or "").strip().lower()
        if kind not in RUN_TYPES:
            continue
        line = line_of(text, m.start())
        if attr(attrs, "src") is not None:
            problems.append(
                "line {}: <script src=...> loads code from a file or website, "
                "which this policy blocks. Put the code inline instead.".format(line)
            )
            continue
        found.append((line, sha256_source(body)))
    return found, problems


def csp_tags(text):
    """Return [(tag start, content value, content start, content end, quote)]."""
    tags = []
    for m in META_RE.finditer(text):
        tag = m.group(0)
        if (attr(tag, "http-equiv") or "").strip().lower() != "content-security-policy":
            continue
        content = find_attr(tag, "content")
        if content is None:
            tags.append((m.start(), "", m.end(), m.end(), None))
        else:
            value, start, end, quote = content
            tags.append((m.start(), value, m.start() + start, m.start() + end, quote))
    return tags


def directives(policy):
    """Return {name: (index of the part, [sources])}, first occurrence wins."""
    found = {}
    for i, part in enumerate(policy.split(";")):
        words = part.split()
        if words and words[0].lower() not in found:
            found[words[0].lower()] = (i, words[1:])
    return found


def main(argv):
    fix = "--fix" in argv[1:]
    with open(PAGE, encoding="utf-8", newline="") as f:
        text = f.read()

    scripts, problems = inline_scripts(text)
    wanted = list(dict.fromkeys(h for _, h in scripts))
    tags = csp_tags(text)

    if not tags:
        if not fix:
            print("index.html has no Content-Security-Policy <meta> tag.")
            print("Run  python3 scripts/check_csp.py --fix  to add the standard one.")
            return 1
        tag = '<meta http-equiv="Content-Security-Policy" content="{}">\n'.format(
            DEFAULT_POLICY.format(hashes=" ".join(wanted))
        )
        anchor = re.search(r"<meta\s+charset[^>]*>[ \t]*\n?", text, re.I) or re.search(
            r"<head\b[^>]*>[ \t]*\n?", text, re.I
        )
        at = anchor.end() if anchor else 0
        text = text[:at] + COMMENT + tag + text[at:]
        with open(PAGE, "w", encoding="utf-8", newline="") as f:
            f.write(text)
        print("Added the standard security policy to index.html.")
        return 0

    if len(tags) > 1:
        problems.append(
            "index.html has {} Content-Security-Policy tags. Keep one: browsers "
            "enforce all of them, so a stale one still blocks the script.".format(len(tags))
        )
    tag_start, raw_policy, value_start, value_end, quote = tags[0]
    first_script = SCRIPT_RE.search(text)
    if first_script and first_script.start() < tag_start:
        problems.append(
            "line {}: the Content-Security-Policy tag must come before every <script>. "
            "Move it to the top of <head>.".format(line_of(text, tag_start))
        )

    policy = html.unescape(raw_policy)
    parsed = directives(policy)
    name = next((n for n in ("script-src-elem", "script-src", "default-src") if n in parsed), None)
    if name is None:
        problems.append("the policy has no script-src directive, so it doesn't restrict scripts.")
        allowed = []
    else:
        allowed = [s for s in parsed[name][1] if HASH_RE.fullmatch(s)]
    missing = [(line, h) for line, h in scripts if h not in allowed]
    stale = [h for h in allowed if h not in wanted]

    if fix and name is not None and quote is not None and (missing or stale):
        index, sources = parsed[name]
        kept = [s for s in sources if not HASH_RE.fullmatch(s)]
        parts = policy.split(";")
        lead = re.match(r"\s*", parts[index]).group(0)
        parts[index] = lead + " ".join([name] + kept + wanted)
        new_policy = ";".join(parts)
        escaped = html.escape(new_policy, quote=True)
        if quote == '"':
            escaped = escaped.replace("&#x27;", "'")
        text = text[:value_start] + escaped + text[value_end:]
        with open(PAGE, "w", encoding="utf-8", newline="") as f:
            f.write(text)
        print("Updated the script fingerprint in index.html's security policy.")
        missing, stale = [], []

    for line, h in missing:
        problems.append(
            "line {}: this script isn't allowed by the security policy, so browsers "
            "won't run it and the page won't work. Its fingerprint is {}.".format(line, h)
        )
    for h in stale:
        problems.append("the policy allows {}, which matches no script on the page.".format(h))

    if problems:
        print("index.html security policy check failed:")
        for p in problems:
            print("  - " + p)
        if missing or stale:
            print("Fix: run  python3 scripts/check_csp.py --fix  and commit the result.")
        return 1

    print(
        "index.html security policy OK: {} inline script{} allowed by fingerprint.".format(
            len(scripts), "" if len(scripts) == 1 else "s"
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
