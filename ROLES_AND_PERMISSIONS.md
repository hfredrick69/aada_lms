# AADA LMS - Roles and Permissions

## Overview
The AADA LMS uses Role-Based Access Control (RBAC) to manage what users can see and do in the system. There are 8 distinct roles, divided between staff roles (use Admin Portal) and student roles (use Student Portal).

---

## Portal Access

### Admin Portal (`/admin_portal`)
Used by all staff/administrative roles:
- Admin
- Staff
- Instructor
- Finance
- Registrar
- Admissions Counselor
- Admissions Manager

### Student Portal (`/frontend`)
Used by:
- Student

---

## Role Definitions

### 1. Admin
**Test Account:** admin@aada.edu / AdminPass!23

**Responsibilities:**
- System administration and configuration
- Full oversight of all operations
- User management across all roles
- System-wide reporting and analytics

**Data Access (CRUD):**
| Entity | Create | Read | Update | Delete |
|--------|--------|------|--------|--------|
| Users | ✅ | ✅ | ✅ | ✅ |
| Programs | ✅ | ✅ | ✅ | ✅ |
| Modules | ✅ | ✅ | ✅ | ✅ |
| Enrollments | ✅ | ✅ | ✅ | ✅ |
| Leads | ✅ | ✅ | ✅ | ✅ |
| Activities | ✅ | ✅ | ✅ | ✅ |
| Attendance | ✅ | ✅ | ✅ | ✅ |
| Skills Checkoffs | ✅ | ✅ | ✅ | ✅ |
| Externships | ✅ | ✅ | ✅ | ✅ |
| Financial Records | ✅ | ✅ | ✅ | ✅ |
| Transcripts | ✅ | ✅ | ✅ | ✅ |
| Credentials | ✅ | ✅ | ✅ | ✅ |
| Complaints | ✅ | ✅ | ✅ | ✅ |

**Admin Portal Pages:**
- ✅ Dashboard
- ✅ Students
- ✅ Leads
- ✅ Courses
- ✅ Payments
- ✅ Externships
- ✅ Reports
- ✅ Settings

---

### 2. Staff
**Test Account:** staff@aada.edu / StaffPass!23

**Responsibilities:**
- Day-to-day student management
- Course and enrollment administration
- Student records maintenance
- Instructor capabilities plus student CRUD

**Data Access (CRUD):**
| Entity | Create | Read | Update | Delete |
|--------|--------|------|--------|--------|
| Users (Students) | ✅ | ✅ | ✅ | ✅ |
| Programs | ❌ | ✅ | ❌ | ❌ |
| Modules | ✅ | ✅ | ✅ | ❌ |
| Enrollments | ✅ | ✅ | ✅ | ✅ |
| Leads | ✅ | ✅ | ✅ | ❌ |
| Activities | ✅ | ✅ | ✅ | ❌ |
| Attendance | ✅ | ✅ | ✅ | ❌ |
| Skills Checkoffs | ✅ | ✅ | ✅ | ❌ |
| Externships | ✅ | ✅ | ✅ | ❌ |

**Admin Portal Pages:**
- ✅ Dashboard
- ✅ Students
- ✅ Leads
- ✅ Courses
- ✅ Externships
- ❌ Payments (view only, no modifications)
- ✅ Reports

---

### 3. Instructor
**Test Account:** instructor@aada.edu / InstructorPass!23

**Responsibilities:**
- Teaching and course delivery
- Student progress tracking
- Grading and assessments
- Skills validation and checkoffs

**Data Access (CRUD):**
| Entity | Create | Read | Update | Delete |
|--------|--------|------|--------|--------|
| Users (Students) | ❌ | ✅ | ❌ | ❌ |
| Modules | ❌ | ✅ | ✅ | ❌ |
| Enrollments | ❌ | ✅ | ❌ | ❌ |
| Attendance | ✅ | ✅ | ✅ | ❌ |
| Skills Checkoffs | ✅ | ✅ | ✅ | ❌ |
| Module Progress | ❌ | ✅ | ✅ | ❌ |
| Grades | ✅ | ✅ | ✅ | ❌ |

**Admin Portal Pages:**
- ✅ Dashboard
- ✅ Students (view only)
- ✅ Courses
- ✅ Reports (their classes only)

