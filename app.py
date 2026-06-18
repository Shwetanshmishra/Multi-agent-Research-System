import os
import streamlit as st
import time

# ─────────────────────────────────────────────────────────────────────────────
# Key loader — works both locally (.env) and on Streamlit Cloud (secrets)
# Must run BEFORE any agent/tool imports so os.environ is populated first
# ─────────────────────────────────────────────────────────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# Streamlit Cloud: push secrets → os.environ so tools.py / agents.py pick them up
try:
    for _k, _v in st.secrets.items():
        os.environ.setdefault(str(_k), str(_v))
except Exception:
    pass

# ─────────────────────────────────────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ResearchMind — Multi-Agent AI System",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# Design tokens & global CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow:ital,wght@0,400;0,500;0,600;0,700;0,800;0,900;1,400&family=Barlow+Condensed:wght@500;600;700;800;900&family=IBM+Plex+Mono:wght@400;500&display=swap');

/* ── Tokens ── */
:root {
  --ink:          #09090B;
  --ink-2:        #111114;
  --ink-3:        #18181C;
  --ink-4:        #222228;
  --border:       #2A2A34;
  --border-soft:  #1E1E26;

  --orange:       #F97316;
  --orange-dim:   #7C3B0E;
  --orange-glow:  rgba(249,115,22,.18);

  --white:        #F4F4F5;
  --grey-1:       #A1A1AA;
  --grey-2:       #52525B;
  --grey-3:       #3F3F46;

  --green:        #22C55E;
  --green-dim:    #14532D;
  --red:          #EF4444;
  --red-dim:      #7F1D1D;
  --blue:         #60A5FA;

  --font-display: 'Barlow Condensed', sans-serif;
  --font-body:    'Barlow', sans-serif;
  --font-mono:    'IBM Plex Mono', monospace;

  --r-sm: 4px;
  --r-md: 8px;
  --r-lg: 14px;
}

/* ── Hard reset ── */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"] {
  background: var(--ink) !important;
  color: var(--white);
  font-family: var(--font-body);
}
[data-testid="stHeader"]    { display: none !important; }
[data-testid="stToolbar"]   { display: none !important; }
footer                      { display: none !important; }
#MainMenu                   { display: none !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
  background: var(--ink-2) !important;
  border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebarContent"] { padding: 0 !important; }

/* ── Input overrides ── */
.stTextInput > div > div > input {
  background: var(--ink-3) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--r-md) !important;
  color: var(--white) !important;
  font-family: var(--font-body) !important;
  font-size: 15px !important;
  padding: 13px 16px !important;
  transition: border-color .15s !important;
}
.stTextInput > div > div > input::placeholder { color: var(--grey-2) !important; }
.stTextInput > div > div > input:focus {
  border-color: var(--orange) !important;
  box-shadow: 0 0 0 3px var(--orange-glow) !important;
  outline: none !important;
}
.stTextInput label { display: none !important; }

/* ── Button ── */
.stButton > button {
  background: var(--orange) !important;
  color: var(--ink) !important;
  border: none !important;
  border-radius: var(--r-md) !important;
  font-family: var(--font-display) !important;
  font-size: 15px !important;
  font-weight: 700 !important;
  letter-spacing: .06em !important;
  text-transform: uppercase !important;
  padding: 13px 26px !important;
  width: 100% !important;
  transition: background .15s, transform .1s !important;
}
.stButton > button:hover   { background: #FB923C !important; transform: translateY(-1px) !important; }
.stButton > button:active  { transform: translateY(0) !important; }
.stButton > button:disabled {
  background: var(--grey-3) !important;
  color: var(--grey-2) !important;
  cursor: not-allowed !important;
}

/* ── Tabs ── */
[data-testid="stTabs"] [role="tablist"] {
  background: var(--ink-3) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--r-md) !important;
  padding: 4px !important;
  gap: 2px !important;
}
[data-testid="stTabs"] [role="tab"] {
  font-family: var(--font-body) !important;
  font-size: 13px !important;
  font-weight: 600 !important;
  color: var(--grey-1) !important;
  border-radius: var(--r-sm) !important;
  padding: 8px 20px !important;
  letter-spacing: .02em !important;
  transition: color .15s !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
  background: var(--ink-4) !important;
  color: var(--white) !important;
  box-shadow: 0 1px 4px rgba(0,0,0,.5) !important;
}

