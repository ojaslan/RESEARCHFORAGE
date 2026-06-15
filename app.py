import streamlit as st
import networkx as nx
import json
import random
from pyvis.network import Network
import tempfile
import os
import pandas as pd

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Knowledge Graph Agent",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .stApp { background-color: #0d1117; color: #e6edf3; }

    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #161b22;
        border-right: 1px solid #30363d;
    }
    section[data-testid="stSidebar"] * { color: #e6edf3 !important; }

    /* Cards */
    .kg-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 1rem 1.25rem;
        margin-bottom: 0.75rem;
    }
    .kg-card h4 { margin: 0 0 0.25rem; color: #58a6ff; font-size: 0.95rem; }
    .kg-card p  { margin: 0; font-size: 0.82rem; color: #8b949e; }

    /* Metric tiles */
    .metric-row { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 1rem; }
    .metric-tile {
        flex: 1; min-width: 110px;
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 0.8rem 1rem;
        text-align: center;
    }
    .metric-tile .val { font-size: 1.7rem; font-weight: 700; color: #58a6ff; }
    .metric-tile .lbl { font-size: 0.72rem; color: #8b949e; text-transform: uppercase; letter-spacing: .05em; }

    /* Section header */
    .section-header {
        font-size: 0.72rem;
        font-weight: 600;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: .08em;
        margin: 1.2rem 0 0.5rem;
    }

    /* Tag pills */
    .tag {
        display: inline-block;
        background: #1f2d3d;
        color: #58a6ff;
        border: 1px solid #2d4a6b;
        border-radius: 20px;
        padding: 2px 10px;
        font-size: 0.75rem;
        margin: 2px 3px;
    }

    /* Buttons */
    .stButton > button {
        background: #238636 !important;
        color: #fff !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        transition: background .2s;
    }
    .stButton > button:hover { background: #2ea043 !important; }

    /* Input fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div {
        background: #0d1117 !important;
        border: 1px solid #30363d !important;
        color: #e6edf3 !important;
        border-radius: 6px !important;
    }

    /* Iframe (graph) border */
    iframe { border-radius: 10px; border: 1px solid #30363d; }

    h1 { color: #e6edf3 !important; font-weight: 700; }
    h2, h3 { color: #c9d1d9 !important; }
    .stMarkdown p { color: #8b949e; }
</style>
""", unsafe_allow_html=True)

# ── Seed data ──────────────────────────────────────────────────────────────────
DEFAULT_DATA = {
    "nodes": [
        # Domains
        {"id": "AI",             "type": "domain",   "label": "Artificial Intelligence", "year": 1956, "citations": 45200},
        {"id": "ML",             "type": "domain",   "label": "Machine Learning",        "year": 1959, "citations": 38700},
        {"id": "NLP",            "type": "domain",   "label": "Natural Language Processing","year": 1950,"citations": 27100},
        {"id": "CV",             "type": "domain",   "label": "Computer Vision",         "year": 1966, "citations": 31400},
        {"id": "RL",             "type": "domain",   "label": "Reinforcement Learning",  "year": 1980, "citations": 18900},

        # Papers
        {"id": "attention",      "type": "paper",    "label": "Attention Is All You Need","year": 2017,"citations": 72000},
        {"id": "bert",           "type": "paper",    "label": "BERT",                    "year": 2018, "citations": 58000},
        {"id": "gpt3",           "type": "paper",    "label": "GPT-3",                   "year": 2020, "citations": 41000},
        {"id": "resnet",         "type": "paper",    "label": "ResNet",                  "year": 2015, "citations": 95000},
        {"id": "alphago",        "type": "paper",    "label": "AlphaGo",                 "year": 2016, "citations": 12000},
        {"id": "gan",            "type": "paper",    "label": "Generative Adversarial Nets","year":2014,"citations": 53000},
        {"id": "llama",          "type": "paper",    "label": "LLaMA",                   "year": 2023, "citations": 14000},
        {"id": "stable_diff",    "type": "paper",    "label": "Stable Diffusion",        "year": 2022, "citations": 9000},

        # Researchers
        {"id": "hinton",         "type": "researcher","label": "Geoffrey Hinton",         "year": 1947,"citations": 310000},
        {"id": "lecun",          "type": "researcher","label": "Yann LeCun",              "year": 1960, "citations": 218000},
        {"id": "bengio",         "type": "researcher","label": "Yoshua Bengio",           "year": 1964, "citations": 247000},
        {"id": "vaswani",        "type": "researcher","label": "Ashish Vaswani",          "year": 1985, "citations": 76000},
        {"id": "lecun2",         "type": "researcher","label": "Tomas Mikolov",           "year": 1981, "citations": 64000},

        # Institutions
        {"id": "google",         "type": "institution","label": "Google DeepMind",       "year": 2010, "citations": 0},
        {"id": "openai",         "type": "institution","label": "OpenAI",                "year": 2015, "citations": 0},
        {"id": "meta_ai",        "type": "institution","label": "Meta AI (FAIR)",        "year": 2013, "citations": 0},
        {"id": "mila",           "type": "institution","label": "Mila – Quebec AI",      "year": 1993, "citations": 0},

        # Techniques
        {"id": "transformer",    "type": "technique","label": "Transformer",             "year": 2017, "citations": 0},
        {"id": "cnn",            "type": "technique","label": "CNN",                     "year": 1989, "citations": 0},
        {"id": "llm",            "type": "technique","label": "Large Language Models",   "year": 2018, "citations": 0},
        {"id": "diffusion",      "type": "technique","label": "Diffusion Models",        "year": 2020, "citations": 0},
    ],
    "edges": [
        # domain → domain
        ("AI","ML","contains"), ("AI","NLP","contains"), ("AI","CV","contains"), ("AI","RL","contains"),
        ("ML","NLP","enables"), ("ML","CV","enables"), ("ML","RL","enables"),
        # papers → domains
        ("attention","NLP","advances"), ("bert","NLP","advances"), ("gpt3","NLP","advances"),
        ("resnet","CV","advances"), ("alphago","RL","advances"), ("gan","CV","advances"),
        ("llama","NLP","advances"), ("stable_diff","CV","advances"),
        # techniques
        ("attention","transformer","introduces"), ("transformer","llm","enables"),
        ("resnet","cnn","extends"), ("stable_diff","diffusion","uses"),
        # researchers → papers
        ("vaswani","attention","authored"), ("hinton","gan","inspired"),
        ("lecun","resnet","inspired"), ("bengio","bert","inspired"),
        # researchers → institutions
        ("hinton","google","affiliated"), ("lecun","meta_ai","affiliated"),
        ("bengio","mila","affiliated"), ("vaswani","google","affiliated"),
        # institutions → papers
        ("google","alphago","produced"), ("openai","gpt3","produced"),
        ("meta_ai","llama","produced"), ("google","attention","produced"),
        ("openai","stable_diff","produced"),
        # cross links
        ("bert","transformer","built_on"), ("gpt3","transformer","built_on"),
        ("llama","transformer","built_on"),
    ]
}

# Node type visual config
TYPE_CONFIG = {
    "domain":      {"color": "#1f6feb", "shape": "dot",     "size": 30, "emoji": "🌐"},
    "paper":       {"color": "#388bfd", "shape": "square",  "size": 18, "emoji": "📄"},
    "researcher":  {"color": "#3fb950", "shape": "triangle","size": 20, "emoji": "👤"},
    "institution": {"color": "#d29922", "shape": "diamond", "size": 22, "emoji": "🏛️"},
    "technique":   {"color": "#bc8cff", "shape": "ellipse", "size": 16, "emoji": "⚙️"},
}

EDGE_COLORS = {
    "contains":   "#1f6feb", "enables":    "#388bfd", "advances":   "#3fb950",
    "introduces": "#bc8cff", "extends":    "#bc8cff", "uses":       "#bc8cff",
    "authored":   "#3fb950", "inspired":   "#3fb950", "affiliated": "#d29922",
    "produced":   "#d29922", "built_on":   "#e3b341",
}

# ── Session state ──────────────────────────────────────────────────────────────
if "graph_data" not in st.session_state:
    st.session_state.graph_data = DEFAULT_DATA.copy()
if "selected_node" not in st.session_state:
    st.session_state.selected_node = None

# ── Helpers ────────────────────────────────────────────────────────────────────
def build_nx(data):
    G = nx.DiGraph()
    for n in data["nodes"]:
        G.add_node(n["id"], **n)
    for e in data["edges"]:
        G.add_edge(e[0], e[1], relation=e[2])
    return G

def render_pyvis(data, filter_types=None, highlight_id=None, physics=True):
    net = Network(height="580px", width="100%", bgcolor="#0d1117",
                  font_color="#e6edf3", directed=True)
    net.set_options(json.dumps({
        "physics": {"enabled": physics, "barnesHut": {"gravitationalConstant": -12000, "springLength": 150}},
        "edges": {"arrows": {"to": {"enabled": True, "scaleFactor": 0.6}},
                  "smooth": {"type": "curvedCW", "roundness": 0.2}},
        "interaction": {"hover": True, "tooltipDelay": 100},
    }))
    for n in data["nodes"]:
        if filter_types and n["type"] not in filter_types:
            continue
        cfg   = TYPE_CONFIG.get(n["type"], {"color":"#58a6ff","shape":"dot","size":15})
        border= "#ffffff" if n["id"] == highlight_id else cfg["color"]
        bw    = 3 if n["id"] == highlight_id else 1
        tip   = f"<b>{n['label']}</b><br>Type: {n['type']}<br>Year: {n.get('year','–')}"
        if n.get("citations"):
            tip += f"<br>Citations: {n['citations']:,}"
        net.add_node(n["id"], label=n["label"], color={"background": cfg["color"],
                     "border": border, "highlight": {"background": "#f0883e", "border": "#ffffff"}},
                     shape=cfg["shape"], size=cfg["size"],
                     borderWidth=bw, title=tip, font={"size": 11, "color": "#e6edf3"})
    visible_ids = {n["id"] for n in data["nodes"] if not filter_types or n["type"] in filter_types}
    for e in data["edges"]:
        if e[0] in visible_ids and e[1] in visible_ids:
            col = EDGE_COLORS.get(e[2], "#484f58")
            net.add_edge(e[0], e[1], label=e[2], color=col,
                         font={"size": 8, "color": "#8b949e", "align": "middle"}, width=1.4)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
    net.save_graph(tmp.name)
    return open(tmp.name, "r", encoding="utf-8").read()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔬 KG Agent")
    st.markdown("<div class='section-header'>Filter by Node Type</div>", unsafe_allow_html=True)

    all_types = list(TYPE_CONFIG.keys())
    selected_types = []
    for t in all_types:
        cfg = TYPE_CONFIG[t]
        if st.checkbox(f"{cfg['emoji']} {t.capitalize()}", value=True, key=f"chk_{t}"):
            selected_types.append(t)

    st.markdown("<div class='section-header'>Physics Simulation</div>", unsafe_allow_html=True)
    physics_on = st.toggle("Enable Physics", value=True)

    st.markdown("<div class='section-header'>Search Node</div>", unsafe_allow_html=True)
    search_q = st.text_input("Node name / keyword", placeholder="e.g. BERT, Hinton…")

    st.markdown("---")
    st.markdown("<div class='section-header'>Add New Node</div>", unsafe_allow_html=True)
    with st.form("add_node_form"):
        new_id    = st.text_input("Node ID (unique)",  placeholder="my_paper")
        new_label = st.text_input("Display Label",     placeholder="My New Paper")
        new_type  = st.selectbox("Type", all_types)
        new_year  = st.number_input("Year", 1900, 2030, 2024)
        new_cite  = st.number_input("Citations", 0, 10_000_000, 0, step=100)
        submitted = st.form_submit_button("➕ Add Node")
        if submitted and new_id and new_label:
            ids = {n["id"] for n in st.session_state.graph_data["nodes"]}
            if new_id in ids:
                st.error("ID already exists.")
            else:
                st.session_state.graph_data["nodes"].append({
                    "id": new_id, "type": new_type, "label": new_label,
                    "year": int(new_year), "citations": int(new_cite)
                })
                st.success(f"Added '{new_label}'")
                st.rerun()

    st.markdown("<div class='section-header'>Add Relationship</div>", unsafe_allow_html=True)
    with st.form("add_edge_form"):
        all_ids = [n["id"] for n in st.session_state.graph_data["nodes"]]
        src = st.selectbox("Source", all_ids, key="src")
        tgt = st.selectbox("Target", all_ids, key="tgt")
        rel = st.text_input("Relation", placeholder="cites, uses, …")
        e_sub = st.form_submit_button("🔗 Add Edge")
        if e_sub and rel:
            st.session_state.graph_data["edges"].append((src, tgt, rel))
            st.success(f"Edge added: {src} → {tgt}")
            st.rerun()

    st.markdown("---")
    if st.button("🔄 Reset to Default"):
        st.session_state.graph_data = DEFAULT_DATA.copy()
        st.rerun()

# ── Main area ──────────────────────────────────────────────────────────────────
st.markdown("# 🔬 Knowledge Graph Agent")
st.markdown("<p style='color:#8b949e;margin-top:-0.5rem'>Research Ecosystem Visualization · Internship Project</p>", unsafe_allow_html=True)

# Tabs
tab_graph, tab_explore, tab_data = st.tabs(["🕸️ Graph View", "🔎 Explore Nodes", "📊 Analytics"])

# ── TAB 1: Graph ───────────────────────────────────────────────────────────────
with tab_graph:
    data  = st.session_state.graph_data
    G     = build_nx(data)

    # Search highlight
    highlight = None
    if search_q:
        matches = [n["id"] for n in data["nodes"]
                   if search_q.lower() in n["label"].lower() or search_q.lower() in n["id"].lower()]
        if matches:
            highlight = matches[0]
            st.info(f"🔍 Highlighting: **{matches[0]}** ({len(matches)} match(es))")

    # Metrics row
    n_nodes = len([n for n in data["nodes"] if n["type"] in selected_types])
    n_edges = len(data["edges"])
    density = nx.density(G)
    components = nx.number_weakly_connected_components(G)

    st.markdown(f"""
    <div class="metric-row">
      <div class="metric-tile"><div class="val">{n_nodes}</div><div class="lbl">Nodes Visible</div></div>
      <div class="metric-tile"><div class="val">{n_edges}</div><div class="lbl">Relationships</div></div>
      <div class="metric-tile"><div class="val">{density:.3f}</div><div class="lbl">Graph Density</div></div>
      <div class="metric-tile"><div class="val">{components}</div><div class="lbl">Components</div></div>
      <div class="metric-tile"><div class="val">{len(data['nodes'])}</div><div class="lbl">Total Nodes</div></div>
    </div>
    """, unsafe_allow_html=True)

    # Legend
    legend_html = "<div style='display:flex;gap:14px;flex-wrap:wrap;margin-bottom:0.75rem;'>"
    for t, cfg in TYPE_CONFIG.items():
        legend_html += f"<span style='font-size:0.78rem;color:{cfg['color']}'>{cfg['emoji']} {t.capitalize()}</span>"
    legend_html += "</div>"
    st.markdown(legend_html, unsafe_allow_html=True)

    # Graph render
    html = render_pyvis(data, filter_types=selected_types if selected_types else None,
                        highlight_id=highlight, physics=physics_on)
    st.components.v1.html(html, height=600, scrolling=False)

    st.markdown("<p style='text-align:center;color:#484f58;font-size:0.75rem;margin-top:0.5rem'>Drag nodes · Scroll to zoom · Hover for details</p>", unsafe_allow_html=True)

# ── TAB 2: Explore ─────────────────────────────────────────────────────────────
with tab_explore:
    data = st.session_state.graph_data
    G    = build_nx(data)

    col_left, col_right = st.columns([1, 2])

    with col_left:
        st.markdown("### Select a Node")
        node_options = {f"{TYPE_CONFIG[n['type']]['emoji']} {n['label']} ({n['id']})": n["id"]
                        for n in data["nodes"]}
        chosen_label = st.selectbox("Node", list(node_options.keys()), label_visibility="collapsed")
        chosen_id    = node_options[chosen_label]
        node_info    = next(n for n in data["nodes"] if n["id"] == chosen_id)
        cfg          = TYPE_CONFIG[node_info["type"]]

        st.markdown(f"""
        <div class="kg-card">
          <h4>{cfg['emoji']} {node_info['label']}</h4>
          <p>Type: <b style='color:{cfg['color']}'>{node_info['type'].capitalize()}</b></p>
          <p>Year: {node_info.get('year','–')}</p>
          {"<p>Citations: <b style='color:#58a6ff'>" + f"{node_info['citations']:,}" + "</b></p>" if node_info.get('citations') else ""}
        </div>
        """, unsafe_allow_html=True)

        # PageRank
        try:
            pr = nx.pagerank(G, alpha=0.85)
            rank_val = pr.get(chosen_id, 0)
            st.markdown(f"<div class='kg-card'><h4>📈 PageRank Score</h4><p style='font-size:1.3rem;color:#58a6ff;font-weight:700'>{rank_val:.5f}</p></div>", unsafe_allow_html=True)
        except Exception:
            pass

    with col_right:
        st.markdown("### Connections")
        out_edges = [(e[1], e[2]) for e in data["edges"] if e[0] == chosen_id]
        in_edges  = [(e[0], e[2]) for e in data["edges"] if e[1] == chosen_id]

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**⬆️ Outgoing ({len(out_edges)})**")
            for nid, rel in out_edges:
                lbl = next((n["label"] for n in data["nodes"] if n["id"] == nid), nid)
                col = EDGE_COLORS.get(rel, "#484f58")
                st.markdown(f"<div class='kg-card'><h4>→ {lbl}</h4><p><span style='color:{col}'>{rel}</span></p></div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"**⬇️ Incoming ({len(in_edges)})**")
            for nid, rel in in_edges:
                lbl = next((n["label"] for n in data["nodes"] if n["id"] == nid), nid)
                col = EDGE_COLORS.get(rel, "#484f58")
                st.markdown(f"<div class='kg-card'><h4>← {lbl}</h4><p><span style='color:{col}'>{rel}</span></p></div>", unsafe_allow_html=True)

        # Mini subgraph
        st.markdown("### Local Subgraph")
        neighbors = set([chosen_id] + [e[1] for e in out_edges] + [e[0] for e in in_edges])
        sub_data  = {
            "nodes": [n for n in data["nodes"] if n["id"] in neighbors],
            "edges": [e for e in data["edges"] if e[0] in neighbors and e[1] in neighbors],
        }
        sub_html = render_pyvis(sub_data, highlight_id=chosen_id, physics=True)
        st.components.v1.html(sub_html, height=340)

# ── TAB 3: Analytics ───────────────────────────────────────────────────────────
with tab_data:
    data = st.session_state.graph_data
    G    = build_nx(data)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Node Distribution")
        type_counts = {}
        for n in data["nodes"]:
            type_counts[n["type"]] = type_counts.get(n["type"], 0) + 1
        df_types = pd.DataFrame(list(type_counts.items()), columns=["Type","Count"])
        st.bar_chart(df_types.set_index("Type"), color="#388bfd")

    with col2:
        st.markdown("### Top Nodes by In-Degree")
        in_deg  = dict(G.in_degree())
        top10   = sorted(in_deg.items(), key=lambda x: x[1], reverse=True)[:10]
        labels  = [next((n["label"] for n in data["nodes"] if n["id"] == nid), nid) for nid, _ in top10]
        df_deg  = pd.DataFrame({"Node": labels, "In-Degree": [d for _, d in top10]})
        st.bar_chart(df_deg.set_index("Node"), color="#3fb950")

    st.markdown("### Citation Leaders")
    df_cite = pd.DataFrame([
        {"Label": n["label"], "Type": n["type"], "Year": n.get("year",""), "Citations": n.get("citations",0)}
        for n in data["nodes"] if n.get("citations",0) > 0
    ]).sort_values("Citations", ascending=False)
    st.dataframe(df_cite, use_container_width=True, hide_index=True)

    st.markdown("### Relationship Types")
    rel_counts = {}
    for e in data["edges"]:
        rel_counts[e[2]] = rel_counts.get(e[2], 0) + 1
    df_rel = pd.DataFrame(list(rel_counts.items()), columns=["Relation","Count"]).sort_values("Count", ascending=False)
    st.dataframe(df_rel, use_container_width=True, hide_index=True)

    st.markdown("### Graph Properties")
    pr = nx.pagerank(G, alpha=0.85)
    top_pr = sorted(pr.items(), key=lambda x: x[1], reverse=True)[:5]
    st.markdown("**Top 5 by PageRank:**")
    for nid, score in top_pr:
        lbl = next((n["label"] for n in data["nodes"] if n["id"] == nid), nid)
        st.markdown(f"- **{lbl}** — `{score:.5f}`")