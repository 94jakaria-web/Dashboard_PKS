import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from PIL import Image

st.set_page_config(
    page_title="Dashboard Serapan Anggaran PKS Batulaki",
    layout="wide"
)

# ==========================================================
# HEADER & LOGO
# ==========================================================
try:
    logo_bkb = Image.open("logo_bkb.jpg")
except Exception:
    logo_bkb = None

col_logo, col_judul, col_tanggal = st.columns([2, 6, 2])

with col_logo:
    if logo_bkb:
        st.image(logo_bkb, width=100)
    else:
        st.info("Logo tidak ditemukan")

with col_judul:
    st.markdown("""
    <div style="display:flex; align-items:right; height:100%; padding-top:10px;">
        <h2 style="margin:0; font-size:50px; white-space:nowrap;">
            📊 SERAPAN ANGGARAN PKS BATULAKI TAHUN 2026
        </h2>
    </div>
    """, unsafe_allow_html=True)

with col_tanggal:
    sekarang = datetime.now()
    st.markdown(f"""
    <div style="text-align:right; padding-top:35px; font-size:14px;">
        <b>{sekarang.strftime("%d %B %Y")}</b><br>
        {sekarang.strftime("%H:%M:%S")}
    </div>
    """, unsafe_allow_html=True)


# ==========================================================
# LOAD DATA & CACHING
# ==========================================================
@st.cache_data
def load_data(nama_file):
    df = pd.read_excel(nama_file, sheet_name="Sheet1")
    df.columns = df.columns.str.strip()
    df["BUDGET"] = pd.to_numeric(df["BUDGET"], errors="coerce").fillna(0)
    df["AKTUAL"] = pd.to_numeric(df["AKTUAL"], errors="coerce").fillna(0)
    return df

df_langsung = load_data("Biaya Langsung PKS.xlsx")
df_tidak_langsung = load_data("Biaya Tidak Langsung PKS.xlsx")
df_produksi = load_data("Produksi.xlsx")
df_tbs = load_data("Produksi TBS.xlsx")


# ==========================================================
# FILTER SIDEBAR
# ==========================================================
st.sidebar.header("🔎 Filter Dashboard")

# Filter PT
daftar_pt = sorted(df_langsung["PT"].dropna().unique())
pt = st.sidebar.selectbox("Pilih PT", ["Semua"] + daftar_pt)

if pt != "Semua":
    df_langsung = df_langsung[df_langsung["PT"] == pt]
    df_tidak_langsung = df_tidak_langsung[df_tidak_langsung["PT"] == pt]
    df_produksi = df_produksi[df_produksi["PT"] == pt]
    df_tbs = df_tbs[df_tbs["PT"] == pt]

# Filter Bulan Manual
daftar_bulan = sorted(df_langsung["BULAN"].dropna().unique())
bulan_terpilih = st.sidebar.multiselect("Pilih Bulan", daftar_bulan)

if bulan_terpilih:
    df_langsung = df_langsung[df_langsung["BULAN"].isin(bulan_terpilih)]
    df_tidak_langsung = df_tidak_langsung[df_tidak_langsung["BULAN"].isin(bulan_terpilih)]
    df_produksi = df_produksi[df_produksi["BULAN"].isin(bulan_terpilih)]
    df_tbs = df_tbs[df_tbs["BULAN"].isin(bulan_terpilih)]

# Filter Periode Cawu
periode = st.sidebar.selectbox(
    "Pilih Periode",
    ["Semua", "Cawu 1 (Jan-Apr)", "Cawu 2 (Mei-Agu)", "Cawu 3 (Sep-Des)"]
)

if periode == "Cawu 1 (Jan-Apr)":
    bulan_filter = [1, 2, 3, 4]
elif periode == "Cawu 2 (Mei-Agu)":
    bulan_filter = [5, 6, 7, 8]
elif periode == "Cawu 3 (Sep-Des)":
    bulan_filter = [9, 10, 11, 12]
else:
    bulan_filter = []

if bulan_filter:
    df_langsung = df_langsung[df_langsung["BULAN"].isin(bulan_filter)]
    df_tidak_langsung = df_tidak_langsung[df_tidak_langsung["BULAN"].isin(bulan_filter)]
    df_produksi = df_produksi[df_produksi["BULAN"].isin(bulan_filter)]
    df_tbs = df_tbs[df_tbs["BULAN"].isin(bulan_filter)]


