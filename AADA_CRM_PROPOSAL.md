# AADA CRM Solution Proposal
**Integrated Student Recruitment & Relationship Management System**

**Version:** 1.0
**Date:** November 6, 2025
**Status:** Proposal - Development Ready

---

## Executive Summary

This proposal outlines a custom-built CRM (Customer Relationship Management) system designed specifically for Atlanta Academy of Dental Assisting (AADA) that seamlessly integrates with the existing LMS/SIS infrastructure. The solution will manage the complete student lifecycle from initial inquiry through enrollment, providing comprehensive recruitment pipeline management, communication tracking, and relationship nurturing capabilities.

**Key Benefits:**
- **Seamless Integration**: Built on existing tech stack (FastAPI/PostgreSQL/React)
- **Unified Data Model**: Direct integration with current user/enrollment systems
- **Role-Based Access**: Leverages existing RBAC for admissions staff
- **HIPAA Compliant**: Maintains existing security standards
- **Cost Effective**: No third-party licensing fees or integration complexity

---

## 1. CRM Requirements for Educational Institution

### 1.1 Lead Management
- **Lead Capture**: Web forms, phone inquiries, events, referrals
- **Lead Qualification**: Scoring system based on program interest, readiness, demographics
- **Lead Assignment**: Auto-assign to admissions counselors based on rules
- **Lead Nurturing**: Automated email sequences, follow-up reminders
- **Conversion Tracking**: Lead → Applicant → Enrolled Student

### 1.2 Application Management
- **Application Portal**: Online application submission
- **Document Management**: Upload/track transcripts, certifications, ID documents
- **Application Review Workflow**: Multi-step approval process
- **Interview Scheduling**: Calendar integration for admissions interviews
- **Decision Tracking**: Accepted/Rejected/Waitlisted status management

### 1.3 Communication Hub
- **Activity Timeline**: Complete history of all interactions
- **Email Integration**: Log/send emails directly from CRM
- **Call Logging**: Track phone conversations with notes
- **SMS Integration**: Text message campaigns and reminders
- **Task Management**: Follow-up reminders and to-dos

### 1.4 Enrollment Pipeline
- **Pipeline Stages**: Inquiry → Lead → Applicant → Accepted → Enrolled
- **Stage Automation**: Trigger actions on stage changes
- **Pipeline Analytics**: Conversion rates, bottlenecks, forecasting
- **Bulk Actions**: Mass email, stage updates, assignments

### 1.5 Reporting & Analytics
- **Lead Source Attribution**: ROI on marketing channels
- **Conversion Funnels**: Drop-off analysis at each stage
- **Counselor Performance**: Leads handled, conversion rates, response times
- **Enrollment Forecasting**: Predictive analytics for upcoming cohorts
- **Custom Reports**: Filterable dashboards for different roles

---

## 2. System Architecture

### 2.1 Technology Stack (Existing + Extensions)

**Backend:**
```
- Framework: FastAPI (Python 3.11+)
- Database: PostgreSQL 14+
- ORM: SQLAlchemy
- Migrations: Alembic
- Task Queue: Celery + Redis (NEW - for email automation)
- Email: SendGrid API (NEW)
- SMS: Twilio API (NEW - optional)
```

**Frontend:**
```
- Framework: React 18+ (TypeScript)
- Portal: Admin Portal (existing) + New CRM Module
- State Management: React Query
- UI Library: Existing component library
- Forms: React Hook Form + Zod validation
```

**Infrastructure:**
```
- Deployment: Docker Compose (existing)
- Background Jobs: Redis + Celery workers
- File Storage: Local filesystem → S3 (future)
```

### 2.2 Integration Points with Existing LMS/SIS

