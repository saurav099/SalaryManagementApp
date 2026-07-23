import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { fetchEmployees } from "../api/client";
import type { EmployeeListItem } from "../types";
import { COUNTRIES, DEPARTMENTS, JOB_LEVELS } from "../types";
import { formatMoney, titleCase } from "../utils/format";

const PAGE_SIZE_OPTIONS = [25, 50, 100];

export function EmployeeListPage() {
  const navigate = useNavigate();

  const [search, setSearch] = useState("");
  const [department, setDepartment] = useState("");
  const [country, setCountry] = useState("");
  const [jobLevel, setJobLevel] = useState("");
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(25);
  const [jumpToPage, setJumpToPage] = useState("");

  const [items, setItems] = useState<EmployeeListItem[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Reset to page 1 whenever a filter or page size changes -- otherwise a
  // user could be stranded on a page number that no longer exists.
  useEffect(() => {
    setPage(1);
  }, [search, department, country, jobLevel, pageSize]);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);

    fetchEmployees({
      page,
      page_size: pageSize,
      search: search || undefined,
      department: department || undefined,
      country: country || undefined,
      job_level: jobLevel || undefined,
    })
      .then((data) => {
        if (cancelled) return;
        setItems(data.items);
        setTotal(data.total);
      })
      .catch(() => {
        if (!cancelled) setError("Couldn't load employees. Is the backend running?");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [page, pageSize, search, department, country, jobLevel]);

  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  function goToPage(target: number) {
    const clamped = Math.min(Math.max(1, target), totalPages);
    setPage(clamped);
    setJumpToPage("");
  }

  function handleJumpSubmit(e: React.FormEvent) {
    e.preventDefault();
    const target = parseInt(jumpToPage, 10);
    if (!Number.isNaN(target)) goToPage(target);
  }

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-xl font-semibold text-[var(--color-ink)]">Employees</h1>
        <p className="text-sm text-[var(--color-ink-muted)]">
          {total.toLocaleString()} people across {DEPARTMENTS.length} departments
        </p>
      </div>

      <div className="mb-4 flex flex-wrap gap-3">
        <input
          type="text"
          placeholder="Search name or email..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-64 rounded-md border border-[var(--color-border-strong)] bg-[var(--color-surface)] px-3 py-2 text-sm outline-none focus:border-[var(--color-accent)] focus:ring-2 focus:ring-[var(--color-accent-soft)]"
        />
        <Select label="Department" value={department} onChange={setDepartment} options={DEPARTMENTS} />
        <Select label="Country" value={country} onChange={setCountry} options={COUNTRIES} />
        <Select
          label="Level"
          value={jobLevel}
          onChange={setJobLevel}
          options={JOB_LEVELS}
          formatOption={titleCase}
        />
      </div>

      <div className="overflow-hidden rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)]">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-[var(--color-border)] bg-[var(--color-canvas)] text-left text-xs font-medium uppercase tracking-wide text-[var(--color-ink-muted)]">
              <th className="px-4 py-3">Name</th>
              <th className="px-4 py-3">Department</th>
              <th className="px-4 py-3">Country</th>
              <th className="px-4 py-3">Level</th>
              <th className="px-4 py-3 text-right">Current salary</th>
            </tr>
          </thead>
          <tbody>
            {error && (
              <tr>
                <td colSpan={5} className="px-4 py-8 text-center text-[var(--color-flag)]">
                  {error}
                </td>
              </tr>
            )}
            {!error && loading && (
              <tr>
                <td colSpan={5} className="px-4 py-8 text-center text-[var(--color-ink-muted)]">
                  Loading...
                </td>
              </tr>
            )}
            {!error && !loading && items.length === 0 && (
              <tr>
                <td colSpan={5} className="px-4 py-8 text-center text-[var(--color-ink-muted)]">
                  No employees match these filters.
                </td>
              </tr>
            )}
            {!error &&
              !loading &&
              items.map((emp) => (
                <tr
                  key={emp.id}
                  onClick={() => navigate(`/employees/${emp.id}`)}
                  className="cursor-pointer border-b border-[var(--color-border)] last:border-0 hover:bg-[var(--color-canvas)]"
                >
                  <td className="px-4 py-3">
                    <div className="font-medium text-[var(--color-ink)]">{emp.name}</div>
                    <div className="text-xs text-[var(--color-ink-muted)]">{emp.email}</div>
                  </td>
                  <td className="px-4 py-3 text-[var(--color-ink-muted)]">{emp.department}</td>
                  <td className="px-4 py-3 text-[var(--color-ink-muted)]">{emp.country}</td>
                  <td className="px-4 py-3 text-[var(--color-ink-muted)]">
                    {titleCase(emp.job_level)}
                  </td>
                  <td className="px-4 py-3 text-right font-medium tabular-nums text-[var(--color-ink)]">
                    {emp.current_salary
                      ? formatMoney(emp.current_salary.amount, emp.current_salary.currency)
                      : "—"}
                  </td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>

      <div className="mt-4 flex flex-wrap items-center justify-between gap-3 text-sm">
        <div className="flex items-center gap-2 text-[var(--color-ink-muted)]">
          <span>Page {page} of {totalPages}</span>
          <span className="text-[var(--color-ink-faint)]">·</span>
          <label className="flex items-center gap-1.5">
            Rows per page
            <select
              value={pageSize}
              onChange={(e) => setPageSize(Number(e.target.value))}
              className="rounded-md border border-[var(--color-border-strong)] bg-[var(--color-surface)] px-2 py-1 text-sm"
            >
              {PAGE_SIZE_OPTIONS.map((size) => (
                <option key={size} value={size}>
                  {size}
                </option>
              ))}
            </select>
          </label>
        </div>

        <div className="flex items-center gap-2">
          <form onSubmit={handleJumpSubmit} className="flex items-center gap-1.5">
            <label htmlFor="jump-to-page" className="text-[var(--color-ink-muted)]">
              Go to page
            </label>
            <input
              id="jump-to-page"
              type="number"
              min={1}
              max={totalPages}
              value={jumpToPage}
              onChange={(e) => setJumpToPage(e.target.value)}
              placeholder={String(page)}
              className="w-16 rounded-md border border-[var(--color-border-strong)] bg-[var(--color-surface)] px-2 py-1 text-sm"
            />
          </form>
          <button
            onClick={() => goToPage(page - 1)}
            disabled={page === 1}
            className="rounded-md border border-[var(--color-border-strong)] px-3 py-1.5 font-medium text-[var(--color-ink)] disabled:opacity-40"
          >
            Previous
          </button>
          <button
            onClick={() => goToPage(page + 1)}
            disabled={page >= totalPages}
            className="rounded-md border border-[var(--color-border-strong)] px-3 py-1.5 font-medium text-[var(--color-ink)] disabled:opacity-40"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
}

function Select({
  label,
  value,
  onChange,
  options,
  formatOption = (s: string) => s,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  options: string[];
  formatOption?: (s: string) => string;
}) {
  return (
    <select
      aria-label={label}
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="rounded-md border border-[var(--color-border-strong)] bg-[var(--color-surface)] px-3 py-2 text-sm text-[var(--color-ink)] outline-none focus:border-[var(--color-accent)]"
    >
      <option value="">{label}: All</option>
      {options.map((opt) => (
        <option key={opt} value={opt}>
          {formatOption(opt)}
        </option>
      ))}
    </select>
  );
}