# ==========================================================
# PREPROSESING DATA TERFILTRASI
# ==========================================================
df_cpo = df_produksi[df_produksi["PRODUK"].astype(str).str.strip().str.upper() == "CPO"].copy()
df_cpo["CAPAIAN_BUDGET"] = (df_cpo["AKTUAL"] / df_cpo["BUDGET"] * 100).replace([float("inf"), -float("inf")], 0).fillna(0)

df_produksi_rpkg = df_produksi[df_produksi["PRODUK"].astype(str).str.strip().str.upper().isin(["CPO", "KERNEL"])].copy()

df_tbs["CAPAIAN_BUDGET"] = (df_tbs["AKTUAL"] / df_tbs["BUDGET"] * 100).replace([float("inf"), -float("inf")], 0).fillna(0)
df_tbs["CAPAIAN_SENSUS"] = (df_tbs["AKTUAL"] / df_tbs["SENSUS"] * 100).replace([float("inf"), -float("inf")], 0).fillna(0)


# Hitung Total
budget_langsung = df_langsung["BUDGET"].sum()
aktual_langsung = df_langsung["AKTUAL"].sum()

budget_tidak = df_tidak_langsung["BUDGET"].sum()
aktual_tidak = df_tidak_langsung["AKTUAL"].sum()

budget_produksi = df_cpo["BUDGET"].sum()
aktual_produksi = df_cpo["AKTUAL"].sum()

budget_produksi_rpkg = df_produksi_rpkg["BUDGET"].sum()
aktual_produksi_rpkg = df_produksi_rpkg["AKTUAL"].sum()

budget_tbs = df_tbs["BUDGET"].sum()
aktual_tbs = df_tbs["AKTUAL"].sum()

# Persentase
persen_produksi = (aktual_produksi / budget_produksi * 100) if budget_produksi > 0 else 0
persen_tbs = (aktual_tbs / budget_tbs * 100) if budget_tbs > 0 else 0

rpkg_langsung_budget = (budget_langsung / budget_produksi_rpkg) if budget_produksi_rpkg > 0 else 0
rpkg_langsung_aktual = (aktual_langsung / aktual_produksi_rpkg) if aktual_produksi_rpkg > 0 else 0

rpkg_tidak_budget = (budget_tidak / budget_produksi_rpkg) if budget_produksi_rpkg > 0 else 0
rpkg_tidak_aktual = (aktual_tidak / aktual_produksi_rpkg) if aktual_produksi_rpkg > 0 else 0

persen_rpkg_langsung = (rpkg_langsung_aktual / rpkg_langsung_budget * 100) if rpkg_langsung_budget > 0 else 0
persen_rpkg_tidak = (rpkg_tidak_aktual / rpkg_tidak_budget * 100) if rpkg_tidak_budget > 0 else 0


# Helper Format Unit
def Kg(x):
    if abs(x) >= 1_000_000_000:
        return f"{x/1_000_000_000:,.2f} Miliar Kg"
    elif abs(x) >= 1_000_000:
        return f"{x/1_000_000:,.2f} Juta Kg"
    elif abs(x) >= 1_000:
        return f"{x/1_000:,.2f} Ribu Kg"
    else:
        return f"{x:,.0f} Kg"

def format_rpkg(x):
    return f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " Rp/Kg"


# ==========================================================
# CSS CUSTOM
# ==========================================================
st.markdown("""
<style>
.rpkg-card {
    background: white;
    border-radius: 10px;
    padding: 20px;
    border-top: 5px solid #12B886;
    box-shadow: 0px 3px 10px rgba(0,0,0,0.1);
    min-height: 250px;
    box-sizing: border-box;
}
.rpkg-header { display: flex; align-items: center; gap: 15px; margin-bottom: 15px; }
.rpkg-icon {
    width: 60px; height: 60px; border-radius: 50%;
    background: #12B886; color: white; display: flex;
    align-items: center; justify-content: center; font-size: 30px; flex-shrink: 0;
}
.rpkg-title { font-size: 20px; color: #60728F; font-weight: 600; line-height: 1.2; }
.rpkg-value { font-size: 32px; font-weight: bold; color: #172033; margin-top: 10px; }
.rpkg-budget { font-size: 16px; color: #60728F; margin-top: 15px; }
.rpkg-status { margin-top: 15px; padding: 12px; text-align: center; font-size: 18px; font-weight: bold; border-radius: 6px; }
.status-under { background: #D1F2E5; color: #00A95C; }
.status-over { background: #FFD1D1; color: #FF0000; }
</style>
""", unsafe_allow_html=True)


