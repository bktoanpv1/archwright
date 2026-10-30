"""doclint: kiểm hình thức tài liệu theo đề xuất type/form.

Đặc tả: docs/research/doc-standards.md §6, các form ở docs/research/forms/.
Bản nhỏ nhất: chỉ kiểm hình thức (frontmatter, mục bắt buộc, liên kết, con số có nguồn),
không kiểm nội dung đúng hay sai.

Dùng:
    python kit/core/tools/doclint.py docs/ [--config doclint.toml] [--root .]

Phán quyết theo quy ước của verify.py:
    PASS (exit 0)    không có lỗi; cảnh báo không làm FAIL
    FAIL (exit 1)    có ít nhất một lỗi
    BLOCKED (exit 2) không có tài liệu nào để kiểm, cấu hình hỏng, hoặc có tài liệu không đọc
                     được metadata (ví dụ khung tên bản vẽ) mà không có lỗi nào khác
"""

from __future__ import annotations

import argparse
import re
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

TYPES = {"description", "plan", "policy", "procedure", "report", "request", "specification", "record"}
ORIGINS = {"authored", "generated", "external"}
DEFAULT_STATUS = {"draft", "reviewed", "approved", "superseded"}
AGENT_ROLES = {"builder", "reviewer", "verifier", "curator", "planner"}
FOREVER = {"", "never", "none", "vô thời hạn", "không hạn"}
EVERYTHING = {"all", "*", "tất cả", "mọi"}

# form của core: trường bắt buộc thêm và tập giá trị status (None = form không dùng status)
CORE_FORMS: dict[str, dict] = {
    "approval": {"fields": ["gate", "subject", "verdict", "approver", "date", "origin"], "status": None},
    "baseline": {"fields": ["gate", "date", "origin"], "status": {"proposed", "frozen", "superseded"}},
    "deviation": {
        "fields": ["waives", "scope", "applies_to", "expires"],
        "status": {"requested", "granted", "refused", "expired", "closed"},
    },
    "change-request": {"fields": [], "status": DEFAULT_STATUS},
    "known-failure": {"fields": [], "status": DEFAULT_STATUS},
    "adr": {"fields": [], "status": DEFAULT_STATUS},
    "design-note": {"fields": [], "status": DEFAULT_STATUS},
    "howto": {"fields": [], "status": DEFAULT_STATUS},
    "verify-report": {"fields": [], "status": DEFAULT_STATUS},
    "review-report": {"fields": [], "status": DEFAULT_STATUS},
    "rules": {"fields": [], "status": DEFAULT_STATUS},
    "register": {"fields": [], "status": DEFAULT_STATUS},
}
VERDICTS = {"approved", "approved-with-conditions", "rejected", "deferred"}

UNIT_RE = re.compile(
    r"(?<![\w.])\d+(?:[.,]\d+)?\s?(?:mA|µA|uA|nA|mV|kV|V|ms|µs|us|GHz|MHz|kHz|Hz|mm|cm|µm|°C|KB|kB|MB|GB|mW|W|Ω|dB)(?![\w])"
)
LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)\)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")


@dataclass
class Finding:
    path: str
    level: str  # "error" | "blocked" | "warn"
    rule: str
    message: str

    def __str__(self) -> str:
        return f"{self.level.upper():5} {self.path}: [{self.rule}] {self.message}"


@dataclass
class Doc:
    path: Path
    rel: str
    meta: dict | None
    body: str
    body_offset: int = 0
    headings: list[str] = field(default_factory=list)


# ---------- đọc frontmatter (tập con YAML, không cần PyYAML) ----------

def _scalar(text: str):
    text = text.strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in "\"'":
        return text[1:-1]
    if text.startswith("[") and text.endswith("]"):
        inner = text[1:-1].strip()
        return [_scalar(x) for x in inner.split(",")] if inner else []
    return text


def _strip_comment(line: str) -> str:
    # chỉ coi " #" là chú thích, để giữ "file.md#anchor"
    m = re.search(r"\s#", line)
    return line[: m.start()] if m else line


