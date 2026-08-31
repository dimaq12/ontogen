# -*- coding: utf-8 -*-
"""HTTP wrapper around the organism — the generic F1 runtime (stdlib, zero
dependencies: this is the core, dialect frameworks don't belong here per I1).

POST /event                 {"id","type",...} -> outcome
GET  /state/<entity>/<inst> -> instance state
GET  /q/<name>              -> {"value": ...}
GET  /health                -> counters
"""
from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from onto.core import genome as genome_mod
from onto.core.organism import Organism


def load_skills(org: Organism, cache_dir) -> dict:
    """Genome skills -> executable bodies from the ribosome's CERTIFIED cache
    (fast, fallback naive). A skill without a body in the cache is not mounted
    (an honest 404: synthesize first)."""
    import pathlib
    from onto.core import skills as SK
    out = {}
    cache = pathlib.Path(cache_dir)
    for name, raw_sk in org.g.skills.items():
        sk = SK.Skill.model_validate(raw_sk)
        for phase in ("fast", "naive"):
            p = cache / f"{name}.{phase}.py"
            if p.exists():
                fn = SK.load_body(p.read_text(encoding="utf-8"),
                                  f"{phase}_{name}", sk.types)
                # U11 (D74): the escape corpus judges the CACHE too — an escape
                # revokes the certificate retroactively; the body is not mounted.
                reg = SK.gate_regressions(
                    sk, fn, cache.parent / "regressions" / f"{name}.jsonl")
                if reg:
                    org.ledger.record("skill_cert_revoked_by_escape",
                                      {"skill": name, "phase": phase,
                                       "why": reg[:300]})
                    continue
                out[name] = (sk, fn, phase)
                break
    return out


def load_externals(org: Organism, base) -> dict:
    """Membrane: island adapters with drift monitors (CORRUPTION wave)."""
    import pathlib
    from onto.core.membrane import External, MonitoredAdapter
    out = {}
    for name, raw in org.g.externals.items():
        ext = External.model_validate(raw)
        out[name] = MonitoredAdapter(name, ext, pathlib.Path(base), org.ledger)
    return out


