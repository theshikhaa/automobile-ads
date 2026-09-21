import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { api } from "../api";

function money(value) {
  return Number(value).toLocaleString("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  });
}

export default function Overview() {
  const [metrics, setMetrics] = useState(null);
  const [insights, setInsights] = useState(null);
  const [health, setHealth] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([api.metrics(), api.insights(), api.health()])
      .then(([m, i, h]) => {
        setMetrics(m);
        setInsights(i);
        setHealth(h);
      })
      .catch((err) => setError(err.message));
  }, []);

  if (error) {
    return (
      <section>
        <h1>Overview</h1>
        <p className="banner error">
          Could not reach the API. Start FastAPI on port 8000 and set{" "}
          <code>VITE_API_URL</code>. {error}
        </p>
      </section>
    );
  }

  if (!metrics || !insights) {
    return (
      <section>
        <h1>Overview</h1>
        <p className="muted">Loading metrics and SHAP…</p>
      </section>
    );
  }

  const shap = insights.global_shap?.values || [];

  return (
    <section>
      <header className="page-head">
        <div>
          <p className="eyebrow">Dashboard</p>
          <h1>Predictions & model health</h1>
          <p className="lede">
            Random Forest pipeline scored on the UCI Automobile reference set.
            SHAP shows which transformed features move price.
          </p>
        </div>
        {health && (
          <div className="pill ok">
            {health.status} · {health.reference_rows} ref rows ·{" "}
            {health.logged_predictions} live scores
          </div>
        )}
      </header>

      <div className="stat-grid">
        <article>
          <span>MAE</span>
          <strong>{money(metrics.mae)}</strong>
        </article>
        <article>
          <span>RMSE</span>
          <strong>{money(metrics.rmse)}</strong>
        </article>
        <article>
          <span>R²</span>
          <strong>{metrics.r2}</strong>
        </article>
        <article>
          <span>MAPE</span>
          <strong>{metrics.mape}%</strong>
        </article>
      </div>

      <div className="split">
        <div className="panel">
          <h2>SHAP — mean |impact|</h2>
          <p className="muted">{insights.global_shap?.source}</p>
          <div className="chart-tall">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={shap.slice(0, 12)}
                layout="vertical"
                margin={{ left: 16, right: 12 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#d7d1c4" />
                <XAxis type="number" tick={{ fontSize: 11 }} />
                <YAxis
                  type="category"
                  dataKey="feature"
                  width={168}
                  tick={{ fontSize: 11 }}
                />
                <Tooltip />
                <Bar dataKey="importance" fill="#b4532a" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="panel">
          <h2>Predicted vs actual</h2>
          <div className="chart-tall">
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart margin={{ left: 8, right: 8 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#d7d1c4" />
                <XAxis
                  dataKey="actual"
                  name="Actual"
                  tick={{ fontSize: 11 }}
                  tickFormatter={(v) => `${Math.round(v / 1000)}k`}
                />
                <YAxis
                  dataKey="predicted"
                  name="Predicted"
                  tick={{ fontSize: 11 }}
                  tickFormatter={(v) => `${Math.round(v / 1000)}k`}
                />
                <Tooltip
                  formatter={(value) => money(value)}
                  labelFormatter={(_, payload) => payload?.[0]?.payload?.make}
                />
                <Scatter data={metrics.pred_vs_actual} fill="#1f4b3a" />
              </ScatterChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="split">
        <div className="panel">
          <h2>Average price by body style</h2>
          <ul className="rank">
            {(insights.avg_price_by_body_style || []).map((row) => (
              <li key={row.body_style}>
                <span>{row.body_style}</span>
                <b>{money(row.avg_price)}</b>
              </li>
            ))}
          </ul>
        </div>
        <div className="panel">
          <h2>Residual histogram</h2>
          <div className="chart">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={metrics.residual_histogram}>
                <CartesianGrid strokeDasharray="3 3" stroke="#d7d1c4" />
                <XAxis dataKey="bin" hide />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="count" fill="#2b3a55" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </section>
  );
}