---

### 4. Registrar
**Test Account:** registrar@aada.edu / RegistrarPass!23

**Responsibilities:**
- Academic records management
- Transcript generation and maintenance
- Credential/certification issuance
- Enrollment verification
- Academic compliance reporting

**Data Access (CRUD):**
| Entity | Create | Read | Update | Delete |
|--------|--------|------|--------|--------|
| Users (Students) | ❌ | ✅ | ✅ | ❌ |
| Enrollments | ❌ | ✅ | ✅ | ❌ |
| Transcripts | ✅ | ✅ | ✅ | ❌ |
| Credentials | ✅ | ✅ | ✅ | ❌ |
| Attendance | ❌ | ✅ | ❌ | ❌ |
| Skills Checkoffs | ❌ | ✅ | ❌ | ❌ |
| Grades | ❌ | ✅ | ✅ | ❌ |
| Compliance Reports | ✅ | ✅ | ✅ | ❌ |

**Admin Portal Pages:**
- ✅ Dashboard
- ✅ Students (records focus)
- ✅ Reports (compliance/academic)
- ❌ Leads
- ❌ Payments

---

### 5. Finance / Financial Aid Officer
**Test Account:** finance@aada.edu / FinancePass!23

**Responsibilities:**
- Payment processing and tracking
- Financial aid administration
- Tuition and fee management
- Withdrawal and refund processing
- Financial reporting

**Data Access (CRUD):**
| Entity | Create | Read | Update | Delete |
|--------|--------|------|--------|--------|
| Users (Students) | ❌ | ✅ | ❌ | ❌ |
| Financial Ledger | ✅ | ✅ | ✅ | ❌ |
| Payments | ✅ | ✅ | ✅ | ❌ |
| Refunds | ✅ | ✅ | ✅ | ❌ |
| Withdrawals | ✅ | ✅ | ✅ | ❌ |
| Enrollments | ❌ | ✅ | ❌ | ❌ |

**Admin Portal Pages:**
- ✅ Dashboard (financial metrics)
- ✅ Students (financial info only)
- ✅ Payments
- ✅ Reports (financial)

---

### 6. Admissions Counselor
**Test Account:** counselor@aada.edu / CounselorPass!23

**Responsibilities:**
- Lead management and follow-up
- Prospective student communication
- Campus tours and information sessions
- Application assistance
- Lead nurturing through pipeline

**Data Access (CRUD):**
| Entity | Create | Read | Update | Delete |
|--------|--------|------|--------|--------|
| Leads | ✅ | ✅ | ✅ | ❌ |
| Activities (Leads) | ✅ | ✅ | ✅ | ✅ |
| Lead Custom Fields | ✅ | ✅ | ✅ | ❌ |
| Programs | ❌ | ✅ | ❌ | ❌ |
| Users (Students) | ❌ | ✅ | ❌ | ❌ |

**Data Restrictions:**
- Can only see leads assigned to them (own leads)
- Cannot delete leads (only mark as lost)
- Cannot modify enrollment records

**Admin Portal Pages:**
- ✅ Dashboard (recruitment metrics)
- ✅ Leads
- ❌ Students (can view but not modify)
- ❌ Courses
- ❌ Payments

---

### 7. Admissions Manager
**Test Account:** admissions@aada.edu / AdmissionsPass!23

**Responsibilities:**
- Admissions team oversight
- Lead assignment and distribution
- Enrollment decision making
- Recruitment strategy and reporting
- All counselor responsibilities

**Data Access (CRUD):**
| Entity | Create | Read | Update | Delete |
|--------|--------|------|--------|--------|
| Leads | ✅ | ✅ | ✅ | ✅ |
| Activities (Leads) | ✅ | ✅ | ✅ | ✅ |
| Lead Custom Fields | ✅ | ✅ | ✅ | ✅ |
| Lead Sources | ✅ | ✅ | ✅ | ❌ |
| Programs | ❌ | ✅ | ❌ | ❌ |
| Users (Students) | ❌ | ✅ | ❌ | ❌ |
| Enrollments | ✅ | ✅ | ❌ | ❌ |

