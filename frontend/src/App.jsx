import { NavLink, Route, Routes } from "react-router-dom";
import Overview from "./pages/Overview.jsx";
import Predict from "./pages/Predict.jsx";
import Drift from "./pages/Drift.jsx";
import ResponsibleAI from "./pages/ResponsibleAI.jsx";

export default function App() {
  return (
    <div className="shell">
      <aside className="rail">
        <div className="brand">
          <span className="mark">AV</span>
          <div>
            <strong>AutoValue Lab</strong>
            
          </div>
        </div>
        <nav>
          <NavLink to="/" end>
            Overview
          </NavLink>
          <NavLink to="/predict">Predict</NavLink>
          <NavLink to="/drift">Drift</NavLink>
          <NavLink to="/responsible-ai">Responsible AI</NavLink>
        </nav>
        <p className="rail-note">
          Estimates are decision-support only. Do not enter personal data.
        </p>
      </aside>
      <main className="canvas">
        <Routes>
          <Route path="/" element={<Overview />} />
          <Route path="/predict" element={<Predict />} />
          <Route path="/drift" element={<Drift />} />
          <Route path="/responsible-ai" element={<ResponsibleAI />} />
        </Routes>
      </main>
    </div>
  );
}
