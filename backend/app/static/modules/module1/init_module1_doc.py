# flake8: noqa
#!/usr/bin/env python3
"""
Creates a complete, LMS-ready Markdown shell for:
Module 1 – Orientation & Professional Foundations (GA-localized, GNPEC-aligned)

Output:
  Module1_Authoring/
    ├─ Module_1_Lessons_Branded.md
    └─ Authoring_Checklist.md

Usage:
  python3 init_module1_doc.py --logo "/path/to/AADA-Logo.png"
"""

import argparse, datetime
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--logo", help="Local path to AADA logo (PNG/JPG). Optional.", default="")
args = parser.parse_args()

out_dir = Path("Module1_Authoring")
out_dir.mkdir(parents=True, exist_ok=True)

logo_md = f"![AADA Logo]({args.logo})" if args.logo else "![AADA Logo](assets/aada_logo.png)"

today = datetime.date.today().isoformat()

md = f"""\
---
title: "Module 1 – Orientation & Professional Foundations"
brand:
  primary: "#D5AA42"   # AADA gold
  background: "#FFFDF9"
  text: "#333333"
ga_gnpec_alignment: true
version: "1.0"
date: "{today}"
---

# Module 1 – Orientation & Professional Foundations
**Atlanta Academy of Dental Assisting (AADA)**

{logo_md}

> **Delivery:** Online + Live (1 kickoff) &nbsp;|&nbsp; **Estimated Time:** ~40 hours
> **Georgia/GNPEC Alignment:** Programmatic Integrity (Std 1), Catalog/Policies (Std 4), Credential/Records (Std 5–6), Refund/Cancellation/Complaint (Std 12–14)

---

## Table of Contents
- [1. Welcome to AADA (Georgia Context)](#1-welcome-to-aada-georgia-context)
- [2. Professionalism & Ethics](#2-professionalism--ethics)
  - [2.1 Georgia Scope & Expectations](#21-georgia-scope--expectations)
  - [2.2 Ethical Decision Framework](#22-ethical-decision-framework)
  - [2.3 Case Studies](#23-case-studies)
- [3. HIPAA & OSHA Essentials](#3-hipaa--osha-essentials)
  - [3.1 HIPAA Privacy Rule (45 CFR Part 164)](#31-hipaa-privacy-rule-45-cfr-part-164)
  - [3.2 OSHA (29 CFR 1910) in Dental Settings](#32-osha-29-cfr-1910-in-dental-settings)
  - [3.3 Infection-Control Basics (Preview)](#33-infection-control-basics-preview)
- [4. Communication & Team Dynamics](#4-communication--team-dynamics)
  - [4.1 Patient-Centered Communication](#41-patient-centered-communication)
  - [4.2 Teamwork & Safety Culture](#42-teamwork--safety-culture)
- [5. Orientation to LMS & Student Policies](#5-orientation-to-lms--student-policies)
  - [5.1 LMS Tasks](#51-lms-tasks)
  - [5.2 GNPEC Policies: Refund, Cancellation, Complaint](#52-gnpec-policies-refund-cancellation-complaint)
- [6. Summary & Assessment](#6-summary--assessment)
- [7. Georgia References](#7-georgia-references)
- [Appendix A: Key Terms & Glossary](#appendix-a-key-terms--glossary)
- [Appendix B: xAPI & H5P Activity Map](#appendix-b-xapi--h5p-activity-map)

---

## 1. Welcome to AADA (Georgia Context)
**Mission:** [WRITE HERE – AADA’s mission statement in 2–4 sentences.]

**Regulatory context (Georgia):**
- GNPEC Minimum Standards require clear objectives; theoretical + practical components; assessment; remediation; final evaluation.
- Unaccredited programs must include **direct, meaningful** live interaction (no fully asynchronous programs). Hands-on public-health training must be **in person**.
[WRITE HERE – Your enrollment/authorization disclosure paragraph.]

**Learning objectives (Module 1):**
- Explain professionalism and ethics in Georgia dental settings.
- Summarize HIPAA privacy & OSHA safety essentials.
- Navigate the AADA LMS; locate Catalog policies (SAP, grading, refund, cancellation, complaint).
- Understand transcript and records basics.

> **Instructor Note:** Keep a copy of the Catalog accessible for live Q&A.

---

## 2. Professionalism & Ethics
### 2.1 Georgia Scope & Expectations
[WRITE HERE – Expectations for DA professionalism in GA: attire, punctuality, confidentiality, respect, inclusivity, documentation, social media boundaries.]

### 2.2 Ethical Decision Framework
1. Identify the patient interest & potential risks
2. Check legal/ethical requirements (HIPAA privacy, OSHA safety)
3. Consult supervisor/policy if uncertain
4. Choose the safest ethical action; document as required

[WRITE HERE – AADA’s internal reporting/escalation path (titles, who to notify).]

### 2.3 Case Studies
- **Confidential Screen at Check-in**: [WRITE HERE – Describe scenario, options, correct response, rationale.]
- **Social Media Post**: [WRITE HERE – No images/name without valid authorization; discuss GA clinic norms.]
- **Pressure to rush**: [WRITE HERE – Safety over speed; how to raise concerns professionally.]

> **Interactive Activity 1 – Ethics Branching (H5P: `M1_H5P_EthicsBranching`)**
> Prompt: “Coworker violates HIPAA (PHI visible). What do you do?”
> Correct path: Report to supervisor & secure PHI.
> Feedback: “Reporting supports patient privacy and Georgia clinic policies.”

---

## 3. HIPAA & OSHA Essentials
### 3.1 HIPAA Privacy Rule (45 CFR Part 164)
**PHI definition & “minimum necessary”**: [WRITE HERE – Define PHI with examples common to a dental office; minimum necessary principle.]
**Common violations**: [WRITE HERE – Unattended monitors, public conversations, unsecured printouts.]
**Practical safeguards**: [WRITE HERE – Screen shields, private calls, verification steps.]

### 3.2 OSHA (29 CFR 1910) in Dental Settings
**Core elements**
- PPE (masks, gloves, eyewear)
- Exposure control (sharps, post-exposure protocols)
- Labels/signage; engineering controls
[WRITE HERE – Where AADA stores/posters/checklists.]

### 3.3 Infection-Control Basics (Preview)
[WRITE HERE – Instrument reprocessing cycle overview; this is a preview for later hands-on labs.]

> **Interactive Activity 2 – Interactive Video (H5P: `M1_H5P_HIPAAHotspot`)**
> At 00:12: “Cover patient file” → Feedback explains minimum necessary + visual privacy.

---

## 4. Communication & Team Dynamics
### 4.1 Patient-Centered Communication
**Preferred language examples:**
- Delay: “Thank you for your patience…”
- Clarification: “Let me double-check to keep things accurate and safe.”
[WRITE HERE – Additional phrases; DEI sensitivity notes.]

### 4.2 Teamwork & Safety Culture
**Chairside hand-offs; cueing; escalation etiquette:** [WRITE HERE – With examples.]
**Respectful prompts:** “Let’s follow PPE steps to keep everyone safe.”
[WRITE HERE – Internal norms (brief huddle, after-action notes).]

> **Interactive Activity 3 – Dialog Cards (H5P: `M1_H5P_DialogCards`)**
> Card examples: “Patient asks about delay” → “Thank you for your patience…”

---

## 5. Orientation to LMS & Student Policies
### 5.1 LMS Tasks
- Upload profile photo; test audio/video; post intro
- Review Catalog sections: SAP, grading, refund, cancellation, complaint
[WRITE HERE – Screenshots/steps if desired.]

### 5.2 GNPEC Policies: Refund, Cancellation, Complaint
- **Refund (Std 12)**: Prorated before **50%** completion; refunds issued within **45 days**; only specific fees can be nonrefundable.
- **Cancellation (Std 13)**: Full refund if cancelling within **72 hours** of signing (minus allowed nonrefundable fees).
- **Complaint (Std 14)**: Internal procedure with timelines; **right to appeal to GNPEC** with contact info.
[WRITE HERE – Your exact Catalog policy language or links.]

> **Interactive Activity 4 – Policy Match (H5P: `M1_H5P_PolicyMatch`)**
> Match descriptions to policy names (Refund, Cancellation, Complaint).

---

## 6. Summary & Assessment
- **Graded Quiz**: 25 items; **≥80%** required
- **Acknowledgment Form**: Student attests to reading Catalog/policies
- **Live Kickoff**: Attendance required; interaction recorded
**Records & Transcript**: Quiz score, attendance, acknowledgment stored permanently.

---

## 7. Georgia References
- GNPEC Minimum Standards (Programmatic Integrity, Catalog, Credential/Records, Refund/Cancellation/Complaint)
- HIPAA Privacy Rule (45 CFR Part 164)
- OSHA (29 CFR 1910) – workplace safety

---

## Appendix A: Key Terms & Glossary
| Term | Definition |
|------|------------|
| PHI | [WRITE HERE] |
| Minimum Necessary | [WRITE HERE] |
| PPE | [WRITE HERE] |
| SAP | [WRITE HERE] |
| GNPEC | [WRITE HERE] |

---

## Appendix B: xAPI & H5P Activity Map
**Stable xAPI Object IDs** (use these in your LMS mapping):
- Welcome Carousel: `https://aada.edu/xapi/m1/welcome-carousel`
- Ethics Branching: `https://aada.edu/xapi/m1/ethics-branching`
- HIPAA Hotspot: `https://aada.edu/xapi/m1/hipaa-hotspot`
- Policy Match: `https://aada.edu/xapi/m1/policy-match`
- Final Quiz: `https://aada.edu/xapi/m1/final-quiz`
- Acknowledgment: `https://aada.edu/xapi/m1/acknowledgment`
- Live Kickoff: `https://aada.edu/xapi/m1/kickoff-live`

> **Assessment Hook**: Post quiz → emit `completed` + `passed/failed`; store score; unlock remediation if <80%.

---

### Author Notes
- Replace all **[WRITE HERE]** blocks with your final text.
- Keep headings (`##`, `###`) intact for LMS navigation.
- You can drop images into `/assets` and reference them: `assets/filename.png`.
"""

