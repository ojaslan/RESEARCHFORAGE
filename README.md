# 🔬 Knowledge Graph Agent



---

## 📌 Overview

The **Knowledge Graph Agent** is an interactive tool that maps and visualizes the AI/ML research ecosystem as a dynamic knowledge graph. It lets you explore relationships between:

| Node Type | Description |
|-----------|-------------|
| 🌐 Domain | High-level research areas (AI, ML, NLP, CV, RL) |
| 📄 Paper | Landmark research papers (BERT, GPT-3, ResNet …) |
| 👤 Researcher | Key scientists (Hinton, LeCun, Bengio …) |
| 🏛️ Institution | Labs and orgs (Google DeepMind, OpenAI, Meta AI …) |
| ⚙️ Technique | Core methods (Transformer, CNN, LLMs, Diffusion …) |

---

## ✨ Features

- **Interactive Force-Directed Graph** — physics-based layout via PyVis
- **Filter by Node Type** — show/hide domains, papers, researchers, etc.
- **Search & Highlight** — find any node instantly
- **Node Explorer** — click any node to see its connections and local subgraph
- **Analytics Dashboard** — citation leaders, PageRank, in-degree charts, relationship stats
- **Add Nodes & Edges** — extend the graph live from the sidebar
- **Reset to Default** — restore the preloaded research ecosystem

---

## 🚀 How to Run

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Launch the app

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## 📁 Project Structure

```
knowledge_graph_agent/
├── app.py            # Main Streamlit application
├── requirements.txt  # Python dependencies
└── README.md         # This file
```

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| [Streamlit](https://streamlit.io) | Web app framework |
| [NetworkX](https://networkx.org) | Graph data structure & algorithms |
| [PyVis](https://pyvis.readthedocs.io) | Interactive graph rendering |
| [Pandas](https://pandas.pydata.org) | Data manipulation & tables |

---

## 📊 Graph Algorithms Used

- **PageRank** — identifies the most influential nodes
- **In-Degree Centrality** — measures how many nodes point to a given node
- **Weakly Connected Components** — counts disconnected subgraphs
- **Graph Density** — ratio of actual edges to possible edges

