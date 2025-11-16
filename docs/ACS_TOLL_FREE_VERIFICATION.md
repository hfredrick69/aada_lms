# Azure Communication Services Toll-Free Verification Form

**Phone Number:** +1 833-547-6172
**Submission Location:** Azure Portal > Communication Services > Regulatory Documents > Add

---

## 1. APPLICATION TYPE

- **Country/Region:** United States
- **Phone Number:** +1 833-547-6172
- **Use Case:** Student enrollment notifications and appointment reminders for vocational training school

---

## 2. COMPANY DETAILS

- **Company Name:** Atlanta Academy of Dental Assisting
- **Company Website:** https://atlantaacademyofdentalassisting.com
  - **IMPORTANT:** Use your PUBLIC website URL, NOT the portal/app URL
- **Contact Name:** [Your name]
- **Contact Email:** [Your email]
- **Contact Phone:** [Your phone]

---

## 3. PROGRAM CONTENT

### Program Description

```
AADA is a vocational dental assisting school. We send transactional SMS notifications to enrolled/prospective students: enrollment agreement signing reminders, class schedule reminders, appointment confirmations, and administrative updates. All messages are informational and sent only to individuals who provide phone number and explicit consent during enrollment.
```
**(~330 chars)**

### Opt-In Method

**Website Form** (during enrollment/lead capture)

### Opt-In Process Description

```
Users opt-in via enrollment form with unchecked consent checkbox: "I consent to receive SMS from AADA regarding enrollment, schedules, and updates. Message frequency varies. Msg&data rates apply. Reply STOP to opt out. Reply HELP for help." Checkbox must be actively selected to submit; not pre-checked.
```
**(~295 chars)**

### Required Screenshot

You MUST provide a screenshot showing the opt-in checkbox on your lead/enrollment form. The screenshot should clearly show:
- The phone number input field
- The unchecked consent checkbox
- The full disclaimer text visible at time of collection

---

## 4. VOLUME ESTIMATE

**Monthly Message Volume:** 500-1000 messages

Breakdown:
- ~50 active students + prospects
- 10-20 messages/month per person (reminders, agreements, appointments)

---

## 5. MESSAGE TEMPLATES

### Template 1: Enrollment Agreement Notification
```
Hi {FirstName}! Your AADA Dental Assisting enrollment agreement is ready to sign. Review and sign here: {URL} Link expires in 7 days. Msg&Data rates may apply. Reply STOP to opt out.
```

### Template 2: Agreement Completed
```
Congratulations {FirstName}! Your AADA Dental Assisting enrollment agreement has been fully executed. Check your email for the signed PDF. Welcome to AADA! Msg&Data rates may apply. Reply STOP to opt out.
```

### Template 3: Appointment Reminder
```
Hi {FirstName}! Reminder: Your AADA {AppointmentType} is scheduled for {DateTime} at {Location}. Msg&Data rates may apply. Reply STOP to opt out.
```

### Template 4: Class Reminder
```
Hi {FirstName}! Reminder: {ClassName} starts {DateTime}. See you there! Msg&Data rates may apply. Reply STOP to opt out.
```

---

## SUBMISSION CHECKLIST

- [ ] Add SMS consent checkbox to lead/enrollment forms in your portal
- [ ] Take screenshot of the form showing the consent checkbox
- [ ] Log into Azure Portal
- [ ] Navigate to: Communication Services > your resource > Regulatory Documents
- [ ] Click "Add" to start the verification wizard
- [ ] Fill in all sections using the content above
- [ ] Upload the opt-in screenshot
- [ ] Submit the application

---

## POST-SUBMISSION

- **Review Time:** 5-6 weeks
- **Status Updates:** Sent to the contact email you provided
- **After Approval:** Set `ACS_SENDER_PHONE=+18335476172` in Container App environment variables

---

## COMMON REJECTION REASONS

1. **Missing opt-in proof** - Must include screenshot showing consent checkbox
2. **Inaccessible URL** - Use your public website URL, not internal portal URL
3. **Pre-checked checkbox** - Consent checkbox must NOT be pre-checked
4. **Missing disclosures** - All messages must include "Reply STOP to opt out"