```
┌─────────────────────────────────────────────────────────┐
│                    AADA LMS/SIS                         │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────┐         ┌──────────────────┐    │
│  │   CRM MODULE     │◄────────┤  EXISTING LMS    │    │
│  │                  │         │                  │    │
│  │ • Leads          │         │ • Users          │    │
│  │ • Applications   │────────►│ • Enrollments    │    │
│  │ • Communications │         │ • Programs       │    │
│  │ • Activities     │         │ • RBAC           │    │
│  │ • Documents      │         │ • Audit Logs     │    │
│  └──────────────────┘         └──────────────────┘    │
│          │                             │               │
│          └─────────────┬───────────────┘               │
│                        │                               │
│              ┌─────────▼─────────┐                     │
│              │  Shared Database  │                     │
│              │   (PostgreSQL)    │                     │
│              └───────────────────┘                     │
└─────────────────────────────────────────────────────────┘
```

**Key Integration Points:**

1. **User Conversion**: When lead/applicant is accepted → create User record → trigger enrollment
2. **Program Integration**: Applications reference existing Program records
3. **RBAC Extension**: New roles (admissions_counselor, admissions_manager)
4. **Audit Logging**: CRM activities logged to existing audit system
5. **Document Storage**: Reuse existing document management patterns

---

## 3. Database Schema Design

### 3.1 New CRM Schema