# ==========================================================
# METRIC CARDS KARTU UTAMA
# ==========================================================
col1, col2, col3, col4 = st.columns(4)

with col1:
    status_produksi = "Under Budget" if persen_produksi <= 100 else "Over Budget"
    class_produksi = "status-under" if persen_produksi <= 100 else "status-over"
    st.html(f"""
    <div class="rpkg-card">
        <div class="rpkg-header">
            <div class="rpkg-icon">🛢️</div>
            <div class="rpkg-title">Produksi CPO</div>
        </div>
        <div class="rpkg-value">{Kg(aktual_produksi)}</div>
        <div class="rpkg-budget">Budget: {Kg(budget_produksi)}</div>
        <div class="rpkg-status {class_produksi}">{persen_produksi:.1f}% — {status_produksi}</div>
    </div>
    """)

with col2:
    status_tbs = "Under Budget" if persen_tbs <= 100 else "Over Budget"
    class_tbs = "status-under" if persen_tbs <= 100 else "status-over"
    st.html(f"""
    <div class="rpkg-card">
        <div class="rpkg-header">
            <div class="rpkg-icon">🌴</div>
            <div class="rpkg-title">Penerimaan TBS</div>
        </div>
        <div class="rpkg-value">{Kg(aktual_tbs)}</div>
        <div class="rpkg-budget">Budget: {Kg(budget_tbs)}</div>
        <div class="rpkg-status {class_tbs}">{persen_tbs:.1f}% — {status_tbs}</div>
    </div>
    """)

with col3:
    status_langsung = "Under Budget" if persen_rpkg_langsung <= 100 else "Over Budget"
    class_langsung = "status-under" if persen_rpkg_langsung <= 100 else "status-over"
    st.html(f"""
    <div class="rpkg-card">
        <div class="rpkg-header">
            <div class="rpkg-icon">⚙</div>
            <div class="rpkg-title">Biaya Langsung PKS</div>
        </div>
        <div class="rpkg-value">{format_rpkg(rpkg_langsung_aktual)}</div>
        <div class="rpkg-budget">Budget: {format_rpkg(rpkg_langsung_budget)}</div>
        <div class="rpkg-status {class_langsung}">{persen_rpkg_langsung:.1f}% — {status_langsung}</div>
    </div>
    """)

with col4:
    status_tidak = "Under Budget" if persen_rpkg_tidak <= 100 else "Over Budget"
    class_tidak = "status-under" if persen_rpkg_tidak <= 100 else "status-over"
    st.html(f"""
    <div class="rpkg-card">
        <div class="rpkg-header">
            <div class="rpkg-icon">🏭</div>
            <div class="rpkg-title">Biaya Tdk Langsung PKS</div>
        </div>
        <div class="rpkg-value">{format_rpkg(rpkg_tidak_aktual)}</div>
        <div class="rpkg-budget">Budget: {format_rpkg(rpkg_tidak_budget)}</div>
        <div class="rpkg-status {class_tidak}">{persen_rpkg_tidak:.1f}% — {status_tidak}</div>
    </div>
    """)


# ==========================================================
# GRAFIK 1: CAPAIAN TBS
# ==========================================================
st.markdown("---")
st.subheader("% Capaian Aktual (Budget vs Sensus) - TBS Produksi")

