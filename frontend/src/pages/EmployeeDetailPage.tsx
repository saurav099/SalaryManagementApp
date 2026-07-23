import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { fetchEmployee, updateSalary } from "../api/client";
import type { EmployeeDetail } from "../types";
import { formatDate, formatMoney, titleCase } from "../utils/format";

export function EmployeeDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [employee, setEmployee] = useState<EmployeeDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [showForm, setShowForm] = useState(false);
  const [amount, setAmount] = useState("");
  const [currency, setCurrency] = useState("USD");
  const [effectiveDate, setEffectiveDate] = useState(
    () => new Date().toISOString().slice(0, 10)
  );
  const [reason, setReason] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  function load() {
    if (!id) return;
    setLoading(true);
    fetchEmployee(Number(id))
      .then(setEmployee)
      .catch(() => setError("Couldn't load this employee."))
      .finally(() => setLoading(false));
  }

  useEffect(load, [id]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!id || !amount) return;
    setSubmitting(true);
    setSubmitError(null);
    try {
      await updateSalary(Number(id), {
        amount,
        currency,
        effective_date: effectiveDate,
        reason: reason || undefined,
      });
      setShowForm(false);
      setAmount("");
      setReason("");
      load(); // refresh so the new history row shows immediately
    } catch {
      setSubmitError("Couldn't save this salary update. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) return <p className="text-[var(--color-ink-muted)]">Loading...</p>;
  if (error || !employee)
    return <p className="text-[var(--color-flag)]">{error ?? "Employee not found."}</p>;

  const current = employee.salary_records[0];

  return (
    <div>
      <button
        onClick={() => navigate("/")}
        className="mb-4 text-sm text-[var(--color-ink-muted)] hover:text-[var(--color-ink)]"
      >
        ← Back to employees
      </button>

      <div className="mb-6 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] p-6">
        <h1 className="text-xl font-semibold text-[var(--color-ink)]">{employee.name}</h1>
        <p className="text-sm text-[var(--color-ink-muted)]">{employee.email}</p>

        <div className="mt-4 grid grid-cols-2 gap-4 text-sm sm:grid-cols-4">
          <Field label="Department" value={employee.department} />
          <Field label="Country" value={employee.country} />
          <Field label="Level" value={titleCase(employee.job_level)} />
          <Field label="Hired" value={formatDate(employee.hire_date)} />
        </div>

        {current && (
          <div className="mt-4 rounded-md bg-[var(--color-accent-soft)] px-4 py-3">
            <div className="text-xs font-medium uppercase tracking-wide text-[var(--color-accent)]">
              Current salary
            </div>
            <div className="text-lg font-semibold tabular-nums text-[var(--color-ink)]">
              {formatMoney(current.amount, current.currency)}
            </div>
          </div>
        )}
      </div>

      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-[var(--color-ink-muted)]">
          Salary history
        </h2>
        <button
          onClick={() => setShowForm((v) => !v)}
          className="rounded-md bg-[var(--color-accent)] px-3 py-1.5 text-sm font-medium text-white hover:bg-[var(--color-accent-hover)]"
        >
          {showForm ? "Cancel" : "Record salary change"}
        </button>
      </div>

      {showForm && (
        <form
          onSubmit={handleSubmit}
          className="mb-6 grid grid-cols-2 gap-3 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] p-4 sm:grid-cols-4"
        >
          <input
            required
            type="number"
            step="0.01"
            placeholder="Amount"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            className="rounded-md border border-[var(--color-border-strong)] px-3 py-2 text-sm"
          />
          <input
            required
            type="text"
            placeholder="Currency (e.g. USD)"
            value={currency}
            onChange={(e) => setCurrency(e.target.value.toUpperCase())}
            maxLength={3}
            className="rounded-md border border-[var(--color-border-strong)] px-3 py-2 text-sm"
          />
          <input
            required
            type="date"
            value={effectiveDate}
            onChange={(e) => setEffectiveDate(e.target.value)}
            className="rounded-md border border-[var(--color-border-strong)] px-3 py-2 text-sm"
          />
          <input
            type="text"
            placeholder="Reason (optional)"
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            className="rounded-md border border-[var(--color-border-strong)] px-3 py-2 text-sm"
          />
          {submitError && (
            <p className="col-span-full text-sm text-[var(--color-flag)]">{submitError}</p>
          )}
          <button
            type="submit"
            disabled={submitting}
            className="col-span-full rounded-md bg-[var(--color-accent)] px-4 py-2 text-sm font-medium text-white hover:bg-[var(--color-accent-hover)] disabled:opacity-50"
          >
            {submitting ? "Saving..." : "Save salary change"}
          </button>
        </form>
      )}

      <div className="overflow-hidden rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)]">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-[var(--color-border)] bg-[var(--color-canvas)] text-left text-xs font-medium uppercase tracking-wide text-[var(--color-ink-muted)]">
              <th className="px-4 py-3">Effective date</th>
              <th className="px-4 py-3">Amount</th>
              <th className="px-4 py-3">Reason</th>
            </tr>
          </thead>
          <tbody>
            {employee.salary_records.map((record) => (
              <tr key={record.id} className="border-b border-[var(--color-border)] last:border-0">
                <td className="px-4 py-3">{formatDate(record.effective_date)}</td>
                <td className="px-4 py-3 font-medium tabular-nums">
                  {formatMoney(record.amount, record.currency)}
                </td>
                <td className="px-4 py-3 text-[var(--color-ink-muted)]">
                  {record.reason ?? "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div className="text-xs uppercase tracking-wide text-[var(--color-ink-faint)]">{label}</div>
      <div className="font-medium text-[var(--color-ink)]">{value}</div>
    </div>
  );
}