```sql
-- Create CRM schema
CREATE SCHEMA IF NOT EXISTS crm;

-- ============================================
-- LEADS TABLE
-- ============================================
CREATE TABLE crm.leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Contact Information
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    secondary_phone VARCHAR(20),
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(2),
    zip_code VARCHAR(10),

    -- Lead Details
    lead_source VARCHAR(50) NOT NULL, -- web_form, phone, event, referral, social_media
    lead_source_detail TEXT, -- Specific campaign, referral name, event name
    program_interest_id UUID REFERENCES programs(id),
    intended_start_date DATE,

    -- Qualification
    lead_status VARCHAR(50) NOT NULL DEFAULT 'new', -- new, contacted, qualified, nurturing, converted, disqualified
    lead_score INT DEFAULT 0, -- 0-100 scoring
    qualification_notes TEXT,

    -- Assignment
    assigned_to_id UUID REFERENCES users(id),
    assigned_at TIMESTAMPTZ,

    -- Tracking
    first_contact_date DATE,
    last_contact_date DATE,
    next_follow_up_date DATE,
    contact_count INT DEFAULT 0,

    -- Conversion
    converted_to_application_id UUID, -- Reference to applications table
    converted_at TIMESTAMPTZ,
    conversion_type VARCHAR(50), -- applied, enrolled_direct, disqualified

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by_id UUID REFERENCES users(id),

    -- Indexes
    CONSTRAINT unique_lead_email UNIQUE(email)
);

CREATE INDEX idx_leads_status ON crm.leads(lead_status);
CREATE INDEX idx_leads_assigned_to ON crm.leads(assigned_to_id);
CREATE INDEX idx_leads_source ON crm.leads(lead_source);
CREATE INDEX idx_leads_program_interest ON crm.leads(program_interest_id);
CREATE INDEX idx_leads_next_follow_up ON crm.leads(next_follow_up_date) WHERE next_follow_up_date IS NOT NULL;


-- ============================================
-- APPLICATIONS TABLE
-- ============================================
CREATE TABLE crm.applications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Applicant (may or may not have lead)
    lead_id UUID REFERENCES crm.leads(id), -- NULL if direct application

    -- Application Details
    application_number VARCHAR(50) UNIQUE NOT NULL, -- APP-2025-00001
    application_status VARCHAR(50) NOT NULL DEFAULT 'submitted',
    -- submitted, under_review, interview_scheduled, accepted, rejected, waitlisted, enrolled

    -- Contact Information (duplicated from lead for direct applicants)
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(20),

    -- Program Details
    program_id UUID NOT NULL REFERENCES programs(id),
    intended_start_date DATE NOT NULL,
    enrollment_type VARCHAR(50) NOT NULL, -- full_time, part_time

    -- Background Information
    date_of_birth DATE,
    ssn_last_four VARCHAR(4), -- Encrypted in production
    has_prior_healthcare_experience BOOLEAN,
    prior_healthcare_details TEXT,
    has_criminal_record BOOLEAN,
    criminal_record_details TEXT,

    -- Education History (JSON for flexibility)
    education_history JSONB, -- [{school, degree, year, gpa}, ...]

    -- Interview
    interview_scheduled_date TIMESTAMPTZ,
    interview_completed_date TIMESTAMPTZ,
    interview_notes TEXT,
    interviewer_id UUID REFERENCES users(id),
    interview_score INT, -- 1-10

    -- Decision
    decision VARCHAR(50), -- accepted, rejected, waitlisted
    decision_date DATE,
    decision_by_id UUID REFERENCES users(id),
    decision_notes TEXT,
    rejection_reason VARCHAR(100),

    -- Enrollment Conversion
    enrolled_as_user_id UUID REFERENCES users(id),
    enrolled_at TIMESTAMPTZ,
    enrollment_id UUID REFERENCES enrollments(id),

    -- Financial
    financial_aid_requested BOOLEAN DEFAULT FALSE,
    estimated_tuition_cost DECIMAL(10,2),

    -- Metadata
    submitted_at TIMESTAMPTZ DEFAULT NOW(),
    reviewed_at TIMESTAMPTZ,
    reviewed_by_id UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT unique_application_email_program UNIQUE(email, program_id, intended_start_date)
);

CREATE INDEX idx_applications_status ON crm.applications(application_status);
CREATE INDEX idx_applications_program ON crm.applications(program_id);
CREATE INDEX idx_applications_lead ON crm.applications(lead_id);
CREATE INDEX idx_applications_number ON crm.applications(application_number);


-- ============================================
-- ACTIVITIES TABLE (Communication Log)
-- ============================================
CREATE TABLE crm.activities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Related Entity (polymorphic)
    entity_type VARCHAR(50) NOT NULL, -- lead, application, user
    entity_id UUID NOT NULL, -- ID of lead, application, or user

    -- Activity Details
    activity_type VARCHAR(50) NOT NULL, -- call, email, sms, meeting, note, task, document_upload
    direction VARCHAR(20), -- inbound, outbound (for calls/emails)
    subject VARCHAR(255),
    description TEXT,
    outcome VARCHAR(50), -- completed, no_answer, voicemail, email_sent, email_opened, etc.

    -- Scheduling (for tasks/meetings)
    due_date TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    is_completed BOOLEAN DEFAULT FALSE,

    -- Assignment
    assigned_to_id UUID REFERENCES users(id),
    completed_by_id UUID REFERENCES users(id),

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by_id UUID REFERENCES users(id)
);

CREATE INDEX idx_activities_entity ON crm.activities(entity_type, entity_id);
CREATE INDEX idx_activities_type ON crm.activities(activity_type);
CREATE INDEX idx_activities_assigned ON crm.activities(assigned_to_id);
CREATE INDEX idx_activities_due_date ON crm.activities(due_date) WHERE is_completed = FALSE;


-- ============================================
-- DOCUMENTS TABLE
-- ============================================
CREATE TABLE crm.documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Related Entity
    entity_type VARCHAR(50) NOT NULL, -- application, lead
    entity_id UUID NOT NULL,

    -- Document Details
    document_type VARCHAR(50) NOT NULL, -- transcript, id_copy, certification, resume, other
    file_name VARCHAR(255) NOT NULL,
    file_size_bytes BIGINT,
    mime_type VARCHAR(100),
    storage_path VARCHAR(500) NOT NULL, -- File path or S3 key

    -- Status
    document_status VARCHAR(50) DEFAULT 'pending_review', -- pending_review, approved, rejected, expired
    reviewed_at TIMESTAMPTZ,
    reviewed_by_id UUID REFERENCES users(id),
    review_notes TEXT,

    -- Metadata
    uploaded_at TIMESTAMPTZ DEFAULT NOW(),
    uploaded_by_id UUID REFERENCES users(id)
);

CREATE INDEX idx_documents_entity ON crm.documents(entity_type, entity_id);
CREATE INDEX idx_documents_type ON crm.documents(document_type);


-- ============================================
-- EMAIL TEMPLATES TABLE
-- ============================================
CREATE TABLE crm.email_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Template Details
    template_name VARCHAR(100) UNIQUE NOT NULL,
    template_type VARCHAR(50) NOT NULL, -- welcome, follow_up, interview_invite, acceptance, rejection
    subject VARCHAR(255) NOT NULL,
    body_html TEXT NOT NULL,
    body_plain TEXT NOT NULL,

    -- Variables (JSON list of available variables)
    available_variables JSONB, -- ['first_name', 'program_name', 'start_date', ...]

    -- Metadata
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by_id UUID REFERENCES users(id)
);


-- ============================================
-- EMAIL CAMPAIGNS TABLE
-- ============================================
CREATE TABLE crm.email_campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Campaign Details
    campaign_name VARCHAR(100) NOT NULL,
    campaign_type VARCHAR(50) NOT NULL, -- one_time, drip_sequence
    template_id UUID REFERENCES crm.email_templates(id),

    -- Targeting
    target_audience VARCHAR(50), -- all_leads, qualified_leads, applicants, custom_filter
    custom_filter_criteria JSONB, -- {lead_status: 'qualified', program_id: 'xxx'}

    -- Scheduling
    send_at TIMESTAMPTZ,
    sent_at TIMESTAMPTZ,
    campaign_status VARCHAR(50) DEFAULT 'draft', -- draft, scheduled, sending, sent, paused

    -- Stats
    total_recipients INT DEFAULT 0,
    emails_sent INT DEFAULT 0,
    emails_opened INT DEFAULT 0,
    emails_clicked INT DEFAULT 0,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by_id UUID REFERENCES users(id)
);


-- ============================================
-- PIPELINE STAGES TABLE (for custom pipelines)
-- ============================================
CREATE TABLE crm.pipeline_stages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    stage_name VARCHAR(50) NOT NULL,
    stage_order INT NOT NULL,
    stage_color VARCHAR(7), -- Hex color for UI
    is_active BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Default stages
INSERT INTO crm.pipeline_stages (stage_name, stage_order, stage_color) VALUES
('Inquiry', 1, '#3B82F6'),
('Contacted', 2, '#8B5CF6'),
('Qualified', 3, '#10B981'),
('Application Submitted', 4, '#F59E0B'),
('Interview Scheduled', 5, '#EC4899'),
('Accepted', 6, '#14B8A6'),
('Enrolled', 7, '#22C55E');
```