/* ── Download button ── */
.stDownloadButton > button {
  background: var(--ink-4) !important;
  color: var(--white) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--r-md) !important;
  font-family: var(--font-body) !important;
  font-size: 13px !important;
  font-weight: 600 !important;
  padding: 10px 16px !important;
  width: 100% !important;
}
.stDownloadButton > button:hover {
  border-color: var(--orange) !important;
  color: var(--orange) !important;
}

/* ── Progress bar ── */
[data-testid="stProgressBar"] > div > div {
  background: var(--orange) !important;
}
[data-testid="stProgressBar"] > div {
  background: var(--ink-4) !important;
  border-radius: 99px !important;
  height: 4px !important;
}

/* ── Markdown in output ── */
.rm p   { color: var(--grey-1); font-size: 14px; line-height: 1.8; margin: 6px 0; }
.rm h1  { color: var(--white); font-family: var(--font-display); font-size: 22px;
          font-weight: 800; letter-spacing: .02em; margin: 20px 0 8px; }
.rm h2  { color: var(--white); font-family: var(--font-display); font-size: 18px;
          font-weight: 700; margin: 16px 0 6px; }
.rm h3  { color: var(--orange); font-size: 13px; font-weight: 700;
          text-transform: uppercase; letter-spacing: .1em; margin: 14px 0 4px; }