if not df_tbs.empty:
    grafik = df_tbs.groupby("UNIT KERJA")[["CAPAIAN_BUDGET", "CAPAIAN_SENSUS"]].mean().reset_index()

    warna_budget = ["#1f77b4" if n >= 100 else "#ff0000" if n >= 95 else "#ff6666" for n in grafik["CAPAIAN_BUDGET"]]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=grafik["UNIT KERJA"], y=grafik["CAPAIAN_BUDGET"],
        name="Aktual vs Budget", marker_color=warna_budget,
        text=grafik["CAPAIAN_BUDGET"].round(1), textposition="outside"
    ))
    fig.add_trace(go.Bar(
        x=grafik["UNIT KERJA"], y=grafik["CAPAIAN_SENSUS"],
        name="Aktual vs Sensus", marker_color="lightgray",
        text=grafik["CAPAIAN_SENSUS"].round(1), textposition="outside"
    ))

    fig.update_layout(
        barmode="group", height=450,
        yaxis_title="Persentase (%)", yaxis=dict(range=[0, 120]),
        legend=dict(orientation="h", y=1.1)
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Data TBS tidak tersedia untuk filter terpilih.")


# ==========================================================
# GRAFIK 2: TREND PRODUKSI CPO
# ==========================================================
st.subheader("📈 Trend Produksi CPO per Bulan")

if not df_cpo.empty:
    trend = df_cpo.groupby("BULAN")[["BUDGET", "AKTUAL"]].sum().reset_index()
    nama_bulan = {1: "Januari", 2: "Februari", 3: "Maret", 4: "April", 5: "Mei", 6: "Juni",
                  7: "Juli", 8: "Agustus", 9: "September", 10: "Oktober", 11: "November", 12: "Desember"}
    
    trend["NAMA_BULAN"] = trend["BULAN"].map(nama_bulan)
    urutan_bulan = list(nama_bulan.values())
    trend["NAMA_BULAN"] = pd.Categorical(trend["NAMA_BULAN"], categories=urutan_bulan, ordered=True)
    trend = trend.sort_values("NAMA_BULAN")

    def format_juta(x):
        return f"{x / 1_000_000:.2f} jt kg"

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=trend["NAMA_BULAN"], y=trend["BUDGET"],
        mode="lines+markers+text", name="Budget",
        text=trend["BUDGET"].apply(format_juta), textposition="top center"
    ))
    fig2.add_trace(go.Scatter(
        x=trend["NAMA_BULAN"], y=trend["AKTUAL"],
        mode="lines+markers+text", name="Aktual",
        text=trend["AKTUAL"].apply(format_juta), textposition="top center"
    ))

    fig2.update_layout(
        xaxis_title="Bulan", yaxis_title="Produksi (kg)",
        height=450, hovermode="x unified"
    )
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.warning("Data CPO tidak tersedia untuk filter terpilih.")


# ==========================================================
# DETAIL BIAYA PER STASIUN & ALERTS
# ==========================================================
st.markdown("## 📊 Komposisi Biaya Langsung per Stasiun")