### 3.2 New RBAC Roles

```sql
-- Add new CRM roles
INSERT INTO roles (id, name, description) VALUES
(gen_random_uuid(), 'admissions_counselor', 'Admissions counselor - manage leads and applications'),
(gen_random_uuid(), 'admissions_manager', 'Admissions manager - oversee admissions team and reporting');
```

---

## 4. API Endpoints

### 4.1 Lead Management API

```python
# /api/crm/leads

POST   /api/crm/leads                    # Create new lead
GET    /api/crm/leads                    # List leads (with filters)
GET    /api/crm/leads/{lead_id}          # Get lead details
PUT    /api/crm/leads/{lead_id}          # Update lead
DELETE /api/crm/leads/{lead_id}          # Delete lead (soft delete)
POST   /api/crm/leads/{lead_id}/assign   # Assign lead to counselor
POST   /api/crm/leads/{lead_id}/convert  # Convert lead to application
GET    /api/crm/leads/{lead_id}/timeline # Get activity timeline
POST   /api/crm/leads/bulk-import        # Import leads from CSV
```

**Example Request:**
```json
POST /api/crm/leads
{
  "first_name": "Sarah",
  "last_name": "Johnson",
  "email": "sarah.j@example.com",
  "phone": "404-555-0123",
  "lead_source": "web_form",
  "lead_source_detail": "Facebook Ad - Spring 2025 Campaign",
  "program_interest_id": "program-uuid",
  "intended_start_date": "2025-03-01"
}
```