def parse_frontmatter(text: str) -> tuple[dict | None, str, int]:
    """Trả (meta, body, số dòng của frontmatter). meta=None khi không có frontmatter."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, text, 0
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        raise ValueError("frontmatter mở bằng --- nhưng không đóng")
    meta: dict = {}
    key = None
    for raw in lines[1:end]:
        line = _strip_comment(raw).rstrip()
        if not line.strip():
            continue
        item = re.match(r"^\s+-\s*(.*)$", line)
        if item and key is not None:
            if not isinstance(meta[key], list):
                meta[key] = []
            meta[key].append(_scalar(item.group(1)))
            continue
        kv = re.match(r"^([A-Za-z_][\w-]*)\s*:\s*(.*)$", line)
        if not kv:
            raise ValueError(f"không đọc được dòng frontmatter: {raw!r}")
        key, value = kv.group(1), kv.group(2)
        meta[key] = _scalar(value) if value.strip() else ""
    return meta, "\n".join(lines[end + 1 :]), end + 1


# ---------- markdown: bỏ code, lấy heading, slug ----------

def strip_code(body: str, keep_inline: bool = False) -> list[tuple[int, str]]:
    """Các dòng ngoài khối code, kèm số dòng (tính từ 1 trong body); inline code bị xoá trừ khi keep_inline."""
    out, fence = [], None
    for n, line in enumerate(body.splitlines(), 1):
        m = re.match(r"^\s*(`{3,}|~{3,})", line)
        if m:
            if fence is None:
                fence = m.group(1)[0] * len(m.group(1))
            elif m.group(1).startswith(fence):
                fence = None
            continue
        if fence is None:
            out.append((n, line if keep_inline else re.sub(r"`[^`]*`", "", line)))
    return out


def slugify(heading: str) -> str:
    """Slug kiểu GitHub: chữ thường, bỏ dấu câu, khoảng trắng thành '-'."""
    text = re.sub(r"`([^`]*)`", r"\1", heading)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = text.strip().lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def anchors(body: str) -> set[str]:
    seen: dict[str, int] = {}
    result = set()
    for _, line in strip_code(body, keep_inline=True):
        h = HEADING_RE.match(line)
        if not h:
            continue
        slug = slugify(h.group(2))
        n = seen.get(slug, 0)
        seen[slug] = n + 1
        result.add(slug if n == 0 else f"{slug}-{n}")
    return result


def headings(body: str) -> list[str]:
    """Tiêu đề đã chuẩn hoá để so khớp: chữ thường, bỏ dấu backtick."""
    return [HEADING_RE.match(l).group(2).replace("`", "").strip().lower()
            for _, l in strip_code(body, keep_inline=True) if HEADING_RE.match(l)]


# ---------- cấu hình ----------

def load_config(path: Path | None) -> dict:
    cfg = {"forms": {k: dict(v) for k, v in CORE_FORMS.items()}, "untyped": "error",
           "agent_roles": set(AGENT_ROLES), "exclude": [], "people": {}, "artefacts": None, "gates": {}}
    if path is None:
        return cfg
    with open(path, "rb") as f:
        data = tomllib.load(f)
    cfg["untyped"] = data.get("untyped", "error")
    cfg["agent_roles"] |= set(data.get("agent_roles", []))
    cfg["exclude"] = data.get("exclude", [])
    cfg["people"] = data.get("people", {})        # người duyệt → domain, cho luật 7 của approval
    cfg["artefacts"] = data.get("artefacts")      # artefact của dự án, cho luật 2 của baseline
    cfg["gates"] = data.get("gates", {})          # cổng → artefact bắt buộc có trong baseline
    for form in data.get("doc_form", []):
        fid = form["id"]
        base = cfg["forms"].get(form.get("extends", ""), {"fields": [], "status": DEFAULT_STATUS})
        cfg["forms"][fid] = {
            "fields": list(base["fields"]) + list(form.get("required_fields", [])),
            "status": base["status"],
            "sections": form.get("required_sections", base.get("sections", [])),
            "type": form.get("type"),
            "files": form.get("files", []),
            "unit": form.get("unit", "file"),
            "meta_from": form.get("meta_from", "sidecar"),
            "manifest": form.get("manifest"),
        }
    return cfg


# ---------- kiểm từng tài liệu ----------

def as_list(value) -> list:
    if value in (None, ""):
        return []
    return value if isinstance(value, list) else [value]


def check_links(doc: Doc, err) -> None:
    for n, line in strip_code(doc.body):
        for target in LINK_RE.findall(line):
            if re.match(r"^[a-z]+:", target):
                continue
            path_part, _, anchor = target.partition("#")
            dest = (doc.path.parent / path_part).resolve() if path_part else doc.path.resolve()
            lineno = n + doc.body_offset
            if not dest.exists():
                err("link", f"dòng {lineno}: không tồn tại {target}")
                continue
            if anchor and dest.suffix == ".md" and dest.is_file():
                text = dest.read_text(encoding="utf-8")
                try:
                    _, body, _ = parse_frontmatter(text)
                except ValueError:
                    body = text
                if anchor not in anchors(body):
                    err("anchor", f"dòng {lineno}: không có mục #{anchor} trong {path_part or doc.path.name}")


def check_doc(doc: Doc, cfg: dict, root: Path) -> list[Finding]:
    f: list[Finding] = []
    err = lambda rule, msg: f.append(Finding(doc.rel, "error", rule, msg))
    warn = lambda rule, msg: f.append(Finding(doc.rel, "warn", rule, msg))

    # liên kết tương đối và anchor: kiểm cả tài liệu chưa có frontmatter
    check_links(doc, err)

    meta = doc.meta
    if meta is None:
        if doc.path.suffix == ".md":
            (err if cfg["untyped"] == "error" else warn)("frontmatter", "không có frontmatter (cần ít nhất id, type, form)")
        else:
            err("frontmatter", "không có metadata: thiếu sidecar <file>.meta.toml hoặc mục trong manifest")
        return f

    for key in ("id", "type", "form"):
        if not meta.get(key):
            err("field", f"thiếu trường bắt buộc '{key}'")

    for t in as_list(meta.get("type")):
        if t not in TYPES:
            err("type", f"type '{t}' không thuộc 7 loại 15289 + record")

    form_id = meta.get("form", "")
    form = cfg["forms"].get(form_id)
    if form_id and form is None:
        err("form", f"form '{form_id}' không có trong core và profile")
    form = form or {"fields": [], "status": DEFAULT_STATUS}

    if form.get("type") and form["type"] not in as_list(meta.get("type")):
        err("type", f"form '{form_id}' khai type '{form['type']}' nhưng tài liệu ghi {meta.get('type')}")

    for key in form["fields"]:
        if not meta.get(key):
            err("field", f"form '{form_id}' cần trường '{key}'")

    if form["status"] is not None:
        status = meta.get("status", "")
        if not status:
            err("field", "thiếu trường 'status'")
        elif status not in form["status"]:
            err("status", f"status '{status}' không hợp lệ cho form '{form_id}' ({', '.join(sorted(form['status']))})")

    if meta.get("origin") and meta["origin"] not in ORIGINS:
        err("origin", f"origin '{meta['origin']}' không thuộc {sorted(ORIGINS)}")
    if meta.get("manual_edits") and meta.get("origin") != "generated":
        err("origin", "manual_edits chỉ dùng khi origin = generated")

    # khớp theo chuỗi con, để "## 3. Kết quả" vẫn khớp mục "Kết quả"
    for section in form.get("sections", []):
        want = section.replace("`", "").lower()
        if not any(want in h for h in doc.headings):
            err("section", f"thiếu mục bắt buộc '{section}'")

    # luật riêng của từng form core, phần chỉ cần chính tài liệu
    if form_id == "approval":
        if meta.get("verdict") and meta["verdict"] not in VERDICTS:
            err("approval", f"verdict '{meta['verdict']}' không thuộc {sorted(VERDICTS)}")
        if meta.get("subject") and "@" not in str(meta["subject"]) and not str(meta["subject"]).startswith("BL-"):
            err("approval", "subject phải có phiên bản bất biến (<id>@<phiên bản>) hoặc là một baseline")
        for who in as_list(meta.get("approver")):
            if str(who).lower() in cfg["agent_roles"]:
                err("approval", f"người duyệt '{who}' là vai trò agent; người duyệt phải là người")
        if meta.get("verdict") in ("approved", "approved-with-conditions") and not as_list(meta.get("evidence")):
            err("approval", "duyệt cho qua mà không có evidence")
        for ev in as_list(meta.get("evidence")):
            p = evidence_path(ev)
            if p and not (root / p).exists():
                err("approval", f"evidence không tồn tại: {p}")
    if form_id == "baseline" and meta.get("status") == "frozen" and not meta.get("approval"):
        err("baseline", "baseline frozen cần trường approval")
    if form_id == "deviation":
        if str(meta.get("expires", "")).strip().lower() in FOREVER:
            err("deviation", "expires không được trống hay vô thời hạn")
        if any(str(x).lower() in EVERYTHING for x in as_list(meta.get("applies_to"))):
            err("deviation", "applies_to không được là 'tất cả': miễn cho mọi thứ là đổi luật")
        if meta.get("status") == "granted" and not meta.get("approval"):
            err("deviation", "miễn trừ granted cần trường approval")

    # con số có nguồn: chỉ cảnh báo, vì regex không phân biệt được ví dụ và khẳng định
    if not as_list(meta.get("sources")):
        hits = [(n + doc.body_offset, m.group(0)) for n, line in strip_code(doc.body) for m in UNIT_RE.finditer(line)]
        if hits:
            sample = ", ".join(f"dòng {n}: {v}" for n, v in hits[:3])
            warn("number-source", f"{len(hits)} con số có đơn vị nhưng frontmatter không có sources ({sample})")

    return f


# ---------- kiểm chéo giữa các tài liệu ----------

MUTABLE_VERSIONS = {"", "latest", "main", "master", "head", "develop", "dev", "trunk"}
BAD_VERDICTS = {"FAIL", "BLOCKED"}


def evidence_path(entry) -> str:
    """'reports/a.md (ghi chú)' → 'reports/a.md'."""
    return str(entry).split(" (")[0].strip()


def report_verdict(path: Path) -> str | None:
    """Phán quyết của một báo cáo: trường verdict trong frontmatter, hoặc dòng 'VERDICT: X'."""
    if not path.is_file():
        return None
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None
    try:
        meta, body, _ = parse_frontmatter(text)
    except ValueError:
        meta, body = None, text
    if meta and str(meta.get("verdict", "")).upper() in {"PASS", "FAIL", "BLOCKED"}:
        return str(meta["verdict"]).upper()
    m = re.search(r"^VERDICT:\s*(PASS|FAIL|BLOCKED)\b", body, re.M)
    return m.group(1) if m else None


def baseline_rows(body: str) -> list[dict]:
    """Bảng artefact của baseline: cột 1 artefact, cột 2 phiên bản, cột 3 'PHÁN QUYẾT · đường dẫn báo cáo'."""
    rows, in_table = [], False
    for _, line in strip_code(body, keep_inline=True):
        if not line.strip().startswith("|"):
            in_table = False
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells[0].lower() == "artefact":
            in_table = True
            continue
        if not in_table or set(cells[0]) <= {"-", ":"} or len(cells) < 3:
            continue
        verdict, _, report = cells[2].partition("·")
        rows.append({"artefact": cells[0].strip("`"), "version": cells[1].strip("`"),
                     "verdict": verdict.strip().upper(), "report": report.strip()})
    return rows


def split_ref(ref) -> tuple[str, str]:
    ident, _, version = str(ref).partition("@")
    return ident.strip(), version.strip()


def check_cross(doc: Doc, cfg: dict, root: Path, index: dict[str, Doc]) -> list[Finding]:
    f: list[Finding] = []
    err = lambda rule, msg: f.append(Finding(doc.rel, "error", rule, msg))
    meta = doc.meta or {}
    form_id = meta.get("form")

    if form_id == "approval":
        passing = meta.get("verdict") in ("approved", "approved-with-conditions")
        # luật 4: bằng chứng FAIL/BLOCKED mà vẫn cho qua thì phải ghi rủi ro đã nhận
        bad = [p for p in map(evidence_path, as_list(meta.get("evidence")))
               if report_verdict(root / p) in BAD_VERDICTS]
        if passing and bad and not as_list(meta.get("accepted_risks")):
            err("approval", f"bằng chứng có FAIL/BLOCKED ({', '.join(bad)}) nhưng accepted_risks trống")
        # luật 7: tài liệu dùng chung cần người duyệt của mọi domain liên quan
        subject = index.get(split_ref(meta.get("subject", ""))[0])
        if subject and subject.meta and as_list(subject.meta.get("shared_with")):
            need = set(as_list(subject.meta.get("shared_with")))
            if subject.meta.get("owner_domain"):
                need.add(subject.meta["owner_domain"])
            have, unknown = set(), False
            for who in as_list(meta.get("approver")):
                domain = cfg["people"].get(str(who))
                if domain is None:
                    unknown = True
                    err("approval", f"không biết domain của người duyệt '{who}' (khai trong [people] của profile)")
                else:
                    have.add(domain)
            if not unknown and need - have:
                err("approval", f"tài liệu dùng chung cần người duyệt của {', '.join(sorted(need - have))}")

    if form_id == "baseline":
        rows = baseline_rows(doc.body)
        if not rows:
            err("baseline", "không đọc được bảng artefact (cột đầu có tiêu đề 'Artefact')")
        for row in rows:
            if row["version"].lower() in MUTABLE_VERSIONS:
                err("baseline", f"{row['artefact']}: phiên bản '{row['version']}' không phải định danh bất biến")
            if cfg["artefacts"] is not None and row["artefact"] not in cfg["artefacts"]:
                err("baseline", f"{row['artefact']}: không có trong danh sách artefact của dự án")
            if row["verdict"] not in {"PASS", "FAIL", "BLOCKED"}:
                err("baseline", f"{row['artefact']}: cột kiểm chứng phải có dạng PASS/FAIL/BLOCKED · <báo cáo>")
            elif row["report"]:
                if not (root / row["report"]).exists():
                    err("baseline", f"{row['artefact']}: báo cáo không tồn tại: {row['report']}")
                else:
                    actual = report_verdict(root / row["report"])
                    if actual and actual != row["verdict"]:
                        err("baseline", f"{row['artefact']}: ghi {row['verdict']} nhưng báo cáo nói {actual} (không khớp)")
        listed = {r["artefact"] for r in rows}
        for art in cfg["gates"].get(meta.get("gate", ""), []):
            if art not in listed:
                err("baseline", f"cổng '{meta.get('gate')}' cần artefact '{art}' nhưng baseline không có")
        # luật 5: chốt baseline còn FAIL/BLOCKED thì bản duyệt phải ghi rủi ro
        if meta.get("status") == "frozen" and any(r["verdict"] in BAD_VERDICTS for r in rows):
            apr = index.get(str(meta.get("approval", "")))
            if apr is None:
                err("baseline", f"không tìm thấy bản duyệt '{meta.get('approval')}'")
            elif not as_list((apr.meta or {}).get("accepted_risks")):
                err("baseline", f"có mục FAIL/BLOCKED nhưng {meta.get('approval')} không có accepted_risks")

    # derived_from: đầu ra cũ hơn nguồn
    for ref in as_list(meta.get("derived_from")):
        ident, version = split_ref(ref)
        source = index.get(ident)
        if not version:
            err("derived", f"derived_from '{ref}' cần phiên bản: <id>@<rev>")
        elif source is None:
            err("derived", f"derived_from '{ref}': không tìm thấy tài liệu id '{ident}'")
        elif source.meta.get("rev") and str(source.meta["rev"]) != version:
            err("derived", f"sinh từ {ident}@{version} nhưng {ident} đã ở rev {source.meta['rev']}: cần sinh lại")

    return f


# ---------- thu thập tài liệu ----------

def rel_of(p: Path, root: Path) -> str:
    rp, rr = p.resolve(), root.resolve()
    return rp.relative_to(rr).as_posix() if rp.is_relative_to(rr) else p.as_posix()


def under(p: Path, paths: list[Path]) -> bool:
    rp = p.resolve()
    return any(rp == q.resolve() or q.resolve() in rp.parents for q in paths)


def collect(paths: list[Path], exclude: list[str], root: Path) -> list[Path]:
    files = []
    for p in paths:
        cands = [p] if p.is_file() else sorted(p.rglob("*.md"))
        for c in cands:
            if c.suffix == ".md" and not any(Path(rel_of(c, root)).match(pat) for pat in exclude):
                files.append(c)
    return files


def toml_meta(entry: dict) -> dict:
    """Giá trị TOML → cùng dạng với frontmatter (chuỗi hoặc danh sách chuỗi)."""
    return {k: [str(x) for x in v] if isinstance(v, list) else str(v) for k, v in entry.items() if k != "files"}


def read_sidecar(path: Path) -> dict | None:
    return tomllib.loads(path.read_text(encoding="utf-8")) if path.is_file() else None


def collect_files(paths: list[Path], cfg: dict, root: Path) -> tuple[list[Doc], list[Finding]]:
    """Tài liệu không phải Markdown, khai bằng [[doc_form]] có 'files'."""
    docs, findings = [], []
    for fid, form in cfg["forms"].items():
        manifest = root / form["manifest"] if form.get("manifest") else None
        for pattern in form.get("files", []):
            matched = [m for m in sorted(root.glob(pattern)) if m.is_file() and under(m, paths)
                       and not m.name.endswith(".meta.toml")
                       and (manifest is None or m.resolve() != manifest.resolve())]
            if not matched:
                continue
            how = form.get("meta_from", "sidecar")
            if how not in ("sidecar", "manifest"):
                findings.append(Finding(pattern, "blocked", "meta",
                                        f"form '{fid}': chưa đọc được metadata từ '{how}'; dùng sidecar hoặc manifest"))
                continue
            entries = []
            if how == "manifest":
                try:
                    with open(manifest, "rb") as fh:
                        entries = tomllib.load(fh).get("doc", [])
                except (OSError, TypeError, tomllib.TOMLDecodeError) as e:
                    findings.append(Finding(form.get("manifest") or fid, "error", "meta", f"không đọc được manifest: {e}"))
                    continue
            if form.get("unit") == "set":
                # cả tập là một tài liệu; sidecar của tập đặt cạnh thư mục chứa nó: <thư mục>.meta.toml
                if how == "sidecar":
                    entry = read_sidecar(root / (Path(pattern).parent.as_posix() + ".meta.toml"))
                else:
                    entry = next((e for e in entries if e.get("files") == pattern), None)
                docs.append(Doc(matched[0], pattern, toml_meta(entry) if entry else None, ""))
                continue
            for m in matched:
                rel = rel_of(m, root)
                if how == "sidecar":
                    entry = read_sidecar(m.with_name(m.name + ".meta.toml"))
                else:
                    entry = next((e for e in entries if Path(rel).match(e.get("files", ""))), None)
                docs.append(Doc(m, rel, toml_meta(entry) if entry else None, ""))
    return docs, findings


def run(paths: list[Path], root: Path, config: Path | None) -> tuple[str, list[Finding], int]:
    try:
        cfg = load_config(config)
    except (OSError, tomllib.TOMLDecodeError, KeyError) as e:
        return "BLOCKED", [Finding(str(config), "error", "config", str(e))], 0

    docs: list[Doc] = []
    findings: list[Finding] = []
    for p in collect(paths, cfg["exclude"], root):
        rel = rel_of(p, root)
        text = p.read_text(encoding="utf-8")
        try:
            meta, body, offset = parse_frontmatter(text)
        except ValueError as e:
            findings.append(Finding(rel, "error", "frontmatter", str(e)))
            meta, body, offset = None, text, 0
        docs.append(Doc(p, rel, meta, body, offset, headings(body)))
    try:
        more, notes = collect_files(paths, cfg, root)
    except tomllib.TOMLDecodeError as e:
        return "BLOCKED", findings + [Finding("sidecar", "error", "meta", f"sidecar hỏng: {e}")], len(docs)
    docs += more
    findings += notes
    if not docs and not notes:
        return "BLOCKED", [], 0

    index: dict[str, Doc] = {}
    for doc in docs:
        did = (doc.meta or {}).get("id")
        if did:
            if did in index:
                findings.append(Finding(doc.rel, "error", "id", f"id '{did}' trùng với {index[did].rel}"))
            else:
                index[did] = doc
    for doc in docs:
        findings += check_doc(doc, cfg, root)
        if doc.meta:
            findings += check_cross(doc, cfg, root, index)

    if any(x.level == "error" for x in findings):
        verdict = "FAIL"
    elif any(x.level == "blocked" for x in findings):
        verdict = "BLOCKED"
    else:
        verdict = "PASS"
    return verdict, findings, len(docs)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Kiểm hình thức tài liệu theo type/form.")
    ap.add_argument("paths", nargs="+", type=Path)
    ap.add_argument("--config", type=Path, help="doclint.toml của dự án hoặc domain pack")
    ap.add_argument("--root", type=Path, default=Path("."), help="gốc để giải đường dẫn evidence, files, manifest")
    args = ap.parse_args(argv)
    # console Windows mặc định cp1252, in tiếng Việt sẽ lỗi UnicodeEncodeError
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    verdict, findings, count = run(args.paths, args.root, args.config)
    for x in findings:
        print(x)
    errors = sum(x.level == "error" for x in findings)
    blocked = sum(x.level == "blocked" for x in findings)
    warns = len(findings) - errors - blocked
    print(f"\n{count} tài liệu · {errors} lỗi · {blocked} không kiểm được · {warns} cảnh báo")
    print(f"VERDICT: {verdict}")
    return {"PASS": 0, "FAIL": 1, "BLOCKED": 2}[verdict]


if __name__ == "__main__":
    sys.exit(main())
