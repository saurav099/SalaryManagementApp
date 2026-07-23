export type EmployeeStatus = "active" | "terminated";

export interface SalaryRecord {
  id: number;
  amount: string;
  currency: string;
  effective_date: string;
  reason: string | null;
  created_at: string;
}

export interface EmployeeListItem {
  id: number;
  name: string;
  email: string;
  department: string;
  country: string;
  job_level: string;
  status: EmployeeStatus;
  current_salary: SalaryRecord | null;
}

export interface EmployeeDetail {
  id: number;
  name: string;
  email: string;
  department: string;
  country: string;
  job_level: string;
  hire_date: string;
  manager_id: number | null;
  status: EmployeeStatus;
  salary_records: SalaryRecord[];
}

export interface PaginatedEmployees {
  total: number;
  page: number;
  page_size: number;
  items: EmployeeListItem[];
}

export interface DepartmentPayStats {
  group: string;
  currency: string;
  headcount: number;
  avg_salary: string;
  median_salary: string;
  min_salary: string;
  max_salary: string;
}

// Kept in sync with backend/seed/seed.py -- there's no "distinct values"
// endpoint yet, so these drive the filter dropdowns directly.
export const DEPARTMENTS = ["Engineering", "Sales", "Marketing", "HR", "Finance", "Operations"];
export const COUNTRIES = ["US", "UK", "India", "Germany", "Singapore"];
export const JOB_LEVELS = ["junior", "mid", "senior", "lead", "manager", "ceo"];