**Example Response:**
```json
{
  "id": "lead-uuid",
  "first_name": "Sarah",
  "last_name": "Johnson",
  "email": "sarah.j@example.com",
  "lead_status": "new",
  "lead_score": 65,
  "assigned_to": {
    "id": "user-uuid",
    "name": "Rita Registrar"
  },
  "program_interest": {
    "id": "program-uuid",
    "name": "Medical Assistant Diploma"
  },
  "created_at": "2025-11-06T10:30:00Z"
}
```

### 4.2 Application Management API

```python
# /api/crm/applications

POST   /api/crm/applications                        # Create application
GET    /api/crm/applications                        # List applications
GET    /api/crm/applications/{app_id}               # Get application details
PUT    /api/crm/applications/{app_id}               # Update application
POST   /api/crm/applications/{app_id}/review        # Start review process
POST   /api/crm/applications/{app_id}/interview     # Schedule interview
POST   /api/crm/applications/{app_id}/decide        # Accept/Reject decision
POST   /api/crm/applications/{app_id}/enroll        # Convert to enrolled student
GET    /api/crm/applications/{app_id}/documents     # List documents
POST   /api/crm/applications/{app_id}/documents     # Upload document
```

### 4.3 Activity Tracking API

```python
# /api/crm/activities

POST   /api/crm/activities                    # Log activity
GET    /api/crm/activities                    # List activities
GET    /api/crm/activities/{activity_id}      # Get activity details
PUT    /api/crm/activities/{activity_id}      # Update activity
DELETE /api/crm/activities/{activity_id}      # Delete activity
POST   /api/crm/activities/{activity_id}/complete # Mark task complete
```

### 4.4 Email Campaign API

```python
# /api/crm/campaigns

POST   /api/crm/campaigns              # Create campaign
GET    /api/crm/campaigns              # List campaigns
GET    /api/crm/campaigns/{id}         # Get campaign details
POST   /api/crm/campaigns/{id}/send    # Send/schedule campaign
GET    /api/crm/campaigns/{id}/stats   # Campaign statistics
```

### 4.5 Reporting API

```python
# /api/crm/reports

GET    /api/crm/reports/pipeline               # Pipeline overview
GET    /api/crm/reports/conversion-funnel      # Conversion funnel
GET    /api/crm/reports/lead-sources           # Lead source performance
GET    /api/crm/reports/counselor-performance  # Counselor metrics
GET    /api/crm/reports/forecast               # Enrollment forecast
```

---

## 5. User Interface Components

### 5.1 CRM Dashboard (Admin Portal)

**Main Navigation:**
```
┌─────────────────────────────────────────────────┐
│  AADA LMS - CRM Module                          │
├─────────────────────────────────────────────────┤
│  Dashboard | Leads | Applications | Activities  │
│  Reports | Settings                             │
└─────────────────────────────────────────────────┘
```

**Dashboard Widgets:**
1. **Pipeline Overview**: Visual funnel showing leads at each stage
2. **Today's Tasks**: Follow-ups, interviews, application reviews due today
3. **My Leads**: Quick access to assigned leads
4. **Recent Activities**: Latest interactions across all leads/applications
5. **Key Metrics**: Conversion rates, average time-to-enroll, lead velocity

### 5.2 Lead Management Interface

**Lead List View:**
- Filterable table (status, source, program, assigned counselor)
- Sortable columns
- Bulk actions (assign, email, update status)
- Quick view panel