def make_server(org: Organism, host: str = "127.0.0.1", port: int = 8090,
                skills_cache: str | None = None,
                genome_base: str | None = None) -> ThreadingHTTPServer:
    lock = threading.Lock()
    skills = load_skills(org, skills_cache) if skills_cache else {}
    externals = load_externals(org, genome_base) if genome_base and org.g.externals else {}
    from onto.core import expr as E
    auth_rules = {evn: E.parse_expr(src)
                  for evn, src in org.g.auth.get("rules", {}).items()}

    def authorize(handler, event) -> tuple[int, dict] | None:
        """U4 (D67): None = let through; otherwise (code, body). The IdP is an island."""
        if not org.g.auth:
            return None
        tok = handler.headers.get("Authorization", "")
        tok = tok[7:] if tok.startswith("Bearer ") else ""
        if not tok:
            return 401, {"error": "auth required: Authorization: Bearer <token>"}
        code, who = externals[org.g.auth["idp"]].call({"token": tok})
        if code != 200 or "error" in who:
            org.ledger.record("auth_denied", {"why": "idp rejected token",
                                              "event": event.get("id")})
            return 401, {"error": "token rejected by idp"}
        principal = {"role": str(who.get("role", "")),
                     "subject": str(who.get("subject", ""))}
        evn = event.get("type", "")
        tree = auth_rules.get(evn) or auth_rules.get("*")
        if tree is None:
            org.ledger.record("auth_denied", {"why": f"no rule for '{evn}' "
                              "(deny-by-default)", "event": event.get("id")})
            return 403, {"error": f"no auth rule for '{evn}' (deny-by-default)"}
        env = {"principal": principal,
               "ev": {k: v for k, v in event.items() if k not in ("id", "type")}}
        try:
            allowed = bool(E.eval_expr(tree, env))
        except Exception as e:  # noqa: BLE001 — a malformed payload doesn't crash it
            allowed, e_ = False, e
        if not allowed:
            org.ledger.record("auth_denied", {"why": f"rule for '{evn}' -> false",
                                              "principal": principal,
                                              "event": event.get("id")})
            return 403, {"error": f"denied by auth rule for '{evn}'",
                         "principal": principal}
        return None

    def authn(handler, surface: str) -> tuple[int, dict] | None:
        """AUTHENTICATION gate for the data / ops / compute surfaces (D93):
        when auth is configured these routes require a VALID IdP token (no
        per-event role — that is authorize()'s job for /event). It closes the
        holes where /ops/ledger leaked the whole journal and /state, /ext,
        /skill, /checkpoint answered unauthenticated. Without an auth block the
        plane is open (opt-in) — stated honestly, not hidden behind a banner.
        Fails CLOSED on missing/rejected/errored/REVOKED idp (mirrors /event)."""
        if not org.g.auth:
            return None
        tok = handler.headers.get("Authorization", "")
        tok = tok[7:] if tok.startswith("Bearer ") else ""
        if not tok:
            return 401, {"error": "auth required: Authorization: Bearer <token>"}
        code, who = externals[org.g.auth["idp"]].call({"token": tok})
        if code != 200 or "error" in who:
            org.ledger.record("auth_denied", {"why": f"idp rejected token "
                                              f"({surface})"})
            return 401, {"error": "token rejected by idp"}
        return None

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *a):     # silence on stdout (logging is the ledger's job)
            pass

        def _send_html(self, html: str) -> None:
            body = html.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _send(self, code: int, obj) -> None:
            body = json.dumps(obj, ensure_ascii=False).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self):
            if self.path == "/checkpoint":
                if (d := authn(self, "/checkpoint")):
                    return self._send(*d)
                with lock:
                    return self._send(200, org.checkpoint())
            if self.path.startswith("/ext/"):
                if (d := authn(self, "/ext")):
                    return self._send(*d)
                name = self.path.split("/", 2)[2]
                if name not in externals:
                    return self._send(404, {"error": f"no external '{name}'"})
                try:
                    n = int(self.headers.get("Content-Length", 0))
                    payload = json.loads(self.rfile.read(n) or b"{}")
                except Exception as e:
                    return self._send(400, {"error": f"bad json: {e}"})
                code, out = externals[name].call(payload)   # no lock: the island is slow
                return self._send(code, out)
            if self.path.startswith("/skill/"):
                if (d := authn(self, "/skill")):
                    return self._send(*d)
                name = self.path.split("/", 2)[2]
                if name not in skills:
                    return self._send(404, {"error": f"skill '{name}' not "
                                            "materialized (run synthesize)"})
                sk, fn, phase = skills[name]
                try:
                    n = int(self.headers.get("Content-Length", 0))
                    case = json.loads(self.rfile.read(n) or b"{}")
                except Exception as e:
                    return self._send(400, {"error": f"bad json: {e}"})
                from onto.core import skills as SK
                try:
                    with lock:
                        out = SK.run_case(fn, sk, case)
                except Exception as e:
                    return self._send(422, {"error": f"{type(e).__name__}: {e}"})
                return self._send(200, {"out": out, "body": phase})
            if self.path != "/event":
                return self._send(404, {"error": "unknown path"})
            try:
                n = int(self.headers.get("Content-Length", 0))
                event = json.loads(self.rfile.read(n) or b"{}")
            except Exception as e:
                return self._send(400, {"error": f"bad json: {e}"})
            event, cerr = genome_mod.coerce_event_in(org.g, event)   # U3/D66
            if cerr:
                return self._send(400, {"error": cerr})
            deny = authorize(self, event)                             # U4/D67
            if deny:
                return self._send(*deny)
            with lock:
                out = org.handle(event)
            self._send(200 if out.get("status") != "error" else 422, out)
            # U6: webhook after the response (don't hold up the client)
            url = org.g.webhooks.get(event.get("type", ""))
            if url and out.get("status") == "applied":
                threading.Thread(target=_webhook, args=(org, url, event, out),
                                 daemon=True).start()

        def do_GET(self):
            import urllib.parse
            path, _, qs = self.path.partition("?")
            qd = dict(urllib.parse.parse_qsl(qs))
            human = qd.pop("repr", "") == "human"      # U3/D66: surface
            if path == "/admin":
                return self._send_html(_admin_html(org))
            if path == "/ops":
                return self._send_html(_ops_html(org))
            if path == "/ops/ledger":                  # U8/D69: tail of the journal
                if (d := authn(self, "/ops/ledger")):  # D93: the journal is not public
                    return self._send(*d)
                kind = qd.get("kind", "")
                limit = int(qd.get("_limit", 100))
                rows = []
                lp = org.ledger.path
                if lp.exists():
                    for line in lp.read_text(encoding="utf-8").splitlines():
                        try:
                            e = json.loads(line)
                        except ValueError:
                            continue
                        if not kind or e.get("kind") == kind:
                            rows.append(e)
                return self._send(200, {"entries": rows[-limit:],
                                        "total": len(rows),
                                        "chain": org.ledger.verify()})
            parts = [urllib.parse.unquote(p) for p in path.split("/") if p]
            # D93: the read plane (state/queries/instances/list) requires
            # authentication when auth is configured; /health stays open
            # (liveness). Without an auth block the plane is open (opt-in).
            if parts[:1] and parts[0] in ("state", "instances", "q", "list"):
                if (d := authn(self, f"/{parts[0]}")):
                    return self._send(*d)
            with lock:
                if parts == ["health"]:
                    return self._send(200, {"ok": True, "counters": org.counters,
                                            "heat": org.heat,
                                            "externals": {n: a.passport()
                                                          for n, a in externals.items()},
                                            "genome": org.g.name})
                if len(parts) == 3 and parts[0] == "state":
                    en, inst = parts[1], parts[2]
                    st = org.state.get(en, {}).get(inst)
                    if st is None:
                        return self._send(404, {"error": f"no state {en}/{inst}"})
                    return self._send(200, genome_mod.render_state(org.g, en, st)
                                      if human else st)
                if len(parts) == 2 and parts[0] == "instances":
                    en = parts[1]
                    if en not in org.state:
                        return self._send(404, {"error": f"no entity {en}"})
                    return self._send(200, {"instances": sorted(org.state[en])})
                if len(parts) == 2 and parts[0] == "q":
                    name = parts[1]
                    try:
                        return self._send(200, {"value": org.query(name, qd)})
                    except KeyError as e:
                        return self._send(404, {"error": str(e)})
                if len(parts) == 2 and parts[0] == "list":
                    en = parts[1]
                    limit = int(qd.pop("_limit", 50))
                    offset = int(qd.pop("_offset", 0))
                    try:
                        rows = org.list_instances(en, qd, limit, offset)
                    except KeyError as e:
                        return self._send(404, {"error": str(e)})
                    if human:
                        rows = [{**genome_mod.render_state(org.g, en, r),
                                 "_key": r["_key"]} for r in rows]
                    return self._send(200, {"rows": rows, "count": len(rows)})
            self._send(404, {"error": "unknown path"})

    return ThreadingHTTPServer((host, port), Handler)