(out_dir / "Module_1_Lessons_Branded.md").write_text(md, encoding="utf-8")

checklist = """# Authoring Checklist – Module 1 (AADA, GA-localized)

## Narrative Sections
- [ ] 1. Welcome – mission, disclosure, GNPEC context
- [ ] 2. Professionalism & Ethics (2.1–2.3) – full text + 3 case studies
- [ ] 3. HIPAA & OSHA – definitions, examples, safeguards, reprocessing preview
- [ ] 4. Communication & Team Dynamics – phrase bank + safety culture
- [ ] 5. LMS & Policies – SAP, grading, refund, cancellation, complaint
- [ ] 6. Summary & Assessment – pass criteria, records/transcripts
- [ ] 7. References – confirm GA citations

## Interactivity (H5P)
- [ ] Ethics Branching – final prompts/feedback
- [ ] HIPAA Hotspot – timestamped hotspots & text
- [ ] Dialog Cards – phrasing set
- [ ] Policy Match – terms & definitions

## Assessment
- [ ] 25 graded items finalized (≥80% threshold communicated)
- [ ] Remediation items prepared (<80% pathway)
- [ ] Acknowledgment Form text

## Accessibility & Branding
- [ ] Alt text for images
- [ ] AADA gold/cream styling consistent
- [ ] Reading level checked
"""
(out_dir / "Authoring_Checklist.md").write_text(checklist, encoding="utf-8")

print(f"✅ Created:\n  {out_dir/'Module_1_Lessons_Branded.md'}\n  {out_dir/'Authoring_Checklist.md'}")
print("Next:")
print("1) Fill in all [WRITE HERE] blocks.")
print("2) Copy into aada_lms/app/static/modules/module1/ when ready.")
