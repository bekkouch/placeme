"""
app.py — PlaceMe : Scraper de leads distributeurs automatiques
- Run complet sans limite
- Résultats affichés par batches de 10
- Export CSV des deux listes
- UI accessible (Lighthouse AA)
"""
import re
import time
import requests
import pandas as pd
import osmnx as ox
import streamlit as st
from bs4 import BeautifulSoup

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="PlaceMe",
    page_icon="📍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# CSS — Palette propre, contraste WCAG AA
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    background: #0c0c12 !important;
    color: #e8e6e0 !important;
    font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stHeader"]  { background: transparent !important; }
[data-testid="stSidebar"] { display: none !important; }
section[data-testid="stMain"] > div { padding-top: 0 !important; }

/* ── Navbar ── */
.navbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.1rem 0 1rem 0;
    border-bottom: 1px solid #1e1e2a;
    margin-bottom: 2.5rem;
}
.navbar-brand {
    font-family: 'Space Mono', monospace;
    font-size: 1.55rem;
    font-weight: 700;
    color: #f0ede6;
    letter-spacing: -1px;
}
.navbar-brand span { color: #c8f55a; }
.navbar-tagline {
    font-size: 0.8rem;
    color: #555;
    font-family: 'Space Mono', monospace;
}

/* ── Search label ── */
.search-label {
    font-size: 0.75rem;
    font-weight: 700;
    color: #555;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 0.4rem;
    font-family: 'Space Mono', monospace;
}

/* ── Input ── */
.stTextInput > div > div > input {
    background: #111118 !important;
    border: 1px solid #2a2a38 !important;
    border-right: none !important;
    border-radius: 4px 0 0 4px !important;
    color: #f0ede6 !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.95rem !important;
    padding: 0.8rem 1rem !important;
    height: 44px !important;
    transition: border-color 0.15s !important;
}
.stTextInput > div > div > input:focus {
    border-color: #c8f55a !important;
    box-shadow: 0 0 0 2px rgba(200,245,90,0.1) !important;
    outline: none !important;
}
.stTextInput label { display: none !important; }

/* ── Launch button ── */
.stButton > button {
    background: #c8f55a !important;
    color: #0c0c12 !important;
    border: none !important;
    border-radius: 0 4px 4px 0 !important;
    font-family: 'Space Mono', monospace !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    height: 44px !important;
    padding: 0 1.4rem !important;
    margin-top: 0 !important;
    cursor: pointer !important;
    transition: opacity 0.15s !important;
    white-space: nowrap !important;
    width: 100% !important;
    letter-spacing: 0.04em !important;
}
.stButton > button:hover { opacity: 0.85 !important; }

/* ── Metric cards ── */
.metrics-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin: 2rem 0;
}
.metric-card {
    background: #111118;
    border: 1px solid #1e1e2a;
    border-radius: 6px;
    padding: 1.2rem 1.5rem;
}
.metric-card .m-label {
    font-size: 0.7rem;
    font-weight: 700;
    color: #555;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-family: 'Space Mono', monospace;
    margin-bottom: 0.3rem;
}
.metric-card .m-value {
    font-family: 'Space Mono', monospace;
    font-size: 2rem;
    font-weight: 700;
    line-height: 1.2;
    color: #c8f55a;
}
.metric-card .m-value.amber { color: #f5a623; }
.metric-card .m-value.white { color: #f0ede6; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid #1e1e2a !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #555 !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.78rem !important;
    border-radius: 0 !important;
    border-bottom: 2px solid transparent !important;
    margin-bottom: -1px !important;
    padding: 0.6rem 1.2rem !important;
}
.stTabs [aria-selected="true"] {
    color: #c8f55a !important;
    border-bottom: 2px solid #c8f55a !important;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border: 1px solid #1e1e2a !important;
    border-radius: 6px !important;
    overflow: hidden !important;
}

/* ── Progress ── */
.stProgress > div > div { background: #c8f55a !important; }
.stProgress > div       { background: #1e1e2a !important; }

/* ── Spinner (orange pour différencier du vert) ── */
.stSpinner > div { border-top-color: #f5a623 !important; }
[data-testid="stSpinner"] p { color: #f5a623 !important; }

/* ── Download buttons ── */
[data-testid="stDownloadButton"] > button {
    background: transparent !important;
    color: #c8f55a !important;
    border: 1px solid #c8f55a !important;
    border-radius: 4px !important;
    font-family: 'Space Mono', monospace !important;
    font-weight: 700 !important;
    font-size: 0.78rem !important;
    padding: 0.45rem 1rem !important;
    transition: opacity 0.15s !important;
    letter-spacing: 0.04em !important;
}
[data-testid="stDownloadButton"] > button:hover { opacity: 0.75 !important; }

/* ── Section heading ── */
.section-heading {
    font-size: 0.7rem;
    font-weight: 700;
    color: #444;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    font-family: 'Space Mono', monospace;
    margin: 0 0 1rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #1e1e2a;
}

div[data-testid="stMarkdownContainer"] p { color: #aaa !important; }
#MainMenu, footer { visibility: hidden !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────
TARGET_TAGS = {
    "amenity": ["hospital", "clinic", "university", "college", "school", "coworking_space"],
    "office":  True,
    "building": ["commercial", "industrial", "office"],
    "leisure": ["sports_centre", "fitness_centre"],
    "shop":    ["mall", "department_store"],
}
INVALID_PATTERNS = [
    "no email", "no valid", "not provided",
    "scrape failed", "no email found", "no email or website",
]
BATCH_SIZE = 10

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def is_valid_email(value) -> bool:
    if pd.isna(value) or not value:
        return False
    v = str(value).lower().strip()
    if any(p in v for p in INVALID_PATTERNS):
        return False
    return bool(re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', v))

def is_valid_phone(value) -> bool:
    if pd.isna(value) or not value:
        return False
    v = str(value).strip()
    return v not in ["", "Not provided", "Non renseigné"] and len(re.sub(r'\D', '', v)) >= 8

def scrape_email_from_website(url) -> str | None:
    if pd.isna(url) or not str(url).startswith("http"):
        return None
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        r = requests.get(str(url), headers=headers, timeout=6)
        if r.status_code == 200:
            text = BeautifulSoup(r.content, "html.parser").get_text()
            emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
            clean = [
                e.lower() for e in emails
                if not re.search(r'\.(png|jpg|jpeg|svg|gif|webp|woff|css|js)$', e)
            ]
            return ", ".join(list(set(clean))) if clean else None
    except Exception:
        pass
    return None

def to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")

# ─────────────────────────────────────────────
# OSM FETCH (cached per city)
# ─────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def fetch_osm(city: str) -> pd.DataFrame:
    pois = ox.features_from_place(city, tags=TARGET_TAGS)
    contact_cols = ["name", "amenity", "office", "phone", "contact:phone",
                    "email", "contact:email", "website"]
    available = [c for c in contact_cols if c in pois.columns]
    df = pois[available].copy()
    df = df.dropna(subset=["name"])

    if "phone" in df.columns and "contact:phone" in df.columns:
        df["final_phone"] = df["phone"].combine_first(df["contact:phone"])
    elif "phone" in df.columns:
        df["final_phone"] = df["phone"]
    else:
        df["final_phone"] = pd.NA

    if "email" in df.columns and "contact:email" in df.columns:
        df["osm_email"] = df["email"].combine_first(df["contact:email"])
    elif "email" in df.columns:
        df["osm_email"] = df["email"]
    else:
        df["osm_email"] = pd.NA

    df["final_email"] = pd.NA
    # Normaliser le nom pour la dédup (lowercase, strip accents simples)
    df["_name_key"] = df["name"].astype(str).str.lower().str.strip()
    df = df.drop_duplicates(subset=["_name_key"]).drop(columns=["_name_key"]).reset_index(drop=True)
    return df

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
for key in ("rows_complets", "rows_incomplets", "total", "city_slug", "done"):
    if key not in st.session_state:
        st.session_state[key] = None

# ─────────────────────────────────────────────
# NAVBAR
# ─────────────────────────────────────────────
st.markdown("""
<nav class="navbar" role="banner">
    <div>
        <div class="navbar-brand">Place<span>Me</span></div>
        <div class="navbar-tagline">Prospection distributeurs automatiques · OpenStreetMap</div>
    </div>
</nav>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SEARCH ROW — form pour supporter Enter
# ─────────────────────────────────────────────
st.markdown('<p class="search-label">Ville cible</p>', unsafe_allow_html=True)

with st.form("search_form", border=False):
    col_input, col_btn = st.columns([5, 1])
    with col_input:
        city = st.text_input(
            label="Ville",
            placeholder="Ex: Grenoble, France  —  Bruxelles, Belgique  —  Lausanne, Suisse",
            label_visibility="collapsed",
            key="city_input",
        )
    with col_btn:
        launch = st.form_submit_button("🔍 Lancer", use_container_width=True)

# ─────────────────────────────────────────────
# PIPELINE
# ─────────────────────────────────────────────
COL_C = ["Nom", "Type", "Téléphone", "Email", "Site web"]
COL_I = ["Nom", "Type", "Téléphone", "Email", "Site web", "Manque"]

def render_results():
    """Affiche les résultats stockés en session_state."""
    rc   = st.session_state.rows_complets
    ri   = st.session_state.rows_incomplets
    tot  = st.session_state.total
    n_c  = len(rc)
    n_i  = len(ri)
    taux = round(n_c / tot * 100) if tot else 0

    st.markdown(f"""
    <div class="metrics-row" role="region" aria-label="Résumé">
        <div class="metric-card">
            <div class="m-label">Total scrapés</div>
            <div class="m-value">{tot}</div>
        </div>
        <div class="metric-card">
            <div class="m-label">Leads complets</div>
            <div class="m-value">{n_c}</div>
        </div>
        <div class="metric-card">
            <div class="m-label">Leads incomplets</div>
            <div class="m-value amber">{n_i}</div>
        </div>
        <div class="metric-card">
            <div class="m-label">Taux de complétion</div>
            <div class="m-value white">{taux}%</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs([f"✅ Leads complets ({n_c})", f"⚠️ Leads incomplets ({n_i})"])
    with tab1:
        if rc:
            st.dataframe(pd.DataFrame(rc, columns=COL_C), use_container_width=True, hide_index=True,
                column_config={"Site web": st.column_config.LinkColumn("Site web")})
        else:
            st.caption("Aucun lead complet trouvé.")
    with tab2:
        if ri:
            st.dataframe(pd.DataFrame(ri, columns=COL_I), use_container_width=True, hide_index=True,
                column_config={"Site web": st.column_config.LinkColumn("Site web"),
                               "Manque":   st.column_config.TextColumn("Données manquantes")})
        else:
            st.caption("Aucun lead incomplet.")

    slug = st.session_state.city_slug
    col_dl1, col_dl2, _ = st.columns([1, 1, 3])
    with col_dl1:
        st.download_button(
            label="⬇️ Exporter leads complets",
            data=to_csv_bytes(pd.DataFrame(rc, columns=COL_C)),
            file_name=f"{slug}_leads_complets.csv",
            mime="text/csv",
            disabled=not rc,
            key="dl_complets",
        )
    with col_dl2:
        st.download_button(
            label="⬇️ Exporter leads incomplets",
            data=to_csv_bytes(pd.DataFrame(ri, columns=COL_I)),
            file_name=f"{slug}_leads_incomplets.csv",
            mime="text/csv",
            disabled=not ri,
            key="dl_incomplets",
        )

# ── Si résultats déjà en mémoire, les afficher directement ──
if st.session_state.done:
    render_results()

# ── Lancement d'un nouveau scraping ──
elif launch and city.strip():
    city = city.strip()

    with st.spinner(f"📡 Téléchargement OpenStreetMap pour **{city}**..."):
        try:
            df = fetch_osm(city)
        except Exception as e:
            st.error(f"**Ville introuvable ou erreur OSM** — {e}")
            st.stop()

    total = len(df)
    st.info(f"**{total} lieux trouvés.** Scraping des emails en cours...", icon="📍")

    progress_bar = st.progress(0, text="Initialisation...")

    st.markdown('<div class="section-heading">Résultats en temps réel</div>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["✅ Leads complets", "⚠️ Leads incomplets"])
    with tab1:
        container_complets = st.empty()
    with tab2:
        container_incomplets = st.empty()

    rows_complets   = []
    rows_incomplets = []
    seen_names      = set()  # évite les doublons résiduels

    def refresh_tables():
        with container_complets:
            if not rows_complets:
                st.caption("Aucun lead complet pour l'instant...")
            else:
                st.dataframe(pd.DataFrame(rows_complets, columns=COL_C),
                    use_container_width=True, hide_index=True,
                    column_config={"Site web": st.column_config.LinkColumn("Site web")})
        with container_incomplets:
            if not rows_incomplets:
                st.caption("Aucun lead incomplet pour l'instant...")
            else:
                st.dataframe(pd.DataFrame(rows_incomplets, columns=COL_I),
                    use_container_width=True, hide_index=True,
                    column_config={"Site web": st.column_config.LinkColumn("Site web"),
                                   "Manque":   st.column_config.TextColumn("Données manquantes")})

    for i, (idx, row) in enumerate(df.iterrows()):
        name       = str(row.get("name", "—"))
        osm_email  = row.get("osm_email")
        website    = row.get("website")
        amenity    = str(row.get("amenity", "")) if pd.notna(row.get("amenity")) else ""
        office     = str(row.get("office",  "")) if pd.notna(row.get("office"))  else ""
        phone      = str(row.get("final_phone", "")) if pd.notna(row.get("final_phone")) else ""
        site       = str(website) if pd.notna(website) else "—"
        type_label = amenity if amenity else office if office else "—"

        final_email = None
        if is_valid_email(osm_email):
            final_email = str(osm_email)
        elif pd.notna(website):
            final_email = scrape_email_from_website(website)
            time.sleep(0.4)

        phone_ok = is_valid_phone(phone)
        email_ok = is_valid_email(final_email)

        # Dédup résiduelle par nom normalisé
        name_key = name.lower().strip()
        if name_key in seen_names:
            pct = (i + 1) / total
            progress_bar.progress(pct, text=f"Traitement {i+1}/{total} — {name[:45]}")
            continue
        seen_names.add(name_key)

        display  = [name, type_label, phone if phone else "—",
                    final_email if final_email else "—", site]

        if email_ok and phone_ok:
            rows_complets.append(display)
        else:
            missing = []
            if not email_ok:  missing.append("email")
            if not phone_ok:  missing.append("téléphone")
            rows_incomplets.append(display + [", ".join(missing)])

        pct = (i + 1) / total
        progress_bar.progress(pct, text=f"Traitement {i+1}/{total} — {name[:45]}")

        if (i + 1) % BATCH_SIZE == 0 or (i + 1) == total:
            refresh_tables()

    progress_bar.progress(1.0, text="✅ Scraping terminé !")

    # Persister en session_state
    city_slug = re.sub(r'[^a-z0-9]', '_', city.lower().split(",")[0].strip())
    st.session_state.rows_complets   = rows_complets
    st.session_state.rows_incomplets = rows_incomplets
    st.session_state.total           = total
    st.session_state.city_slug       = city_slug
    st.session_state.done            = True
    st.rerun()

elif launch and not city.strip():
    st.warning("Entre un nom de ville pour commencer.", icon="⚠️")
