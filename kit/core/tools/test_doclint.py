"""Test cho doclint. Chạy: python -m unittest kit/core/tools/test_doclint.py"""

import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import doclint  # noqa: E402


def write(root: Path, rel: str, text: str) -> Path:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(textwrap.dedent(text).lstrip(), encoding="utf-8")
    return p


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def lint(self, *rels, config=None):
        paths = [self.root / r for r in rels] or [self.root]
        return doclint.run(paths, self.root, config)

    def rules(self, findings, level="error"):
        return [f.rule for f in findings if f.level == level]


class Frontmatter(Base):
    def test_parse_subset(self):
        meta, body, offset = doclint.parse_frontmatter(textwrap.dedent("""\
            ---
            id: SPEC-1   # chú thích
            type: [specification, description]
            sources: [refs/a.txt#L12]
            approver:
              - An
              - Bình
            ---
            # Tiêu đề
            """))
        self.assertEqual(meta["id"], "SPEC-1")
        self.assertEqual(meta["type"], ["specification", "description"])
        self.assertEqual(meta["sources"], ["refs/a.txt#L12"])
        self.assertEqual(meta["approver"], ["An", "Bình"])
        self.assertEqual(offset, 8)
        self.assertTrue(body.startswith("# Tiêu đề"))

    def test_unclosed_frontmatter_is_error(self):
        write(self.root, "a.md", "---\nid: X\n# không đóng\n")
        verdict, findings, _ = self.lint("a.md")
        self.assertEqual(verdict, "FAIL")
        self.assertIn("frontmatter", self.rules(findings))


class Verdicts(Base):
    def test_no_documents_is_blocked(self):
        verdict, _, count = self.lint()
        self.assertEqual((verdict, count), ("BLOCKED", 0))

    def test_valid_doc_passes(self):
        write(self.root, "a.md", """
            ---
            id: D-1
            type: description
            form: design-note
            status: draft
            ---
            # A
            """)
        verdict, findings, _ = self.lint("a.md")
        self.assertEqual(verdict, "PASS", findings)

    def test_untyped_doc_fails_by_default_and_warns_when_relaxed(self):
        write(self.root, "a.md", "# Không có frontmatter\n")
        self.assertEqual(self.lint("a.md")[0], "FAIL")
        cfg = write(self.root, "doclint.toml", 'untyped = "warn"\n')
        verdict, findings, _ = self.lint("a.md", config=cfg)
        self.assertEqual(verdict, "PASS")
        self.assertIn("frontmatter", self.rules(findings, "warn"))

    def test_broken_config_is_blocked(self):
        cfg = write(self.root, "doclint.toml", "untyped = \n")
        write(self.root, "a.md", "# A\n")
        self.assertEqual(self.lint("a.md", config=cfg)[0], "BLOCKED")


class Fields(Base):
    def doc(self, **meta):
        lines = "\n".join(f"{k}: {v}" for k, v in meta.items())
        write(self.root, "a.md", f"---\n{lines}\n---\n# A\n")
        return self.lint("a.md")

    def test_unknown_type_form_status(self):
        _, findings, _ = self.doc(id="X", type="decision", form="mystery", status="done")
        self.assertEqual(sorted(self.rules(findings)), ["form", "status", "type"])

    def test_missing_required(self):
        _, findings, _ = self.doc(type="report", form="verify-report")
        self.assertEqual(self.rules(findings).count("field"), 2)  # id, status

    def test_manual_edits_needs_generated(self):
        _, findings, _ = self.doc(id="X", type="specification", form="register", status="draft",
                                  origin="authored", manual_edits="[dnp]")
        self.assertIn("origin", self.rules(findings))

    def test_duplicate_id(self):
        for name in ("a.md", "b.md"):
            write(self.root, name, "---\nid: X\ntype: plan\nform: howto\nstatus: draft\n---\n")
        _, findings, _ = self.lint()
        self.assertIn("id", self.rules(findings))


