import { useEffect, useMemo, useState } from "react";
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

const RAW_HINTS = new Set([
  "car_volume",
  "power_to_weight_ratio",
  "average_mpg",
  "engine_power_ratio",
  "weight_category",
  "fuel_efficiency_category",
  "engine_size_category",
  "horsepower_category",
]);

export default function Predict() {
  const [fields, setFields] = useState([]);
  const [form, setForm] = useState(null);
  const [result, setResult] = useState(null);
  const [explain, setExplain] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [showDerived, setShowDerived] = useState(false);

  useEffect(() => {
    Promise.all([api.schema(), api.sample()])
      .then(([schema, sample]) => {
        setFields(schema.fields);
        setForm(sample);
      })
      .catch((err) => setError(err.message));
  }, []);

  const visibleFields = useMemo(
    () => fields.filter((field) => showDerived || !RAW_HINTS.has(field.name)),
    [fields, showDerived]
  );

  function update(name, value, type) {
    setForm((prev) => ({
      ...prev,
      [name]: type === "numeric" ? Number(value) : value,
    }));
  }

  async function onSubmit(event) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      const [prediction, shap] = await Promise.all([
        api.predict(form),
        api.explain(form),
      ]);
      setResult(prediction);
      setExplain(shap);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  if (!form) {
    return (
      <section>
        <h1>Predict</h1>
        <p className="muted">{error || "Loading schema…"}</p>
      </section>
    );
  }

  return (
    <section>
      <header className="page-head">
        <div>
          <p className="eyebrow">Scoring</p>
          <h1>Price estimate</h1>
          <p className="lede">
            Submitting this form calls <code>/api/v1/predict</code> and{" "}
            <code>/api/v1/explain</code>. Specs are stored locally for drift
            checks — no names, VINs, or contact details.
          </p>
        </div>
      </header>

      {error && <p className="banner error">{error}</p>}

      <div className="split wide-left">
        <form className="panel form" onSubmit={onSubmit}>
          <div className="form-toolbar">
            <label>
              <input
                type="checkbox"
                checked={showDerived}
                onChange={(event) => setShowDerived(event.target.checked)}
              />
              Show derived features
            </label>
            <button
              type="button"
              className="ghost"
              onClick={() =>
                api.sample().then(setForm).catch((err) => setError(err.message))
              }
            >
              Load sample
            </button>
          </div>
          <div className="form-grid">
            {visibleFields.map((field) => (
              <label key={field.name}>
                {field.name.replaceAll("_", " ")}
                {field.type === "categorical" ? (
                  <select
                    value={form[field.name]}
                    onChange={(event) =>
                      update(field.name, event.target.value, field.type)
                    }
                  >
                    {field.options.map((option) => (
                      <option key={option} value={option}>
                        {option}
                      </option>
                    ))}
                  </select>
                ) : (
                  <input
                    type="number"
                    step="any"
                    value={form[field.name]}
                    onChange={(event) =>
                      update(field.name, event.target.value, field.type)
                    }
                    required
                  />
                )}
              </label>
            ))}
          </div>
          <button type="submit" disabled={busy}>
            {busy ? "Scoring…" : "Predict price"}
          </button>
        </form>

        <div className="stack">
          <div className="panel result">
            <h2>Model output</h2>
            {result ? (
              <>
                <p className="price">
                  {Number(result.predicted_price).toLocaleString("en-US", {
                    style: "currency",
                    currency: "USD",
                  })}
                </p>
                <p className="muted">
                  Point estimate in USD. Not an appraisal. Base SHAP value{" "}
                  {explain?.base_value != null
                    ? Number(explain.base_value).toLocaleString("en-US", {
                        style: "currency",
                        currency: "USD",
                      })
                    : "n/a"}
                  .
                </p>
              </>
            ) : (
              <p className="muted">Run a prediction to see the estimate.</p>
            )}
          </div>
          <div className="panel">
            <h2>Local SHAP</h2>
            {explain ? (
              <div className="chart-tall">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={explain.top_contributions}
                    layout="vertical"
                    margin={{ left: 8, right: 8 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#d7d1c4" />
                    <XAxis type="number" tick={{ fontSize: 11 }} />
                    <YAxis
                      type="category"
                      dataKey="feature"
                      width={160}
                      tick={{ fontSize: 10 }}
                    />
                    <Tooltip />
                    <Bar dataKey="shap_value" radius={[0, 4, 4, 0]}>
                      {explain.top_contributions.map((row) => (
                        <Cell
                          key={row.feature}
                          fill={row.shap_value >= 0 ? "#1f4b3a" : "#b4532a"}
                        />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <p className="muted">
                Positive bars push the price up from the baseline; negative bars
                pull it down.
              </p>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