.rm a   { color: var(--orange); text-decoration: none; }
.rm a:hover { text-decoration: underline; }
.rm ul, .rm ol { color: var(--grey-1); font-size: 14px; line-height: 1.8; padding-left: 20px; }
.rm li  { margin-bottom: 4px; }
.rm code {
  background: var(--ink-4); color: var(--orange);
  border-radius: 3px; padding: 1px 6px;
  font-family: var(--font-mono); font-size: 12px;
}
.rm pre {
  background: var(--ink-4) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--r-md) !important;
  padding: 14px !important; overflow-x: auto;
}
.rm hr  { border: none; border-top: 1px solid var(--border); margin: 16px 0; }
.rm blockquote {
  border-left: 3px solid var(--orange);
  background: var(--ink-3);
  padding: 10px 16px;
  border-radius: 0 var(--r-sm) var(--r-sm) 0;
  margin: 12px 0;
  color: var(--grey-1);
}
.rm strong { color: var(--white); font-weight: 600; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 99px; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Session state
# ─────────────────────────────────────────────────────────────────────────────
def _init():
    defs = dict(
        running=False, done=False, error=None,
        search_results="", scraped_content="",
        report="", feedback="",
        elapsed=0.0, step=0, history=[],
    )
    for k, v in defs.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init()


# ─────────────────────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────────────────────
STEPS = [
    ("01", "🔍", "Search",  "Discovers & ranks sources"),
    ("02", "📖", "Reader",  "Reads & extracts content"),
    ("03", "✍", "Writer",  "Synthesises the report"),
    ("04", "🧐", "Critic",  "Evaluates quality"),
]

with st.sidebar:
    # Brand block
    st.markdown("""
    <div style="padding:28px 24px 22px;border-bottom:1px solid #2A2A34;">
      <div style="font-family:'Barlow Condensed',sans-serif;
                  font-size:11px;font-weight:700;color:#F97316;
                  letter-spacing:.18em;text-transform:uppercase;
                  margin-bottom:10px;">Multi-Agent AI System</div>
      <div style="font-family:'Barlow Condensed',sans-serif;
                  font-size:36px;font-weight:900;line-height:1;color:#F4F4F5;">
        Research<span style="color:#F97316;">Mind</span>
      </div>
      <div style="font-size:12px;color:#52525B;margin-top:8px;">
        Four agents · One report
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Pipeline stages
    st.markdown("""
    <div style="padding:20px 24px 8px;">
      <div style="font-family:'IBM Plex Mono',monospace;font-size:10px;
                  color:#3F3F46;letter-spacing:.15em;text-transform:uppercase;
                  margin-bottom:14px;">Pipeline Stages</div>
    """, unsafe_allow_html=True)

    s = st.session_state.step
    for num, icon, name, desc in STEPS:
        idx = int(num)
        if s == 5 or s > idx:
            bar_col, badge_bg, badge_col, badge_txt = "#22C55E", "#14532D", "#22C55E", "DONE"
            left_col = "#22C55E"
        elif s == idx:
            bar_col, badge_bg, badge_col, badge_txt = "#F97316", "#7C3B0E", "#F97316", "LIVE"
            left_col = "#F97316"
        else:
            bar_col, badge_bg, badge_col, badge_txt = "#2A2A34", "#18181C", "#52525B", "IDLE"
            left_col = "#2A2A34"

        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;
                    padding:12px 0;border-bottom:1px solid #1E1E26;">
          <div style="width:3px;height:38px;background:{left_col};
                      border-radius:2px;flex-shrink:0;"></div>
          <div style="font-family:'Barlow Condensed',sans-serif;
                      font-size:13px;font-weight:800;color:#3F3F46;
                      flex-shrink:0;">{num}</div>
          <div style="flex:1;min-width:0;">
            <div style="font-size:13px;font-weight:700;color:#F4F4F5;">
              {icon} {name}
            </div>
            <div style="font-size:11px;color:#52525B;margin-top:2px;">{desc}</div>
          </div>
          <div style="background:{badge_bg};color:{badge_col};
                      font-family:'IBM Plex Mono',monospace;
                      font-size:9px;font-weight:500;
                      padding:3px 7px;border-radius:99px;
                      flex-shrink:0;">{badge_txt}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Stats
    runs = len(st.session_state.history)
    words = len(st.session_state.report.split()) if st.session_state.report else 0
    st.markdown(f"""
    <div style="padding:20px 24px;border-top:1px solid #1E1E26;margin-top:auto;">
      <div style="display:flex;gap:0;border:1px solid #2A2A34;
                  border-radius:8px;overflow:hidden;">
        <div style="flex:1;padding:12px 14px;background:#111114;">
          <div style="font-size:10px;color:#52525B;font-family:'IBM Plex Mono',monospace;
                      text-transform:uppercase;letter-spacing:.1em;">Runs</div>
          <div style="font-size:22px;font-weight:800;color:#F4F4F5;
                      font-family:'Barlow Condensed',sans-serif;">{runs}</div>
        </div>
        <div style="width:1px;background:#2A2A34;"></div>
        <div style="flex:1;padding:12px 14px;background:#111114;">
          <div style="font-size:10px;color:#52525B;font-family:'IBM Plex Mono',monospace;
                      text-transform:uppercase;letter-spacing:.1em;">Words</div>
          <div style="font-size:22px;font-weight:800;color:#F4F4F5;
                      font-family:'Barlow Condensed',sans-serif;">{words:,}</div>
        </div>
        <div style="width:1px;background:#2A2A34;"></div>
        <div style="flex:1;padding:12px 14px;background:#111114;">
          <div style="font-size:10px;color:#52525B;font-family:'IBM Plex Mono',monospace;
                      text-transform:uppercase;letter-spacing:.1em;">Time</div>
          <div style="font-size:22px;font-weight:800;color:#F4F4F5;
                      font-family:'Barlow Condensed',sans-serif;">{st.session_state.elapsed:.0f}s</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # History
    if st.session_state.history:
        st.markdown("""
        <div style="padding:0 24px 8px;">
          <div style="font-family:'IBM Plex Mono',monospace;font-size:10px;
                      color:#3F3F46;letter-spacing:.15em;text-transform:uppercase;
                      margin-bottom:10px;">Recent Topics</div>
        """, unsafe_allow_html=True)
        for h in reversed(st.session_state.history[-4:]):
            short = h[:30] + "…" if len(h) > 30 else h
            st.markdown(f"""
            <div style="font-size:12px;color:#52525B;padding:6px 0;
                        border-bottom:1px solid #1E1E26;
                        white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
              ↳ {short}
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Main — Hero header
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="
  padding: 48px 0 32px;
  border-bottom: 1px solid #2A2A34;
  margin-bottom: 32px;
">
  <div style="
    font-family:'Barlow Condensed',sans-serif;
    font-size:11px;font-weight:700;
    color:#F97316;letter-spacing:.2em;
    text-transform:uppercase;margin-bottom:12px;
  ">Multi-Agent AI System</div>

  <div style="
    font-family:'Barlow Condensed',sans-serif;
    font-size:clamp(52px,7vw,80px);
    font-weight:900;line-height:.95;
    color:#F4F4F5;letter-spacing:-.01em;
    margin-bottom:18px;
  ">
    Research<span style="color:#F97316;">Mind</span>
  </div>

  <p style="
    font-size:15px;color:#71717A;
    max-width:580px;line-height:1.65;margin:0;
  ">
    Four specialised AI agents collaborate — searching, scraping, writing,
    and critiquing — to deliver a polished research report on any topic.
  </p>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Input row
# ─────────────────────────────────────────────────────────────────────────────
col_in, col_btn = st.columns([5, 1], gap="small")
with col_in:
    topic = st.text_input(
        "topic",
        placeholder="Enter a research topic — e.g.  The future of nuclear fusion energy",
        label_visibility="collapsed",
    )
with col_btn:
    st.markdown('<div style="height:2px"></div>', unsafe_allow_html=True)
    run = st.button("RUN  ▶", disabled=st.session_state.running)


# ─────────────────────────────────────────────────────────────────────────────
# Status bar  (always visible, changes content)
# ─────────────────────────────────────────────────────────────────────────────
status_ph = st.empty()

def render_status(msg, kind="idle"):
    colours = {
        "idle":    ("#18181C", "#2A2A34", "#52525B"),
        "running": ("#0F1F3D", "#1D3A8A", "#93C5FD"),
        "done":    ("#052E1E", "#065F46", "#6EE7B7"),
        "error":   ("#2D0A0A", "#7F1D1D", "#FCA5A5"),
    }
    bg, border, col = colours.get(kind, colours["idle"])
    dot = "●" if kind == "running" else ("✓" if kind == "done" else ("✕" if kind == "error" else "○"))
    status_ph.markdown(f"""
    <div style="
      background:{bg};border:1px solid {border};
      border-radius:{6}px;padding:11px 16px;
      font-family:'IBM Plex Mono',monospace;
      font-size:12px;color:{col};
      display:flex;align-items:center;gap:10px;
      margin:10px 0 18px;
    ">
      <span style="font-size:10px;">{dot}</span>
      <span>{msg}</span>
    </div>
    """, unsafe_allow_html=True)

if st.session_state.running:
    render_status("Pipeline running…", "running")
elif st.session_state.done:
    render_status(f"Complete in {st.session_state.elapsed:.1f}s  ·  {len(st.session_state.report.split()):,} words generated", "done")
elif st.session_state.error:
    render_status(f"Error — {st.session_state.error[:120]}", "error")
else:
    render_status("Idle  ·  Enter a topic and click RUN", "idle")


# ─────────────────────────────────────────────────────────────────────────────
# Trigger
# ─────────────────────────────────────────────────────────────────────────────
if run:
    if not topic.strip():
        st.warning("Please enter a research topic.")
    else:
        for k in ("search_results","scraped_content","report","feedback","error"):
            st.session_state[k] = "" if k != "error" else None
        st.session_state.update(running=True, done=False, step=0, elapsed=0.0)
        st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# Pipeline execution
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.running and not st.session_state.done:

    prog_ph = st.empty()

    def set_progress(pct, txt):
        prog_ph.progress(pct, text=f"**{txt}**")

    t0 = time.time()

    try:
        from agents import run_search_agent, run_reader_agent, writer_chain, critic_chain

        # Step 1 — Search
        st.session_state.step = 1
        render_status("Step 1 / 4 — Search Agent  ·  querying the web for sources…", "running")
        set_progress(8, "Search Agent is scanning the web…")

        st.session_state.search_results = run_search_agent(topic)

        # Step 2 — Reader
        st.session_state.step = 2
        render_status("Step 2 / 4 — Reader Agent  ·  reading and extracting content…", "running")
        set_progress(35, "Reader Agent is extracting content from sources…")

        st.session_state.scraped_content = run_reader_agent(st.session_state.search_results)

        # Step 3 — Writer
        st.session_state.step = 3
        render_status("Step 3 / 4 — Writer Agent  ·  composing the research report…", "running")
        set_progress(62, "Writer Agent is composing the report…")

        research = f"SEARCH RESULTS\n{st.session_state.search_results}\n\nSCRAPED CONTENT\n{st.session_state.scraped_content}"
        st.session_state.report = writer_chain.invoke({"topic": topic, "research": research})

        # Step 4 — Critic
        st.session_state.step = 4
        render_status("Step 4 / 4 — Critic Agent  ·  evaluating quality and accuracy…", "running")
        set_progress(86, "Critic Agent is evaluating the report…")

        st.session_state.feedback = critic_chain.invoke({"report": st.session_state.report})

        # Done
        st.session_state.elapsed = round(time.time() - t0, 1)
        st.session_state.step    = 5
        st.session_state.done    = True
        st.session_state.running = False
        st.session_state.history.append(topic)
        prog_ph.progress(100, text="**Pipeline complete.**")
        time.sleep(0.4)
        st.rerun()

    except ImportError as e:
        st.session_state.error   = f"Import error: {e}"
        st.session_state.running = False
        st.session_state.step    = 0
        st.rerun()
    except Exception as e:
        st.session_state.error   = str(e)
        st.session_state.running = False
        st.session_state.step    = 0
        st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# Results
# ─────────────────────────────────────────────────────────────────────────────
def output_panel(content: str, mono: bool = False):
    font = "font-family:'IBM Plex Mono',monospace;font-size:13px;" if mono else ""
    st.markdown(f"""
    <div style="
      background:#111114;border:1px solid #2A2A34;
      border-radius:8px;padding:28px 32px;
      max-height:560px;overflow-y:auto;
      {font}
    " class="rm">
    """, unsafe_allow_html=True)
    st.markdown(content)
    st.markdown("</div>", unsafe_allow_html=True)


if st.session_state.done:
    # Section label
    st.markdown("""
    <div style="
      font-family:'IBM Plex Mono',monospace;font-size:10px;
      color:#3F3F46;letter-spacing:.2em;text-transform:uppercase;
      margin-bottom:14px;
    ">Output</div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([
        "🔍  Sources",
        "📖  Extracted Content",
        "✍  Research Report",
        "🧐  Critic Review",
    ])

    with tab1:
        output_panel(st.session_state.search_results)

    with tab2:
        output_panel(st.session_state.scraped_content)

    with tab3:
        c1, c2 = st.columns([6, 1], gap="small")
        with c1:
            output_panel(st.session_state.report)
        with c2:
            st.markdown('<div style="height:2px"></div>', unsafe_allow_html=True)
            st.download_button(
                "⬇ .md",
                data=st.session_state.report,
                file_name=f"researchmind_{int(time.time())}.md",
                mime="text/markdown",
                use_container_width=True,
            )

    with tab4:
        # Critic gets a two-column layout: quality pill + content
        ca, cb = st.columns([1, 3], gap="small")
        with ca:
            st.markdown("""
            <div style="
              background:#111114;border:1px solid #2A2A34;
              border-radius:8px;padding:24px 16px;
              text-align:center;
            ">
              <div style="font-size:10px;color:#3F3F46;
                          font-family:'IBM Plex Mono',monospace;
                          letter-spacing:.15em;text-transform:uppercase;
                          margin-bottom:12px;">Quality Gate</div>
              <div style="font-size:40px;margin-bottom:10px;">🧐</div>
              <div style="font-size:12px;color:#52525B;line-height:1.5;">
                Independent review of accuracy, depth & coherence
              </div>
            </div>
            """, unsafe_allow_html=True)
        with cb:
            output_panel(st.session_state.feedback)

else:
    # ── Empty / idle state ────────────────────────────────────────────────────
    if not st.session_state.running:
        st.markdown("""
        <div style="
          background:#111114;border:1px dashed #2A2A34;
          border-radius:12px;padding:72px 32px;
          text-align:center;margin-top:8px;
        ">
          <div style="font-size:48px;margin-bottom:16px;">⚗️</div>
          <div style="
            font-family:'Barlow Condensed',sans-serif;
            font-size:22px;font-weight:800;
            color:#F4F4F5;margin-bottom:8px;
          ">Ready to research</div>
          <div style="font-size:14px;color:#52525B;max-width:380px;margin:0 auto;">
            Type any topic above and click <strong style="color:#F97316;">RUN</strong>
            to start the four-agent pipeline.
          </div>
        </div>
        """, unsafe_allow_html=True)