class CoreForms(Base):
    def test_approval_rules(self):
        write(self.root, "apr.md", """
            ---
            id: APR-1
            type: record
            form: approval
            gate: merge
            subject: firmware
            verdict: approved
            approver: [reviewer]
            date: 2026-10-29
            origin: authored
            evidence: [reports/missing.md]
            ---
            """)
        _, findings, _ = self.lint("apr.md")
        msgs = " | ".join(f.message for f in findings if f.rule == "approval")
        self.assertIn("phiên bản bất biến", msgs)
        self.assertIn("vai trò agent", msgs)
        self.assertIn("không tồn tại", msgs)

    def test_approval_valid(self):
        write(self.root, "reports/v.md", "x\n")
        write(self.root, "apr.md", """
            ---
            id: APR-1
            type: record
            form: approval
            gate: merge
            subject: firmware@a1b2c3d
            verdict: approved
            approver: [An]
            date: 2026-10-29
            origin: authored
            evidence: [reports/v.md]
            ---
            """)
        verdict, findings, _ = self.lint("apr.md")
        self.assertEqual(verdict, "PASS", findings)

    def test_deviation_must_be_scoped_and_expire(self):
        write(self.root, "dev.md", """
            ---
            id: DEV-1
            type: [record, request]
            form: deviation
            waives: drc:clearance
            scope: U4
            applies_to: [all]
            expires: never
            status: granted
            ---
            """)
        _, findings, _ = self.lint("dev.md")
        self.assertEqual(self.rules(findings).count("deviation"), 3)

    def test_frozen_baseline_needs_approval(self):
        write(self.root, "bl.md", "---\nid: BL-1\ntype: record\nform: baseline\ngate: freeze\n"
                                  "date: 2026-10-29\norigin: generated\nstatus: frozen\n---\n")
        _, findings, _ = self.lint("bl.md")
        self.assertIn("baseline", self.rules(findings))


class ProfileForms(Base):
    def test_pack_form_with_sections_and_type(self):
        cfg = write(self.root, "doclint.toml", """
            [[doc_form]]
            id = "sim-report"
            type = "report"
            extends = "review-report"
            required_sections = ["Trường hợp tải", "Kết quả"]
            """)
        write(self.root, "a.md", "---\nid: S-1\ntype: description\nform: sim-report\nstatus: draft\n---\n## Kết quả\n")
        _, findings, _ = self.lint("a.md", config=cfg)
        self.assertEqual(sorted(self.rules(findings)), ["section", "type"])

    def test_section_with_inline_code(self):
        cfg = write(self.root, "doclint.toml", '[[doc_form]]\nid = "f"\nrequired_sections = ["Luật cho `doclint`"]\n')
        write(self.root, "a.md", "---\nid: A\ntype: plan\nform: f\nstatus: draft\n---\n## Luật cho `doclint`\n")
        verdict, findings, _ = self.lint("a.md", config=cfg)
        self.assertEqual(verdict, "PASS", findings)


class Links(Base):
    def test_slug_matches_github(self):
        self.assertEqual(doclint.slugify("6.1. Hai trục: `type` và `form`"), "61-hai-trục-type-và-form")
        self.assertEqual(doclint.slugify("4. Agent: 4 vai trò chung, chuyên môn hoá bằng checklist"),
                         "4-agent-4-vai-trò-chung-chuyên-môn-hoá-bằng-checklist")

    def test_broken_file_and_anchor(self):
        write(self.root, "b.md", "# Có thật\n")
        write(self.root, "a.md", """
            ---
            id: A
            type: plan
            form: howto
            status: draft
            ---
            [ok](b.md#có-thật) [mất](c.md) [sai](b.md#không-có) `[bỏ qua](x.md)`
            ```
            [trong code](y.md)
            ```
            """)
        _, findings, _ = self.lint("a.md")
        self.assertEqual(sorted(self.rules(findings)), ["anchor", "link"])