**Lead Detail View:**
```
┌──────────────────────────────────────────────────────┐
│  Sarah Johnson                       [Edit] [Convert]│
│  sarah.j@example.com | 404-555-0123                 │
│  Status: Qualified | Score: 75/100                  │
├──────────────────────────────────────────────────────┤
│  Program Interest: Medical Assistant Diploma        │
│  Start Date: March 2025                             │
│  Source: Facebook Ad - Spring Campaign              │
│  Assigned To: Rita Registrar                        │
│  Next Follow-up: Nov 10, 2025                       │
├──────────────────────────────────────────────────────┤
│  TIMELINE                                            │
│  ┌────────────────────────────────────────────────┐ │
│  │ [📞] Phone Call - Nov 5, 2025 10:30 AM        │ │
│  │     Discussed program details, very interested │ │
│  │     Next: Send program brochure                │ │
│  │                                                 │ │
│  │ [📧] Email Sent - Nov 3, 2025 2:15 PM         │ │
│  │     Welcome email - Opened Nov 3, 3:22 PM     │ │
│  │                                                 │ │
│  │ [🌐] Lead Created - Nov 3, 2025 2:00 PM       │ │
│  │     Source: Facebook Ad                        │ │
│  └────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────┘
```

### 5.3 Application Review Interface

**Application List:**
- Status-based views (Submitted, Under Review, Interview Scheduled, etc.)
- Reviewer assignment
- Batch processing

**Application Detail:**
- Applicant information
- Document checklist with review status
- Interview scheduling
- Decision workflow (Accept/Reject/Waitlist with notes)
- Enrollment button (creates User + Enrollment records)

### 5.4 Activity Log Interface

**Quick Add Activity:**
- Type selector (Call, Email, SMS, Meeting, Note, Task)
- Entity selector (Which lead/application)
- Date/time picker
- Description field
- Outcome selector

**Task Management:**
- My Tasks view (Today, This Week, Overdue)
- Task creation with due dates
- Task completion tracking

---

## 6. Development Phases

### Phase 1: Foundation (2-3 weeks)
**Goal:** Core CRM database and lead management

**Tasks:**
1. Create CRM database schema (leads, activities, documents tables)
2. Implement Lead CRUD API endpoints
3. Build basic Lead list/detail pages in Admin Portal
4. Implement lead assignment functionality
5. Create activity logging API
6. Basic timeline view for lead activities

**Deliverables:**
- ✅ Leads can be created manually or via API
- ✅ Counselors can view assigned leads
- ✅ Activities can be logged against leads
- ✅ Simple lead list and detail views

### Phase 2: Application Management (3-4 weeks)
**Goal:** Application submission and review workflow

**Tasks:**
1. Create applications database table
2. Build application submission API
3. Implement document upload/management
4. Create application review workflow
5. Build application list/detail UI
6. Implement interview scheduling
7. Create decision workflow (Accept/Reject)
8. Build enrollment conversion (Application → User + Enrollment)

**Deliverables:**
- ✅ Applicants can submit applications online
- ✅ Staff can review applications and documents
- ✅ Interview scheduling and tracking
- ✅ Accept/Reject workflow
- ✅ Accepted applicants automatically create User + Enrollment

### Phase 3: Communication & Automation (2-3 weeks)
**Goal:** Email campaigns and automated follow-ups

**Tasks:**
1. Integrate SendGrid for email sending
2. Create email templates system
3. Build email campaign API
4. Implement Celery + Redis for background jobs
5. Create automated email sequences (nurture campaigns)
6. Build email template editor UI
7. Implement email tracking (opens, clicks)
8. Add SMS integration (optional - Twilio)

**Deliverables:**
- ✅ Email templates for common scenarios
- ✅ Bulk email campaigns
- ✅ Automated drip email sequences
- ✅ Email tracking and analytics

### Phase 4: Reporting & Analytics (2 weeks)
**Goal:** Dashboards and performance metrics