def _admin_html(org: Organism) -> str:
    """U5 (D61): the admin panel is emitted from the genome — population tables,
    event forms, queries. Zero hand-written UI code for the operator."""
    import html as H
    g = org.g
    ent_sections = []
    for en, ent in g.entities.items():
        cols = "".join(f"<th>{H.escape(f)}</th>" for f in sorted(ent.state))
        ent_sections.append(f"""
<details open><summary><b>{H.escape(en)}</b>
  <span class=m>({'dynamic' if ent.instances == 'dynamic' else len(ent.instances)})</span></summary>
<table id="t_{en}"><thead><tr><th>key</th>{cols}</tr></thead><tbody></tbody></table>
</details>""")
    ev_forms = []
    _PH = {"decimal": "12.34", "timestamp": "2026-01-01T00:00:00Z"}
    for evn, fields in g.events.items():
        inputs = "".join(
            f'<label>{H.escape(f)} <input name="{H.escape(f)}" '
            f'data-t="{g.reprs.get(f"{evn}.{f}", t)}" '
            f'placeholder="{_PH.get(g.reprs.get(f"{evn}.{f}", ""), "")}" '
            f'size="12"></label> '
            for f, t in fields.items())
        ev_forms.append(f"""
<form class=ev data-type="{H.escape(evn)}">
  <b>{H.escape(evn)}</b> {inputs}
  <button>POST</button> <span class=r></span></form>""")
    queries = "".join(
        f'<button class=q data-n="{H.escape(n)}">{H.escape(n)}</button> '
        for n in g.queries)
    return f"""<!doctype html><meta charset=utf-8>
<title>{H.escape(g.name)} · onto admin</title>
<style>
body{{font:14px system-ui;margin:2rem;max-width:70rem}}
table{{border-collapse:collapse;margin:.5rem 0}}
td,th{{border:1px solid #ccc;padding:2px 8px;font-variant-numeric:tabular-nums}}
form.ev{{margin:.3rem 0}} .m{{color:#888}} .r{{color:#065}} 
input{{margin-right:.4rem}} button{{cursor:pointer}}
</style>
<h1>{H.escape(g.name)} <span class=m>· onto admin (generated from genome)</span></h1>
{'<p><label>token <input id=tok size=24 placeholder="Bearer token (U4)"></label></p>' if g.auth else ''}
<h2>Events</h2>{''.join(ev_forms)}
<h2>Queries</h2><p>{queries}<span id=qr class=r></span></p>
<h2>Entities</h2>{''.join(ent_sections)}
<script>
async function refresh() {{
  for (const t of document.querySelectorAll('table')) {{
    const en = t.id.slice(2);
    const d = await (await fetch('/list/' + en + '?_limit=200&repr=human')).json();
    const tb = t.tBodies[0]; tb.innerHTML = '';
    for (const r of d.rows) {{
      const tr = tb.insertRow();
      tr.insertCell().textContent = r._key;
      for (const th of t.tHead.rows[0].cells)
        if (th.textContent != 'key')
          tr.insertCell().textContent = r[th.textContent];
    }}
  }}
}}
document.querySelectorAll('form.ev').forEach(f => f.onsubmit = async e => {{
  e.preventDefault();
  const ev = {{id: 'admin-' + Date.now(), type: f.dataset.type}};
  for (const i of f.querySelectorAll('input'))
    ev[i.name] = i.dataset.t == 'int' ? parseInt(i.value || '0') : i.value;
  const tok = document.getElementById('tok');
  if (tok) localStorage.setItem('onto_tok', tok.value);
  const hdr = tok && tok.value ? {{Authorization: 'Bearer ' + tok.value}} : {{}};
  const out = await (await fetch('/event', {{method: 'POST', headers: hdr,
    body: JSON.stringify(ev)}})).json();
  f.querySelector('.r').textContent = JSON.stringify(out.outcomes || out);
  refresh();
}});
document.querySelectorAll('.q').forEach(b => b.onclick = async () => {{
  const d = await (await fetch('/q/' + b.dataset.n)).json();
  document.getElementById('qr').textContent = b.dataset.n + ' = ' + d.value;
}});
const _tok = document.getElementById('tok');
if (_tok) _tok.value = localStorage.getItem('onto_tok') || '';
refresh(); setInterval(refresh, 3000);
</script>"""