class Numbers(Base):
    def test_number_without_sources_warns_only(self):
        write(self.root, "a.md", "---\nid: A\ntype: plan\nform: howto\nstatus: draft\n---\nDòng ngủ 20 µA, `5 mA` trong code.\n")
        verdict, findings, _ = self.lint("a.md")
        self.assertEqual(verdict, "PASS")
        warn = [f for f in findings if f.rule == "number-source"]
        self.assertEqual(len(warn), 1)
        self.assertIn("1 con số", warn[0].message)


REPORT_BLOCKED = "---\nid: R-1\ntype: report\nform: verify-report\nstatus: draft\n---\n\nVERDICT: BLOCKED\n"
REPORT_PASS = "---\nid: R-2\ntype: report\nform: verify-report\nstatus: draft\nverdict: PASS\n---\n"


def approval(subject, approver="[An]", evidence="[reports/r1.md]", extra=""):
    return (f"---\nid: APR-1\ntype: record\nform: approval\ngate: merge\nsubject: {subject}\n"
            f"verdict: approved\napprover: {approver}\ndate: 2026-10-29\norigin: authored\n"
            f"evidence: {evidence}\n{extra}---\n")


class ApprovalCrossChecks(Base):
    def test_blocked_evidence_needs_accepted_risks(self):
        write(self.root, "reports/r1.md", REPORT_BLOCKED)
        write(self.root, "apr.md", approval("firmware@a1b2c3d"))
        _, findings, _ = self.lint("apr.md", "reports")
        self.assertTrue(any("accepted_risks" in f.message for f in findings), findings)

        write(self.root, "apr.md", approval("firmware@a1b2c3d", extra="accepted_risks: [chưa đo HIL]\n"))
        verdict, findings, _ = self.lint("apr.md", "reports")
        self.assertEqual(verdict, "PASS", findings)

    def test_shared_doc_needs_approver_from_each_domain(self):
        cfg = write(self.root, "doclint.toml", '[people]\nAn = "pcb-design"\n"Bình" = "embedded-mcu"\n')
        write(self.root, "reports/r1.md", REPORT_PASS)
        write(self.root, "pinmap.md", "---\nid: PINMAP\ntype: specification\nform: register\nstatus: draft\n"
                                      "rev: B\nowner_domain: pcb-design\nshared_with: [embedded-mcu]\n---\n")
        write(self.root, "apr.md", approval("PINMAP@B"))
        _, findings, _ = self.lint("apr.md", "pinmap.md", "reports", config=cfg)
        self.assertTrue(any("embedded-mcu" in f.message for f in findings), findings)

        write(self.root, "apr.md", approval("PINMAP@B", approver="[An, Bình]"))
        verdict, findings, _ = self.lint("apr.md", "pinmap.md", "reports", config=cfg)
        self.assertEqual(verdict, "PASS", findings)

    def test_unknown_approver_domain(self):
        write(self.root, "reports/r1.md", REPORT_PASS)
        write(self.root, "pinmap.md", "---\nid: PINMAP\ntype: specification\nform: register\nstatus: draft\n"
                                      "owner_domain: pcb-design\nshared_with: [embedded-mcu]\n---\n")
        write(self.root, "apr.md", approval("PINMAP@B"))
        _, findings, _ = self.lint("apr.md", "pinmap.md", "reports")
        self.assertTrue(any("không biết domain" in f.message for f in findings), findings)


BASELINE = """---
id: BL-1
type: record
form: baseline
gate: design-freeze
date: 2026-10-29
origin: generated
status: {status}
{extra}---

# BL-1

| Artefact | Phiên bản | Kiểm chứng | Đổi |
| --- | --- | --- | --- |
| firmware | {version} | {verdict} · reports/r1.md | - |
"""