**Data Restrictions:**
- Can see ALL leads (not just assigned to them)
- Can assign/reassign leads to counselors
- Can approve/deny applications
- Cannot modify enrolled student records (handoff to registrar)

**Admin Portal Pages:**
- ✅ Dashboard (full recruitment analytics)
- ✅ Leads
- ✅ Students (view only)
- ❌ Courses
- ❌ Payments
- ✅ Reports (admissions/recruitment)

---

### 8. Student
**Test Accounts:**
- alice.student@aada.edu / AlicePass!23
- bob.student@aada.edu / BobLearner!23

**Responsibilities:**
- Complete coursework and modules
- Track own progress
- View grades and transcripts
- Manage financial obligations
- Access learning materials

**Data Access (CRUD):**
| Entity | Create | Read | Update | Delete |
|--------|--------|------|--------|--------|
| Own User Profile | ❌ | ✅ | ✅ | ❌ |
| Own Enrollments | ❌ | ✅ | ❌ | ❌ |
| Own Progress | ✅* | ✅ | ✅* | ❌ |
| Own Attendance | ❌ | ✅ | ❌ | ❌ |
| Own Grades | ❌ | ✅ | ❌ | ❌ |
| Own Transcript | ❌ | ✅ | ❌ | ❌ |
| Own Financial Records | ❌ | ✅ | ❌ | ❌ |
| Own Payments | ✅* | ✅ | ❌ | ❌ |
| Complaints | ✅ | ✅ | ❌ | ❌ |

*Creates through learning activity, not direct CRUD

**Data Restrictions:**
- Can ONLY see their own data
- Cannot see other students' information
- Cannot modify grades or official records
- Cannot delete any records

**Student Portal Pages:**
- ✅ Dashboard (personal progress)
- ✅ My Courses
- ✅ My Progress
- ✅ My Grades
- ✅ My Transcript
- ✅ My Financial Info
- ✅ Profile Settings

---

## Role Hierarchy

```
Admin (Full System Access)
  │
  ├─ Staff (Student + Course Management)
  │   └─ Instructor (Course Delivery)
  │
  ├─ Registrar (Academic Records)
  │
  ├─ Finance (Financial Management)
  │
  ├─ Admissions Manager (Full Recruitment)
  │   └─ Admissions Counselor (Lead Management)
  │
  └─ Student (Own Records Only)
```

---

## Data Flow / Handoffs

### Lead → Enrolled Student
1. **Admissions Counselor** creates lead in CRM
2. **Admissions Manager** reviews and approves application
3. **Admissions Manager** creates enrollment (converts lead → student)
4. **Handoff to Registrar** for academic records
5. **Handoff to Finance** for payment setup
6. **Handoff to Staff/Instructor** for course delivery

### Student Progress → Transcript
1. **Instructor** tracks attendance and validates skills
2. **Instructor** records grades
3. **Registrar** generates official transcript
4. **Registrar** issues credentials upon completion

### Financial Obligations
1. **Finance** sets up payment plan
2. **Student** makes payments
3. **Finance** processes refunds if withdrawal occurs
4. **Registrar** notes withdrawal in academic record

---

## Implementation Notes

### Page Access Control
Pages use the `RoleGate` component:
```jsx
<RoleGate allowedRoles={['admin', 'staff', 'admissions_counselor']}>
  <LeadsPage />
</RoleGate>
```

### API Endpoint Protection
Backend routes check user roles:
```python
@router.get("/leads")
def get_leads(current_user: User = Depends(get_current_user)):
    if not any(role.name in ['admin', 'staff', 'admissions_counselor', 'admissions_manager']
               for role in current_user.roles):
        raise HTTPException(403, "Forbidden")
```

### Data Filtering
- **Admissions Counselor** sees: `WHERE assigned_to_id = current_user.id`
- **Admissions Manager** sees: `All leads`
- **Student** sees: `WHERE user_id = current_user.id`

---

## Future Enhancements

1. **Granular Permissions**: Move from role-based to permission-based (e.g., "leads.create", "leads.delete")
2. **Custom Roles**: Allow admins to create custom roles with specific permissions
3. **Audit Logging**: Track who created/modified what and when
4. **Field-Level Permissions**: Restrict specific fields (e.g., SSN) to certain roles
5. **Time-Based Access**: Temporary permissions or access windows
