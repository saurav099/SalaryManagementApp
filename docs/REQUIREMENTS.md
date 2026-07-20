# Employee Salary Management System — Requirements

## Goal
Replace ACME's spreadsheet-based salary tracking with a web application that lets the HR Manager view, update, and understand salary data for ~10,000 employees across multiple countries — and answer basic questions about how the org pays people.

## Primary user
**HR Manager** (single-user assumption for this exercise — see Out of Scope).

## Core jobs-to-be-done
1. Find an employee and see their current salary and salary history.
2. Update an employee's salary (as a new, dated record — not an overwrite).
3. Understand pay patterns across the org: by department, country, and job level
   (averages, medians, ranges, headcount).
4. Search/filter/browse 10,000 employees without the UI or queries falling over.

## In scope
- Employee directory: list, search (name/email), filter (department, country, level, status), paginated.
- Employee detail view: profile + full salary history (not just current salary).
- Salary update flow: recording a new salary creates a new dated record; history is preserved and auditable.
- Org-level pay insights: average/median salary by department, by country, and by job level; headcount per segment.
- Seed script generating 10,000 realistic employees with non-uniform salary distributions (varying by level/department/country), so the insights view is meaningful rather
  than flat random noise.
- Backend API + database indexes sufficient to keep list/search/filter/analytics queries fast at 10k-employee scale.
- Automated tests for salary-history logic, filtering/pagination, and analytics queries.

## Explicitly out of scope (and why)
- **Authentication / role-based access control** — assumes a single trusted HR-admin user for this exercise. A real system needs this, but building it well would eat  
  time better spent on the core salary/analytics logic the assessment is evaluating.
- **Multi-currency conversion (live FX rates)** — salary is stored as `(amount, currency)` per record so the data model is honest about multi-country pay, but no FX 
  conversion/normalization is performed. Real FX handling needs a rate source, historical rate tracking, and rounding/compliance rules that are a project of their own.
- **Payroll processing, tax, and compliance** (deductions, statutory filings, country-specific pay rules) — this is a salary *record-keeping and insight* tool, not a 
  payroll engine.
- **Employee self-service** (employees viewing their own pay) — HR-manager-only tool for this exercise; a self-service portal has a different permission model and UX.
- **Org-chart / manager-hierarchy features beyond a plain `manager_id` field** — useful eventually, but not needed to answer "how does the org pay people."
- **Bulk import/export (CSV upload)** — a natural next feature (and close to the spreadsheet workflow it replaces), but not required to demonstrate the core architecture; 
  noted as a fast follow.

## Non-functional notes
- Must stay responsive at 10,000-employee scale: paginated list endpoints, indexed columns for the filters/searches above, and analytics computed via aggregate SQL
  queries rather than loading all rows into application memory.
- Salary changes are append-only (new record per change) so the system never loses history to an accidental overwrite.

## Fast follows
Auth/RBAC, CSV bulk import/export, FX-normalized reporting, audit log of *who* changed a salary and when, org-chart view.
