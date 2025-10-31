# Codex Instructions – Build Module 1 (Orientation & Professional Foundations)

## Objective
Generate a **complete instructional manuscript** for **Module 1 – Orientation & Professional Foundations** of the **Atlanta Academy of Dental Assisting (AADA)** program.

**Goal:** produce a single Markdown file `aada_lms/app/static/modules/module1/Module_1_Lessons_Branded.md` containing 12 000–15 000 words (~25 pages) of verified, Georgia-localized instructional content aligned with GNPEC, OSHA, and HIPAA requirements.



## Instructional Design Parameters

Each module in the AADA program must align to the approved **program clock hours** and **GNPEC Standard 1** requirements for theory + practice balance.

| Parameter                    | Requirement                                                  | Notes                                                        |
| ---------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| **Total program length**     | ~920 clock hours                                             | Distributed across 10 modules                                |
| **Module 1 duration**        | **40 clock hours** (theory + orientation)                    | Includes 34 hours asynchronous/self-paced + 6 hours live (kickoff + Q&A) |
| **Equivalent text volume**   | ~12 000 – 15 000 words (≈ 25 pages of narrative)             | 1 hour ≈ 300–400 words of substantive instructional text     |
| **Reading : Practice ratio** | 70 % theory reading / 30 % interactivity (H5P, quizzes, discussions) | Matches GNPEC Std 1.2 (e–f)                                  |
| **Assessment time**          | 1 clock hour (25 graded + 10 practice questions)             | Quizzes, reflection activities                               |
| **Remediation allowance**    | 10 % of module hours                                         | Optional retake and review work                              |
| **Instructor-led sessions**  | 2 live events (orientation and Q&A)                          | Required for meaningful interaction per GNPEC Std 1.10(b)    |

Codex must ensure that:
- The instructional text length aligns with the **40-hour module** target.  
- The pacing reflects **student engagement for adult learners** (reading, interaction, reflection).  
- Each section clearly identifies the **approximate time on task**, e.g.:

---

## Search & Source Policy
Codex must actively search the public web and restrict factual material to **authoritative domains**.

**Allow only:**
- `gnpec.georgia.gov`
- `gbd.georgia.gov`
- `osha.gov`
- `cdc.gov`
- `hhs.gov`
- `ada.org`
- `danb.org`
- `cdcfoundation.org`
- `ed.gov`
- `nih.gov`
- `who.int`
- `georgia.gov`

**Disallow:**
- `wikipedia.org`
- commercial / marketing / AI-generated / content-farm sites

Each factual paragraph must include an inline citation such as:  
`(CDC, 2016, https://www.cdc.gov/oralhealth/infectioncontrol/guidelines)`

If a claim cannot be verified, omit it or mark `[VERIFY SOURCE]`.

---

## Writing Guidelines
1. **Tone:** professional, instructional, grade-12 reading level.  
2. **Audience:** dental-assistant students in Georgia (ages 18–35).  
3. **Compliance:**  
   - GNPEC Standards 1, 4, 5 – 6, 12 – 14  
   - Georgia Board of Dentistry Rules (O.C.G.A. § 43-11; GA Rule 150-14)  
   - OSHA 29 CFR 1910 (infection control & PPE)  
   - HIPAA 45 CFR Part 160–164  
   - CDC Guidelines for Infection Control in Dental Settings (2003/2016)  
4. **Branding:** use AADA gold `#D5AA42` / cream `#FFFDF9` palette; include `![AADA Logo](assets/aada_logo.png)` at the top.  
5. **Structure:** follow the section layout below exactly so LMS anchors and xAPI/H5P mappings remain valid.  
6. **Length:** ~12 000–15 000 words (≈ 25 pages).  
7. **Include:**  
   - Georgia-specific regulatory references  
   - at least 3 case studies (ethics, HIPAA, communication)  
   - 10–15 inline “Knowledge Check” callouts  
   - complete glossary (≥ 30 terms)  
   - inline H5P/xAPI cues using existing IDs.  

---

## Section Outline

```markdown
# Module 1 – Orientation & Professional Foundations
**Atlanta Academy of Dental Assisting (AADA)**  
![AADA Logo](assets/aada_logo.png)

> **Delivery:** Online + Live (1 Kick-off) | **Estimated Time:** ~40 hours  
> **Georgia/GNPEC Alignment:** Standards 1, 4, 5 – 6, 12 – 14

## 1. Welcome to AADA (Georgia Context)
### 1.1 Mission and Program Authorization
### 1.2 Learning Objectives
### 1.3 GNPEC Requirements Overview
### 1.4 Student Expectations & Success Tips  

## 2. Professionalism & Ethics
### 2.1 Professional Conduct in Georgia Dental Settings
### 2.2 Ethical Decision Framework
### 2.3 Case Studies and Discussion Prompts  
> **Interactive Activity 1 – Ethics Branching (H5P: `M1_H5P_EthicsBranching`)**

## 3. HIPAA & OSHA Essentials
### 3.1 HIPAA Privacy Rule (45 CFR Part 164)
### 3.2 OSHA (29 CFR 1910) in Dental Settings
### 3.3 Infection-Control Basics (Preview of Lab)  
> **Interactive Activity 2 – HIPAA Hotspot (H5P: `M1_H5P_HIPAAHotspot`)**

## 4. Communication & Team Dynamics
### 4.1 Patient-Centered Communication
### 4.2 Teamwork & Safety Culture  
> **Interactive Activity 3 – Dialog Cards (H5P: `M1_H5P_DialogCards`)**

## 5. Orientation to LMS & Student Policies
### 5.1 Using the AADA LMS
### 5.2 Satisfactory Academic Progress (SAP) and Grading
### 5.3 Refund, Cancellation, and Complaint Policies (GNPEC Stds 12–14)  
> **Interactive Activity 4 – Policy Match (H5P: `M1_H5P_PolicyMatch`)**

## 6. Summary & Assessment
### 6.1 Knowledge Check Overview
### 6.2 Acknowledgment Form Instructions
### 6.3 Transcript & Record Retention (GNPEC Stds 5–6)

## 7. Georgia References
## Appendix A: Key Terms & Glossary
## Appendix B: xAPI & H5P Activity Map