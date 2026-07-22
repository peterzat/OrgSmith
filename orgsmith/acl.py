"""ACL overlay: read-access ground truth derived from org structure.

Pure and deterministic: grants are a function of the charter's posture,
the manifest, and engagement teams. Never authored, never randomized;
re-running rewrites identical bytes. Mirrors emit-evals: requires the pure
stages, mutates no pipeline state. Orgs generated before this overlay
simply lack ledger/acl.json, and every consumer treats that as a visible
skip.
"""

from __future__ import annotations

import re

from .artifacts import (
    load_charter,
    load_engagements,
    load_foundation,
    load_manifest,
)
from .paths import OrgPaths
from .schemas import (
    AclGrant,
    AclLedger,
    DistributionList,
    DistributionListsLedger,
    write_model,
)
from .state import load_state, require_stages


def derive_distribution_lists(charter, foundation) -> DistributionListsLedger:
    """The internal mailing lists mail may address (M14). Deterministic: All
    Staff first, then one list per department, in charter order, capped at the
    recipe's count. Members are people employed AS OF the corpus end (matching
    acl's present-tense semantics). A pure function of charter + foundation, so
    it re-emits byte-identically and knob-off recipes derive an empty ledger."""
    mail = charter.doc_culture.mail
    n = mail.distribution_lists if mail is not None else 0
    end = charter.doc_culture.date_range[1]

    def employed(p) -> bool:
        return p.employment.start <= end and (
            p.employment.end is None or p.employment.end >= end
        )

    active = [p for p in foundation.people if employed(p)]
    candidates = [("All Staff", "all-staff", [p.id for p in active])]
    for dept in charter.headcount:  # charter order (first dept holds the CEO)
        members = [p.id for p in active if p.dept == dept]
        if members:
            # Sanitize to the DistributionList.id charset (^dl:[a-z0-9.-]+$):
            # collapse any run of out-of-charset chars (spaces, '&', '/', ...)
            # to a single hyphen so a dept like "R&D" yields a valid id.
            local = re.sub(r"[^a-z0-9.-]+", "-", dept.lower()).strip("-")
            candidates.append((f"{dept} Team", local, members))
    lists = [
        DistributionList(
            id=f"dl:{local}",
            name=name,
            address=f"{local}@{charter.domain}",
            members=members,
        )
        for name, local, members in candidates[:n]
    ]
    return DistributionListsLedger(slug=charter.slug, lists=lists)


def derive_acl(charter, foundation, engagements, manifest) -> AclLedger:
    """One grant per internal person, roster order, doc paths sorted.

    Grants are read access **as of the end of the corpus**, so a person who
    left mid-history holds none: their account is gone, and access is a
    present-tense property of the live share, not a record of what they could
    once see. `open` therefore means "everyone currently employed reads
    everything", not "everyone who ever worked here" (BACKLOG:
    acl-blind-to-departure, resolved 2026-07-16).

    A departed person stays a principal with an empty doc list rather than
    being dropped: ACL-01 requires principals to mirror the roster, and an
    empty expected set is a real visibility question ("does your system deny
    a departed employee?") that `score` grades by exact set match.

    Symmetry worth naming: joining is not scoped the same way. A current hire
    reads documents that predate them, because a real new joiner is handed the
    existing share. Only leaving revokes.

    open: every currently-employed person reads every manifest document.
    departmental: engagement documents are readable by that engagement's
    internal participants plus the CEO-equivalent; financial summaries by
    the CEO-equivalent plus the workbook's author; everything else
    (firm-level documents) by everyone. Employment scoping applies on top of
    all three.

    Misfiled noise (M15) follows its folder, not its content: a real share's
    ACL lives on directories, so a misfile is readable by the union of its
    destination folder's non-derived readers. Engagement A's letter misfiled
    into engagement B's folder is readable by B's team (and by everyone when
    it lands in an open folder) -- deliberately, as ground truth.
    """
    ceo = next(p for p in foundation.people if p.reports_to is None)
    eng_by_id = {e.id: e for e in engagements.engagements}
    readable: dict[str, list[str]] = {p.id: [] for p in foundation.people}
    # `end is None` is the roster's own encoding of "still employed"
    # (EmploymentSpan). Every document keeps at least one reader under every
    # posture because the CEO-equivalent cannot depart: churn only retires
    # seats that manage nobody, so ACL-02 stays satisfied by construction.
    current = {p.id for p in foundation.people if p.employment.end is None}

    def doc_readers(entry) -> set[str]:
        if charter.acl_posture == "open":
            return set(readable)
        if entry.engagement is not None:
            eng = eng_by_id[entry.engagement]
            return set(eng.internal_participants) | {ceo.id}
        if entry.genre == "financial_summary":
            return {ceo.id} | set(entry.authors)
        return set(readable)

    folder_readers: dict[str, set[str]] = {}
    for entry in manifest:
        if entry.noise_kind == "misfile" or "/" not in entry.path:
            continue
        folder = entry.path.rsplit("/", 1)[0]
        folder_readers.setdefault(folder, set()).update(doc_readers(entry))

    for entry in manifest:
        folder = entry.path.rsplit("/", 1)[0] if "/" in entry.path else ""
        if entry.noise_kind == "misfile" and folder in folder_readers:
            readers = folder_readers[folder]
        else:
            readers = doc_readers(entry)
        # `current` is roster-derived, so this also drops externals, which
        # carry no grants.
        for pid in readers & current:
            readable[pid].append(entry.path)

    grants = [
        AclGrant(person=p.id, docs=sorted(readable[p.id]))
        for p in foundation.people
    ]
    return AclLedger(
        slug=charter.slug, posture=charter.acl_posture, grants=grants
    )


def render_permissions(charter, foundation, acl: AclLedger) -> str:
    """Human-readable twin of acl.json, rendered into the share root."""
    people = {p.id: p for p in foundation.people}
    lines = [
        "# PERMISSIONS",
        "",
        f"Read-access ground truth for {charter.name} ({acl.slug}); "
        f"posture: {acl.posture}.",
        f"Derived from ledger/acl.json; regenerate with `python -m "
        f"orgsmith acl {acl.slug}`.",
    ]
    for grant in acl.grants:
        person = people[grant.person]
        lines += ["", f"## {person.name} ({person.title})", ""]
        lines += [f"- {doc}" for doc in grant.docs]
    return "\n".join(lines) + "\n"


def run_acl(paths: OrgPaths) -> int:
    state = load_state(paths)
    require_stages(state, "charter", "foundation", "fabric", "docplan")

    charter = load_charter(paths)
    foundation = load_foundation(paths)
    acl = derive_acl(
        charter, foundation, load_engagements(paths), load_manifest(paths)
    )
    write_model(paths.acl_json, acl)
    paths.share_dir.mkdir(parents=True, exist_ok=True)
    paths.permissions_md.write_text(
        render_permissions(charter, foundation, acl), encoding="utf-8"
    )
    # M14: the distribution-list ledger, derived beside acl.json. Written only
    # when the recipe declares them, so knob-off orgs gain no artifact and
    # DL-01 grandfathers by charter.
    dls = derive_distribution_lists(charter, foundation)
    dl_note = ""
    if dls.lists:
        write_model(paths.distribution_lists_json, dls)
        dl_note = f", {len(dls.lists)} distribution lists"
    print(
        f"acl: {len(acl.grants)} grants ({acl.posture}) -> "
        f"{paths.acl_json} + {paths.permissions_md}{dl_note}"
    )
    return 0
