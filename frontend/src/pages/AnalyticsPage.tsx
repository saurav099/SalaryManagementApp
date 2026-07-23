import { useEffect, useMemo, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { fetchPayStats } from "../api/client";
import type { DepartmentPayStats } from "../types";
import { formatMoney, titleCase } from "../utils/format";

type Dimension = "department" | "country" | "job_level";

const DIMENSIONS: { value: Dimension; label: string }[] = [
  { value: "department", label: "Department" },
  { value: "country", label: "Country" },
  { value: "job_level", label: "Job level" },
];

export function AnalyticsPage() {
  const [dimension, setDimension] = useState<Dimension>("department");
  const [stats, setStats] = useState<DepartmentPayStats[]>([]);
  const [currency, setCurrency] = useState<string>("USD");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetchPayStats(dimension)
      .then(setStats)
      .finally(() => setLoading(false));
  }, [dimension]);

  const availableCurrencies = useMemo(
    () => Array.from(new Set(stats.map((s) => s.currency))).sort(),
    [stats]
  );

  // Keep the selected currency valid whenever the dimension (and therefore
  // the available currency set) changes.
  useEffect(() => {
    if (availableCurrencies.length > 0 && !availableCurrencies.includes(currency)) {
      setCurrency(availableCurrencies[0]);
    }
  }, [availableCurrencies, currency]);

  const chartRows = stats
    .filter((s) => s.currency === currency)
    .map((s) => ({
      group: dimension === "job_level" ? titleCase(s.group) : s.group,
      avg_salary: parseFloat(s.avg_salary),
      median_salary: parseFloat(s.median_salary),
    }));

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-xl font-semibold text-[var(--color-ink)]">Pay analytics</h1>
        <p className="text-sm text-[var(--color-ink-muted)]">
          How the org pays people, broken down by {dimension.replace("_", " ")}
        </p>
      </div>

      <div className="mb-4 flex flex-wrap items-center gap-2">
        {DIMENSIONS.map((d) => (
          <button
            key={d.value}
            onClick={() => setDimension(d.value)}
            className={`rounded-md px-3 py-1.5 text-sm font-medium ${
              dimension === d.value
                ? "bg-[var(--color-accent)] text-white"
                : "border border-[var(--color-border-strong)] text-[var(--color-ink)] hover:bg-[var(--color-canvas)]"
            }`}
          >
            {d.label}
          </button>
        ))}

        {availableCurrencies.length > 1 && (
          <select
            aria-label="Currency"
            value={currency}
            onChange={(e) => setCurrency(e.target.value)}
            className="ml-auto rounded-md border border-[var(--color-border-strong)] bg-[var(--color-surface)] px-3 py-1.5 text-sm"
          >
            {availableCurrencies.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        )}
      </div>

      <p className="mb-4 text-xs text-[var(--color-ink-faint)]">
        Figures are shown one currency at a time by design — averaging pay across
        currencies without a conversion rate would produce a meaningless number.
      </p>

      {!loading && chartRows.length > 0 && (
        <div className="mb-6 h-72 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] p-4">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartRows}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
              <XAxis dataKey="group" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`} />
              <Tooltip
                formatter={(value) => formatMoney(Number(value ?? 0), currency)}
              />
              <Bar dataKey="avg_salary" fill="var(--color-accent)" radius={[4, 4, 0, 0]} name="Average" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      <div className="overflow-hidden rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)]">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-[var(--color-border)] bg-[var(--color-canvas)] text-left text-xs font-medium uppercase tracking-wide text-[var(--color-ink-muted)]">
              <th className="px-4 py-3">{titleCase(dimension.replace("_", " "))}</th>
              <th className="px-4 py-3">Currency</th>
              <th className="px-4 py-3 text-right">Headcount</th>
              <th className="px-4 py-3 text-right">Average</th>
              <th className="px-4 py-3 text-right">Median</th>
              <th className="px-4 py-3 text-right">Min</th>
              <th className="px-4 py-3 text-right">Max</th>
            </tr>
          </thead>
          <tbody>
            {loading && (
              <tr>
                <td colSpan={7} className="px-4 py-8 text-center text-[var(--color-ink-muted)]">
                  Loading...
                </td>
              </tr>
            )}
            {!loading &&
              stats.map((row) => (
                <tr
                  key={`${row.group}-${row.currency}`}
                  className="border-b border-[var(--color-border)] last:border-0"
                >
                  <td className="px-4 py-3 font-medium">
                    {dimension === "job_level" ? titleCase(row.group) : row.group}
                  </td>
                  <td className="px-4 py-3 text-[var(--color-ink-muted)]">{row.currency}</td>
                  <td className="px-4 py-3 text-right tabular-nums">{row.headcount}</td>
                  <td className="px-4 py-3 text-right tabular-nums">
                    {formatMoney(row.avg_salary, row.currency)}
                  </td>
                  <td className="px-4 py-3 text-right tabular-nums">
                    {formatMoney(row.median_salary, row.currency)}
                  </td>
                  <td className="px-4 py-3 text-right tabular-nums">
                    {formatMoney(row.min_salary, row.currency)}
                  </td>
                  <td className="px-4 py-3 text-right tabular-nums">
                    {formatMoney(row.max_salary, row.currency)}
                  </td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}