**Tasks:**
1. Build pipeline report (conversion funnel)
2. Create lead source attribution report
3. Implement counselor performance metrics
4. Build enrollment forecasting
5. Create dashboard with key widgets
6. Implement custom report builder
7. Add export functionality (CSV/PDF)

**Deliverables:**
- ✅ Visual pipeline dashboard
- ✅ Lead source ROI analysis
- ✅ Counselor performance tracking
- ✅ Enrollment forecasting
- ✅ Custom reports and exports

### Phase 5: Advanced Features (2-3 weeks)
**Goal:** Enhanced functionality and optimization

**Tasks:**
1. Lead scoring algorithm
2. Bulk import from CSV
3. Advanced search and filtering
4. Calendar integration for interviews/meetings
5. Mobile-responsive optimizations
6. Notification system (email/in-app)
7. Integration with existing xAPI for CRM events
8. Performance optimization and caching

**Deliverables:**
- ✅ Intelligent lead scoring
- ✅ CSV import for bulk lead creation
- ✅ Advanced search capabilities
- ✅ Calendar sync
- ✅ Push notifications

---

## 7. Integration with Existing LMS

### 7.1 User Conversion Flow

When an application is accepted and enrolled:

```python
# Pseudo-code for enrollment conversion
def convert_application_to_enrollment(application_id: UUID, enrolling_user_id: UUID):
    """
    Convert accepted application into enrolled student.
    Creates User record and Enrollment record.
    """
    # 1. Get application
    application = db.query(Application).filter(Application.id == application_id).first()

    # 2. Create User record
    user = User(
        email=application.email,
        first_name=application.first_name,
        last_name=application.last_name,
        status="active",
        # Send password reset email
    )
    db.add(user)
    db.flush()

    # 3. Assign "student" role
    student_role = db.query(Role).filter(Role.name == "student").first()
    db.add(UserRole(user_id=user.id, role_id=student_role.id))

    # 4. Create Enrollment record
    enrollment = Enrollment(
        user_id=user.id,
        program_id=application.program_id,
        start_date=application.intended_start_date,
        status="active"
    )
    db.add(enrollment)
    db.flush()

    # 5. Update application record
    application.enrolled_as_user_id = user.id
    application.enrolled_at = datetime.now()
    application.enrollment_id = enrollment.id
    application.application_status = "enrolled"

    # 6. Log activity
    log_activity(
        entity_type="application",
        entity_id=application.id,
        activity_type="enrollment_created",
        description=f"Application converted to enrollment. User: {user.email}",
        created_by_id=enrolling_user_id
    )

    # 7. Trigger welcome email
    send_welcome_email(user.email, user.first_name, enrollment.program.name)

    db.commit()
    return user, enrollment
```

### 7.2 Shared Data Access

**CRM can read from LMS:**
- Programs (for application program selection)
- Users (for lead/application assignment)
- Enrollments (to check if converted student is active)

**LMS can read from CRM:**
- Lead/Application data for student context
- Activity history for student support

---

## 8. Technical Specifications

### 8.1 Performance Requirements

- **Page Load Time**: < 2 seconds for all CRM pages
- **API Response Time**: < 500ms for all CRUD operations
- **Bulk Operations**: Process 1000+ leads/emails within 5 minutes
- **Concurrent Users**: Support 50+ simultaneous admissions staff

### 8.2 Security Requirements

- **RBAC**: Only admissions_counselor, admissions_manager, admin, staff can access CRM
- **Data Encryption**: Encrypt SSN, date of birth at rest (pgcrypto)
- **Audit Logging**: Log all CRM activities to existing audit system
- **HIPAA Compliance**: Maintain existing HIPAA compliance standards
- **Document Security**: Secure file storage with access controls

### 8.3 Data Retention

