#!/usr/bin/env python3
"""Generate an interactive UAT wizard from a YAML scenario file.

Produces a self-contained HTML file with embedded CSS and JS that guides
a non-technical tester through acceptance testing step-by-step.

Usage:
    python3 generate_uat_wizard.py scenarios.yaml --output docs/uat-wizard.html

Template version: 1.0 (2026-03-14)
Agency: Smith AI Agency — central UAT capability
"""

import argparse
import html
import json
import sys
from pathlib import Path

try:
    import yaml  # type: ignore[import-untyped]
except ImportError:
    print("Error: PyYAML required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


def load_scenarios(path: Path) -> dict:
    """Load and validate the YAML scenario file."""
    with open(path) as f:
        data: dict = yaml.safe_load(f)  # type: ignore[assignment]

    required = ["project", "epic", "version", "title", "scenarios"]
    missing = [k for k in required if k not in data]
    if missing:
        print(f"Error: Missing required fields: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)

    if not data["scenarios"]:
        print("Error: No scenarios defined", file=sys.stderr)
        sys.exit(1)

    for i, s in enumerate(data["scenarios"]):
        for field in ["id", "feature", "title", "checks"]:
            if field not in s:
                print(f"Error: Scenario {i + 1} missing '{field}'", file=sys.stderr)
                sys.exit(1)

    data.setdefault("prerequisites", [])
    data.setdefault("cross_cutting", [])
    data.setdefault("exploratory", [])
    data.setdefault("deployment_type", "cli")

    return data


def generate_html(data: dict) -> str:
    """Generate the complete HTML wizard from scenario data."""
    title = html.escape(data["title"])
    project = html.escape(data["project"])
    epic = html.escape(data["epic"])
    version = html.escape(data["version"])
    json_data = json.dumps(data, indent=None, ensure_ascii=True)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>UAT Wizard — {title}</title>
<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&family=Roboto+Mono:wght@400&display=swap" rel="stylesheet">
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: 'Roboto', system-ui, sans-serif; background: #1a1a2e; color: #e0e0e0; min-height: 100vh; }}
.container {{ max-width: 720px; margin: 0 auto; padding: 1.5rem; }}
header {{ text-align: center; padding: 2rem 0 1rem; }}
header h1 {{ font-size: 1.5rem; font-weight: 500; color: #4db6ac; }}
header .meta {{ font-size: 0.8rem; color: #888; margin-top: 0.4rem; }}
.progress {{ background: #2d2d44; border-radius: 8px; height: 8px; margin: 1.5rem 0; overflow: hidden; }}
.progress-fill {{ background: linear-gradient(90deg, #009688, #4db6ac); height: 100%; border-radius: 8px; transition: width 0.4s ease; }}
.progress-text {{ text-align: center; font-size: 0.75rem; color: #888; margin-bottom: 1.5rem; }}
.card {{ background: #16213e; border: 1px solid #2d2d44; border-radius: 12px; padding: 2rem; margin-bottom: 1rem; }}
.card h2 {{ font-size: 1.2rem; font-weight: 500; color: #fff; margin-bottom: 0.3rem; }}
.card .feature-badge {{ display: inline-block; background: #009688; color: #fff; font-size: 0.65rem; font-weight: 700; padding: 0.15rem 0.5rem; border-radius: 4px; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem; }}
.card .severity {{ display: inline-block; font-size: 0.65rem; font-weight: 700; padding: 0.15rem 0.5rem; border-radius: 4px; margin-left: 0.4rem; text-transform: uppercase; }}
.severity-blocker {{ background: #c62828; color: #fff; }}
.severity-major {{ background: #e65100; color: #fff; }}
.severity-minor {{ background: #f9a825; color: #1a1a2e; }}
.card p {{ color: #b0b0b0; line-height: 1.6; margin: 0.8rem 0; }}
.command-block {{ background: #0a0e1a; border: 1px solid #2d2d44; border-radius: 8px; padding: 1rem; margin: 1rem 0; position: relative; }}
.command-block code {{ font-family: 'Roboto Mono', monospace; font-size: 0.8rem; color: #4db6ac; white-space: pre-wrap; word-break: break-all; }}
.copy-btn {{ position: absolute; top: 0.5rem; right: 0.5rem; background: #2d2d44; border: none; color: #888; font-size: 0.7rem; padding: 0.3rem 0.6rem; border-radius: 4px; cursor: pointer; transition: all 0.2s; }}
.copy-btn:hover {{ background: #009688; color: #fff; }}
.checks {{ list-style: none; margin: 1rem 0; }}
.checks li {{ padding: 0.5rem 0; padding-left: 1.8rem; position: relative; color: #ccc; font-size: 0.9rem; }}
.checks li::before {{ content: '○'; position: absolute; left: 0; color: #555; font-size: 1.1rem; }}
.verdict-buttons {{ display: flex; gap: 0.8rem; margin: 1.5rem 0 1rem; }}
.verdict-btn {{ flex: 1; padding: 0.9rem; border: 2px solid #2d2d44; border-radius: 8px; background: transparent; color: #888; font-family: 'Roboto', sans-serif; font-size: 0.9rem; font-weight: 500; cursor: pointer; transition: all 0.2s; text-transform: uppercase; letter-spacing: 0.05em; }}
.verdict-btn:hover {{ border-color: #555; color: #ccc; }}
.verdict-btn.pass {{ border-color: #2e7d32; color: #2e7d32; }}
.verdict-btn.pass.selected {{ background: #2e7d32; color: #fff; }}
.verdict-btn.fail {{ border-color: #c62828; color: #c62828; }}
.verdict-btn.fail.selected {{ background: #c62828; color: #fff; }}
.verdict-btn.skip {{ border-color: #555; color: #555; }}
.verdict-btn.skip.selected {{ background: #555; color: #fff; }}
.comment-field {{ width: 100%; background: #0a0e1a; border: 1px solid #2d2d44; border-radius: 8px; color: #e0e0e0; font-family: 'Roboto', sans-serif; font-size: 0.85rem; padding: 0.8rem; min-height: 60px; resize: vertical; }}
.comment-field::placeholder {{ color: #555; }}
.comment-field:focus {{ outline: none; border-color: #009688; }}
.nav-buttons {{ display: flex; gap: 0.8rem; justify-content: space-between; margin: 1.5rem 0; }}
.nav-btn {{ padding: 0.7rem 1.5rem; border: none; border-radius: 8px; font-family: 'Roboto', sans-serif; font-size: 0.85rem; font-weight: 500; cursor: pointer; transition: all 0.2s; }}
.nav-btn.prev {{ background: #2d2d44; color: #ccc; }}
.nav-btn.prev:hover {{ background: #3d3d54; }}
.nav-btn.next {{ background: #009688; color: #fff; }}
.nav-btn.next:hover {{ background: #00897b; }}
.nav-btn:disabled {{ opacity: 0.3; cursor: not-allowed; }}
.summary-table {{ width: 100%; border-collapse: collapse; margin: 1rem 0; }}
.summary-table th, .summary-table td {{ padding: 0.6rem 0.8rem; text-align: left; border-bottom: 1px solid #2d2d44; font-size: 0.85rem; }}
.summary-table th {{ color: #888; font-weight: 500; text-transform: uppercase; font-size: 0.7rem; letter-spacing: 0.05em; }}
.result-pass {{ color: #4caf50; }}
.result-fail {{ color: #ef5350; }}
.result-skip {{ color: #888; }}
.result-pending {{ color: #555; }}
.stats {{ display: flex; gap: 1rem; justify-content: center; margin: 1.5rem 0; flex-wrap: wrap; }}
.stat {{ text-align: center; padding: 1rem 1.5rem; background: #0a0e1a; border-radius: 8px; min-width: 80px; }}
.stat .num {{ font-size: 1.8rem; font-weight: 700; }}
.stat .label {{ font-size: 0.7rem; color: #888; text-transform: uppercase; margin-top: 0.2rem; }}
.overall {{ text-align: center; margin: 2rem 0; }}
.overall .verdict {{ font-size: 1.3rem; font-weight: 700; padding: 0.8rem 2rem; border-radius: 8px; display: inline-block; }}
.overall .verdict.all-pass {{ background: #1b5e20; color: #4caf50; }}
.overall .verdict.has-fail {{ background: #b71c1c; color: #ef5350; }}
.overall .verdict.incomplete {{ background: #2d2d44; color: #888; }}
.download-btn {{ display: block; width: 100%; padding: 1rem; background: #009688; color: #fff; border: none; border-radius: 8px; font-family: 'Roboto', sans-serif; font-size: 1rem; font-weight: 500; cursor: pointer; margin: 1rem 0; transition: background 0.2s; }}
.download-btn:hover {{ background: #00897b; }}
.reset-btn {{ display: block; width: 100%; padding: 0.7rem; background: transparent; color: #555; border: 1px solid #2d2d44; border-radius: 8px; font-family: 'Roboto', sans-serif; font-size: 0.8rem; cursor: pointer; margin: 0.5rem 0; }}
.reset-btn:hover {{ color: #c62828; border-color: #c62828; }}
.prereq-list {{ list-style: none; }}
.prereq-list li {{ padding: 0.8rem 0; border-bottom: 1px solid #2d2d44; }}
.prereq-list li:last-child {{ border-bottom: none; }}
.prereq-step {{ font-weight: 500; color: #ccc; margin-bottom: 0.3rem; }}
.exploratory {{ background: #1a1a2e; border: 1px dashed #2d2d44; border-radius: 8px; padding: 1.5rem; margin: 1rem 0; }}
.exploratory h3 {{ color: #ffc107; font-size: 0.9rem; margin-bottom: 0.8rem; }}
.exploratory ul {{ list-style: disc; padding-left: 1.5rem; }}
.exploratory li {{ color: #b0b0b0; padding: 0.3rem 0; font-size: 0.85rem; }}
.hidden {{ display: none !important; }}
@media (max-width: 600px) {{
  .container {{ padding: 1rem; }}
  .card {{ padding: 1.2rem; }}
  .verdict-buttons {{ flex-direction: column; gap: 0.5rem; }}
  .stats {{ gap: 0.5rem; }}
  .stat {{ padding: 0.7rem 1rem; min-width: 60px; }}
}}
</style>
</head>
<body>
<div class="container">
  <header>
    <h1>UAT Wizard</h1>
    <div class="meta">{project} &middot; {epic} &middot; {version}</div>
  </header>

  <div class="progress"><div class="progress-fill" id="progressFill"></div></div>
  <div class="progress-text" id="progressText"></div>

  <div id="wizardContent"></div>

  <div class="nav-buttons">
    <button class="nav-btn prev" id="prevBtn" onclick="navigate(-1)">Back</button>
    <button class="nav-btn next" id="nextBtn" onclick="navigate(1)">Next</button>
  </div>

  <button class="reset-btn" onclick="resetWizard()">Reset all progress</button>
</div>

<script>
const DATA = {json_data};

const STORAGE_KEY = 'uat-' + DATA.project + '-' + DATA.epic + '-' + DATA.version;

// Build steps array: prerequisites, scenarios, cross_cutting, exploratory, summary
const steps = [];
if (DATA.prerequisites && DATA.prerequisites.length) steps.push({{ type: 'prerequisites' }});
DATA.scenarios.forEach(function(s) {{ steps.push({{ type: 'scenario', data: s }}); }});
if (DATA.cross_cutting) DATA.cross_cutting.forEach(function(s) {{ steps.push({{ type: 'scenario', data: s }}); }});
if (DATA.exploratory && DATA.exploratory.length) steps.push({{ type: 'exploratory' }});
steps.push({{ type: 'summary' }});

let state = loadState();
let currentStep = state.currentStep || 0;

function loadState() {{
  try {{
    const saved = localStorage.getItem(STORAGE_KEY);
    return saved ? JSON.parse(saved) : {{ currentStep: 0, results: {{}}, startedAt: new Date().toISOString() }};
  }} catch(e) {{
    return {{ currentStep: 0, results: {{}}, startedAt: new Date().toISOString() }};
  }}
}}

function saveState() {{
  state.currentStep = currentStep;
  try {{ localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); }} catch(e) {{}}
}}

function escapeHtml(text) {{
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}}

function renderStep() {{
  const step = steps[currentStep];
  const content = document.getElementById('wizardContent');
  let h = '';

  if (step.type === 'prerequisites') {{
    h = '<div class="card"><h2>Prerequisites</h2>';
    h += '<p>Complete these steps before starting the test scenarios.</p>';
    h += '<ol class="prereq-list">';
    DATA.prerequisites.forEach(function(p, i) {{
      h += '<li><div class="prereq-step">' + (i+1) + '. ' + escapeHtml(p.step) + '</div>';
      if (p.command) h += '<div class="command-block"><code>' + escapeHtml(p.command) + '</code><button class="copy-btn" onclick="copyCmd(this)">Copy</button></div>';
      h += '</li>';
    }});
    h += '</ol></div>';
  }}

  else if (step.type === 'scenario') {{
    const s = step.data;
    const r = state.results[s.id] || {{}};
    const sev = s.severity || 'minor';
    h = '<div class="card">';
    h += '<span class="feature-badge">' + escapeHtml(s.feature || '') + '</span>';
    if (sev) h += '<span class="severity severity-' + sev + '">' + sev + '</span>';
    h += '<h2>' + escapeHtml(s.title) + '</h2>';
    if (s.description) h += '<p>' + escapeHtml(s.description) + '</p>';
    if (s.command) {{
      h += '<div class="command-block"><code>' + escapeHtml(s.command) + '</code>';
      h += '<button class="copy-btn" onclick="copyCmd(this)">Copy</button></div>';
    }}
    h += '<ul class="checks">';
    (s.checks || []).forEach(function(c) {{ h += '<li>' + escapeHtml(c) + '</li>'; }});
    h += '</ul>';
    h += '<div class="verdict-buttons">';
    h += '<button class="verdict-btn pass' + (r.verdict === 'pass' ? ' selected' : '') + '" onclick="setVerdict(\\''+s.id+'\\',\\'pass\\')">Pass</button>';
    h += '<button class="verdict-btn fail' + (r.verdict === 'fail' ? ' selected' : '') + '" onclick="setVerdict(\\''+s.id+'\\',\\'fail\\')">Fail</button>';
    h += '<button class="verdict-btn skip' + (r.verdict === 'skip' ? ' selected' : '') + '" onclick="setVerdict(\\''+s.id+'\\',\\'skip\\')">Skip</button>';
    h += '</div>';
    h += '<textarea class="comment-field" placeholder="Optional: add a comment..." oninput="setComment(\\''+s.id+'\\', this.value)">' + escapeHtml(r.comment || '') + '</textarea>';
    h += '</div>';
  }}

  else if (step.type === 'exploratory') {{
    h = '<div class="card"><div class="exploratory"><h3>Exploratory Testing (Optional)</h3>';
    h += '<p>Try these edge cases if you have time:</p><ul>';
    DATA.exploratory.forEach(function(e) {{ h += '<li>' + escapeHtml(e) + '</li>'; }});
    h += '</ul></div></div>';
  }}

  else if (step.type === 'summary') {{
    h = renderSummary();
  }}

  content.innerHTML = h;
  updateProgress();
  updateNavButtons();
  saveState();
}}

function renderSummary() {{
  const allScenarios = DATA.scenarios.concat(DATA.cross_cutting || []);
  let passed = 0, failed = 0, skipped = 0, pending = 0;
  allScenarios.forEach(function(s) {{
    const r = state.results[s.id];
    if (!r || !r.verdict) pending++;
    else if (r.verdict === 'pass') passed++;
    else if (r.verdict === 'fail') failed++;
    else skipped++;
  }});
  const total = allScenarios.length;
  let verdictClass = 'incomplete';
  let verdictText = 'Incomplete — ' + pending + ' scenarios remaining';
  if (pending === 0 && failed === 0) {{ verdictClass = 'all-pass'; verdictText = 'All Passed — Ready to Approve'; }}
  else if (pending === 0 && failed > 0) {{ verdictClass = 'has-fail'; verdictText = failed + ' Failed — Needs Fixes'; }}

  let h = '<div class="card">';
  h += '<h2>UAT Summary</h2>';
  h += '<div class="stats">';
  h += '<div class="stat"><div class="num result-pass">' + passed + '</div><div class="label">Passed</div></div>';
  h += '<div class="stat"><div class="num result-fail">' + failed + '</div><div class="label">Failed</div></div>';
  h += '<div class="stat"><div class="num result-skip">' + skipped + '</div><div class="label">Skipped</div></div>';
  h += '<div class="stat"><div class="num result-pending">' + pending + '</div><div class="label">Pending</div></div>';
  h += '</div>';
  h += '<div class="overall"><div class="verdict ' + verdictClass + '">' + verdictText + '</div></div>';
  h += '<table class="summary-table"><thead><tr><th>Scenario</th><th>Feature</th><th>Result</th><th>Comment</th></tr></thead><tbody>';
  allScenarios.forEach(function(s) {{
    const r = state.results[s.id] || {{}};
    const v = r.verdict || 'pending';
    h += '<tr><td>' + escapeHtml(s.id) + '</td><td>' + escapeHtml(s.feature || s.title) + '</td>';
    h += '<td class="result-' + v + '">' + v.toUpperCase() + '</td>';
    h += '<td>' + escapeHtml(r.comment || '—') + '</td></tr>';
  }});
  h += '</tbody></table>';
  h += '<button class="download-btn" onclick="downloadResults()">Download Results as Markdown</button>';
  h += '</div>';
  return h;
}}

function setVerdict(id, verdict) {{
  if (!state.results[id]) state.results[id] = {{}};
  state.results[id].verdict = verdict;
  state.results[id].timestamp = new Date().toISOString();
  saveState();
  renderStep();
}}

function setComment(id, comment) {{
  if (!state.results[id]) state.results[id] = {{}};
  state.results[id].comment = comment;
  saveState();
}}

function navigate(dir) {{
  const next = currentStep + dir;
  if (next >= 0 && next < steps.length) {{
    currentStep = next;
    renderStep();
    window.scrollTo(0, 0);
  }}
}}

function updateProgress() {{
  const allScenarios = DATA.scenarios.concat(DATA.cross_cutting || []);
  const done = allScenarios.filter(function(s) {{ return state.results[s.id] && state.results[s.id].verdict; }}).length;
  const total = allScenarios.length;
  const pct = total > 0 ? (done / total * 100) : 0;
  document.getElementById('progressFill').style.width = pct + '%';
  document.getElementById('progressText').textContent = done + ' of ' + total + ' scenarios completed';
}}

function updateNavButtons() {{
  document.getElementById('prevBtn').disabled = currentStep === 0;
  const isLast = currentStep === steps.length - 1;
  document.getElementById('nextBtn').textContent = isLast ? 'Done' : 'Next';
  document.getElementById('nextBtn').disabled = isLast;
}}

function copyCmd(btn) {{
  const code = btn.parentElement.querySelector('code').textContent;
  navigator.clipboard.writeText(code).then(function() {{
    btn.textContent = 'Copied!';
    setTimeout(function() {{ btn.textContent = 'Copy'; }}, 1500);
  }});
}}

function downloadResults() {{
  const allScenarios = DATA.scenarios.concat(DATA.cross_cutting || []);
  let md = '# UAT Results — ' + DATA.title + '\\n\\n';
  md += '**Project:** ' + DATA.project + '\\n';
  md += '**Epic:** ' + DATA.epic + '\\n';
  md += '**Version:** ' + DATA.version + '\\n';
  md += '**Date:** ' + new Date().toISOString().split('T')[0] + '\\n\\n';
  md += '## Results\\n\\n';
  md += '| Scenario | Feature | Result | Comment |\\n';
  md += '|----------|---------|--------|---------|\\n';
  let passed = 0, failed = 0;
  allScenarios.forEach(function(s) {{
    const r = state.results[s.id] || {{}};
    const v = (r.verdict || 'PENDING').toUpperCase();
    if (r.verdict === 'pass') passed++;
    if (r.verdict === 'fail') failed++;
    md += '| ' + s.id + ' | ' + (s.feature || s.title) + ' | ' + v + ' | ' + (r.comment || '—') + ' |\\n';
  }});
  md += '\\n## Verdict\\n\\n';
  if (failed > 0) md += '**REJECTED** — ' + failed + ' scenario(s) failed.\\n';
  else if (passed === allScenarios.length) md += '**APPROVED** — all scenarios passed.\\n';
  else md += '**INCOMPLETE** — not all scenarios have been tested.\\n';
  md += '\\n**Tester signature:** _________________ **Date:** _____________\\n';

  const blob = new Blob([md], {{ type: 'text/markdown' }});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'uat-results-' + DATA.epic + '-' + DATA.version + '.md';
  a.click();
  URL.revokeObjectURL(url);
}}

function resetWizard() {{
  if (confirm('Reset all progress? This cannot be undone.')) {{
    localStorage.removeItem(STORAGE_KEY);
    state = {{ currentStep: 0, results: {{}}, startedAt: new Date().toISOString() }};
    currentStep = 0;
    renderStep();
  }}
}}

// Keyboard navigation
document.addEventListener('keydown', function(e) {{
  if (e.target.tagName === 'TEXTAREA') return;
  if (e.key === 'ArrowRight') navigate(1);
  if (e.key === 'ArrowLeft') navigate(-1);
}});

// Initial render
renderStep();
</script>
</body>
</html>"""


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate an interactive UAT wizard from a YAML scenario file."
    )
    parser.add_argument("scenarios", type=Path, help="Path to YAML scenario file")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("docs/uat-wizard.html"),
        help="Output HTML file path (default: docs/uat-wizard.html)",
    )
    args = parser.parse_args()

    if not args.scenarios.exists():
        print(f"Error: File not found: {args.scenarios}", file=sys.stderr)
        sys.exit(1)

    data = load_scenarios(args.scenarios)
    html_content = generate_html(data)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    html_out = html_content.rstrip() + "\n"
    args.output.write_text(html_out, encoding="utf-8")

    scenario_count = len(data["scenarios"]) + len(data.get("cross_cutting", []))
    print(f"Generated UAT wizard: {args.output} ({scenario_count} scenarios)")


if __name__ == "__main__":
    main()