def _ops_html(org: Organism) -> str:
    """U8 (D69): the OPERATOR console — the ledger (journal of proofs), the
    attestations of the externals, heat, checkpoint. Emitted from the organism;
    interviews/molt live in the CLI (onto fix/propose) — the console shows their
    traces in the ledger."""
    import html as H
    g = org.g
    return f"""<!doctype html><meta charset=utf-8>
<title>{H.escape(g.name)} · onto ops</title>
<style>
body{{font:14px system-ui;margin:2rem;max-width:76rem}}
table{{border-collapse:collapse;margin:.5rem 0;width:100%}}
td,th{{border:1px solid #ccc;padding:2px 8px;font-variant-numeric:tabular-nums;
      text-align:left;vertical-align:top}}
.m{{color:#888}} .bad{{color:#a00}} pre{{margin:0;white-space:pre-wrap}}
button{{cursor:pointer}} input,select{{margin-right:.5rem}}
</style>
<h1>{H.escape(g.name)} <span class=m>· onto ops (operator console)</span></h1>
<p id=hc class=m></p>
<p>
<select id=kind><option value="">all entries</option></select>
<input id=lim value=100 size=4>
<button id=refresh>refresh</button>
<button id=ckpt>checkpoint</button> <span id=cr class=m></span>
</p>
<table id=led><thead><tr><th>#</th><th>kind</th><th>payload</th></tr></thead>
<tbody></tbody></table>
<script>
const seen = new Set();
async function health() {{
  const h = await (await fetch('/health')).json();
  const ex = Object.entries(h.externals || {{}}).map(([n, p]) =>
    n + (p.cert_valid ? ' ✓' : ' ✗REVOKED') + ' (' + p.violations + ' viol)')
    .join(' · ');
  document.getElementById('hc').textContent =
    'applied=' + h.counters.applied + ' dup=' + h.counters.dup +
    ' | heat: ' + JSON.stringify(h.heat) + (ex ? ' | externals: ' + ex : '');
}}
async function led() {{
  const kind = document.getElementById('kind').value;
  const lim = document.getElementById('lim').value || 100;
  const d = await (await fetch('/ops/ledger?kind=' + kind + '&_limit=' + lim)).json();
  const tb = document.querySelector('#led tbody'); tb.innerHTML = '';
  d.entries.forEach((e, i) => {{
    seen.add(e.kind);
    const tr = tb.insertRow();
    tr.insertCell().textContent = d.total - d.entries.length + i + 1;
    const k = tr.insertCell(); k.textContent = e.kind;
    if (/denied|violation|revoke|error|red/.test(e.kind)) k.className = 'bad';
    const c = tr.insertCell();
    const p = Object.assign({{}}, e); delete p.kind; delete p.prev;
    c.innerHTML = '<pre>' + JSON.stringify(p) + '</pre>';
  }});
  const sel = document.getElementById('kind');
  const have = new Set([...sel.options].map(o => o.value));
  for (const k of seen) if (!have.has(k)) sel.add(new Option(k, k));
}}
document.getElementById('refresh').onclick = () => {{ health(); led(); }};
document.getElementById('ckpt').onclick = async () => {{
  const r = await (await fetch('/checkpoint', {{method: 'POST'}})).json();
  document.getElementById('cr').textContent = 'checkpoint: ' + JSON.stringify(r);
  led();
}};
health(); led(); setInterval(() => {{ health(); led(); }}, 4000);
</script>"""


def _webhook(org: Organism, url: str, event: dict, out: dict) -> None:
    """U6: delivery to the outside. An error = a ledger webhook_error, the organism lives on."""
    import urllib.request
    try:
        req = urllib.request.Request(
            url, data=json.dumps({"event": event, "outcomes":
                                  out.get("outcomes", {})}).encode(),
            headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=5)
    except Exception as e:  # noqa: BLE001
        org.ledger.record("webhook_error",
                          {"url": url, "event": event.get("id"),
                           "why": f"{type(e).__name__}: {str(e)[:120]}"})