- **Active Leads**: Retained indefinitely while active
- **Converted Leads**: Archived after conversion (soft delete)
- **Disqualified Leads**: Archived after 1 year
- **Applications**: Retained for 7 years (compliance requirement)
- **Activities**: Retained indefinitely for historical tracking
- **Documents**: Retained for 7 years

---

## 9. Development Timeline

**Total Estimated Time: 12-15 weeks**

```
Week 1-3:   Phase 1 - Foundation (Lead Management)
Week 4-7:   Phase 2 - Application Management
Week 8-10:  Phase 3 - Communication & Automation
Week 11-12: Phase 4 - Reporting & Analytics
Week 13-15: Phase 5 - Advanced Features & Polish
```

**Parallel Development Opportunities:**
- Backend API development (Weeks 1-10)
- Frontend UI development (Weeks 2-12, can start after Phase 1 APIs)
- Testing and QA (Ongoing throughout)

---

## 10. Cost Estimates

### 10.1 Development Costs
- **Phase 1-2 (Core CRM)**: 6-7 weeks development
- **Phase 3-4 (Automation + Reporting)**: 4 weeks development
- **Phase 5 (Advanced Features)**: 2-3 weeks development

### 10.2 Operational Costs (Monthly)
- **SendGrid Email**: $0-15/month (up to 40k emails, then $0.001/email)
- **Twilio SMS** (optional): ~$0.0075/SMS
- **Redis**: Free (self-hosted in Docker)
- **Additional Storage**: Minimal (documents)

**Total Monthly Operating Cost: $15-50** (depending on email/SMS volume)

---

## 11. Success Metrics

### 11.1 System Performance
- ✅ 100% uptime during business hours
- ✅ < 500ms API response times
- ✅ Zero data loss

### 11.2 Business Impact
- **Increased Conversion**: 15-25% improvement in lead-to-enrollment conversion
- **Reduced Time-to-Enroll**: 30% faster application processing
- **Improved Response Time**: < 24 hour response to all new leads
- **Better Lead Attribution**: Clear ROI on all marketing channels
- **Higher Staff Efficiency**: 40% more leads managed per counselor

---

## 12. Risk Mitigation

### 12.1 Technical Risks
- **Risk**: Data migration complexity
  - **Mitigation**: Phase 1 starts fresh, migrate historical data later

- **Risk**: Email deliverability issues
  - **Mitigation**: Use SendGrid (established provider), implement DKIM/SPF

- **Risk**: Performance degradation with large datasets
  - **Mitigation**: Proper indexing, pagination, caching strategy

### 12.2 Business Risks
- **Risk**: Staff adoption challenges
  - **Mitigation**: Training sessions, intuitive UI, gradual rollout

- **Risk**: Integration bugs with existing LMS
  - **Mitigation**: Comprehensive testing, staging environment

---

## 13. Next Steps

1. **Review & Approve** this proposal
2. **Prioritize Features** - Confirm Phase 1-5 priorities
3. **Set Timeline** - Confirm development start date
4. **Assign Resources** - Development team allocation
5. **Create Detailed Specs** - Phase 1 technical specifications
6. **Setup Infrastructure** - Redis, SendGrid accounts
7. **Begin Development** - Phase 1 kickoff

---

## Appendix A: API Endpoint Reference

Complete API documentation will be available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

All CRM endpoints will be versioned: `/api/crm/v1/*`

---

## Appendix B: UI Mockups

Detailed UI mockups for each component will be created in Phase 1 planning.

Key screens:
1. CRM Dashboard
2. Lead List View
3. Lead Detail View
4. Application List View
5. Application Detail View
6. Application Review Interface
7. Interview Scheduling
8. Email Campaign Builder
9. Pipeline Kanban Board
10. Reports Dashboard

---

**Document Version History:**
- v1.0 (2025-11-06): Initial proposal

**Author:** Claude Code
**Contact:** For questions or clarifications, please refer to the AADA LMS Systems Integration Specification
