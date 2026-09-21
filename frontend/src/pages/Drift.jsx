import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { api } from "../api";

export default function Drift() {
  const [report, setReport] = useState(null);
  const [error, setError] = useState("");

  function load() {
    api
      .drift()
      .then(setReport)
      .catch((err) => setError(err.message));
  }

  useEffect(() => {
    load();
  }, []);

  if (error) {
    return (
      <section>
        <h1>Drift checks</h1>
        <p className="banner error">{error}</p>
      </section>
    );
  }

  if (!report) {
    return (
      <section>
        <h1>Drift checks</h1>
        <p className="muted">Loading PSI report…</p>
      </section>
    );
  }

  return (
    <section>
      <header className="page-head">
        <div>
          <p className="eyebrow">Monitoring</p>
          <h1>Feature drift</h1>
          <p className="lede">
            Population Stability Index compares live <code>/predict</code>{" "}
            payloads with the UCI reference distribution. PSI ≥ 0.20 is flagged.
          </p>
        </div>
        <button className="ghost" type="button" onClick={load}>
          Refresh
        </button>
      </header>

      <div className="stat-grid">
        <article>
          <span>Status</span>
          <strong>{report.status.replaceAll("_", " ")}</strong>
        </article>
        <article>
          <span>Live scores</span>
          <strong>{report.n_production}</strong>
        </article>
        <article>
          <span>Reference rows</span>
          <strong>{report.n_reference}</strong>
        </article>
        <article>
          <span>Shifted features</span>
          <strong>{report.shifted_features ?? 0}</strong>
        </article>
      </div>

      {report.message && <p className="banner">{report.message}</p>}

      {report.features?.length > 0 && (
        <div className="panel">
          <h2>PSI by numeric feature</h2>
          <div className="chart-tall">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={report.features} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#d7d1c4" />
                <XAxis type="number" tick={{ fontSize: 11 }} />
                <YAxis
                  type="category"
                  dataKey="feature"
                  width={150}
                  tick={{ fontSize: 11 }}
                />
                <Tooltip />
                <Bar dataKey="psi" radius={[0, 4, 4, 0]}>
                  {report.features.map((row) => (
                    <Cell
                      key={row.feature}
                      fill={row.status === "shift" ? "#b4532a" : "#1f4b3a"}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
          <table>
            <thead>
              <tr>
                <th>Feature</th>
                <th>PSI</th>
                <th>Reference mean</th>
                <th>Live mean</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {report.features.map((row) => (
                <tr key={row.feature}>
                  <td>{row.feature}</td>
                  <td>{row.psi}</td>
                  <td>{row.reference_mean}</td>
                  <td>{row.production_mean}</td>
                  <td>{row.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
