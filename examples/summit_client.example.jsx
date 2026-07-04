/**
 * Summit → Quorum integration (paste-ready reference)
 *
 * Drop-in React hook + component for summit-app to embed the careers council.
 * Talks to a Quorum server (see DEPLOY.md) via REST + SSE. Keep Quorum's URL
 * behind Summit's own backend proxy in production (auth + rate limiting there),
 * per INTEGRATION.md rules — never expose the raw Quorum endpoint publicly.
 *
 * Usage:
 *   <CouncilPanel quorumUrl="/api/quorum" sponsorData={rows} />
 * where /api/quorum is Summit's authenticated proxy to the Quorum server.
 */
import { useRef, useState } from "react";

export function useDeliberation(quorumUrl) {
  const [events, setEvents] = useState([]); // {type, phase?, role?, emoji?, text?...}
  const [verdict, setVerdict] = useState(null);
  const [running, setRunning] = useState(false);
  const esRef = useRef(null);

  const convene = ({ title, body, council = "careers", context = {} }) => {
    setEvents([]); setVerdict(null); setRunning(true);
    // SSE endpoint is GET; context goes via the POST endpoint if needed —
    // for sponsor data, Summit's proxy should inject `context` server-side
    // so it never round-trips through the client.
    const qs = new URLSearchParams({ title, body, council }).toString();
    const es = new EventSource(`${quorumUrl}/deliberate/stream?${qs}`);
    esRef.current = es;
    const push = (e) => setEvents((prev) => [...prev, JSON.parse(e.data)]);
    es.addEventListener("phase", push);
    es.addEventListener("message", push);
    es.addEventListener("ballot", push);
    es.addEventListener("verdict", (e) => {
      setVerdict(JSON.parse(e.data));
      es.close(); setRunning(false);
    });
    es.onerror = () => { es.close(); setRunning(false); };
  };

  const cancel = () => { esRef.current?.close(); setRunning(false); };
  return { events, verdict, running, convene, cancel };
}

export default function CouncilPanel({ quorumUrl, sponsorData }) {
  const { events, verdict, running, convene } = useDeliberation(quorumUrl);
  const [body, setBody] = useState("");

  return (
    <div className="council-panel">
      <textarea
        value={body}
        onChange={(e) => setBody(e.target.value)}
        placeholder="Describe your decision — any language / 任何语言"
      />
      <button
        disabled={running || !body.trim()}
        onClick={() => convene({ title: body.slice(0, 60), body })}
      >
        {running ? "The council is deliberating…" : "🏛️ Convene the council"}
      </button>

      {events.map((ev, i) =>
        ev.type === "phase" ? (
          <h4 key={i}>{ev.phase}</h4>
        ) : ev.type === "message" ? (
          <p key={i}><b>{ev.emoji} {ev.role}:</b> {ev.text}</p>
        ) : ev.type === "ballot" ? (
          <p key={i}>🗳️ {ev.role}: <b>{ev.stance}</b> ({Math.round(ev.confidence * 100)}%)</p>
        ) : null
      )}

      {verdict && (
        <div className="verdict">
          <h3>⚖️ {verdict.decision}</h3>
          <p>{verdict.summary}</p>
          <p><i>Dissent: {verdict.dissent}</i></p>
          <ol>{verdict.action_plan.map((s, i) => <li key={i}>{s}</li>)}</ol>
          {/* NON-NEGOTIABLE: always render the disclaimer */}
          <small>{verdict.disclaimer}</small>
        </div>
      )}
    </div>
  );
}

/*
 * Summit backend proxy sketch (Node/Netlify function) — injects sponsor data
 * server-side and enforces auth + rate limits:
 *
 *   export async function handler(req) {
 *     requireAuth(req);                       // Summit session
 *     rateLimit(req.user.id, 5, "1h");        // e.g. 5 councils/hour
 *     const { title, body } = await req.json();
 *     const context = { sponsor_data: await topSponsorsFor(req.user) };
 *     const r = await fetch(`${QUORUM_URL}/deliberate`, {
 *       method: "POST",
 *       headers: { "content-type": "application/json" },
 *       body: JSON.stringify({ title, body, council: "careers", context }),
 *     });
 *     return new Response(await r.text(), { status: r.status });
 *   }
 */