class BaselineChecks(Base):
    def test_mutable_version_and_verdict_mismatch(self):
        write(self.root, "reports/r1.md", REPORT_BLOCKED)
        write(self.root, "bl.md", BASELINE.format(status="proposed", extra="", version="main", verdict="PASS"))
        _, findings, _ = self.lint("bl.md", "reports")
        msgs = " | ".join(f.message for f in findings if f.rule == "baseline")
        self.assertIn("bất biến", msgs)
        self.assertIn("không khớp", msgs)

    def test_artefacts_and_gate_coverage_from_profile(self):
        cfg = write(self.root, "doclint.toml", 'artefacts = ["firmware", "device-config"]\n'
                                               '[gates]\ndesign-freeze = ["firmware", "device-config"]\n')
        write(self.root, "reports/r1.md", REPORT_PASS)
        write(self.root, "bl.md", BASELINE.format(status="proposed", extra="", version="a1b2c3d", verdict="PASS"))
        _, findings, _ = self.lint("bl.md", "reports", config=cfg)
        self.assertTrue(any("device-config" in f.message for f in findings), findings)

    def test_frozen_with_blocked_row_needs_risks_in_approval(self):
        write(self.root, "reports/r1.md", REPORT_BLOCKED)
        write(self.root, "bl.md", BASELINE.format(status="frozen", extra="approval: APR-1\n",
                                                  version="a1b2c3d", verdict="BLOCKED"))
        write(self.root, "apr.md", approval("BL-1"))
        _, findings, _ = self.lint("bl.md", "apr.md", "reports")
        self.assertTrue(any(f.rule == "baseline" and "accepted_risks" in f.message for f in findings), findings)


class DerivedFrom(Base):
    def test_stale_derivation(self):
        write(self.root, "layout.md", "---\nid: LAYOUT\ntype: specification\nform: register\nstatus: draft\nrev: C\n---\n")
        write(self.root, "fab.md", "---\nid: FAB\ntype: specification\nform: register\nstatus: draft\n"
                                   "derived_from: [LAYOUT@B]\n---\n")
        _, findings, _ = self.lint()
        self.assertIn("derived", self.rules(findings))

    def test_unknown_source_id(self):
        write(self.root, "fab.md", "---\nid: FAB\ntype: specification\nform: register\nstatus: draft\n"
                                   "derived_from: [NOPE@B]\n---\n")
        _, findings, _ = self.lint()
        self.assertIn("derived", self.rules(findings))


class NonMarkdown(Base):
    def test_sidecar_per_file(self):
        cfg = write(self.root, "doclint.toml", '[[doc_form]]\nid = "drawing"\ntype = "specification"\n'
                                               'files = ["cad/*.pdf"]\nmeta_from = "sidecar"\n')
        write(self.root, "cad/a.pdf", "x")
        write(self.root, "cad/b.pdf", "x")
        write(self.root, "cad/a.pdf.meta.toml", 'id = "DWG-1"\ntype = "specification"\nform = "drawing"\nstatus = "draft"\n')
        _, findings, count = self.lint("cad", config=cfg)
        self.assertEqual(count, 2)
        self.assertEqual([f.path for f in findings if f.level == "error"], ["cad/b.pdf"])

    def test_set_with_manifest(self):
        cfg = write(self.root, "doclint.toml", '[[doc_form]]\nid = "fab-package"\ntype = "specification"\n'
                                               'files = ["fab/*"]\nunit = "set"\nmeta_from = "manifest"\n'
                                               'manifest = "fab/manifest.toml"\nrequired_fields = ["rev"]\n')
        write(self.root, "fab/top.gbr", "x")
        write(self.root, "fab/drill.drl", "x")
        write(self.root, "fab/manifest.toml", '[[doc]]\nfiles = "fab/*"\nid = "FAB-1"\ntype = "specification"\n'
                                              'form = "fab-package"\nstatus = "draft"\n')
        _, findings, count = self.lint("fab", config=cfg)
        self.assertEqual(count, 1)
        self.assertEqual([f.rule for f in findings if f.level == "error"], ["field"])  # thiếu rev

    def test_title_block_is_blocked(self):
        cfg = write(self.root, "doclint.toml", '[[doc_form]]\nid = "drawing"\ntype = "specification"\n'
                                               'files = ["cad/*.pdf"]\nmeta_from = "title-block"\n')
        write(self.root, "cad/a.pdf", "x")
        verdict, findings, _ = self.lint("cad", config=cfg)
        self.assertEqual(verdict, "BLOCKED", findings)


if __name__ == "__main__":
    unittest.main()