if not df_langsung.empty:
    kolom_stasiun = "STASIUN"
    tabel_stasiun = df_langsung.groupby(kolom_stasiun, as_index=False).agg(
        BUDGET=("BUDGET", "sum"),
        AKTUAL=("AKTUAL", "sum")
    )

    tabel_stasiun["BUDGET_RPKG"] = (tabel_stasiun["BUDGET"] / budget_produksi_rpkg) if budget_produksi_rpkg > 0 else 0
    tabel_stasiun["AKTUAL_RPKG"] = (tabel_stasiun["AKTUAL"] / aktual_produksi_rpkg) if aktual_produksi_rpkg > 0 else 0

    tabel_stasiun["SELISIH"] = (
        (tabel_stasiun["AKTUAL_RPKG"] / tabel_stasiun["BUDGET_RPKG"] - 1) * 100
    ).replace([float("inf"), -float("inf")], 0).fillna(0)

    tabel_stasiun["PROPORSI"] = (
        (tabel_stasiun["AKTUAL"] / aktual_langsung * 100) if aktual_langsung > 0 else 0
    )

    tabel_stasiun = tabel_stasiun.sort_values("PROPORSI", ascending=False)

    # Total
    total_budget_rpkg = (budget_langsung / budget_produksi_rpkg) if budget_produksi_rpkg > 0 else 0
    total_aktual_rpkg = (aktual_langsung / aktual_produksi_rpkg) if aktual_produksi_rpkg > 0 else 0
    total_selisih = ((total_aktual_rpkg / total_budget_rpkg - 1) * 100) if total_budget_rpkg > 0 else 0

    tabel_tampil = tabel_stasiun[[kolom_stasiun, "BUDGET_RPKG", "AKTUAL_RPKG", "SELISIH", "PROPORSI"]].copy()
    tabel_tampil.columns = ["Stasiun / Komponen Biaya", "Budget (Rp/Kg)", "Aktual (Rp/Kg)", "Selisih (%)", "% Proporsi Biaya"]

    baris_total = pd.DataFrame({
        "Stasiun / Komponen Biaya": ["TOTAL BIAYA LANGSUNG"],
        "Budget (Rp/Kg)": [total_budget_rpkg],
        "Aktual (Rp/Kg)": [total_aktual_rpkg],
        "Selisih (%)": [total_selisih],
        "% Proporsi Biaya": [100.0]
    })

    tabel_tampil = pd.concat([tabel_tampil, baris_total], ignore_index=True)

    col_kiri, col_kanan = st.columns([1, 1], gap="medium")

    with col_kiri:
        st.markdown("### 📋 Detail Biaya per Stasiun")
        st.dataframe(
            tabel_tampil,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Stasiun / Komponen Biaya": st.column_config.TextColumn(width="medium"),
                "Budget (Rp/Kg)": st.column_config.NumberColumn(format="%.2f"),
                "Aktual (Rp/Kg)": st.column_config.NumberColumn(format="%.2f"),
                "Selisih (%)": st.column_config.NumberColumn(format="%.1f%%"),
                "% Proporsi Biaya": st.column_config.NumberColumn(format="%.1f%%")
            },
            height=500
        )

    with col_kanan:
        st.markdown("### 🚨 Alert Stasiun Kritis")

        # Top 3 Proporsi
        top_proporsi = tabel_stasiun.head(3)
        html_proporsi = """<div style="background:#FFF4E5; border-left:5px solid #FF9800; border-radius:6px; padding:14px; margin-bottom:15px;">
        <div style="font-size:15px; font-weight:bold; color:#E65100; margin-bottom:10px;">🟠 3 Proporsi Biaya Terbesar</div>"""
        
        for i, (_, row) in enumerate(top_proporsi.iterrows(), start=1):
            html_proporsi += f"""
            <div style="background:white; border:1px solid #ddd; border-radius:5px; padding:10px; margin-bottom:7px;">
                <div style="font-weight:bold; color:#333; font-size:13px;">{i}. {row[kolom_stasiun]}</div>
                <div style="font-size:12px; color:#666; margin-top:4px;">
                    Proporsi: <span style="color:#FF9800; font-weight:bold;">{row["PROPORSI"]:.1f}%</span> &nbsp;|&nbsp;
                    Aktual: <b>{row["AKTUAL_RPKG"]:.2f} Rp/Kg</b>
                </div>
            </div>"""
        html_proporsi += "</div>"
        st.html(html_proporsi)

        # Top 3 Selisih Over Budget
        top_selisih = tabel_stasiun.sort_values("SELISIH", ascending=False).head(3)
        html_selisih = """<div style="background:#FFE5E5; border-left:5px solid #F44336; border-radius:6px; padding:14px; margin-bottom:15px;">
        <div style="font-size:15px; font-weight:bold; color:#D32F2F; margin-bottom:10px;">🔴 3 Selisih Terbesar / Over Budget</div>"""

        for i, (_, row) in enumerate(top_selisih.iterrows(), start=1):
            html_selisih += f"""
            <div style="background:white; border:1px solid #ddd; border-radius:5px; padding:10px; margin-bottom:7px;">
                <div style="font-weight:bold; color:#333; font-size:13px;">{i}. {row[kolom_stasiun]}</div>
                <div style="font-size:12px; margin-top:4px;">
                    Selisih: <span style="color:#F44336; font-weight:bold;">{row["SELISIH"]:+.1f}%</span> &nbsp;|&nbsp;
                    Aktual: <b>{row["AKTUAL_RPKG"]:.2f} Rp/Kg</b>
                </div>
                <div style="font-size:11px; color:#777; margin-top:3px;">Budget: {row["BUDGET_RPKG"]:.2f} Rp/Kg</div>
            </div>"""
        html_selisih += "</div>"
        st.html(html_selisih)

        # Perhatian Manajemen
        st.html("""
        <div style="background:#E3F2FD; border-left:5px solid #2196F3; border-radius:6px; padding:14px;">
            <div style="font-size:14px; font-weight:bold; color:#1565C0; margin-bottom:7px;">💡 Perhatian Manajemen</div>
            <div style="font-size:12px; color:#444; line-height:1.5;">
                Prioritaskan evaluasi stasiun yang memiliki proporsi biaya tinggi dan selisih Rp/Kg positif. Stasiun tersebut memberikan kontribusi terbesar terhadap total biaya langsung sekaligus memiliki tekanan terhadap budget.
            </div>
        </div>
        """)
else:
    st.warning("Data Biaya Langsung tidak tersedia untuk filter terpilih.")
