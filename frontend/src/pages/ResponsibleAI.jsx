export default function ResponsibleAI() {
  return (
    <section>
      <header className="page-head">
        <div>
          <p className="eyebrow">Governance</p>
          <h1>Responsible AI</h1>
          <p className="lede">
            Checklist for fairness, privacy, and consent. The full report is{" "}
            <code>Responsible_AI.md</code> in the repository.
          </p>
        </div>
      </header>

      <div className="consent">
        This dashboard sends vehicle specifications to a machine-learning model
        to estimate price. In this lab, payloads are stored locally so we can
        check data drift. Do not enter personal information. The estimate is not
        a professional appraisal.
      </div>

      <div className="split">
        <article className="panel">
          <h2>Fairness</h2>
          <ul className="checks">
            <li>Pass — no race, gender, income, or other personal attributes.</li>
            <li>Watch — <code>make</code> is a market feature and a possible proxy.</li>
            <li>Limit — sparse luxury makes will have higher error.</li>
            <li>Rule — do not vary quotes by customer identity.</li>
          </ul>
        </article>
        <article className="panel">
          <h2>Privacy</h2>
          <ul className="checks">
            <li>Pass — schema has no name, email, VIN, or plate.</li>
            <li>Pass — training data is the public UCI Automobile set.</li>
            <li>Pass — prediction log is local, capped, and gitignored.</li>
            <li>Partial — use HTTPS when the API is hosted.</li>
          </ul>
        </article>
      </div>
      <div className="split">
        <article className="panel">
          <h2>Consent</h2>
          <ul className="checks">
            <li>Opt-in scoring only (form submit or POST).</li>
            <li>Users are told a model produces the estimate.</li>
            <li>Lab logs can be deleted by removing the JSON log file.</li>
            <li>Not for credit, insurance, or automated purchasing.</li>
          </ul>
        </article>
        <article className="panel">
          <h2>Accountability</h2>
          <ul className="checks">
            <li>SHAP local + global explanations on the API and UI.</li>
            <li>Drift via PSI; metrics via MAE / RMSE / R² / MAPE.</li>
            <li>Docker image for a reproducible API runtime.</li>
            <li>Human review required before any high-impact decision.</li>
          </ul>
        </article>
      </div>
    </section>
  );
}
