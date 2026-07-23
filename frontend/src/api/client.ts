import axios from "axios";
import type {
  DepartmentPayStats,
  EmployeeDetail,
  PaginatedEmployees,
} from "../types";

const API_BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export const api = axios.create({ baseURL: API_BASE_URL });

export interface EmployeeListParams {
  page?: number;
  page_size?: number;
  search?: string;
  department?: string;
  country?: string;
  job_level?: string;
}

export async function fetchEmployees(
  params: EmployeeListParams
): Promise<PaginatedEmployees> {
  const { data } = await api.get<PaginatedEmployees>("/employees", { params });
  return data;
}

export async function fetchEmployee(id: number): Promise<EmployeeDetail> {
  const { data } = await api.get<EmployeeDetail>(`/employees/${id}`);
  return data;
}

export interface SalaryUpdatePayload {
  amount: string;
  currency: string;
  effective_date: string;
  reason?: string;
}

export async function updateSalary(
  employeeId: number,
  payload: SalaryUpdatePayload
) {
  const { data } = await api.post(`/employees/${employeeId}/salary`, payload);
  return data;
}

export async function fetchPayStats(
  dimension: "department" | "country" | "job_level"
): Promise<DepartmentPayStats[]> {
  const { data } = await api.get<DepartmentPayStats[]>(
    `/analytics/pay-by/${dimension}`
  );
  return data;
}