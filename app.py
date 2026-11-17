import logging
logging.getLogger('streamlit.runtime.scriptrunner_utils.script_run_context').setLevel(logging.ERROR)
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import gspread
from google.oauth2.service_account import Credentials
import os
import math
import io
import re
import graphviz
import base64

# 1. KONFIGURASI HALAMAN
st.set_page_config(
    page_title="PLN UP3 Bekasi Apps",
    layout="wide",
    page_icon="⚡",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. LOGIKA BACKGROUND SIDEBAR (KEMBALI KE PUTIH)
# ==========================================
bg_sidebar_css = ""

# ==========================================
# 3. CSS UTAMA
# ==========================================
theme_css = """
    :root { color-scheme: light !important; }
    html, body, p, h1, h2, h3, h4, h5, h6, li, a, input, button, label, textarea, .stMarkdown { font-family: 'Inter', 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important; }
    .stApp { background-color: #F4F6F9 !important; color: #333333 !important; }
    
    /* Background default jika gambar tidak ada */
    section[data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 1px solid #E0E0E0 !important; }
    
    .sidebar-logo-text { font-size: 1.25rem; font-weight: 900; color: #333333; letter-spacing: -0.5px; line-height: 1.1; }
    .sidebar-logo-sub { font-size: 1.25rem; color: #00AFF0; font-weight: 800; text-transform: uppercase; letter-spacing: -0.5px; line-height: 1.2; margin-top: 8px; }
    .sidebar-logo-container { border-bottom: 1px solid rgba(255, 255, 255, 0.2); margin-bottom: 25px; padding-bottom: 20px;}
    
    /* Expander / Dropdown Styling */
    div[data-testid="stExpander"] { background-color: #FFFFFF !important; border: 1px solid #E0E0E0 !important; border-radius: 8px !important; margin-bottom: 15px !important; box-shadow: 0 2px 4px rgba(0,0,0,0.02); overflow: hidden;}
    div[data-testid="stExpander"] details summary { background-color: #F0F2F6 !important; padding: 10px 15px !important; }
    div[data-testid="stExpander"] details summary:hover { background-color: #EAEAEA !important; }
    div[data-testid="stExpander"] details summary p { font-size: 16px !important; font-weight: 700 !important; color: #333333 !important; }
    div[data-testid="stExpander"] details summary svg { fill: #333333 !important; color: #333333 !important; }
    div[data-testid="stExpander"] [data-testid="stExpanderDetails"] { background-color: #FFFFFF !important; padding-top: 15px !important;}
    
    /* Form Inputs */
    div[data-baseweb="select"] > div { 
        background-color: #FFFFFF !important; 
        border: 2px solid #00AFF0 !important; 
        border-radius: 8px !important; 
        box-shadow: 0 2px 4px rgba(0, 175, 240, 0.15) !important;
    }
    div[data-baseweb="select"] > div > div { color: #333333 !important; font-weight: 600; }
    div[data-baseweb="select"] svg { fill: #00AFF0 !important; }
    label[data-testid="stWidgetLabel"] p { color: #555555 !important; font-weight: 600; }
    input[type="text"], input[type="number"] { background-color: #FFFFFF !important; color: #333333 !important; border: 1px solid #E0E0E0 !important; border-radius: 6px !important; }
    div[data-testid="stCheckbox"] p { color: #333333 !important; }
    ul[data-baseweb="menu"] { background-color: #FFFFFF !important; border: 1px solid #E0E0E0 !important; }
    ul[data-baseweb="menu"] li { color: #333333 !important; background-color: transparent !important; }
    ul[data-baseweb="menu"] li:hover, ul[data-baseweb="menu"] li[aria-selected="true"] { background-color: #F0FAFF !important; color: #00AFF0 !important;}
    [data-testid="stDataFrame"], [data-testid="stDataEditor"] iframe, iframe[title*="data_editor"] { filter: none !important; }
    
    /* Sidebar Buttons Default (Ditimpah bg_sidebar_css di atas jika ada gambar) */
    section[data-testid="stSidebar"] div[data-testid="stButton"] button { background-color: #F8F9FA !important; border: 1px solid #E0E0E0 !important; min-height: 48px !important; padding: 12px 10px !important; margin-bottom: 6px !important; border-radius: 8px !important; }
    section[data-testid="stSidebar"] div[data-testid="stButton"] button p { font-size: 15px !important; font-weight: 600 !important; color: #333333 !important; }
    section[data-testid="stSidebar"] div[data-testid="stButton"] button:hover { border-color: #00AFF0 !important; background-color: #F0FAFF !important; }
    section[data-testid="stSidebar"] div[data-testid="stButton"] button:hover p { color: #00AFF0 !important; }
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="primary"] { background-color: #E0F7FF !important; border: 1px solid #00AFF0 !important; }
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="primary"] p { color: #00AFF0 !important; font-weight: bold !important; }
    
    /* Layout & Headers - CENTERED TEXT */
    .custom-header { background: linear-gradient(90deg, #00AFF0 0%, #33bfff 100%); color: white; padding: 25px 30px; border-radius: 12px; margin-bottom: 25px; margin-top: 10px; box-shadow: 0 4px 15px rgba(0, 175, 240, 0.3); display: flex; justify-content: center; align-items: center; text-align: center; min-height: 100px; }
    .stTabs [data-baseweb="tab-list"] { background-color: #FFFFFF; border-radius: 8px; padding: 5px; border: 1px solid #E0E0E0; box-shadow: 0 2px 4px rgba(0,0,0,0.02);}
    .stTabs [data-baseweb="tab"] { font-weight: 600; color: #666666; }
    .stTabs [aria-selected="true"] { background-color: #E0F7FF; color: #00AFF0; }
    div[data-testid="stPlotlyChart"] { background-color: #FFFFFF !important; border: 1px solid #E0E0E0 !important; border-radius: 16px; padding: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important; margin-bottom: 20px !important; }
    
    /* Tabel Rekap */
    .rekap-custom, .rekap-1juta { border: 2px solid #000; background-color:#FFFFFF; width: 100%; border-collapse: collapse; font-family: 'Inter', sans-serif; margin-top: 15px;}
    .rekap-custom th, .rekap-custom td, .rekap-1juta th, .rekap-1juta td { border: 1px solid #000; color: #000; padding: 12px 15px; text-align: center; vertical-align: middle; font-size: 15px;}
    .rekap-custom .header-main { background-color: #FFC000; color:#000; border-bottom: 2px solid #000; font-size: 20px; font-weight: 900;}
    .bg-unit, .bg-unit-1j { background-color: #F4B084 !important; color:#000 !important; font-weight: bold;}
    .bg-totplg, .bg-lunas-1j { background-color: #9BC2E6 !important; color:#000 !important; font-weight: bold;}
    .bg-rptlawal { background-color: #B4A7D6 !important; color:#000 !important; font-weight: bold;}
    .bg-plgblm, .bg-belum-1j { background-color: #A9D08E !important; color:#000 !important; font-weight: bold;}
    .bg-rptlblm { background-color: #D99694 !important; color:#000 !important; font-weight: bold;}
    .rekap-custom tbody tr, .rekap-1juta tbody tr { background-color: #FFFFFF; transition: all 0.2s;}
    .rekap-custom tbody tr:hover, .rekap-1juta tbody tr:hover { background-color: #F8F9FA; }
    .rekap-custom .col-unit, .rekap-1juta .col-unit { background-color: #FFFFFF; color: #000; font-weight: bold;}
    .rekap-custom .row-total td, .rekap-1juta .row-total td { background-color: #F0F2F6; color:#000; font-weight: 900; font-size: 17px;}
    
    /* TOMBOL DOWNLOAD */
    .main div[data-testid="stDownloadButton"] button { background-color: #00AFF0 !important; color: #FFFFFF !important; border: none !important; border-radius: 8px !important; font-weight: bold !important; transition: all 0.3s ease; }
    .main div[data-testid="stDownloadButton"] button:hover { background-color: #008CDB !important; transform: scale(1.02); box-shadow: 0 4px 10px rgba(0, 175, 240, 0.3); }

    /* TOOLTIP INFO */
    .info-tooltip { position: relative; display: inline-block; cursor: help; margin-left: 8px; font-size: 18px; }
    .info-tooltip .tooltip-text { visibility: hidden; width: 300px; background-color: #2C3E50; color: #FFFFFF; text-align: left; border-radius: 8px; padding: 12px 15px; position: absolute; z-index: 99999; bottom: 130%; left: 50%; transform: translateX(-50%); opacity: 0; transition: opacity 0.3s ease; font-size: 13px; font-weight: 500; box-shadow: 0 4px 12px rgba(0,0,0,0.2); line-height: 1.5; font-family: 'Inter', sans-serif; }
    .info-tooltip .tooltip-text::after { content: ""; position: absolute; top: 100%; left: 50%; margin-left: -6px; border-width: 6px; border-style: solid; border-color: #2C3E50 transparent transparent transparent; }
    .info-tooltip:hover .tooltip-text { visibility: visible; opacity: 1; }
"""

# ==========================================
# 4. MENERAPKAN CSS
# ==========================================
st.markdown(f"""
    <style>
        {theme_css}
        {bg_sidebar_css}
        
        .stAppDeployButton {{ display: none !important; }}
        footer {{ display: none !important; }}
        header[data-testid="stHeader"] {{ display: block !important; visibility: visible !important; background-color: transparent !important; box-shadow: none !important; z-index: 99999 !important; }}
        
        /* --- 1. TOMBOL TUTUP (<< DI DALAM SIDEBAR) --- */
        [data-testid="stSidebarCollapseButton"] {{
            background-color: #00AFF0 !important;
            color: #FFFFFF !important;
            border-radius: 50% !important;
            box-shadow: 0 4px 12px rgba(0, 175, 240, 0.6) !important;
            opacity: 1 !important;
            visibility: visible !important;
            transition: all 0.3s ease !important;
            padding: 8px !important;
        }}
        [data-testid="stSidebarCollapseButton"] svg {{
            fill: #FFFFFF !important;
            color: #FFFFFF !important;
            width: 20px !important;
            height: 20px !important;
        }}
        [data-testid="stSidebarCollapseButton"]:hover {{
            transform: scale(1.15) !important;
            background-color: #008CDB !important;
            box-shadow: 0 6px 16px rgba(0, 175, 240, 0.8) !important;
        }}

        /* --- 2. TOMBOL BUKA (>> DI LUAR SIDEBAR) SELALU MUNCUL --- */
        [data-testid="collapsedControl"] {{
            background-color: #00AFF0 !important;
            color: #FFFFFF !important;
            border-radius: 50% !important;
            box-shadow: 0 4px 12px rgba(0, 175, 240, 0.6) !important;
            opacity: 1 !important;
            visibility: visible !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            width: 45px !important;
            height: 45px !important;
            transition: all 0.3s ease !important;
            border: none !important;
            position: fixed !important;
            top: 15px !important;
            left: 15px !important;
            z-index: 999999 !important;
        }}
        
        [data-testid="collapsedControl"] svg {{
            fill: #FFFFFF !important;
            color: #FFFFFF !important;
            width: 20px !important;
            height: 20px !important;
        }}
        
        [data-testid="collapsedControl"]:hover {{
            transform: scale(1.15) !important;
            background-color: #008CDB !important;
            box-shadow: 0 6px 16px rgba(0, 175, 240, 0.8) !important;
        }}
        
        .main .block-container {{ padding-top: 4.5rem !important; padding-left: 2rem !important; padding-right: 2rem !important; max-width: 100% !important; }}
        section[data-testid="stSidebar"] .block-container {{ padding-top: 1.5rem !important; margin-top: 0px; }}
        [data-testid="stSidebar"] img {{ margin-bottom: 8px !important; margin-top: 0px !important; }}
        
        /* Teks H2 Center Alignment */
        .custom-header h2 {{ color: white !important; margin: 0 !important; padding: 0 !important; font-size: 2.2rem; font-weight: 800; letter-spacing: -0.5px; text-align: center; width: 100%; }}
        
        .stTabs [data-baseweb="tab-list"] {{ gap: 4px; }}
        .stTabs [data-baseweb="tab"] {{ height: 40px; background-color: transparent; border-radius: 6px; padding: 0 20px; border: none; }}
        .scroll-box::-webkit-scrollbar {{ width: 6px; }}
        .scroll-box::-webkit-scrollbar-track {{ background: transparent; }}
        .scroll-box::-webkit-scrollbar-thumb {{ background: rgba(136, 136, 136, 0.5); border-radius: 4px; }}
        .scroll-box::-webkit-scrollbar-thumb:hover {{ background: rgba(136, 136, 136, 0.8); }}
    </style>
""", unsafe_allow_html=True)

# VARIABEL WARNA DINAMIS PLOTLY & CARDS
color_palettes = [
    {"T": "#1f77b4", "R": "#2ca02c"},
    {"T": "#9467bd", "R": "#17becf"},
    {"T": "#ff7f0e", "R": "#8c564b"},
    {"T": "#d62728", "R": "#e377c2"}
]
FIXED_PERCENT_COLOR = "#ff7f0e"
WARNING_RED = "#D32F2F"
SUCCESS_GREEN = "#2E7D32"
BG_CHART = "#FFFFFF"
BG_PAPER = "#FFFFFF"
FONT_COLOR = "#333333"
GRID_COLOR = "#EEEEEE"
HOVER_BG = "#FFFFFF"
HOVER_FONT = "#000000"
TABLE_HEADER_BG = "#E0F7FF"
TABLE_CELL_BG = "#FFFFFF"

def render_summary_cards(placeholder, det_tercapai, det_belum):
    len_tercapai, len_belum = len(det_tercapai), len(det_belum)
    if len_tercapai == 0 and len_belum == 0:
        return

    def build_list(items, color_t, color_r):
        if not items:
            return "<p style='font-size:13px; color:#888; text-align:center; padding-top:10px;'>Tidak ada data bulan ini.</p>"
        html_list = ""
        for item in items:
            html_list += f"<div style='margin-bottom: 10px; padding-bottom: 10px; border-bottom: 1px dashed rgba(136,136,136,0.3);'><div style='font-size: 14px; font-weight: 800; color: {color_r}; margin-bottom: 4px;'>📍 {item['label']}</div><div style='font-size: 13px; display: flex; justify-content: space-between; font-weight: 500;'><span style='color: #888;'>Target: <b style='color: {color_t};'>{item['t']}</b></span><span style='color: #888;'>Real: <b style='color: {color_r};'>{item['r']}</b></span></div></div>"
        return html_list

    t_col, b_col, text_sub, bg_t, bg_b, border_t, border_b = "#2E7D32", "#D32F2F", "#555555", "#F6FEF9", "#FFF9F9", "#C8E6C9", "#FFCDD2"

    html = f"""<div style="display: flex; gap: 20px; margin-bottom: 25px; align-items: flex-start;"><details class="custom-card" style="flex: 1; background: {bg_t}; border: 1px solid {border_t}; border-left: 6px solid {t_col}; border-radius: 12px; box-shadow: 0 8px 16px rgba(0,0,0,0.15); cursor: pointer;"><summary style="padding: 25px; outline: none; list-style: none;"><div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;"><p style="margin: 0; font-size: 14px; color: {text_sub}; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;">✅ Target Tercapai</p><span style="font-size: 11px; color: {text_sub}; background: rgba(136,136,136,0.1); padding: 3px 8px; border-radius: 10px; font-weight: bold;">🔽 DETAIL</span></div><h3 style="margin: 0; color: {t_col}; font-size: 38px; font-weight: 900; text-shadow: 0 0 15px rgba(0, 230, 118, 0.2);">{len_tercapai} <span style="font-size: 16px; font-weight: 600; color: {text_sub};">Bulan</span></h3></summary><div class="scroll-box" style="padding: 0 25px 25px 25px; max-height: 250px; overflow-y: auto;"><div style="margin-top: 5px; padding-top: 15px; border-top: 1px solid {border_t};">{build_list(det_tercapai, "#1f77b4", t_col)}</div></div></details><details class="custom-card" style="flex: 1; background: {bg_b}; border: 1px solid {border_b}; border-left: 6px solid {b_col}; border-radius: 12px; box-shadow: 0 8px 16px rgba(0,0,0,0.15); cursor: pointer;"><summary style="padding: 25px; outline: none; list-style: none;"><div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;"><p style="margin: 0; font-size: 14px; color: {text_sub}; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;">🚨 Belum Tercapai</p><span style="font-size: 11px; color: {text_sub}; background: rgba(136,136,136,0.1); padding: 3px 8px; border-radius: 10px; font-weight: bold;">🔽 DETAIL</span></div><h3 style="margin: 0; color: {b_col}; font-size: 38px; font-weight: 900; text-shadow: 0 0 15px rgba(255, 23, 68, 0.2);">{len_belum} <span style="font-size: 16px; font-weight: 600; color: {text_sub};">Bulan</span></h3></summary><div class="scroll-box" style="padding: 0 25px 25px 25px; max-height: 250px; overflow-y: auto;"><div style="margin-top: 5px; padding-top: 15px; border-top: 1px solid {border_b};">{build_list(det_belum, "#1f77b4", b_col)}</div></div></details></div>"""
    placeholder.markdown(html, unsafe_allow_html=True)

def render_download_buttons(fig_obj, nama_file, key_id):
    try:
        # Lebar dan tinggi PNG dibesarkan (misal: 1920x1080) dengan scale=2 agar resolusinya tajam (3840x2160)
        png_data = fig_obj.to_image(format="png", width=1920, height=1080, scale=2)
        
        # PDF dibiarkan persis seperti semula
        pdf_data = fig_obj.to_image(format="pdf", width=1200, height=700)
        
        c1, c2, _ = st.columns([1, 1, 4])
        c1.download_button(label="⬇️ PNG", data=png_data, file_name=f"{nama_file}.png", mime="image/png", use_container_width=True, type="primary", key=f"dl_png_{key_id}")
        c2.download_button(label="⬇️ PDF", data=pdf_data, file_name=f"{nama_file}.pdf", mime="application/pdf", use_container_width=True, type="primary", key=f"dl_pdf_{key_id}")
    except Exception as e:
        st.warning("Fitur download memuat. Pastikan 'kaleido' terinstal di requirements.txt")

# ==========================================
# LOAD & CLEAN DATA FUNCTIONS
# ==========================================
@st.cache_data(ttl=600)
def load_data():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    try:
        if os.path.exists("credentials.json"):
            credentials = Credentials.from_service_account_file("credentials.json", scopes=scopes)
        elif "gcp_service_account" in st.secrets:
            credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
        else:
            return None

        gc = gspread.authorize(credentials)
        try:
            sh = gc.open("Raw Data Dashboard KN dan Pemasaran")
            ws = sh.worksheet("REKAP KINERJA")
        except:
            sh = gc.open("Data Mentah PLN UP3 Bekasi")
            ws = sh.sheet1
        data = ws.get_all_values()
        return pd.DataFrame(data[1:], columns=data[0])
    except Exception as e:
        return None

@st.cache_data(ttl=600)
def load_mindmap_architecture():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    try:
        if os.path.exists("credentials.json"):
            credentials = Credentials.from_service_account_file("credentials.json", scopes=scopes)
        elif "gcp_service_account" in st.secrets:
            credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
        else:
            return None, None
        gc = gspread.authorize(credentials)
        sh = gc.open("Raw Data Dashboard KN dan Pemasaran")
        try:
            df_master = pd.DataFrame(sh.worksheet("MASTER_PETA").get_all_values()[1:], columns=sh.worksheet("MASTER_PETA").get_all_values()[0])
        except:
            df_master = pd.DataFrame()
        try:
            df_input = pd.DataFrame(sh.worksheet("INPUT_BULANAN").get_all_values()[1:], columns=sh.worksheet("INPUT_BULANAN").get_all_values()[0])
        except:
            df_input = pd.DataFrame()
        return df_master, df_input
    except Exception:
        return None, None

@st.cache_data(ttl=600)
def load_piutang_from_gsheet():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    try:
        if os.path.exists("credentials.json"):
            credentials = Credentials.from_service_account_file("credentials.json", scopes=scopes)
        elif "gcp_service_account" in st.secrets:
            credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
        else:
            return pd.DataFrame()
        gc = gspread.authorize(credentials)
        sh = gc.open("Raw Data Dashboard KN dan Pemasaran")
        df = pd.DataFrame(sh.worksheet("ROC PIUTANG").get_all_values()[1:], columns=sh.worksheet("ROC PIUTANG").get_all_values()[0])
        return df
    except Exception as e:
        return pd.DataFrame()

@st.cache_data(ttl=600)
def load_hcs_from_gsheet():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    try:
        if os.path.exists("credentials.json"):
            credentials = Credentials.from_service_account_file("credentials.json", scopes=scopes)
        elif "gcp_service_account" in st.secrets:
            credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
        else:
            return pd.DataFrame()
        gc = gspread.authorize(credentials)
        sh = gc.open("Raw Data Dashboard KN dan Pemasaran")
        df = pd.DataFrame(sh.worksheet("HCS").get_all_values()[1:], columns=sh.worksheet("HCS").get_all_values()[0])
        return df
    except Exception as e:
        return pd.DataFrame()

@st.cache_data(ttl=600)
def load_spklu_from_gsheet():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    try:
        if os.path.exists("credentials.json"):
            credentials = Credentials.from_service_account_file("credentials.json", scopes=scopes)
        elif "gcp_service_account" in st.secrets:
            credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
        else:
            return pd.DataFrame()
        gc = gspread.authorize(credentials)
        sh = gc.open("Raw Data Dashboard KN dan Pemasaran")
        try:
            raw_data = sh.worksheet("Data SPKLU").get_all_values()
        except Exception:
            return pd.DataFrame()
        if len(raw_data) < 2:
            return pd.DataFrame()
        
        df = pd.DataFrame(raw_data[1:], columns=raw_data[0])
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        def clean_val(val):
            if pd.isna(val):
                return 0.0
            s = str(val).strip().replace('.', '').replace(',', '.')
            if not s or s.upper() in ['NAN', 'TOTAL', '-']:
                return 0.0
            try:
                return float(s)
            except:
                return 0.0

        for c in df.columns:
            cu = str(c).upper()
            if 'TRX' in cu or 'KWH' in cu or 'RP' in cu:
                df[c] = df[c].apply(clean_val)
        return df
    except Exception as e:
        return pd.DataFrame()

def parse_uploaded_excel(file_bytes):
    return pd.read_excel(io.BytesIO(file_bytes))

def clean_data(df):
    if df is None or df.empty:
        return pd.DataFrame(), [], [], [], []
    if 'BULAN' not in df.columns or 'ULP' not in df.columns:
        return pd.DataFrame(), [], [], [], []
    cols_T, cols_R, cols_P, rename_map, unique_indicators = [], [], [], {}, set()
    cols_to_keep = ['BULAN', 'ULP']
    for col in df.columns:
        jenis = ""
        if '(T)' in col:
            jenis = " (Target)"
        elif '(R)' in col:
            jenis = " (Realisasi)"
        elif '(%)' in col:
            jenis = " (%)"
        if jenis:
            cols_to_keep.append(col)
            base_name_raw = str(col).split('(')[0].strip().upper()
            if "PENJUALAN" in base_name_raw:
                base_name = "Penjualan Tenaga Listrik"
            elif "RUPIAH TRANSAKSI" in base_name_raw:
                base_name = "Rupiah Transaksi PLN Mobile"
            elif "TRANSAKSI" in base_name_raw:
                base_name = "Transaksi PLN Mobile"
            elif "TERSAMBUNG" in base_name_raw:
                base_name = "Penambahan Daya Tersambung"
            elif "TEMATIK" in base_name_raw:
                base_name = "Penambahan Pelanggan Produk Tematik"
            elif "PELANGGAN" in base_name_raw:
                base_name = "Penambahan Jumlah Pelanggan"
            elif "KOGOL" in base_name_raw:
                base_name = "Rata Rata Saldo Tgl 20 Non-Kogol 1 & 2"
            elif "AKHIR BULAN" in base_name_raw or "SALDO AKHIR" in base_name_raw:
                base_name = "Rata-Rata Saldo Akhir Bulan"
            elif "PRR" in base_name_raw:
                base_name = "Pelunasan PRR"
            elif "BIAYA PENYAMBUNGAN" in base_name_raw:
                base_name = "Penambahan Biaya Penyambungan"
            elif "RATING" in base_name_raw:
                base_name = "Rating PLN Mobile"
            elif "16500" in base_name_raw:
                base_name = "REKAP DAYA DIATAS 16500 BELUM LUNAS > TGL 20"
            else:
                base_name = str(col).split('(')[0].strip().title()

            unique_indicators.add(base_name)
            rename_map[col] = base_name + jenis
            if jenis == " (Target)":
                cols_T.append(base_name + jenis)
            elif jenis == " (Realisasi)":
                cols_R.append(base_name + jenis)
            else:
                cols_P.append(base_name + jenis)

    df_clean = df[cols_to_keep].copy()
    df_clean.rename(columns=rename_map, inplace=True)
    df_clean['ULP'] = df_clean['ULP'].astype(str).str.strip()
    df_clean['BULAN'] = df_clean['BULAN'].astype(str).str.strip().str.replace('-', ' ')
    try:
        split_data = df_clean['BULAN'].str.split(' ', expand=True)
        df_clean['Nama_Bulan'] = split_data[0].str.title()
        df_clean['Tahun'] = split_data[1]
    except:
        df_clean['Nama_Bulan'] = df_clean['BULAN'].str.title()
        df_clean['Tahun'] = "Unknown"

    month_map = {
        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'Mei': 5, 'Jun': 6,
        'Jul': 7, 'Agu': 8, 'Sep': 9, 'Okt': 10, 'Nov': 11, 'Des': 12,
        'Januari': 1, 'Februari': 2, 'Maret': 3, 'April': 4, 'Juni': 6,
        'Juli': 7, 'Agustus': 8, 'September': 9, 'Oktober': 10, 'November': 11, 'Desember': 12
    }
    df_clean['Month_Num'] = df_clean['Nama_Bulan'].map(month_map).fillna(99).astype(int)

    for c in cols_T + cols_R + cols_P:
        if c in df_clean.columns:
            s = df_clean[c].astype(str).str.replace('Rp', '').str.replace('%', '').str.strip().str.replace('.', '').str.replace(',', '.')
            df_clean[c] = pd.to_numeric(s, errors='coerce').fillna(0)
    return df_clean, cols_T, cols_R, cols_P, sorted(list(unique_indicators))

def format_indo(x, is_percent=False):
    if pd.isna(x) or str(x).strip() == "" or str(x).strip() == "0":
        return "-"
    try:
        v = float(x)
        if v == 0:
            return "-"
        if is_percent:
            s = f"{v:,.1f}"
            if s.endswith(".0"):
                s = s[:-2]
            return s.replace(",", "X").replace(".", ",").replace("X", ".")
        else:
            if v.is_integer():
                return f"{int(v):,}".replace(",", ".")
            else:
                s = f"{v:,.2f}".rstrip("0").rstrip(".")
                return s.replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return str(x)

def sidebar_logo():
    logo_list = ["logo_pln_transparan.png", "LOGO PLN TRANSPARAN.png", "logo.png"]
    found = next((f for f in logo_list if os.path.exists(f)), None)
    logo_col = "#333333"
    img_html = ""
    if found:
        try:
            with open(found, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode()
            img_html = f'<img src="data:image/png;base64,{encoded_string}" width="130" style="margin-bottom: 5px !important; display: block;">'
        except:
            pass
    st.sidebar.markdown(f"""
        <div class="sidebar-logo-container" style="margin-top: -15px;">
            {img_html}
            <div style="line-height: 1.1;">
                <div class="sidebar-logo-text" style="color:{logo_col}; margin-top: 0px;">PLN UP3 <span style="color:#00AFF0;">BEKASI</span></div>
                <div class="sidebar-logo-sub" style="margin-top: 4px;">Dashboard Kinerja Niaga</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# MODULES DASHBOARD
# ==========================================
def show_mindmap_generator():
    st.markdown("<div class='custom-header'><h2>MIND MAP</h2></div>", unsafe_allow_html=True)
            
    with st.spinner("Menghubungkan ke database Google Sheet..."):
        df_master, df_input = load_mindmap_architecture()
    if df_master is None or df_input is None:
        st.error("❌ **Gagal terhubung ke Google Sheet!**")
        return
    if df_master.empty or df_input.empty:
        st.warning("⚠️ Sheet **MASTER_PETA** atau **INPUT_BULANAN** belum ditemukan.")
        return

    bulan_col = next((c for c in df_input.columns if "BULAN" in str(c).upper()), None)
    if not bulan_col:
        st.error("❌ Kolom 'BULAN' tidak ditemukan di Sheet INPUT_BULANAN.")
        return

    list_bulan = df_input[bulan_col].unique().tolist()
    c_ctrl1, c_ctrl2, c_ctrl3 = st.columns([1.2, 1.8, 1.5])
    with c_ctrl1:
        pilih_bulan = st.selectbox("Pilih Bulan Laporan:", list_bulan)
    with c_ctrl2:
        fokus_view = st.selectbox("Pecah Flowchart:", ["Tampilkan Semua (Bawaan)", "Fokus INTENSIFIKASI", "Fokus EKSTENSIFIKASI"])
    with c_ctrl3:
        arah_view = st.selectbox("Orientasi Garis:", ["Atas ke Bawah (Vertical)", "Kiri ke Kanan (Horizontal)"])

    df_bulan_ini = df_input[df_input[bulan_col] == pilih_bulan]
    if df_bulan_ini.empty:
        return
    row_data = df_bulan_ini.iloc[0]

    real_val_text = "0"
    real_val_num = 1.0
    col_real_total = next((c for c in row_data.index if str(c).strip().upper() in ['REAL TOTAL', 'TOTAL']), None)
    if col_real_total:
        real_val_text = str(row_data[col_real_total]).strip()
        try:
            real_val_num = float(real_val_text.replace('.', '').replace(',', '.'))
            real_val_num = 1.0 if real_val_num == 0 else real_val_num
        except:
            pass

    target_val_text = "0"
    target_val_num = 0.0
    col_target_total = next((c for c in row_data.index if str(c).strip().upper() == 'TARGET TOTAL'), None)
    if col_target_total:
        target_val_text = str(row_data[col_target_total]).strip()
        try:
            target_val_num = float(target_val_text.replace('.', '').replace(',', '.'))
        except:
            pass

    master_cols = {c.strip().upper(): c for c in df_master.columns}
    item_col = master_cols.get('ITEM')
    induk_col = master_cols.get('INDUK')

    def get_raw_val(nama_item):
        for c in row_data.index:
            if str(c).strip().upper() == str(nama_item).upper():
                val_str = str(row_data[c]).strip()
                if not val_str or val_str.upper() == 'NAN':
                    return "0"
                return val_str
        return "0"

    def to_float(raw_str):
        try:
            return float(str(raw_str).replace('.', '').replace(',', '.'))
        except:
            return 0.0

    def fmt_pct(val):
        try:
            s = f"{float(val):,.2f}"
            return s.replace(",", "X").replace(".", ",").replace("X", ".")
        except:
            return str(val)

    try:
        # --- CLEAN VERSION: COMPACT & NATURAL LAYOUT ---
        dot = graphviz.Digraph()
        dot.graph_attr['ordering'] = 'out'
        
        dot.attr(rankdir='TB' if arah_view == "Atas ke Bawah (Vertical)" else 'LR', nodesep='0.01', ranksep='0.15', splines='ortho', ratio='compress')
        dot.attr('node', shape='plaintext', margin='0')
        dot.attr('edge', color='#000000', style='bold', arrowhead='none', penwidth='2')

        valid_nodes = set()
        all_induk_raw = set(df_master[induk_col].astype(str).str.strip().str.upper())
        all_anak_raw = set(df_master[item_col].astype(str).str.strip().str.upper())
        
        if fokus_view == "Tampilkan Semua (Bawaan)": 
            valid_nodes = all_induk_raw.union(all_anak_raw)
        else:
            target_root = fokus_view.replace("Fokus ", "").strip().upper()
            valid_nodes.add(target_root)
            valid_nodes.add("TOTAL") 
            
            level_1 = set(df_master[df_master[induk_col].str.upper() == target_root][item_col].str.upper())
            valid_nodes.update(level_1)
            for l1 in level_1:
                level_2 = set(df_master[df_master[induk_col].str.upper() == l1][item_col].str.upper())
                valid_nodes.update(level_2)
                for l2 in level_2:
                    level_3 = set(df_master[df_master[induk_col].str.upper() == l2][item_col].str.upper())
                    valid_nodes.update(level_3)

        drawn_nodes = set()

        def draw_node(n_name):
            if n_name not in valid_nodes or n_name in drawn_nodes:
                return
            drawn_nodes.add(n_name)
            
            parent_series = df_master[df_master[item_col].astype(str).str.strip().str.upper() == n_name][induk_col]
            parent_val = parent_series.iloc[0].strip().upper() if not parent_series.empty else ""
            
            bg_col = "#9BC2E6" if parent_val == "TOTAL" else "#E2F0D9"
            font_sz = "16" if parent_val == "TOTAL" else "14" 
            
            raw_val = get_raw_val(n_name)
            pct = (to_float(raw_val) / real_val_num) * 100 if real_val_num else 0
            label_html = f"""<<TABLE BORDER="2" CELLBORDER="1" CELLSPACING="0" CELLPADDING="2" COLOR="#000000"><TR><TD COLSPAN="3" BGCOLOR="{bg_col}" ALIGN="CENTER"><FONT POINT-SIZE="{font_sz}"><B>{n_name}</B></FONT></TD></TR><TR><TD BGCOLOR="#FFFFFF" ALIGN="CENTER"><FONT POINT-SIZE="12">Realisasi</FONT></TD><TD BGCOLOR="#FFFFFF" ALIGN="CENTER"><FONT POINT-SIZE="14"><B>{raw_val}</B></FONT></TD><TD BGCOLOR="#FFFFFF" ALIGN="CENTER"><FONT POINT-SIZE="12"><B>GWH</B></FONT></TD></TR><TR><TD BGCOLOR="#FFFFFF" ALIGN="CENTER"><FONT POINT-SIZE="12">Kontribusi</FONT></TD><TD BGCOLOR="#FFFFFF" ALIGN="CENTER"><FONT POINT-SIZE="14" COLOR="blue"><B>{fmt_pct(pct)}</B></FONT></TD><TD BGCOLOR="#FFFFFF" ALIGN="CENTER"><FONT POINT-SIZE="12" COLOR="blue"><B>%</B></FONT></TD></TR></TABLE>>"""
            dot.node(n_name, label=label_html)

        if "TOTAL" in valid_nodes:
            pct_pencapaian = (real_val_num / target_val_num * 100) if target_val_num > 0 else 0
            label_html = f"""<<TABLE BORDER="2" CELLBORDER="1" CELLSPACING="0" CELLPADDING="2" COLOR="#000000"><TR><TD COLSPAN="3" BGCOLOR="#FFC000" ALIGN="CENTER"><FONT POINT-SIZE="18"><B>TOTAL</B></FONT></TD></TR><TR><TD BGCOLOR="#FFFFFF" ALIGN="CENTER"><FONT POINT-SIZE="12">Target</FONT></TD><TD BGCOLOR="#FFFFFF" ALIGN="CENTER"><FONT POINT-SIZE="14"><B>{target_val_text}</B></FONT></TD><TD BGCOLOR="#FFFFFF" ALIGN="CENTER"><FONT POINT-SIZE="12"><B>GWH</B></FONT></TD></TR><TR><TD BGCOLOR="#FFFFFF" ALIGN="CENTER"><FONT POINT-SIZE="12">Real</FONT></TD><TD BGCOLOR="#FFFFFF" ALIGN="CENTER"><FONT POINT-SIZE="14"><B>{real_val_text}</B></FONT></TD><TD BGCOLOR="#FFFFFF" ALIGN="CENTER"><FONT POINT-SIZE="12"><B>GWH</B></FONT></TD></TR><TR><TD BGCOLOR="#FFFFFF" ALIGN="CENTER"><FONT POINT-SIZE="12">% Capaian</FONT></TD><TD BGCOLOR="#FFFFFF" ALIGN="CENTER"><FONT POINT-SIZE="14" COLOR="blue"><B>{fmt_pct(pct_pencapaian)}</B></FONT></TD><TD BGCOLOR="#FFFFFF" ALIGN="CENTER"><FONT POINT-SIZE="12" COLOR="blue"><B>%</B></FONT></TD></TR></TABLE>>"""
            dot.node("TOTAL", label=label_html, ordering="out")
            drawn_nodes.add("TOTAL")

        for idx, row in df_master.iterrows():
            parent = str(row[induk_col]).strip().upper()
            child = str(row[item_col]).strip().upper()
            
            if parent == 'NAN' or child == 'NAN' or not parent or not child:
                continue
            if parent not in valid_nodes or child not in valid_nodes:
                continue
            
            draw_node(child)
            
            if parent == "TOTAL" and child == "NATURAL GROWTH":
                dot.edge(parent, child, weight="100")
            elif parent == "TOTAL" and child == "EKSTENSIFIKASI":
                dot.edge(parent, child, tailport='e', headport='w', constraint='false')
            else:
                dot.edge(parent, child)

        if "TOTAL" in valid_nodes and "EKSTENSIFIKASI" in valid_nodes:
            dot.body.append('{ rank=same; "TOTAL"; "EKSTENSIFIKASI"; }')

        web_dot_source = dot.source
        st.markdown("<br>", unsafe_allow_html=True)
        dot.graph_attr['dpi'] = '300'

        st.markdown("<div style='background-color: white; padding: 20px; border-radius: 10px;'>", unsafe_allow_html=True)
        st.graphviz_chart(web_dot_source, use_container_width=False)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        try:
            png_data = dot.pipe(format='png')
            pdf_data = dot.pipe(format='pdf')
            col_dl1, col_dl2, _ = st.columns([1.5, 1.5, 5])
            nama_file_base = f"MindMap_{pilih_bulan}_{fokus_view.replace(' ', '_')}"
            col_dl1.download_button(label="⬇️ Download PNG", data=png_data, file_name=f"{nama_file_base}.png", mime="image/png", use_container_width=True, type="primary")
            col_dl2.download_button(label="⬇️ Download PDF", data=pdf_data, file_name=f"{nama_file_base}.pdf", mime="application/pdf", use_container_width=True, type="primary")
        except Exception:
            pass
    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")

def show_quick_graph():
    st.markdown("### Quick Graph Maker")

    with st.expander("🛠️ Pengaturan Grafik & Estetika", expanded=True):
        col1, col2, col3, col4 = st.columns([1.5, 2.5, 1, 1])
        with col1:
            chart_type = st.selectbox("Jenis Grafik", ["Line Chart (Garis)", "Bar Chart (Batang)"])
        with col2:
            chart_title = st.text_input("Judul Grafik", "Grafik Perbandingan Kinerja")
        with col3:
            st.write("Opsi Fill")
            use_area_fill = st.toggle("Area Fill", value=False, disabled=(chart_type != "Line Chart (Garis)"))
        with col4:
            font_size_mult = st.number_input("Skala Font", min_value=0.5, max_value=2.0, value=1.0, step=0.1)

        c1_r2, c2_r2, c3_r2, c4_r2 = st.columns([1.5, 2.5, 1, 1])
        with c1_r2:
            current_bg = BG_CHART
            bg_chart_color = st.color_picker("Warna Latar Grafik", current_bg)
        with c2_r2:
            y_axis_title = st.text_input("Nama Sumbu Y", "Nilai")
        with c3_r2:
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            show_grid = st.toggle("Tampilkan Grid", value=False)
        with c4_r2:
            ruang_atas = st.number_input("Ruang Atas", min_value=1.0, max_value=5.0, value=1.4, step=0.1)

    st.markdown("---")
    st.markdown("##### 2. Isi Data & Kelola Kolom")
    if 'quick_data_final' not in st.session_state:
        st.session_state.quick_data_final = pd.DataFrame({
            "Sumbu Y (Tahun/Garis)": ["2024", "2025", "2026"],
            "Jan": ["10", "12", ""], "Feb": ["20", "22", ""], "Mar": ["15", "18", ""], "Apr": ["25", "28", ""],
            "Mei": ["30", "32", ""], "Jun": ["28", "30", ""], "Jul": ["35", "38", ""], "Agu": ["40", "42", ""],
            "Sep": ["38", "40", ""], "Okt": ["45", "48", ""], "Nov": ["50", "55", ""], "Des": ["48", "52", ""]
        })

    ui_buttons = st.container()
    ui_table = st.container()

    with ui_table:
        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
        edited_quick_df = st.data_editor(st.session_state.quick_data_final, num_rows="dynamic", use_container_width=True)
        if not edited_quick_df.equals(st.session_state.quick_data_final):
            st.session_state.quick_data_final = edited_quick_df

    with ui_buttons:
        col_t2, col_t3 = st.columns([3, 2])
        with col_t2:
            c_in, c_btn = st.columns([3, 1])
            new_category = c_in.text_input("Tambah Kolom/Bulan", label_visibility="collapsed", placeholder="+ Tambah Kolom (Bulan Baru)")
            if c_btn.button("Tambah", type="primary", use_container_width=True):
                if new_category and new_category not in st.session_state.quick_data_final.columns:
                    st.session_state.quick_data_final[new_category] = ""
                    st.rerun()
        with col_t3:
            c_sel, c_del = st.columns([3, 1])
            list_kolom = [c for c in st.session_state.quick_data_final.columns if c != "Sumbu Y (Tahun/Garis)"]
            kolom_dihapus = c_sel.multiselect("Hapus Kolom", list_kolom, placeholder="- Pilih Kolom Dihapus -", label_visibility="collapsed")
            if c_del.button("Hapus", use_container_width=True):
                if kolom_dihapus:
                    st.session_state.quick_data_final = st.session_state.quick_data_final.drop(columns=kolom_dihapus)
                    st.rerun()

    list_tahun_yoy = edited_quick_df.iloc[:, 0].astype(str).str.strip().tolist()
    with st.expander("🚀 Fitur Advanced: Mini Graph YoY (Pojok Kanan)", expanded=False):
        enable_yoy = st.toggle("Tampilkan Mini Graph YoY", value=False)
        c_ya, c_yb = st.columns(2)
        with c_ya:
            yoy_a = st.selectbox("Tahun A (Baru/Saat Ini) - POSISI ATAS", list_tahun_yoy, index=len(list_tahun_yoy)-1 if len(list_tahun_yoy) > 0 else 0)
        with c_yb:
            yoy_b = st.selectbox("Tahun B (Lama/Pembanding) - POSISI BAWAH", list_tahun_yoy, index=len(list_tahun_yoy)-2 if len(list_tahun_yoy) > 1 else 0)

    st.markdown("---")
    st.markdown("##### 3. Hasil Grafik (Estetika Neon Pulse)")

    try:
        plot_df = edited_quick_df.copy()
        id_col = plot_df.columns[0]
        text_df = edited_quick_df.set_index(id_col).T
        text_df.columns = text_df.columns.astype(str).str.strip()

        def fix_indo_number(x):
            s = str(x).strip()
            s = re.sub(r'[^\d.,-]', '', s)
            if not s:
                return s
            if '.' in s and ',' in s:
                return s.replace('.', '').replace(',', '.')
            elif '.' in s and ',' not in s:
                parts = s.split('.')
                if len(parts[-1]) == 3 or s.count('.') > 1:
                    return s.replace('.', '')
                return s
            elif ',' in s and '.' not in s:
                return s.replace(',', '.')
            return s

        for col in plot_df.columns[1:]:
            plot_df[col] = plot_df[col].apply(fix_indo_number)
        plot_df = plot_df.set_index(id_col).T
        plot_df = plot_df.apply(pd.to_numeric, errors='coerce')
        plot_df.columns = plot_df.columns.astype(str).str.strip()

        max_y_val = plot_df.max().max()
        if pd.isna(max_y_val) or max_y_val == 0:
            max_y_val = 100
        ceiling_y = max_y_val * ruang_atas

        custom_colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2"]
        bg_hex = bg_chart_color.lstrip('#')
        r, g, b = tuple(int(bg_hex[i:i+2], 16) for i in (0, 2, 4))
        luminance = (0.299 * r + 0.587 * g + 0.114 * b)

        if luminance < 128:
            custom_font_color, custom_grid_color, marker_border_color = "#FAFAFA", "rgba(255,255,255,0.15)", "#333333"
        else:
            custom_font_color, custom_grid_color, marker_border_color = "#333333", "rgba(0,0,0,0.1)", "#333333"

        if chart_type == "Line Chart (Garis)":
            fig = px.line(plot_df, markers=True, color_discrete_sequence=custom_colors)
            for trace in fig.data:
                trace.text = text_df[str(trace.name).strip()].tolist()
            fig.update_traces(mode='lines+markers+text', texttemplate='%{text}', textposition='top center', textfont=dict(family="Inter", size=28 * font_size_mult, color=custom_font_color, weight='bold'), line=dict(width=6), marker=dict(size=20, line=dict(width=4, color=marker_border_color)), fill='tozeroy' if use_area_fill else 'none', connectgaps=True, cliponaxis=False)
        else:
            fig = px.bar(plot_df, barmode='group', color_discrete_sequence=custom_colors)
            for trace in fig.data:
                trace.text = text_df[str(trace.name).strip()].tolist()
            fig.update_traces(texttemplate='%{text}', textfont=dict(family="Inter", size=28 * font_size_mult, color=custom_font_color, weight='bold'), textangle=0, textposition="outside", cliponaxis=False, width=0.4)

        outline_col, main_col = "#FFFFFF", "#003865"
        title_annotations = []
        for dx in [-3, -2, 0, 2, 3]:
            for dy in [-3, -2, 0, 2, 3]:
                if dx == 0 and dy == 0:
                    continue
                title_annotations.append(dict(text=f"<b>{chart_title}</b>", x=0.0, y=1.20, xref="paper", yref="paper", showarrow=False, font=dict(family="Inter", size=30 * font_size_mult, color=outline_col), xanchor="left", yanchor="middle", xshift=dx, yshift=dy))
        title_annotations.append(dict(text=f"<b>{chart_title}</b>", x=0.0, y=1.20, xref="paper", yref="paper", showarrow=False, font=dict(family="Inter", size=30 * font_size_mult, color=main_col), xanchor="left", yanchor="middle", xshift=0, yshift=0))

        yoy_a_clean, yoy_b_clean = str(yoy_a).strip(), str(yoy_b).strip()
        if enable_yoy and yoy_a_clean in plot_df.columns and yoy_b_clean in plot_df.columns:
            col_a_data = plot_df[yoy_a_clean]
            last_valid_month_pos = -1
            for i, val in enumerate(col_a_data):
                if pd.notna(val):
                    last_valid_month_pos = i

            if last_valid_month_pos >= 0:
                sum_a = plot_df[yoy_a_clean].iloc[:last_valid_month_pos+1].sum()
                sum_b = plot_df[yoy_b_clean].iloc[:last_valid_month_pos+1].sum()
                yoy_pct = ((sum_a - sum_b) / sum_b * 100) if sum_b > 0 else 0
                x_base, max_width, y_bar_a, y_bar_b, b_height = 0.55, 0.20, 1.18, 1.06, 0.05
                y_center_a, y_center_b = y_bar_a + b_height/2, y_bar_b + b_height/2
                w_a = (sum_a / max(sum_a, sum_b) * max_width) if max(sum_a, sum_b) > 0 else 0
                w_b = (sum_b / max(sum_a, sum_b) * max_width) if max(sum_a, sum_b) > 0 else 0
                idx_c_a, idx_c_b = plot_df.columns.get_loc(yoy_a_clean) % len(custom_colors), plot_df.columns.get_loc(yoy_b_clean) % len(custom_colors)
                color_a, color_b = custom_colors[idx_c_a], custom_colors[idx_c_b]

                fig.add_shape(type="line", xref="paper", yref="paper", x0=x_base, y0=y_bar_b - 0.02, x1=x_base, y1=y_bar_a + b_height + 0.02, line=dict(color=custom_font_color, width=2))
                fig.add_shape(type="rect", xref="paper", yref="paper", x0=x_base, y0=y_bar_a, x1=x_base + w_a, y1=y_bar_a + b_height, fillcolor=color_a, line=dict(width=0))
                fig.add_shape(type="rect", xref="paper", yref="paper", x0=x_base, y0=y_bar_b, x1=x_base + w_b, y1=y_bar_b + b_height, fillcolor=color_b, line=dict(width=0))
                title_annotations.append(dict(xref="paper", yref="paper", x=x_base - 0.015, y=y_center_a, text=f"<b>{yoy_a}</b>", showarrow=False, xanchor="right", yanchor="middle", font=dict(color=custom_font_color, size=15 * font_size_mult)))
                title_annotations.append(dict(xref="paper", yref="paper", x=x_base - 0.015, y=y_center_b, text=f"<b>{yoy_b}</b>", showarrow=False, xanchor="right", yanchor="middle", font=dict(color=custom_font_color, size=15 * font_size_mult)))

                def format_yoy(x):
                    try:
                        v = float(x)
                        return f"{int(v):,}".replace(",", ".") if v.is_integer() else f"{v:,.2f}".rstrip("0").rstrip(".").replace(",", "X").replace(".", ",").replace("X", ".")
                    except:
                        return str(x)

                text_a_x, text_b_x = x_base + w_a + 0.015, x_base + w_b + 0.015
                val_text_a = f"<b><span style='font-size:{24*font_size_mult}px'>{format_yoy(sum_a)}</span></b> <span style='font-size:{16*font_size_mult}px; color:#A0A0A0'>{y_axis_title}</span>"
                val_text_b = f"<b><span style='font-size:{24*font_size_mult}px'>{format_yoy(sum_b)}</span></b> <span style='font-size:{16*font_size_mult}px; color:#A0A0A0'>{y_axis_title}</span>"
                title_annotations.append(dict(xref="paper", yref="paper", x=text_a_x, y=y_center_a, text=val_text_a, showarrow=False, xanchor="left", yanchor="middle", font=dict(color=custom_font_color)))
                title_annotations.append(dict(xref="paper", yref="paper", x=text_b_x, y=y_center_b, text=val_text_b, showarrow=False, xanchor="left", yanchor="middle", font=dict(color=custom_font_color)))

                x_box_center, y_box_center = x_base + max_width + 0.18, y_center_b
                fig.add_shape(type="line", xref="paper", yref="paper", x0=text_b_x + 0.10, y0=y_center_b, x1=x_box_center - 0.07, y1=y_center_b, line=dict(color=custom_font_color, width=1.5, dash='dot'))
                fig.add_shape(type="line", xref="paper", yref="paper", x0=text_a_x + 0.10, y0=y_center_a, x1=x_box_center, y1=y_center_a, line=dict(color=custom_font_color, width=1.5, dash='dot'))
                fig.add_shape(type="line", xref="paper", yref="paper", x0=x_box_center, y0=y_center_a, x1=x_box_center, y1=y_box_center + 0.05, line=dict(color=custom_font_color, width=1.5, dash='dot'))
                bg_badge = "rgba(240,240,245,0.95)"
                badge_color = SUCCESS_GREEN if yoy_pct >= 0 else WARNING_RED
                sign = "+" if yoy_pct > 0 else ""
                title_annotations.append(dict(xref="paper", yref="paper", x=x_box_center, y=y_box_center, text=f"<span style='font-size:{14*font_size_mult}px; color:#A0A0A0'><i>YoY:</i></span><br><b><span style='color:{badge_color}; font-size:{26 * font_size_mult}px;'>{sign}{yoy_pct:,.2f}%</span></b>".replace(",", "X").replace(".", ",").replace("X", "."), showarrow=False, xanchor="center", yanchor="middle", font=dict(color=custom_font_color, size=16 * font_size_mult), bgcolor=bg_badge, bordercolor=badge_color, borderwidth=1.5, borderpad=8))
                title_annotations.append(dict(xref="paper", yref="paper", x=x_base + 0.10, y=1.28, text=f"<b>Akumulasi {y_axis_title} Bulanan</b>", showarrow=False, xanchor="center", yanchor="bottom", font=dict(color=custom_font_color, size=18 * font_size_mult, family="Inter")))

        fig.update_layout(height=650, plot_bgcolor=bg_chart_color, paper_bgcolor=bg_chart_color, font=dict(color=custom_font_color, family="Inter"), title="", annotations=title_annotations, margin=dict(l=20, r=20, t=180, b=120), hovermode="x unified", hoverlabel=dict(bgcolor=HOVER_BG, font_size=16, font_family="Inter", font_color=HOVER_FONT, bordercolor=custom_colors[0]), legend=dict(title="", orientation="h", yanchor="top", y=-0.18, xanchor="center", x=0.5, font=dict(size=18 * font_size_mult, weight="bold", color=custom_font_color)))
        fig.update_xaxes(title_text="", showgrid=False, tickfont=dict(size=18 * font_size_mult, weight='bold', color=custom_font_color), range=[-0.5, len(plot_df) - 0.5])
        fig.update_yaxes(title_text=y_axis_title, title_font=dict(size=20 * font_size_mult, weight='bold', color=custom_font_color, family="Inter"), showgrid=show_grid, gridwidth=1, gridcolor=custom_grid_color, linecolor=custom_grid_color, range=[0, ceiling_y], showticklabels=False)

        c_kiri, c_tengah, c_kanan = st.columns([0.025, 0.95, 0.025])
        with c_tengah:
            st.plotly_chart(fig, use_container_width=True, config={'displaylogo': False, 'modeBarButtonsToRemove': ['select2d', 'lasso2d']})
            render_download_buttons(fig, "Quick_Graph", "qg")
    except Exception:
        st.warning("Silakan isi data angka di tabel untuk memunculkan grafik.")

def show_dashboard_kinerja(df, selected_indicator):
    with st.expander(f"🛠️ Filter Data: {selected_indicator}", expanded=True):
        c1, c2, c3, c4 = st.columns(4)
        list_tahun = sorted(df['Tahun'].unique().tolist(), reverse=True)
        in_tahun = c1.selectbox("Tahun", list_tahun, key=f"c_th_{selected_indicator}")
        df_year = df[df['Tahun'] == in_tahun]
        list_bulan = df_year[['Nama_Bulan', 'Month_Num']].drop_duplicates().sort_values('Month_Num')['Nama_Bulan'].tolist() or ["Data Kosong"]
        in_bs = c2.selectbox("Mulai", list_bulan, index=0, key=f"c_bs_{selected_indicator}")
        in_be = c3.selectbox("Sampai", list_bulan, index=len(list_bulan)-1, key=f"c_be_{selected_indicator}")
        in_ulp = c4.selectbox("Unit (ULP)", sorted(df['ULP'].unique().tolist()), key=f"c_ulp_{selected_indicator}")

        st.write("")
        c_opt1, c_opt2, c_opt3, c_btn = st.columns([1, 1, 1, 2])
        with c_opt1:
            chk_t = st.checkbox("Target", value=True, key=f"c_t_{selected_indicator}")
        with c_opt2:
            chk_r = st.checkbox("Realisasi", value=True, key=f"c_r_{selected_indicator}")
        with c_opt3:
            chk_p = st.checkbox("Persen", value=True, key=f"c_p_{selected_indicator}")
        with c_btn:
            if st.button("➕ Tambah Data", type="primary", use_container_width=True, key=f"c_btn_{selected_indicator}"):
                new_row = {"Label": f"{in_ulp} {in_tahun}", "Tahun": in_tahun, "Bulan_Awal": in_bs, "Bulan_Akhir": in_be, "ULP": in_ulp, "Indikator": selected_indicator, "T": chk_t, "R": chk_r, "%": chk_p}
                st.session_state.comparison_data = pd.concat([st.session_state.comparison_data, pd.DataFrame([new_row])], ignore_index=True)
                st.session_state.comparison_data = st.session_state.comparison_data.sort_values(by=['Tahun'], ascending=[False])
                st.rerun()

        st.markdown("""<div style='display: flex; align-items: center; margin-bottom: 10px;'><h5 style='margin: 0;'>🗑️ Kelola Filter</h5><div class='info-tooltip' style='transform: translateY(-3px);'>ℹ️<span class='tooltip-text'><b>💡 Panduan Kelola Filter:</b><br>Tabel ini menyimpan daftar grafik yang Anda tampilkan di layar.<br><br>• <b>Hapus Grafik:</b> Centang kotak kosong di paling kiri baris data, lalu tekan tombol <b>Delete</b> di keyboard.<br>• <b>Edit Filter:</b> Klik ganda (double click) pada teks di dalam tabel jika ingin mengubah isinya.</span></div></div>""", unsafe_allow_html=True)
        edited = st.data_editor(st.session_state.comparison_data, num_rows="dynamic", hide_index=True, key=f"ed_col_{selected_indicator}", use_container_width=True)
        if not edited.equals(st.session_state.comparison_data): 
            st.session_state.comparison_data = edited
            st.rerun()

    chart_df = st.session_state.comparison_data[st.session_state.comparison_data['Indikator'] == selected_indicator].copy() if not st.session_state.comparison_data.empty else pd.DataFrame()
    card_placeholder = st.empty()
    det_tercapai, det_belum = [], []

    if not chart_df.empty:
        num_rows_table = sum(row['T'] + row['R'] + row['%'] for _, row in chart_df.iterrows())
        tinggi_header, tinggi_per_baris, tinggi_grafik, jarak_antar_lantai = 80, 45, 450, 80
        tinggi_tabel_total = tinggi_header + (num_rows_table * tinggi_per_baris)
        dynamic_height = tinggi_grafik + tinggi_tabel_total + jarak_antar_lantai

        fig = make_subplots(rows=2, cols=1, shared_xaxes=False, vertical_spacing=jarak_antar_lantai/dynamic_height, specs=[[{"secondary_y": True}], [{"type": "table"}]], row_heights=[tinggi_grafik/dynamic_height, tinggi_tabel_total/dynamic_height])
        month_lookup = df[['Nama_Bulan', 'Month_Num']].drop_duplicates().set_index('Nama_Bulan')['Month_Num']
        matrix_rows, item_colors, m_cols = [], [], ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']

        max_y_val = 0
        for index, row in chart_df.iterrows():
            try:
                s_num, e_num = month_lookup.get(row['Bulan_Awal'], 0), month_lookup.get(row['Bulan_Akhir'], 99)
                sel_nums = list(range(min(s_num, e_num), max(s_num, e_num) + 1))
            except:
                sel_nums = []
            d_val = df[(df['Tahun'] == row['Tahun']) & (df['Month_Num'].isin(sel_nums)) & (df['ULP'] == row['ULP'])].copy()
            if row['T'] and row['Indikator'] + " (Target)" in d_val.columns:
                max_y_val = max(max_y_val, pd.to_numeric(d_val[row['Indikator'] + " (Target)"], errors='coerce').max())
            if row['R'] and row['Indikator'] + " (Realisasi)" in d_val.columns:
                max_y_val = max(max_y_val, pd.to_numeric(d_val[row['Indikator'] + " (Realisasi)"], errors='coerce').max())

        ceiling_y = max_y_val * 1.15 if max_y_val > 0 else 100

        for index, row in chart_df.iterrows():
            scheme = color_palettes[index % len(color_palettes)]
            try:
                s_num, e_num = month_lookup.get(row['Bulan_Awal'], 0), month_lookup.get(row['Bulan_Akhir'], 99)
                sel_nums = list(range(min(s_num, e_num), max(s_num, e_num) + 1))
            except:
                sel_nums = []
            d_val = df[(df['Tahun'] == row['Tahun']) & (df['Month_Num'].isin(sel_nums)) & (df['ULP'] == row['ULP'])].copy().sort_values('Month_Num')
            if d_val.empty:
                continue

            t_c, r_c, p_c = row['Indikator'] + " (Target)", row['Indikator'] + " (Realisasi)", row['Indikator'] + " (%)"
            def gv(m, c):
                return d_val[d_val['Month_Num'] == m][c].values[0] if not d_val[d_val['Month_Num'] == m].empty and c in d_val.columns else 0

            t_raw = d_val[t_c].fillna(0).tolist() if t_c in d_val.columns else [0] * len(d_val)
            r_raw = d_val[r_c].fillna(0).tolist() if r_c in d_val.columns else [0] * len(d_val)

            for m, tv, rv in zip(d_val['Nama_Bulan'], t_raw, r_raw):
                v_t, v_r = float(tv) if pd.notna(tv) else 0.0, float(rv) if pd.notna(rv) else 0.0
                item_data = {"label": f"{row['Label']} - {m}", "t": format_indo(tv), "r": format_indo(rv)}
                if v_t > 0 or v_r > 0:
                    if v_r >= v_t:
                        det_tercapai.append(item_data)
                    else:
                        det_belum.append(item_data)

            if row['T'] and t_c in d_val.columns:
                c_data = [format_indo(v) for v in d_val[t_c]]
                marker_line_colors = []
                for tv, rv in zip(t_raw, r_raw):
                    v_t, v_r = float(tv) if pd.notna(tv) else 0.0, float(rv) if pd.notna(rv) else 0.0
                    if v_r < v_t and v_t > 0:
                        marker_line_colors.append(WARNING_RED)
                    else:
                        marker_line_colors.append('#FFFFFF')

                fig.add_trace(go.Scatter(x=d_val['Nama_Bulan'], y=d_val[t_c], name=f"Target: {row['Label']}      ", mode='lines+markers', line=dict(color=scheme["T"], width=2, dash='dash'), marker=dict(size=8, symbol='circle', line=dict(color=marker_line_colors, width=2)), customdata=c_data, hovertemplate=f"Target: %{{customdata}}<extra></extra>"), row=1, col=1, secondary_y=False)
                vals = [gv(i, t_c) for i in range(1, 13)]
                matrix_rows.append({'Item': f"■ Target: {row['Label']}", **dict(zip(m_cols, [format_indo(x) for x in vals])), 'TOTAL': format_indo(sum(vals))})
                item_colors.append(scheme["T"])

            if row['R'] and r_c in d_val.columns:
                c_data = [format_indo(v) for v in d_val[r_c]]
                fig.add_trace(go.Bar(x=d_val['Nama_Bulan'], y=d_val[r_c], name=f"Realisasi: {row['Label']}      ", marker_color=scheme["R"], customdata=c_data, hovertemplate=f"Realisasi: %{{customdata}}<extra></extra>", offsetgroup=f"{index}", width=0.2), row=1, col=1, secondary_y=False)
                vals = [gv(i, r_c) for i in range(1, 13)]
                matrix_rows.append({'Item': f"■ Realisasi: {row['Label']}", **dict(zip(m_cols, [format_indo(x) for x in vals])), 'TOTAL': format_indo(sum(vals))})
                item_colors.append(scheme["R"])

            if row['%'] and p_c in d_val.columns:
                c_data = [format_indo(v, True) for v in d_val[p_c]]
                fig.add_trace(go.Scatter(x=d_val['Nama_Bulan'], y=d_val[p_c], name=f"Persen: {row['Label']}      ", mode='lines+markers', line=dict(color=FIXED_PERCENT_COLOR, width=3), marker=dict(size=8, color=FIXED_PERCENT_COLOR), customdata=c_data, hovertemplate=f"Persen: %{{customdata}}%<extra></extra>"), row=1, col=1, secondary_y=True)
                vals = [gv(i, p_c) for i in range(1, 13)]
                s_t = sum([gv(i, t_c) for i in range(1, 13)])
                s_r = sum([gv(i, r_c) for i in range(1, 13)])
                tot = (s_r / s_t * 100) if s_t > 0 else 0
                matrix_rows.append({'Item': f"■ Persen: {row['Label']}", **dict(zip(m_cols, [format_indo(x, True) for x in vals])), 'TOTAL': format_indo(tot, True)})
                item_colors.append(FIXED_PERCENT_COLOR)

        render_summary_cards(card_placeholder, det_tercapai, det_belum)

        headers = ['Item'] + m_cols + ['TOTAL']
        if matrix_rows:
            table_cols = [[r[h] for r in matrix_rows] for h in headers]
            fig.add_trace(go.Table(columnwidth=[22] + [12]*12 + [15], header=dict(values=[f"<b>{h}</b>" for h in headers], fill_color=TABLE_HEADER_BG, align='center', font=dict(color=FONT_COLOR, size=12, family="Inter"), line_color=GRID_COLOR), cells=dict(values=table_cols, fill_color=TABLE_CELL_BG, align=['left'] + ['center']*13, font=dict(color=[item_colors]*14, size=11, family="Inter"), height=tinggi_per_baris, line_color=GRID_COLOR)), row=2, col=1)

        fig.update_layout(height=dynamic_height, margin=dict(l=10, r=10, t=80, b=20), legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5, font=dict(size=14, weight='bold', color=FONT_COLOR)), hovermode="x unified", hoverlabel=dict(bgcolor=HOVER_BG, font_size=15, font_family="Inter", font_color=HOVER_FONT, bordercolor=color_palettes[0]["T"]), plot_bgcolor=BG_CHART, paper_bgcolor=BG_PAPER, barmode='group', bargap=0.3, bargroupgap=0.1)
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor=GRID_COLOR, showline=True, linewidth=1, linecolor=GRID_COLOR, tickfont=dict(family="Inter", weight="bold", color=FONT_COLOR, size=13), row=1, col=1)
        fig.update_yaxes(title_text="Target", secondary_y=False, showgrid=True, gridwidth=1, gridcolor=GRID_COLOR, range=[0, ceiling_y], tickfont=dict(family="Inter", weight="bold", color=color_palettes[0]["T"], size=13), title_font=dict(family="Inter", weight="bold", color=color_palettes[0]["T"], size=15), row=1, col=1)
        fig.update_yaxes(range=[0, 130], secondary_y=True, visible=False, row=1, col=1)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True, 'displaylogo': False, 'toImageButtonOptions': {'format': 'png', 'filename': 'Grafik_Kinerja_PLN', 'height': dynamic_height, 'width': 1600, 'scale': 2}})
    else:
        st.info("Belum ada data. Tambahkan melalui panel di atas.")

def show_dashboard_cc(df, selected_indicator):
    with st.expander(f"🛠️ Filter Data (Column Vs Column): {selected_indicator}", expanded=True):
        c1, c2, c3, c4 = st.columns(4)
        list_tahun = sorted(df['Tahun'].unique().tolist(), reverse=True)
        in_tahun = c1.selectbox("Tahun", list_tahun, key=f"cc_th_{selected_indicator}")
        df_year = df[df['Tahun'] == in_tahun]
        list_bulan = df_year[['Nama_Bulan', 'Month_Num']].drop_duplicates().sort_values('Month_Num')['Nama_Bulan'].tolist() or ["Data Kosong"]
        in_bs = c2.selectbox("Mulai", list_bulan, index=0, key=f"cc_bs_{selected_indicator}")
        in_be = c3.selectbox("Sampai", list_bulan, index=len(list_bulan)-1, key=f"cc_be_{selected_indicator}")
        in_ulp = c4.selectbox("Unit (ULP)", sorted(df['ULP'].unique().tolist()), key=f"cc_ulp_{selected_indicator}")

        st.write("")
        c_opt1, c_opt2, c_opt3, c_btn = st.columns([1, 1, 1, 2])
        with c_opt1:
            chk_t = st.checkbox("Target", value=True, key=f"cc_t_{selected_indicator}")
        with c_opt2:
            chk_r = st.checkbox("Realisasi", value=True, key=f"cc_r_{selected_indicator}")
        with c_opt3:
            chk_p = st.checkbox("Persen", value=True, key=f"cc_p_{selected_indicator}")
        with c_btn:
            if st.button("➕ Tambah Data", type="primary", use_container_width=True, key=f"cc_btn_{selected_indicator}"):
                new_row = {"Label": f"{in_ulp} {in_tahun}", "Tahun": in_tahun, "Bulan_Awal": in_bs, "Bulan_Akhir": in_be, "ULP": in_ulp, "Indikator": selected_indicator, "T": chk_t, "R": chk_r, "%": chk_p}
                st.session_state.cc_data = pd.concat([st.session_state.cc_data, pd.DataFrame([new_row])], ignore_index=True)
                st.session_state.cc_data = st.session_state.cc_data.sort_values(by=['Tahun'], ascending=[False])
                st.rerun()

        st.markdown("""<div style='display: flex; align-items: center; margin-bottom: 10px;'><h5 style='margin: 0;'>🗑️ Kelola Filter (Column Vs Column)</h5><div class='info-tooltip' style='transform: translateY(-3px);'>ℹ️<span class='tooltip-text'><b>💡 Panduan Kelola Filter:</b><br>Tabel ini menyimpan daftar grafik yang Anda tampilkan di layar.<br><br>• <b>Hapus Grafik:</b> Centang kotak kosong di paling kiri baris data, lalu tekan tombol <b>Delete</b> di keyboard.<br>• <b>Edit Filter:</b> Klik ganda (double click) pada teks di dalam tabel jika ingin mengubah isinya.</span></div></div>""", unsafe_allow_html=True)
        edited = st.data_editor(st.session_state.cc_data, num_rows="dynamic", hide_index=True, key=f"ed_cc_{selected_indicator}", use_container_width=True)
        if not edited.equals(st.session_state.cc_data): 
            st.session_state.cc_data = edited
            st.rerun()

    chart_df = st.session_state.cc_data[st.session_state.cc_data['Indikator'] == selected_indicator].copy() if not st.session_state.cc_data.empty else pd.DataFrame()
    card_placeholder = st.empty()
    det_tercapai, det_belum = [], []

    if not chart_df.empty:
        num_rows_table = sum(row['T'] + row['R'] + row['%'] for _, row in chart_df.iterrows())
        tinggi_header, tinggi_per_baris, tinggi_grafik, jarak_antar_lantai = 80, 45, 450, 80
        tinggi_tabel_total = tinggi_header + (num_rows_table * tinggi_per_baris)
        dynamic_height = tinggi_grafik + tinggi_tabel_total + jarak_antar_lantai

        fig = make_subplots(rows=2, cols=1, shared_xaxes=False, vertical_spacing=jarak_antar_lantai/dynamic_height, specs=[[{"secondary_y": True}], [{"type": "table"}]], row_heights=[tinggi_grafik/dynamic_height, tinggi_tabel_total/dynamic_height])
        month_lookup = df[['Nama_Bulan', 'Month_Num']].drop_duplicates().set_index('Nama_Bulan')['Month_Num']
        matrix_rows, item_colors, m_cols = [], [], ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']

        max_y_val = 0
        for index, row in chart_df.iterrows():
            try:
                s_num, e_num = month_lookup.get(row['Bulan_Awal'], 0), month_lookup.get(row['Bulan_Akhir'], 99)
                sel_nums = list(range(min(s_num, e_num), max(s_num, e_num) + 1))
            except:
                sel_nums = []
            d_val = df[(df['Tahun'] == row['Tahun']) & (df['Month_Num'].isin(sel_nums)) & (df['ULP'] == row['ULP'])].copy()
            if row['T'] and row['Indikator'] + " (Target)" in d_val.columns:
                max_y_val = max(max_y_val, pd.to_numeric(d_val[row['Indikator'] + " (Target)"], errors='coerce').max())
            if row['R'] and row['Indikator'] + " (Realisasi)" in d_val.columns:
                max_y_val = max(max_y_val, pd.to_numeric(d_val[row['Indikator'] + " (Realisasi)"], errors='coerce').max())
        ceiling_y = max_y_val * 1.15 if max_y_val > 0 else 100

        for index, row in chart_df.iterrows():
            scheme = color_palettes[index % len(color_palettes)]
            try:
                s_num, e_num = month_lookup.get(row['Bulan_Awal'], 0), month_lookup.get(row['Bulan_Akhir'], 99)
                sel_nums = list(range(min(s_num, e_num), max(s_num, e_num) + 1))
            except:
                sel_nums = []
            d_val = df[(df['Tahun'] == row['Tahun']) & (df['Month_Num'].isin(sel_nums)) & (df['ULP'] == row['ULP'])].copy().sort_values('Month_Num')
            if d_val.empty:
                continue

            t_c, r_c, p_c = row['Indikator'] + " (Target)", row['Indikator'] + " (Realisasi)", row['Indikator'] + " (%)"
            def gv(m, c):
                return d_val[d_val['Month_Num'] == m][c].values[0] if not d_val[d_val['Month_Num'] == m].empty and c in d_val.columns else 0

            t_raw = d_val[t_c].fillna(0).tolist() if t_c in d_val.columns else [0] * len(d_val)
            r_raw = d_val[r_c].fillna(0).tolist() if r_c in d_val.columns else [0] * len(d_val)

            for m, tv, rv in zip(d_val['Nama_Bulan'], t_raw, r_raw):
                v_t, v_r = float(tv) if pd.notna(tv) else 0.0, float(rv) if pd.notna(rv) else 0.0
                item_data = {"label": f"{row['Label']} - {m}", "t": format_indo(tv), "r": format_indo(rv)}
                if v_t > 0 or v_r > 0:
                    if v_r >= v_t:
                        det_tercapai.append(item_data)
                    else:
                        det_belum.append(item_data)

            if row['T'] and t_c in d_val.columns:
                c_data_T = [format_indo(v) for v in d_val[t_c]]
                fig.add_trace(go.Bar(
                    x=d_val['Nama_Bulan'], y=d_val[t_c],
                    name=f"Target: {row['Label']}      ",
                    marker_color=scheme["T"],
                    customdata=c_data_T,
                    hovertemplate=f"Target: %{{customdata}}<extra></extra>",
                    offsetgroup=f"T_{index}", width=0.2
                ), row=1, col=1, secondary_y=False)
                vals = [gv(i, t_c) for i in range(1, 13)]
                matrix_rows.append({'Item': f"■ Target: {row['Label']}", **dict(zip(m_cols, [format_indo(x) for x in vals])), 'TOTAL': format_indo(sum(vals))})
                item_colors.append(scheme["T"])

            if row['R'] and r_c in d_val.columns:
                c_data_R = [format_indo(v) for v in d_val[r_c]]
                fig.add_trace(go.Bar(
                    x=d_val['Nama_Bulan'], y=d_val[r_c],
                    name=f"Realisasi: {row['Label']}      ",
                    marker_color=scheme["R"],
                    offsetgroup=f"R_{index}",
                    customdata=c_data_R,
                    hovertemplate=f"Realisasi: %{{customdata}}<extra></extra>", width=0.2
                ), row=1, col=1, secondary_y=False)
                vals = [gv(i, r_c) for i in range(1, 13)]
                matrix_rows.append({'Item': f"■ Realisasi: {row['Label']}", **dict(zip(m_cols, [format_indo(x) for x in vals])), 'TOTAL': format_indo(sum(vals))})
                item_colors.append(scheme["R"])

            if row['%'] and p_c in d_val.columns:
                c_data = [format_indo(v, True) for v in d_val[p_c]]
                fig.add_trace(go.Scatter(x=d_val['Nama_Bulan'], y=d_val[p_c], name=f"Persen: {row['Label']}      ", mode='lines+markers', line=dict(color=FIXED_PERCENT_COLOR, width=3), marker=dict(size=8, color=FIXED_PERCENT_COLOR), customdata=c_data, hovertemplate=f"Persen: %{{customdata}}%<extra></extra>"), row=1, col=1, secondary_y=True)
                vals = [gv(i, p_c) for i in range(1, 13)]
                s_t = sum([gv(i, t_c) for i in range(1, 13)])
                s_r = sum([gv(i, r_c) for i in range(1, 13)])
                tot = (s_r / s_t * 100) if s_t > 0 else 0
                matrix_rows.append({'Item': f"■ Persen: {row['Label']}", **dict(zip(m_cols, [format_indo(x, True) for x in vals])), 'TOTAL': format_indo(tot, True)})
                item_colors.append(FIXED_PERCENT_COLOR)

        render_summary_cards(card_placeholder, det_tercapai, det_belum)

        headers = ['Item'] + m_cols + ['TOTAL']
        if matrix_rows:
            table_cols = [[r[h] for r in matrix_rows] for h in headers]
            fig.add_trace(
                go.Table(
                    columnwidth=[22] + [12]*12 + [15],
                    header=dict(values=[f"<b>{h}</b>" for h in headers], fill_color=TABLE_HEADER_BG, align='center', font=dict(color=FONT_COLOR, size=12, family="Inter"), line_color=GRID_COLOR),
                    cells=dict(values=table_cols, fill_color=TABLE_CELL_BG, align=['left'] + ['center']*13, font=dict(color=[item_colors]*14, size=11, family="Inter"), height=tinggi_per_baris, line_color=GRID_COLOR)
                ), row=2, col=1)

        fig.update_layout(height=dynamic_height, margin=dict(l=10, r=10, t=80, b=20), legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5, font=dict(size=14, weight='bold', color=FONT_COLOR)), hovermode="x unified", hoverlabel=dict(bgcolor=HOVER_BG, font_size=15, font_family="Inter", font_color=HOVER_FONT, bordercolor=color_palettes[0]["T"]), plot_bgcolor=BG_CHART, paper_bgcolor=BG_PAPER, barmode='group', bargap=0.35, bargroupgap=0.1)
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor=GRID_COLOR, showline=True, linewidth=1, linecolor=GRID_COLOR, tickfont=dict(family="Inter", weight="bold", color=FONT_COLOR, size=13), row=1, col=1)
        fig.update_yaxes(title_text="Target", secondary_y=False, showgrid=True, gridwidth=1, gridcolor=GRID_COLOR, range=[0, ceiling_y], tickfont=dict(family="Inter", weight="bold", color=color_palettes[0]["T"], size=13), title_font=dict(family="Inter", weight="bold", color=color_palettes[0]["T"], size=15), row=1, col=1)
        fig.update_yaxes(title_text="Persentase (%)", secondary_y=True, showgrid=False, showticklabels=True, tickfont=dict(family="Inter", weight="bold", color=FIXED_PERCENT_COLOR, size=13), title_font=dict(family="Inter", weight="bold", color=FIXED_PERCENT_COLOR, size=15), row=1, col=1)

        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True, 'displaylogo': False, 'toImageButtonOptions': {'format': 'png', 'filename': 'Grafik_Tren_PLN', 'height': dynamic_height, 'width': 1600, 'scale': 2}})
        
    else:
        st.info("Belum ada data. Tambahkan melalui panel di atas.")

def show_analisis_tren(df, selected_indicator):
    with st.expander(f"🛠️ Filter Garis: {selected_indicator}", expanded=True):
        c1, c2, c3, c4 = st.columns(4)
        available_years = sorted(df['Tahun'].unique().tolist(), reverse=True) if not df.empty else ["Data Kosong"]
        in_tahun = c1.selectbox("Tahun", available_years, key=f"l_th_{selected_indicator}")
        df_year = df[df['Tahun'] == in_tahun]
        list_bulan = df_year[['Nama_Bulan', 'Month_Num']].drop_duplicates().sort_values('Month_Num')['Nama_Bulan'].tolist() or ["Data Kosong"]
        in_bs = c2.selectbox("Mulai", list_bulan, index=0, key=f"l_bs_{selected_indicator}")
        in_be = c3.selectbox("Sampai", list_bulan, index=len(list_bulan)-1, key=f"l_be_{selected_indicator}")
        in_ulp = c4.selectbox("Unit (ULP)", sorted(df['ULP'].unique().tolist()), key=f"l_ulp_{selected_indicator}")

        st.write("")
        c_opt1, c_opt2, c_opt3, c_btn = st.columns([1, 1, 1, 2])
        with c_opt1:
            l_t = st.checkbox("Target", value=True, key=f"l_t_{selected_indicator}")
        with c_opt2:
            l_r = st.checkbox("Realisasi", value=True, key=f"l_r_{selected_indicator}")
        with c_opt3:
            l_p = st.checkbox("Persen", value=True, key=f"l_p_{selected_indicator}")
        with c_btn:
            if st.button("➕ Tambah Data", type="primary", use_container_width=True, key=f"l_btn_{selected_indicator}"):
                new_row = {"Label": f"{in_ulp} {in_tahun}", "Tahun": in_tahun, "Bulan_Awal": in_bs, "Bulan_Akhir": in_be, "ULP": in_ulp, "Indikator": selected_indicator, "T": l_t, "R": l_r, "%": l_p}
                st.session_state.line_data = pd.concat([st.session_state.line_data, pd.DataFrame([new_row])], ignore_index=True)
                st.session_state.line_data = st.session_state.line_data.sort_values(by=['Tahun'], ascending=[False])
                st.rerun()

        st.markdown("""<div style='display: flex; align-items: center; margin-bottom: 10px;'><h5 style='margin: 0;'>🗑️ Kelola Filter</h5><div class='info-tooltip' style='transform: translateY(-3px);'>ℹ️<span class='tooltip-text'><b>💡 Panduan Kelola Filter:</b><br>Tabel ini menyimpan daftar grafik yang Anda tampilkan di layar.<br><br>• <b>Hapus Grafik:</b> Centang kotak kosong di paling kiri baris data, lalu tekan tombol <b>Delete</b> di keyboard.<br>• <b>Edit Filter:</b> Klik ganda (double click) pada teks di dalam tabel jika ingin mengubah isinya.</span></div></div>""", unsafe_allow_html=True)
        edited = st.data_editor(st.session_state.line_data, num_rows="dynamic", hide_index=True, key=f"ed_line_{selected_indicator}", use_container_width=True)
        if not edited.equals(st.session_state.line_data):
            st.session_state.line_data = edited
            st.session_state.line_data = st.session_state.line_data.sort_values(by=['Tahun'], ascending=[False])
            st.rerun()

    chart_df = st.session_state.line_data[st.session_state.line_data['Indikator'] == selected_indicator].copy() if not st.session_state.line_data.empty else pd.DataFrame()
    card_placeholder = st.empty()
    det_tercapai, det_belum = [], []

    if not chart_df.empty:
        num_rows_table = sum(row['T'] + row['R'] + row['%'] for _, row in chart_df.iterrows())
        tinggi_header, tinggi_per_baris, tinggi_grafik, jarak_antar_lantai = 80, 45, 500, 80
        tinggi_tabel_total = tinggi_header + (num_rows_table * tinggi_per_baris)
        dynamic_height = tinggi_grafik + tinggi_tabel_total + jarak_antar_lantai

        fig = make_subplots(rows=2, cols=1, shared_xaxes=False, vertical_spacing=jarak_antar_lantai/dynamic_height, specs=[[{"secondary_y": True}], [{"type": "table"}]], row_heights=[tinggi_grafik/dynamic_height, tinggi_tabel_total/dynamic_height])
        month_lookup = df[['Nama_Bulan', 'Month_Num']].drop_duplicates().set_index('Nama_Bulan')['Month_Num']
        def get_short_name(name):
            n = name.upper()
            if "BEKASI KOTA" in n: return "BKT"
            elif "BABELAN" in n: return "BBL"
            elif "MUSTIKAJAYA" in n: return "MTJ"
            elif "MEDAN SATRIA" in n: return "MDS"
            elif "BANTARGEBANG" in n: return "BTG"
            elif "JATIWARINGIN" in n: return "JTW"
            elif "PRIMA" in n: return "PRM"
            elif "CIKARANG" in n: return "CKR"
            return n[:3]

        matrix_rows, item_colors, m_cols = [], [], ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']

        max_y_val = 0
        for index, row in chart_df.iterrows():
            try:
                s_num, e_num = month_lookup.get(row['Bulan_Awal'], 0), month_lookup.get(row['Bulan_Akhir'], 99)
                sel_nums = list(range(min(s_num, e_num), max(s_num, e_num) + 1))
            except:
                sel_nums = []
            d_val = df[(df['Tahun'] == row['Tahun']) & (df['Month_Num'].isin(sel_nums)) & (df['ULP'] == row['ULP'])].copy()
            if row['T'] and row['Indikator'] + " (Target)" in d_val.columns:
                max_y_val = max(max_y_val, pd.to_numeric(d_val[row['Indikator'] + " (Target)"], errors='coerce').max())
            if row['R'] and row['Indikator'] + " (Realisasi)" in d_val.columns:
                max_y_val = max(max_y_val, pd.to_numeric(d_val[row['Indikator'] + " (Realisasi)"], errors='coerce').max())

        ceiling_y = max_y_val * 1.15 if max_y_val > 0 else 100

        for index, row in chart_df.iterrows():
            scheme = color_palettes[index % len(color_palettes)]
            try:
                s_num, e_num = month_lookup.get(row['Bulan_Awal'], 0), month_lookup.get(row['Bulan_Akhir'], 99)
                sel_nums = list(range(min(s_num, e_num), max(s_num, e_num) + 1))
            except:
                sel_nums = []
            d_val = df[(df['Tahun'] == row['Tahun']) & (df['Month_Num'].isin(sel_nums)) & (df['ULP'] == row['ULP'])].copy().sort_values('Month_Num')
            if d_val.empty:
                continue

            badge = get_short_name(row['ULP'])
            x_Lt, x_Lr, x_R = -0.01 - (index * 0.08), -0.05 - (index * 0.08), 1.01 + (index * 0.08)
            t_c, r_c, p_c = row['Indikator'] + " (Target)", row['Indikator'] + " (Realisasi)", row['Indikator'] + " (%)"
            def gv(m, c):
                return d_val[d_val['Month_Num'] == m][c].values[0] if not d_val[d_val['Month_Num'] == m].empty and c in d_val.columns else 0

            t_raw = d_val[t_c].fillna(0).tolist() if t_c in d_val.columns else [0] * len(d_val)
            r_raw = d_val[r_c].fillna(0).tolist() if r_c in d_val.columns else [0] * len(d_val)

            for m, tv, rv in zip(d_val['Nama_Bulan'], t_raw, r_raw):
                v_t, v_r = float(tv) if pd.notna(tv) else 0.0, float(rv) if pd.notna(rv) else 0.0
                item_data = {"label": f"{row['Label']} - {m}", "t": format_indo(tv), "r": format_indo(rv)}
                if v_t > 0 or v_r > 0:
                    if v_r >= v_t:
                        det_tercapai.append(item_data)
                    else:
                        det_belum.append(item_data)

            if row['T'] and t_c in d_val.columns:
                y0 = d_val.iloc[0][t_c]
                marker_line_colors = []
                for tv, rv in zip(t_raw, r_raw):
                    v_t, v_r = float(tv) if pd.notna(tv) else 0.0, float(rv) if pd.notna(rv) else 0.0
                    if v_r < v_t and v_t > 0:
                        marker_line_colors.append(WARNING_RED)
                    else:
                        marker_line_colors.append('#FFFFFF')

                fig.add_trace(go.Scatter(x=d_val['Nama_Bulan'], y=d_val[t_c], name=f"Target: {row['Label']}      ", mode='lines+markers+text', text=[f"<b>{format_indo(v)}</b>" for v in d_val[t_c]], textposition="top center", textfont=dict(family="Inter", size=12, color=scheme["T"], weight="bold"), line=dict(color=scheme["T"], width=1.5, dash='dash'), marker=dict(size=8, symbol='circle', line=dict(color=marker_line_colors, width=2)), hovertemplate="Target: %{y:,.2f}"), row=1, col=1, secondary_y=False)

                if pd.notna(y0):
                    fig.add_annotation(x=d_val['Nama_Bulan'].values[0], y=y0, text=badge, showarrow=False, bgcolor=scheme["T"], font=dict(color="#161A22", size=10, weight="bold"), xanchor="right", xshift=-25 - (index * 70), row=1, col=1)

                vals = [gv(i, t_c) for i in range(1, 13)]
                matrix_rows.append({'Item': f"■ Target: {row['Label']}", **dict(zip(m_cols, [format_indo(x) for x in vals])), 'TOTAL': format_indo(sum(vals))})
                item_colors.append(scheme["T"])

            if row['R'] and r_c in d_val.columns:
                y0 = d_val.iloc[0][r_c]
                fig.add_trace(go.Scatter(x=d_val['Nama_Bulan'], y=d_val[r_c], name=f"Realisasi: {row['Label']}      ", mode='lines+markers+text', text=[f"<b>{format_indo(v)}</b>" for v in d_val[r_c]], textposition="bottom center", textfont=dict(family="Inter", size=12, color=scheme["R"], weight="bold"), line=dict(color=scheme["R"], width=3, shape='spline', smoothing=0.8), marker=dict(size=8), hovertemplate="Realisasi: %{y:,.2f}"), row=1, col=1, secondary_y=False)

                if pd.notna(y0):
                    fig.add_annotation(x=d_val['Nama_Bulan'].values[0], y=y0, text=badge, showarrow=False, bgcolor=scheme["R"], font=dict(color="#161A22", size=10, weight="bold"), xanchor="right", xshift=-60 - (index * 70), row=1, col=1)

                vals = [gv(i, r_c) for i in range(1, 13)]
                matrix_rows.append({'Item': f"■ Realisasi: {row['Label']}", **dict(zip(m_cols, [format_indo(x) for x in vals])), 'TOTAL': format_indo(sum(vals))})
                item_colors.append(scheme["R"])

            if row['%'] and p_c in d_val.columns:
                y_last = d_val[p_c].values[-1]
                fig.add_trace(go.Scatter(x=d_val['Nama_Bulan'], y=d_val[p_c], name=f"Persen: {row['Label']}      ", mode='lines+markers+text', text=[f"<b>{format_indo(v, True)}</b>" for v in d_val[p_c]], textposition="top center", textfont=dict(family="Inter", size=12, color=FIXED_PERCENT_COLOR), line=dict(color=FIXED_PERCENT_COLOR, width=3, shape='spline', smoothing=0.8), marker=dict(size=8), hovertemplate="Persen: %{y:.1f}%"), row=1, col=1, secondary_y=True)

                if pd.notna(y_last):
                    fig.add_annotation(x=d_val['Nama_Bulan'].values[-1], y=y_last, yref="y2", text=badge, showarrow=False, bgcolor=FIXED_PERCENT_COLOR, font=dict(color="#161A22", size=10, weight="bold"), xanchor="left", xshift=25 + (index * 40), row=1, col=1)

                vals = [gv(i, p_c) for i in range(1, 13)]
                s_t = sum([gv(i, t_c) for i in range(1, 13)])
                s_r = sum([gv(i, r_c) for i in range(1, 13)])
                tot = (s_r / s_t * 100) if s_t > 0 else 0
                matrix_rows.append({'Item': f"■ Persen: {row['Label']}", **dict(zip(m_cols, [format_indo(x, True) for x in vals])), 'TOTAL': format_indo(tot, True)})
                item_colors.append(FIXED_PERCENT_COLOR)

        render_summary_cards(card_placeholder, det_tercapai, det_belum)

        headers = ['Item'] + m_cols + ['TOTAL']
        if matrix_rows:
            table_cols = [[r[h] for r in matrix_rows] for h in headers]
            fig.add_trace(
                go.Table(
                    columnwidth=[22] + [12]*12 + [15],
                    header=dict(values=[f"<b>{h}</b>" for h in headers], fill_color=TABLE_HEADER_BG, align='center', font=dict(color=FONT_COLOR, size=12, family="Inter"), line_color=GRID_COLOR),
                    cells=dict(values=table_cols, fill_color=TABLE_CELL_BG, align=['left'] + ['center']*13, font=dict(color=[item_colors]*14, size=11, family="Inter"), height=tinggi_per_baris, line_color=GRID_COLOR)
                ), row=2, col=1)

        margin_left = 100 + (len(chart_df) * 70)
        margin_right = 80 + (len(chart_df) * 40)

        fig.update_layout(height=dynamic_height, margin=dict(l=10, r=10, t=80, b=20), legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5, font=dict(size=14, weight='bold', color=FONT_COLOR)), hovermode="x unified", hoverlabel=dict(bgcolor=HOVER_BG, font_size=15, font_family="Inter", font_color=HOVER_FONT, bordercolor=color_palettes[0]["T"]), plot_bgcolor=BG_CHART, paper_bgcolor=BG_PAPER)
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor=GRID_COLOR, showline=True, linewidth=1, linecolor=GRID_COLOR, tickfont=dict(family="Inter", weight="bold", color=FONT_COLOR, size=13), row=1, col=1)
        fig.update_yaxes(title_text="Target", secondary_y=False, showgrid=True, gridwidth=1, gridcolor=GRID_COLOR, range=[0, ceiling_y], tickfont=dict(family="Inter", weight="bold", color=color_palettes[0]["T"], size=13), title_font=dict(family="Inter", weight="bold", color=color_palettes[0]["T"], size=15), row=1, col=1)
        fig.update_yaxes(title_text="Persentase (%)", secondary_y=True, showgrid=False, showticklabels=True, tickfont=dict(family="Inter", weight="bold", color=FIXED_PERCENT_COLOR, size=13), title_font=dict(family="Inter", weight="bold", color=FIXED_PERCENT_COLOR, size=15), row=1, col=1)

        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True, 'displaylogo': False, 'toImageButtonOptions': {'format': 'png', 'filename': 'Grafik_Tren_PLN', 'height': dynamic_height, 'width': 1600, 'scale': 2}})
        
    else:
        st.info("Belum ada data. Tambahkan melalui panel di atas.")

# ==========================================
# 6. VIEW KHUSUS: REKAP PIUTANG, HCS, SPKLU
# ==========================================
def show_tabel_rekap_16500(df_work):
    st.markdown("### 📊 Tabel Rekap Data")
    st.caption("TOTAL PELANGGAN & RPTL AWAL = Mengambil data pelanggan dengan DAYA >= 16500.<br>PLG BLM LUNAS = Filter tambahan mencari kata 'BELUM' pada kolom STATUS.", unsafe_allow_html=True)
    if df_work.empty:
        st.warning("⚠️ Data Kosong.")
        return

    ulp_mapping = {'53711': 'Bekasi Kota', '53731': 'Medan Satria', '53732': 'Babelan', '53741': 'Bantargebang', '53742': 'Mustikajaya', '53771': 'Prima Bekasi'}

    unit_col = next((c for c in df_work.columns if str(c).upper().strip() in ['UNITUP', 'UNIT UP']), None)
    if not unit_col:
        unit_col = next((c for c in df_work.columns if 'UNIT' in str(c).upper().strip() and 'UP' in str(c).upper().strip() and 'UPI' not in str(c).upper().strip() and 'AP' not in str(c).upper().strip()), None)
    daya_col = next((c for c in df_work.columns if str(c).upper().strip() == 'DAYA'), None)
    rptl_col = next((c for c in df_work.columns if str(c).upper().strip() == 'RPPTL'), None)
    status_col = next((c for c in df_work.columns if str(c).upper().strip() == 'STATUS'), None)
    if not status_col:
        status_col = next((c for c in df_work.columns if 'STATUS' in str(c).upper().strip() and 'LALU' not in str(c).upper().strip()), None)

    if unit_col and daya_col:
        df_work['CLEAN_UNITUP'] = df_work[unit_col].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        def clean_raw_daya(val):
            try:
                if pd.isna(val): return 0.0
                if isinstance(val, (int, float)): return float(val)
                s = str(val).upper().replace('VA', '').strip().replace('.', '').replace(',', '')
                return float(s)
            except:
                return 0.0
        def clean_raw_rptl(val):
            try:
                if pd.isna(val): return 0.0
                if isinstance(val, (int, float)): return float(val)
                s = str(val).upper().replace('RP', '').strip()
                s = re.sub(r'\,0+$', '', s)
                s = re.sub(r'\.0+$', '', s)
                s = re.sub(r'[^\d\-]', '', s)
                if not s: return 0.0
                return float(s)
            except:
                return 0.0

        df_work['CLEAN_DAYA'] = df_work[daya_col].apply(clean_raw_daya)
        df_work['CLEAN_RPPTL'] = df_work[rptl_col].apply(clean_raw_rptl) if rptl_col else 0.0
        df_work['CLEAN_STATUS'] = df_work[status_col].astype(str).str.upper().str.strip() if status_col else 'UNKNOWN'

        df_total_pelanggan = df_work[df_work['CLEAN_DAYA'] >= 16500]
        df_plg_blm = df_total_pelanggan[df_total_pelanggan['CLEAN_STATUS'].str.contains('BELUM', na=False)] if status_col else pd.DataFrame(columns=df_total_pelanggan.columns)
    else:
        st.error(f"❌ Kolom tidak ditemukan! Pengecekan: UNITUP={'Ada' if unit_col else 'Gagal'}, DAYA={'Ada' if daya_col else 'Gagal'}")
        df_total_pelanggan = pd.DataFrame(columns=['CLEAN_UNITUP', 'CLEAN_RPPTL'])
        df_plg_blm = pd.DataFrame(columns=['CLEAN_UNITUP', 'CLEAN_RPPTL'])

    count_total_plg = df_total_pelanggan.groupby('CLEAN_UNITUP').size().to_dict()
    sum_rptl_awal = df_total_pelanggan.groupby('CLEAN_UNITUP')['CLEAN_RPPTL'].sum().to_dict()
    count_plg_blm = df_plg_blm.groupby('CLEAN_UNITUP').size().to_dict()
    sum_rptl_blm = df_plg_blm.groupby('CLEAN_UNITUP')['CLEAN_RPPTL'].sum().to_dict()

    rekap_data = {}
    for unit_id in ulp_mapping.keys():
        rekap_data[unit_id] = {
            "tot_plg": count_total_plg.get(unit_id, 0),
            "rptl_awal": int(sum_rptl_awal.get(unit_id, 0)),
            "plg_blm": count_plg_blm.get(unit_id, 0),
            "rptl_blm": int(sum_rptl_blm.get(unit_id, 0))
        }

    total_plg = sum(rekap_data[u]["tot_plg"] for u in ulp_mapping.keys())
    total_rptl_awal = sum(rekap_data[u]["rptl_awal"] for u in ulp_mapping.keys())
    total_plg_blm = sum(rekap_data[u]["plg_blm"] for u in ulp_mapping.keys())
    total_rptl_blm = sum(rekap_data[u]["rptl_blm"] for u in ulp_mapping.keys())

    rows_html = ""
    for unit_id in ulp_mapping.keys():
        str_tot_plg = f"{rekap_data[unit_id]['tot_plg']:,}".replace(',', '.')
        str_rptl_awal = f"{rekap_data[unit_id]['rptl_awal']:,}".replace(',', '.')
        str_plg_blm = f"{rekap_data[unit_id]['plg_blm']:,}".replace(',', '.')
        str_rptl_blm = f"{rekap_data[unit_id]['rptl_blm']:,}".replace(',', '.')
        rows_html += f"<tr><td class='col-unit'>{unit_id}</td><td>{str_tot_plg}</td><td>Rp {str_rptl_awal}</td><td>{str_plg_blm}</td><td>Rp {str_rptl_blm}</td></tr>\n"

    str_total_plg_all = f"{total_plg:,}".replace(',', '.')
    str_total_rptl_awal = f"{total_rptl_awal:,}".replace(',', '.')
    str_total_plg_blm = f"{total_plg_blm:,}".replace(',', '.')
    str_total_rptl_blm = f"{total_rptl_blm:,}".replace(',', '.')

    html_code = f"""<table class="rekap-custom">
<thead><tr><th colspan="5" class="header-main">REKAP DAYA DIATAS 16500 BELUM LUNAS &gt; TGL 20</th></tr>
<tr><th class="bg-unit">UNIT UP</th><th class="bg-totplg">TOTAL PELANGGAN</th><th class="bg-rptlawal">RPTL AWAL</th><th class="bg-plgblm">PLG BLM LUNAS</th><th class="bg-rptlblm">RPTL BLM LUNAS</th></tr></thead>
<tbody>{rows_html}<tr class="row-total"><td class="bg-unit">TOTAL</td><td class="bg-totplg">{str_total_plg_all}</td><td class="bg-rptlawal">Rp {str_total_rptl_awal}</td><td class="bg-plgblm">{str_total_plg_blm}</td><td class="bg-rptlblm">Rp {str_total_rptl_blm}</td></tr></tbody></table>"""

    st.markdown(html_code, unsafe_allow_html=True)
    st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
    col_chart1, col_chart2 = st.columns(2)

    units_list, rptl_blm_list, plg_blm_list, chart_data = [], [], [], []
    for unit_id, data in rekap_data.items():
        label = f"{unit_id} - {ulp_mapping.get(unit_id, unit_id)}"
        units_list.append(label)
        rptl_blm_list.append(data['rptl_blm'])
        plg_blm_list.append(data['plg_blm'])
        if data['rptl_blm'] > 0:
            chart_data.append({'Unit': label, 'RPTL Belum Lunas': data['rptl_blm']})

    with col_chart1:
        if chart_data:
            df_chart = pd.DataFrame(chart_data)
            fig_donut = px.pie(df_chart, values='RPTL Belum Lunas', names='Unit', hole=0.45, color_discrete_sequence=px.colors.qualitative.Set2)
            fig_donut.update_traces(textposition='inside', textinfo='percent+label', hovertemplate="<b>%{label}</b><br>RPTL Belum Lunas: Rp %{value:,.0f}<br>Porsi: %{percent}<extra></extra>", marker=dict(line=dict(color=BG_CHART, width=3)), hoverlabel=dict(bgcolor=HOVER_BG, bordercolor="#00E5FF", font_size=15, font_family="Inter", font_color=HOVER_FONT))
            fig_donut.update_layout(title=dict(text="Persentase Penyumbang Piutang", font=dict(size=22, color=FONT_COLOR, family="Inter", weight="bold"), x=0.5, y=0.95, xanchor='center', yanchor='top'), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=70, b=120, l=20, r=20), legend=dict(orientation="h", yanchor="top", y=-0.35, xanchor="center", x=0.5, font=dict(color=FONT_COLOR)), hovermode="closest")
            st.plotly_chart(fig_donut, use_container_width=True)

    with col_chart2:
        custom_plg = [f"{v:,}".replace(',', '.') for v in plg_blm_list]
        custom_rptl = [f"Rp {v:,}".replace(',', '.') for v in rptl_blm_list]
        fig_combo = make_subplots(specs=[[{"secondary_y": True}]])
        fig_combo.add_trace(go.Bar(x=units_list, y=plg_blm_list, name="Plg Belum Lunas", marker_color="#9BC2E6", text=custom_plg, textposition='auto', customdata=custom_plg, hovertemplate="<b>%{x}</b><br>Jumlah: %{customdata} Pelanggan<extra></extra>"), secondary_y=False)
        fig_combo.add_trace(go.Scatter(x=units_list, y=rptl_blm_list, name="RPTL Belum Lunas", mode="lines+markers", line=dict(color=WARNING_RED, width=4), marker=dict(size=10, color="#FFFFFF", line=dict(color=WARNING_RED, width=3)), customdata=custom_rptl, hovertemplate="<b>%{x}</b><br>Nominal: %{customdata}<extra></extra>"), secondary_y=True)
        fig_combo.update_layout(title=dict(text="Volume Pelanggan vs Nilai Rupiah", font=dict(size=22, color=FONT_COLOR, family="Inter", weight="bold"), x=0.5, y=0.95, xanchor='center', yanchor='top'), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=70, b=120, l=10, r=10), legend=dict(orientation="h", yanchor="top", y=-0.35, xanchor="center", x=0.5, font=dict(color=FONT_COLOR)), hovermode="x unified", hoverlabel=dict(bgcolor=HOVER_BG, bordercolor="#00E5FF", font_size=15, font_family="Inter", font_color=HOVER_FONT))
        fig_combo.update_xaxes(showgrid=False, tickfont=dict(color=FONT_COLOR))
        fig_combo.update_yaxes(title_text="", showgrid=True, gridcolor=GRID_COLOR, secondary_y=False, tickfont=dict(color=FONT_COLOR))
        fig_combo.update_yaxes(title_text="", showgrid=False, secondary_y=True, tickfont=dict(color=FONT_COLOR))
        st.plotly_chart(fig_combo, use_container_width=True)

def show_tabel_rekap_1juta(df_work):
    st.markdown("### 📊 Tabel Rekap Piutang >= Rp 1 Juta")
    st.caption("Menyaring seluruh pelanggan yang memiliki tagihan (RPPTL) senilai **Rp 1.000.000 atau lebih**, lalu dipisahkan berdasarkan status pembayarannya.")
    if df_work.empty:
        st.warning("⚠️ Data Kosong.")
        return

    ulp_mapping = {'53711': 'Bekasi Kota', '53731': 'Medan Satria', '53732': 'Babelan', '53741': 'Bantargebang', '53742': 'Mustikajaya', '53771': 'Prima Bekasi'}

    unit_col = next((c for c in df_work.columns if str(c).upper().strip() in ['UNITUP', 'UNIT UP']), None)
    if not unit_col:
        unit_col = next((c for c in df_work.columns if 'UNIT' in str(c).upper().strip() and 'UP' in str(c).upper().strip() and 'UPI' not in str(c).upper().strip() and 'AP' not in str(c).upper().strip()), None)
    rptl_col = next((c for c in df_work.columns if str(c).upper().strip() == 'RPPTL'), None)
    status_col = next((c for c in df_work.columns if str(c).upper().strip() == 'STATUS'), None)
    if not status_col:
        status_col = next((c for c in df_work.columns if 'STATUS' in str(c).upper().strip() and 'LALU' not in str(c).upper().strip()), None)

    if unit_col and rptl_col:
        df_work['CLEAN_UNITUP'] = df_work[unit_col].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        def clean_raw_rptl(val):
            try:
                if pd.isna(val): return 0.0
                if isinstance(val, (int, float)): return float(val)
                s = str(val).upper().replace('RP', '').strip()
                s = re.sub(r'\,0+$', '', s)
                s = re.sub(r'\.0+$', '', s)
                s = re.sub(r'[^\d\-]', '', s)
                if not s: return 0.0
                return float(s)
            except:
                return 0.0

        df_work['CLEAN_RPPTL'] = df_work[rptl_col].apply(clean_raw_rptl)
        df_work['CLEAN_STATUS'] = df_work[status_col].astype(str).str.upper().str.strip() if status_col else 'UNKNOWN'
        df_1juta = df_work[df_work['CLEAN_RPPTL'] >= 1000000]
        df_belum = df_1juta[df_1juta['CLEAN_STATUS'].str.contains('BELUM', na=False)] if status_col else pd.DataFrame(columns=df_1juta.columns)
        df_lunas = df_1juta[~df_1juta['CLEAN_STATUS'].str.contains('BELUM', na=False)] if status_col else pd.DataFrame(columns=df_1juta.columns)
    else:
        st.error(f"❌ Kolom tidak lengkap! UNITUP={'Ada' if unit_col else 'Gagal'}, RPPTL={'Ada' if rptl_col else 'Gagal'}")
        df_1juta = pd.DataFrame(columns=['CLEAN_UNITUP', 'CLEAN_RPPTL'])
        df_lunas = pd.DataFrame(columns=['CLEAN_UNITUP', 'CLEAN_RPPTL'])
        df_belum = pd.DataFrame(columns=['CLEAN_UNITUP', 'CLEAN_RPPTL'])

    lunas_plg = df_lunas.groupby('CLEAN_UNITUP').size().to_dict()
    lunas_rptl = df_lunas.groupby('CLEAN_UNITUP')['CLEAN_RPPTL'].sum().to_dict()
    belum_plg = df_belum.groupby('CLEAN_UNITUP').size().to_dict()
    belum_rptl = df_belum.groupby('CLEAN_UNITUP')['CLEAN_RPPTL'].sum().to_dict()

    rows_html = ""
    tot_lunas_plg, tot_lunas_rptl, tot_belum_plg, tot_belum_rptl = 0, 0, 0, 0
    for unit_id in ulp_mapping.keys():
        v_lunas_plg = lunas_plg.get(unit_id, 0)
        v_lunas_rptl = int(lunas_rptl.get(unit_id, 0))
        v_belum_plg = belum_plg.get(unit_id, 0)
        v_belum_rptl = int(belum_rptl.get(unit_id, 0))
        tot_lunas_plg += v_lunas_plg
        tot_lunas_rptl += v_lunas_rptl
        tot_belum_plg += v_belum_plg
        tot_belum_rptl += v_belum_rptl
        str_lp = f"{v_lunas_plg:,}".replace(',', '.')
        str_lr = f"Rp {v_lunas_rptl:,}".replace(',', '.')
        str_bp = f"{v_belum_plg:,}".replace(',', '.')
        str_br = f"Rp {v_belum_rptl:,}".replace(',', '.')
        rows_html += f"<tr><td class='col-unit'>{unit_id}</td><td>{str_lp}</td><td>{str_lr}</td><td>{str_bp}</td><td>{str_br}</td></tr>\n"

    str_tot_lp = f"{tot_lunas_plg:,}".replace(',', '.')
    str_tot_lr = f"Rp {tot_lunas_rptl:,}".replace(',', '.')
    str_tot_bp = f"{tot_belum_plg:,}".replace(',', '.')
    str_tot_br = f"Rp {tot_belum_rptl:,}".replace(',', '.')

    html_code = f"""<table class="rekap-1juta">
<thead><tr><th rowspan="2" class="bg-unit-1j">UNIT UP</th><th colspan="2" class="bg-lunas-1j">LUNAS</th><th colspan="2" class="bg-belum-1j">BELUM LUNAS</th></tr>
<tr><th class="bg-lunas-1j">JUMLAH PLG</th><th class="bg-lunas-1j">RPTL</th><th class="bg-belum-1j">JUMLAH PLG</th><th class="bg-belum-1j">RPTL</th></tr></thead>
<tbody>{rows_html}<tr class="row-total"><td class="bg-unit-1j">TOTAL</td><td class="bg-lunas-1j">{str_tot_lp}</td><td class="bg-lunas-1j">{str_tot_lr}</td><td class="bg-belum-1j">{str_tot_bp}</td><td class="bg-belum-1j">{str_tot_br}</td></tr></tbody></table>"""

    st.markdown(html_code, unsafe_allow_html=True)
    st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)

    chart_data_1j = []
    for unit_id in ulp_mapping.keys():
        label = f"{unit_id} - {ulp_mapping.get(unit_id, unit_id)}"
        v_l_rptl = int(lunas_rptl.get(unit_id, 0))
        v_b_rptl = int(belum_rptl.get(unit_id, 0))
        if v_l_rptl > 0 or v_b_rptl > 0:
            chart_data_1j.append({'Unit': label, 'Status': 'Lunas', 'Nominal': v_l_rptl, 'Text': f"Rp {v_l_rptl:,}".replace(',', '.')})
            chart_data_1j.append({'Unit': label, 'Status': 'Belum Lunas', 'Nominal': v_b_rptl, 'Text': f"Rp {v_b_rptl:,}".replace(',', '.')})

    if chart_data_1j:
        df_chart_1j = pd.DataFrame(chart_data_1j)
        fig_stack = px.bar(df_chart_1j, x="Nominal", y="Unit", color="Status", orientation='h', color_discrete_map={"Lunas": "#00E5FF", "Belum Lunas": WARNING_RED}, text="Text")
        fig_stack.update_traces(textposition='outside', cliponaxis=False, textfont=dict(family="Inter", size=14, color=FONT_COLOR, weight='bold'), hovertemplate="<b>%{y}</b><br>Status: %{fullData.name}<br>Nominal: %{text}<extra></extra>", marker=dict(line=dict(color=BG_CHART, width=1.5)), width=0.2)
        fig_stack.update_layout(barmode='group', yaxis=dict(autorange="reversed", tickfont=dict(color=FONT_COLOR)), title=dict(text="Rasio Keberhasilan Penagihan (Lunas vs Belum Lunas)", font=dict(size=22, color=FONT_COLOR, family="Inter", weight="bold"), x=0.5, y=0.95, xanchor='center', yanchor='top'), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=20, r=150, t=70, b=20), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5, font=dict(size=14, weight='bold', color=FONT_COLOR)), xaxis_title="", yaxis_title="", hoverlabel=dict(bgcolor=HOVER_BG, bordercolor="#00E5FF", font_size=15, font_family="Inter", font_color=HOVER_FONT))
        fig_stack.update_xaxes(showgrid=True, gridcolor=GRID_COLOR, showticklabels=False)
        st.plotly_chart(fig_stack, use_container_width=True)

def show_piutang_data_mentah(df_raw):
    st.markdown("### 📋 Data Mentah Excel")
    if df_raw.empty:
        st.warning("⚠️ Data Kosong.")
        return
    st.info(f"📊 Menampilkan seluruh data | Total: **{len(df_raw):,}** baris")
    MAX_ROWS = 5000
    if len(df_raw) > MAX_ROWS:
        st.warning(f"⚠️ Menampilkan {MAX_ROWS} baris pertama dari total {len(df_raw):,} baris agar browser tetap ringan.")
        st.dataframe(df_raw.head(MAX_ROWS), use_container_width=True, height=500)
    else:
        st.dataframe(df_raw, use_container_width=True, height=500)

def show_hcs_dashboard():
    st.markdown("<div class='custom-header'><h2>Dashboard HCS</h2></div>", unsafe_allow_html=True)

    with st.spinner("⏳ Mengambil data HCS dari Google Sheet (Sheet: HCS)..."):
        df_hcs_raw = load_hcs_from_gsheet()

    if df_hcs_raw.empty:
        st.error("❌ Gagal mengambil data atau Sheet 'HCS' kosong/tidak ditemukan.")
    else:
        try:
            df_hcs = df_hcs_raw.copy()
            df_hcs.columns = [str(c).upper().strip() for c in df_hcs.columns]

            if 'DAYA' in df_hcs.columns:
                def clean_daya(val):
                    try:
                        return int(float(str(val).replace(',', '').strip()))
                    except:
                        return 0
                df_hcs['DAYA_CLEAN'] = df_hcs['DAYA'].apply(clean_daya)

                count_7700 = len(df_hcs[df_hcs['DAYA_CLEAN'] == 7700])
                count_13200 = len(df_hcs[df_hcs['DAYA_CLEAN'] == 13200])
                count_total = len(df_hcs)

                fmt_total = f"{count_total:,}".replace(',', '.')
                fmt_7700 = f"{count_7700:,}".replace(',', '.')
                fmt_13200 = f"{count_13200:,}".replace(',', '.')

                bg_card, border_card, font_main, font_sub = "#FFFFFF", "#E0E0E0", "#333333", "#888888"

                st.markdown(f"""
                <div style="display: flex; gap: 15px; margin-bottom: 25px; flex-wrap: wrap;">
                    <div style="flex: 1; min-width: 200px; background-color: {bg_card}; border: 1px solid {border_card}; border-radius: 12px; padding: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); border-left: 5px solid #00E5FF;">
                        <p style="margin:0; font-size: 13px; color: {font_sub}; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px;">Total Pelanggan HCS</p>
                        <h2 style="margin: 8px 0 0 0; color: {font_main}; font-size: 28px; font-weight: 900;">{fmt_total}</h2>
                    </div>
                    <div style="flex: 1; min-width: 200px; background-color: {bg_card}; border: 1px solid {border_card}; border-radius: 12px; padding: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); border-left: 5px solid #FF9100;">
                        <p style="margin:0; font-size: 13px; color: {font_sub}; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px;">Daya 7.700 VA</p>
                        <h2 style="margin: 8px 0 0 0; color: #FF9100; font-size: 28px; font-weight: 900;">{fmt_7700} <span style="font-size: 14px; color: {font_sub}; font-weight: 600;">PLG</span></h2>
                    </div>
                    <div style="flex: 1; min-width: 200px; background-color: {bg_card}; border: 1px solid {border_card}; border-radius: 12px; padding: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); border-left: 5px solid #00E676;">
                        <p style="margin:0; font-size: 13px; color: {font_sub}; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px;">Daya 13.200 VA</p>
                        <h2 style="margin: 8px 0 0 0; color: #00E676; font-size: 28px; font-weight: 900;">{fmt_13200} <span style="font-size: 14px; color: {font_sub}; font-weight: 600;">PLG</span></h2>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("---")
                st.markdown("### 📊 Analitik HCS")
                st.markdown("##### 📊 Jumlah Pelanggan Berdasarkan Daya")

                data_daya = {'Daya': ['7.700 VA', '13.200 VA'], 'Jumlah': [count_7700, count_13200]}
                fig_daya = px.bar(pd.DataFrame(data_daya), x='Daya', y='Jumlah', color='Daya', text='Jumlah', color_discrete_map={'7.700 VA': '#8BC34A', '13.200 VA': '#FF0000'})
                fig_daya.update_traces(texttemplate='%{y}', textposition='outside', cliponaxis=False, textfont=dict(family="Inter", size=16, color=FONT_COLOR, weight='bold'), width=0.4)
                fig_daya.update_layout(height=450, margin=dict(t=40, b=120, l=80, r=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=FONT_COLOR, family="Inter"), showlegend=False)
                fig_daya.update_xaxes(title="", showgrid=False, tickfont=dict(size=16, weight='bold', color=FONT_COLOR))
                fig_daya.update_yaxes(title_text="Jumlah Pelanggan", title_standoff=25, showgrid=True, gridcolor=GRID_COLOR, tickfont=dict(color=FONT_COLOR))
                st.plotly_chart(fig_daya, use_container_width=True, config={'displaylogo': False})
                render_download_buttons(fig_daya, "HCS_Berdasarkan_Daya", "bar_daya_simple")

                st.markdown("<br>", unsafe_allow_html=True)
                def kategori_daya(val):
                    if val == 7700: return "7.700 VA"
                    elif val == 13200: return "13.200 VA"
                    else: return "Lainnya"

                st.markdown("##### 🍩 Komposisi Daya")
                df_hcs['Kategori Daya Pie'] = df_hcs['DAYA_CLEAN'].apply(kategori_daya)
                df_pie = df_hcs['Kategori Daya Pie'].value_counts().reset_index()
                df_pie.columns = ['Kategori', 'Jumlah']

                fig_pie = px.pie(df_pie, values='Jumlah', names='Kategori', color='Kategori', hole=0.5, color_discrete_map={"7.700 VA": "#FF9100", "13.200 VA": "#00E676", "Lainnya": "#D500F9"})
                fig_pie.update_traces(textposition='inside', textinfo='percent+label', marker=dict(line=dict(color=BG_CHART, width=2)))
                fig_pie.update_layout(height=400, margin=dict(t=20, b=20, l=10, r=10), showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=FONT_COLOR))
                st.plotly_chart(fig_pie, use_container_width=True, config={'displaylogo': False})
                render_download_buttons(fig_pie, "Komposisi_Daya_HCS", "pie")

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("##### 📊 HCS Berdasarkan Daya Terpasang per Unit")
                candidate_cols = ['UNITUP', 'UNIT UP', 'UNIT_UP']
                ulp_code_col = next((c for c in df_hcs.columns if str(c).upper().strip() in candidate_cols), None)

                if ulp_code_col is not None:
                    user_ulp_mapping = {'53711': 'Bekasi Kota', '53731': 'Medan Satria', '53732': 'Babelan', '53741': 'Bantargebang', '53742': 'Mustikajaya', '53771': 'Prima Bekasi'}
                    df_hcs['ULP_CODE_CLEAN'] = df_hcs[ulp_code_col].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
                    df_hcs['NAMA_UNIT'] = df_hcs['ULP_CODE_CLEAN'].map(user_ulp_mapping).fillna('Lainnya')
                    df_hcs['Daya Label'] = df_hcs['DAYA_CLEAN'].apply(kategori_daya)

                    df_col_grouped = df_hcs[(df_hcs['DAYA_CLEAN'] == 7700) | (df_hcs['DAYA_CLEAN'] == 13200)].groupby(['Daya Label', 'NAMA_UNIT']).size().reset_index(name='Jumlah')
                    df_col_grouped.columns = ['Daya', 'Unit', 'Jumlah']
                    df_col_grouped['Unit'] = df_col_grouped['Unit'].map({'Bekasi Kota': 'BKT', 'Medan Satria': 'MDS', 'Babelan': 'BBL', 'Bantargebang': 'BTG', 'Mustikajaya': 'MTG', 'Lainnya': 'Lainnya'})

                    fig_grouped_col = px.bar(df_col_grouped, x='Daya', y='Jumlah', color='Unit', barmode='group', text='Jumlah', color_discrete_map={'BKT': '#1f77b4', 'MDS': '#ff7f0e', 'BBL': '#2ca02c', 'BTG': '#17becf', 'MTG': '#9467bd', 'Lainnya': '#A0A0A0'}, category_orders={'Daya': ['7.700 VA', '13.200 VA']})
                    fig_grouped_col.update_traces(texttemplate='%{y}', textposition='outside', cliponaxis=False, textfont=dict(family="Inter", size=14, color=FONT_COLOR, weight='bold'))
                    fig_grouped_col.update_layout(height=500, margin=dict(t=40, b=120, l=80, r=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=FONT_COLOR, family="Inter"), legend=dict(title="", orientation="h", yanchor="top", y=-0.3, xanchor="center", x=0.5))
                    fig_grouped_col.update_xaxes(title="", showgrid=False, tickfont=dict(size=18, weight='bold', color=FONT_COLOR))
                    fig_grouped_col.update_yaxes(title_text="Jumlah Pelanggan", title_standoff=25, showgrid=True, gridcolor=GRID_COLOR, tickfont=dict(color=FONT_COLOR))
                    st.plotly_chart(fig_grouped_col, use_container_width=True, config={'displaylogo': False})
                    render_download_buttons(fig_grouped_col, "HCS_Berdasarkan_Daya_Per_Unit", "bar_unit")
                else:
                    st.info("Kolom kode unit (UNITUP / UNIT UP) tidak ditemukan dalam file untuk membuat Grafik Batang ini.")

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("##### 📈 Tren Peremajaan per Bulan (Berdasarkan Daya)")
                if 'BULAN' in df_hcs.columns and 'TAHUN' in df_hcs.columns:
                    df_trend_raw = df_hcs.copy()
                    df_trend_raw['TAHUN'] = pd.to_numeric(df_trend_raw['TAHUN'], errors='coerce').fillna(0).astype(int)
                    df_trend_raw['BULAN'] = pd.to_numeric(df_trend_raw['BULAN'], errors='coerce').fillna(0).astype(int)
                    df_trend_raw = df_trend_raw[(df_trend_raw['TAHUN'] > 2000) & (df_trend_raw['BULAN'] >= 1) & (df_trend_raw['BULAN'] <= 12)]
                    df_trend_raw['Kategori Daya'] = df_trend_raw['DAYA_CLEAN'].apply(kategori_daya)

                    df_trend = df_trend_raw.groupby(['TAHUN', 'BULAN', 'Kategori Daya']).size().reset_index(name='Jumlah').sort_values(by=['TAHUN', 'BULAN'])
                    df_trend['Periode'] = df_trend['BULAN'].map({1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'Mei', 6: 'Jun', 7: 'Jul', 8: 'Agu', 9: 'Sep', 10: 'Okt', 11: 'Nov', 12: 'Des'}) + " " + df_trend['TAHUN'].astype(str)

                    fig_trend = px.line(df_trend, x='Periode', y='Jumlah', color='Kategori Daya', markers=True, text='Jumlah', color_discrete_map={"7.700 VA": "#FF9100", "13.200 VA": "#00E676", "Lainnya": "#D500F9"})
                    fig_trend.update_traces(mode='lines+markers+text', textposition='top center', textfont=dict(family="Inter", size=14, weight='bold'), line=dict(width=4), marker=dict(size=12, line=dict(width=2, color=BG_CHART)), cliponaxis=False)
                    fig_trend.update_layout(height=550, margin=dict(t=40, b=130, l=80, r=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=FONT_COLOR), legend=dict(title="", orientation="h", yanchor="top", y=-0.35, xanchor="center", x=0.5))
                    fig_trend.update_xaxes(showgrid=False, title="", type='category', categoryorder='array', categoryarray=df_trend['Periode'].unique().tolist(), tickangle=-45)
                    fig_trend.update_yaxes(showgrid=True, gridcolor=GRID_COLOR, title_text="Jumlah Pelanggan", title_standoff=25)
                    st.plotly_chart(fig_trend, use_container_width=True, config={'displaylogo': False})
                    render_download_buttons(fig_trend, "Tren_Bulanan_HCS", "trend")
                else:
                    st.info("Kolom BULAN/TAHUN tidak ditemukan untuk membuat Grafik Tren.")

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("##### 📈 Progres Penambahan HCS per Tahun")
                if 'TAHUN' in df_hcs.columns and ulp_code_col is not None:
                    df_year_raw = df_hcs.copy()
                    df_year_raw['TAHUN'] = pd.to_numeric(df_year_raw['TAHUN'], errors='coerce').fillna(0).astype(int)
                    df_year_raw = df_year_raw[df_year_raw['TAHUN'] > 2000]
                    df_year_raw['ULP_CODE_CLEAN'] = df_year_raw[ulp_code_col].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
                    df_year_raw['NAMA_UNIT'] = df_year_raw['ULP_CODE_CLEAN'].map({'53711': 'BKT', '53731': 'MDS', '53732': 'BBL', '53741': 'BTG', '53742': 'MTG', '53771': 'PRM'}).fillna('Lainnya')

                    df_year_grouped = df_year_raw.groupby(['TAHUN', 'NAMA_UNIT']).size().reset_index(name='Jumlah')
                    df_year_grouped.columns = ['Tahun', 'Unit', 'Jumlah']

                    fig_grouped_year = px.bar(df_year_grouped, x='Tahun', y='Jumlah', color='Unit', barmode='group', text='Jumlah', color_discrete_map={'BKT': '#1f77b4', 'MDS': '#ff7f0e', 'BBL': '#2ca02c', 'BTG': '#17becf', 'MTG': '#9467bd', 'Lainnya': '#A0A0A0'}, category_orders={'Tahun': sorted(df_year_grouped['Tahun'].unique().tolist())})
                    fig_grouped_year.update_traces(texttemplate='%{y}', textposition='outside', cliponaxis=False, textfont=dict(family="Inter", size=14, color=FONT_COLOR, weight='bold'))
                    fig_grouped_year.update_layout(height=500, margin=dict(t=40, b=120, l=80, r=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=FONT_COLOR, family="Inter"), legend=dict(title="", orientation="h", yanchor="top", y=-0.3, xanchor="center", x=0.5))
                    fig_grouped_year.update_xaxes(title="", showgrid=False, tickfont=dict(size=18, weight='bold', color=FONT_COLOR), type='category')
                    fig_grouped_year.update_yaxes(title_text="Jumlah Pelanggan", title_standoff=25, showgrid=True, gridcolor=GRID_COLOR, tickfont=dict(color=FONT_COLOR))
                    st.plotly_chart(fig_grouped_year, use_container_width=True, config={'displaylogo': False})
                    render_download_buttons(fig_grouped_year, "Progres_Tahunan_HCS", "year")
                else:
                    st.info("Kolom TAHUN / kode unit tidak ditemukan untuk membuat Grafik Progres Tahunan.")

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("---")
                st.markdown("### 📋 Data Mentah HCS")
                cols_to_drop = ['DAYA_CLEAN', 'Kategori Daya', 'Daya Pelanggan', 'Kategori Daya Pie', 'ULP_CODE_CLEAN', 'NAMA_UNIT', 'Daya Label', 'UNIT_SHORT']
                if len(df_hcs) > 5000:
                    st.dataframe(df_hcs.drop(columns=cols_to_drop, errors='ignore').head(5000), use_container_width=True, height=500)
                else:
                    st.dataframe(df_hcs.drop(columns=cols_to_drop, errors='ignore'), use_container_width=True, height=500)
            else:
                st.error("❌ Kolom 'DAYA' tidak ditemukan dalam Sheet 'HCS'. Pastikan format sesuai.")
                st.dataframe(df_hcs.head(), use_container_width=True)
        except Exception as e:
            st.error(f"Gagal memproses data HCS dari Google Sheet: {e}")

def show_spklu_dashboard():
    st.markdown("<div class='custom-header'><h2>Dashboard SPKLU</h2></div>", unsafe_allow_html=True)

    with st.spinner("⏳ Mengambil data SPKLU dari Google Sheet..."):
        df_spklu_raw = load_spklu_from_gsheet()

    if df_spklu_raw.empty:
        st.warning("⚠️ Data Kosong atau Sheet 'Data SPKLU' belum ditemukan/format tidak sesuai.")
    else:
        try:
            df_spklu = df_spklu_raw.copy()
            
            # --- IDENTIFIKASI KOLOM ---
            tahun_col = next((c for c in df_spklu.columns if 'TAHUN' in str(c).upper().strip()), None)
            bulan_col = next((c for c in df_spklu.columns if 'BULAN' in str(c).upper().strip()), None)
            ulp_col = next((c for c in df_spklu.columns if 'ULP' in str(c).upper()), None)
            nama_spklu_col = next((c for c in df_spklu.columns if 'NAMA SPKLU' in str(c).upper() or ('NAMA' in str(c).upper() and 'ULP' not in str(c).upper())), None)

            trx_cols = [c for c in df_spklu.columns if 'TRX' in str(c).upper()]
            kwh_cols = [c for c in df_spklu.columns if 'KWH' in str(c).upper() and 'RP' not in str(c).upper()]
            rp_cols = [c for c in df_spklu.columns if 'RP' in str(c).upper()]

            # Filter baris TOTAL atau Nama kosong
            if ulp_col and nama_spklu_col:
                df_spklu = df_spklu[df_spklu[nama_spklu_col].astype(str).str.strip() != '']
                df_spklu = df_spklu[~df_spklu[ulp_col].astype(str).str.upper().str.contains('TOTAL')]

            # --- KALKULASI TOTAL UNTUK SUMMARY CARD ---
            def clean_val_general(val):
                if pd.isna(val): return 0.0
                if isinstance(val, (int, float)): return float(val)
                s = str(val).strip().replace('.', '').replace(',', '.')
                if not s or s.upper() in ['NAN', 'TOTAL', '-']: return 0.0
                try: return float(s)
                except: return 0.0

            for c in trx_cols + kwh_cols + rp_cols:
                df_spklu[c] = df_spklu[c].apply(clean_val_general)

            total_trx = df_spklu[trx_cols].sum().sum() if trx_cols else 0
            total_kwh = df_spklu[kwh_cols].sum().sum() if kwh_cols else 0
            total_rp = df_spklu[rp_cols].sum().sum() if rp_cols else 0

            # --- DETEKSI PERIODE OTOMATIS ---
            periode_text = "Semua Periode"
            if tahun_col and bulan_col:
                try:
                    temp_df = df_spklu[[tahun_col, bulan_col]].copy()
                    m_dict = {
                        'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MEI': 5, 'JUN': 6,
                        'JUL': 7, 'AGU': 8, 'SEP': 9, 'OKT': 10, 'NOV': 11, 'DES': 12, 
                        'JANUARI': 1, 'FEBRUARI': 2, 'MARET': 3, 'APRIL': 4, 'JUNI': 6,
                        'JULI': 7, 'AGUSTUS': 8, 'SEPTEMBER': 9, 'OKTOBER': 10, 'NOVEMBER': 11, 'DESEMBER': 12
                    }
                    temp_df['M_Num'] = temp_df[bulan_col].astype(str).str.upper().str.strip().map(m_dict)
                    temp_df['Y_Num'] = pd.to_numeric(temp_df[tahun_col], errors='coerce')
                    temp_df = temp_df.dropna(subset=['M_Num', 'Y_Num'])
                    
                    if not temp_df.empty:
                        temp_df = temp_df.sort_values(['Y_Num', 'M_Num'])
                        first_row = temp_df.iloc[0]
                        last_row = temp_df.iloc[-1]
                        rev_m_dict = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'Mei', 6: 'Jun', 7: 'Jul', 8: 'Agu', 9: 'Sep', 10: 'Okt', 11: 'Nov', 12: 'Des'}
                        
                        m1, y1 = rev_m_dict.get(first_row['M_Num'], ''), int(first_row['Y_Num'])
                        m2, y2 = rev_m_dict.get(last_row['M_Num'], ''), int(last_row['Y_Num'])
                        
                        if y1 == y2 and m1 == m2:
                            periode_text = f"Periode: {m1} {y1}"
                        elif y1 == y2:
                            periode_text = f"Periode: {m1} - {m2} {y1}"
                        else:
                            periode_text = f"Periode: {m1} {y1} - {m2} {y2}"
                except:
                    pass
            
            # --- TAMPILKAN SUMMARY CARDS ---
            st.markdown(f"""
            <div style="display: flex; gap: 15px; margin-bottom: 25px; flex-wrap: wrap;">
                <div style="flex: 1; min-width: 200px; background-color: #FFFFFF; border: 1px solid #E0E0E0; border-radius: 12px; padding: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); border-left: 5px solid #00AFF0;">
                    <p style="margin:0; font-size: 13px; color: #888888; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px;">Total Keseluruhan Transaksi</p>
                    <p style="margin: 2px 0 0 0; font-size: 11px; color: #A0A0A0; font-weight: 600;">{periode_text}</p>
                    <h2 style="margin: 8px 0 0 0; color: #333333; font-size: 26px; font-weight: 900;">{int(total_trx):,} <span style="font-size: 14px; color: #888888; font-weight: 600;">Kali</span></h2>
                </div>
                <div style="flex: 1; min-width: 200px; background-color: #FFFFFF; border: 1px solid #E0E0E0; border-radius: 12px; padding: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); border-left: 5px solid #2ca02c;">
                    <p style="margin:0; font-size: 13px; color: #888888; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px;">Total Keseluruhan Energi</p>
                    <p style="margin: 2px 0 0 0; font-size: 11px; color: #A0A0A0; font-weight: 600;">{periode_text}</p>
                    <h2 style="margin: 8px 0 0 0; color: #2ca02c; font-size: 26px; font-weight: 900;">{format_indo(total_kwh)} <span style="font-size: 14px; color: #888888; font-weight: 600;">kWh</span></h2>
                </div>
                <div style="flex: 1; min-width: 200px; background-color: #FFFFFF; border: 1px solid #E0E0E0; border-radius: 12px; padding: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); border-left: 5px solid #ff7f0e;">
                    <p style="margin:0; font-size: 13px; color: #888888; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px;">Total Keseluruhan Pendapatan</p>
                    <p style="margin: 2px 0 0 0; font-size: 11px; color: #A0A0A0; font-weight: 600;">{periode_text}</p>
                    <h2 style="margin: 8px 0 0 0; color: #ff7f0e; font-size: 26px; font-weight: 900;">Rp {format_indo(total_rp)}</h2>
                </div>
            </div>
            """.replace(',', '.').replace('. Kali', ' Kali'), unsafe_allow_html=True)

            st.markdown("---")

            if not nama_spklu_col:
                st.warning("⚠️ Kolom 'Nama SPKLU' tidak ditemukan, grafik detail tidak dapat ditampilkan.")
            elif not trx_cols and not kwh_cols:
                st.warning("⚠️ Kolom 'TRX' atau 'KWH' tidak ditemukan di tabel.")
            else:
                df_spklu['Total_kWh_Calc'] = df_spklu[kwh_cols].sum(axis=1)
                df_spklu['Total_Trx_Calc'] = df_spklu[trx_cols].sum(axis=1)
                df_perf = df_spklu[df_spklu['Total_Trx_Calc'] > 0]
                
                tab_trend, tab_pie, tab_bar, tab_data = st.tabs(["📈 Trend YoY Analysis", "🍩 Porsi ULP", "🏆 Top 5 SPKLU", "📋 Data Detail"])
                
                # ==========================================
                # TABS 1: TREN PERTUMBUHAN (YOY KOMPLEKS)
                # ==========================================
                with tab_trend:
                    if bulan_col and tahun_col:
                        list_tahun_spklu = sorted([t for t in df_spklu[tahun_col].unique() if str(t).strip() != ''], reverse=True)
                        if len(list_tahun_spklu) > 0:
                            st.markdown("##### ⚙️ Parameter Analisis Tren")
                            c1, c2, c3 = st.columns([1, 1, 1.5])
                            with c1:
                                tahun_a = st.selectbox("Tahun Utama (A)", list_tahun_spklu, index=0)
                            with c2:
                                tahun_b = st.selectbox("Tahun Pembanding (B)", list_tahun_spklu, index=1 if len(list_tahun_spklu) > 1 else 0)
                            with c3:
                                st.markdown("<div style='margin-bottom: 5px; font-size:14px; font-weight:600;'>Mode Perhitungan</div>", unsafe_allow_html=True)
                                mode_tampilan = st.radio("Mode Tampilan", ["Bulanan", "Akumulasi (Year-to-Date)"], horizontal=True, label_visibility="collapsed")

                            df_tren_raw = df_spklu.copy()
                            df_tren_raw['Total_TRX_All'] = df_tren_raw[trx_cols].sum(axis=1) if trx_cols else 0
                            df_tren_raw['Total_KWH_All'] = df_tren_raw[kwh_cols].sum(axis=1) if kwh_cols else 0
                            df_tren_raw['Total_RP_All'] = df_tren_raw[rp_cols].sum(axis=1) if rp_cols else 0

                            month_dict = {
                                'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MEI': 5, 'JUN': 6,
                                'JUL': 7, 'AGU': 8, 'SEP': 9, 'OKT': 10, 'NOV': 11, 'DES': 12, 
                                'JANUARI': 1, 'FEBRUARI': 2, 'MARET': 3, 'APRIL': 4, 'JUNI': 6,
                                'JULI': 7, 'AGUSTUS': 8, 'SEPTEMBER': 9, 'OKTOBER': 10, 'NOVEMBER': 11, 'DESEMBER': 12
                            }
                            
                            df_base = pd.DataFrame({'Month_Num': range(1, 13), 'Nama_Bulan': ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']})

                            def process_trend_data(year, mode):
                                df_y = df_tren_raw[df_tren_raw[tahun_col].astype(str) == str(year)].copy()
                                
                                # Hapus baris akumulasi aggregate (Total) untuk menghindari double count
                                if ulp_col:
                                    df_y = df_y[~df_y[ulp_col].astype(str).str.upper().str.contains('TOTAL|UP3|BEKASI|JUMLAH', na=False)]
                                    
                                df_y['Month_Num'] = df_y[bulan_col].astype(str).str.upper().map(month_dict)
                                df_y = df_y.dropna(subset=['Month_Num'])
                                
                                df_g = df_y.groupby('Month_Num')[['Total_TRX_All', 'Total_KWH_All', 'Total_RP_All']].sum().reset_index()
                                df_res = pd.merge(df_base, df_g, on='Month_Num', how='left')

                                max_month = df_g['Month_Num'].max() if not df_g.empty else 0

                                if mode == "Akumulasi (Year-to-Date)" and max_month > 0:
                                    idx_limit = int(max_month) - 1 
                                    df_res.loc[:idx_limit, ['Total_TRX_All', 'Total_KWH_All', 'Total_RP_All']] = df_res.loc[:idx_limit, ['Total_TRX_All', 'Total_KWH_All', 'Total_RP_All']].fillna(0)
                                    df_res['Total_TRX_All'] = df_res['Total_TRX_All'].cumsum()
                                    df_res['Total_KWH_All'] = df_res['Total_KWH_All'].cumsum()
                                    df_res['Total_RP_All'] = df_res['Total_RP_All'].cumsum()
                                    df_res.loc[idx_limit+1:, ['Total_TRX_All', 'Total_KWH_All', 'Total_RP_All']] = float('nan')

                                return df_res

                            df_a = process_trend_data(tahun_a, mode_tampilan)
                            df_b = process_trend_data(tahun_b, mode_tampilan)

                            def create_yoy_fig(df_1, df_2, col_val, title, y_title, is_rp=False, is_trx=False):
                                df_a_plot = df_1.copy()
                                df_b_plot = df_2.copy()

                                # Skalakan nilai menjadi jutaan jika Rupiah
                                if is_rp:
                                    df_a_plot[col_val] = df_a_plot[col_val] / 1_000_000
                                    df_b_plot[col_val] = df_b_plot[col_val] / 1_000_000
                                    y_title = "Pendapatan (Juta Rp)" 

                                def fmt_val(v):
                                    if pd.isna(v) or (v == 0 and mode_tampilan != "Akumulasi (Year-to-Date)"):
                                        return ""
                                    if is_rp:
                                        return f"{v:.2f}".replace('.', ',') + " Rp"
                                    if is_trx:
                                        return f"{int(v):,} Trx".replace(',', '.')
                                    return f"{format_indo(v)} kWh"

                                color_a = "#00AFF0"  # Biru (Tahun A)
                                color_b = "#ff7f0e"  # Oranye (Tahun B)

                                fig = go.Figure()
                                
                                # --- GARIS GRAFIK UTAMA ---
                                text_b = [fmt_val(v) for v in df_b_plot[col_val]]
                                fig.add_trace(go.Scatter(
                                    x=df_b_plot['Nama_Bulan'], y=df_b_plot[col_val], 
                                    name=f"Tahun {tahun_b} (Pembanding)", mode="lines+markers+text", 
                                    line=dict(color=color_b, width=5), 
                                    marker=dict(size=10, color=color_b), 
                                    text=text_b, textposition='bottom center',
                                    textfont=dict(weight='bold', color=color_b, size=15), 
                                    hovertemplate=f"<b>{tahun_b}</b><br>%{{x}}: %{{text}}<extra></extra>"
                                ))

                                text_a = [fmt_val(v) for v in df_a_plot[col_val]]
                                fig.add_trace(go.Scatter(
                                    x=df_a_plot['Nama_Bulan'], y=df_a_plot[col_val], 
                                    name=f"Tahun {tahun_a} (Utama)", mode="lines+markers+text", 
                                    line=dict(color=color_a, width=6), 
                                    marker=dict(size=14, color="#FFFFFF", line=dict(color=color_a, width=4)), 
                                    text=text_a, textposition='top center', 
                                    textfont=dict(weight='bold', color=color_a, size=17), 
                                    hovertemplate=f"<b>{tahun_a}</b><br>%{{x}}: %{{text}}<extra></extra>"
                                ))

                                # ==========================================
                                # FITUR ADVANCED: MINI GRAPH YOY (POSISI KIRI ATAS)
                                # ==========================================
                                y_main_title = 1.50
                                y_sub_title = 1.40
                                y_bar_a = 1.30
                                y_bar_b = 1.20
                                
                                x_base = 0.04
                                max_width = 0.12
                                b_height = 0.04

                                y_center_a = y_bar_a + b_height / 2
                                y_center_b = y_bar_b + b_height / 2
                                
                                valid_mask = df_a_plot[col_val].notna() & (df_a_plot[col_val] != 0)
                                last_valid_idx = valid_mask[::-1].idxmax() if valid_mask.any() else -1

                                sum_a, sum_b = 0, 0
                                if last_valid_idx != -1:
                                    if mode_tampilan == "Akumulasi (Year-to-Date)":
                                        sum_a = df_a_plot.loc[last_valid_idx, col_val]
                                        sum_b = df_b_plot.loc[last_valid_idx, col_val]
                                    else:
                                        sum_a = df_a_plot.loc[:last_valid_idx, col_val].sum()
                                        sum_b = df_b_plot.loc[:last_valid_idx, col_val].sum()

                                yoy_pct = ((sum_a - sum_b) / sum_b * 100) if sum_b > 0 else 0

                                w_a = (sum_a / max(sum_a, sum_b) * max_width) if max(sum_a, sum_b) > 0 else 0
                                w_b = (sum_b / max(sum_a, sum_b) * max_width) if max(sum_a, sum_b) > 0 else 0

                                # Menggambar Shape & Bar
                                fig.add_shape(type="line", xref="paper", yref="paper", x0=x_base, y0=y_bar_b - 0.02, x1=x_base, y1=y_bar_a + b_height + 0.02, line=dict(color="#FFFFFF", width=2))
                                fig.add_shape(type="rect", xref="paper", yref="paper", x0=x_base, y0=y_bar_a, x1=x_base + w_a, y1=y_bar_a + b_height, fillcolor=color_a, line=dict(width=0))
                                fig.add_shape(type="rect", xref="paper", yref="paper", x0=x_base, y0=y_bar_b, x1=x_base + w_b, y1=y_bar_b + b_height, fillcolor=color_b, line=dict(width=0))
                                
                                title_annotations = []
                                title_annotations.append(dict(xref="paper", yref="paper", x=0.01, y=y_main_title, text=f"<b>{title}</b>", showarrow=False, xanchor="left", yanchor="bottom", font=dict(color="#FFFFFF", size=24, family="Inter")))
                                title_annotations.append(dict(xref="paper", yref="paper", x=x_base - 0.01, y=y_sub_title, text=f"<b>Akumulasi {y_title.split('(')[0]} (YTD)</b>", showarrow=False, xanchor="left", yanchor="bottom", font=dict(color="#FFFFFF", size=14, family="Inter")))

                                # Label Tahun
                                title_annotations.append(dict(xref="paper", yref="paper", x=x_base - 0.01, y=y_center_a, text=f"<b>{tahun_a}</b>", showarrow=False, xanchor="right", yanchor="middle", font=dict(color="#FFFFFF", size=13)))
                                title_annotations.append(dict(xref="paper", yref="paper", x=x_base - 0.01, y=y_center_b, text=f"<b>{tahun_b}</b>", showarrow=False, xanchor="right", yanchor="middle", font=dict(color="#FFFFFF", size=13)))

                                # Label Angka Total
                                def format_yoy_text_func(v):
                                    if is_rp:
                                        return f"{v:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.') + " Jt Rp"
                                    if is_trx:
                                        return f"{int(v):,} Trx".replace(',', '.')
                                    return f"{format_indo(v)} kWh"

                                text_val_x = x_base + max_width + 0.02 
                                title_annotations.append(dict(xref="paper", yref="paper", x=text_val_x, y=y_center_a, text=f"<b><span style='font-size:16px'>{format_yoy_text_func(sum_a)}</span></b>", showarrow=False, xanchor="left", yanchor="middle", font=dict(color="#FFFFFF")))
                                title_annotations.append(dict(xref="paper", yref="paper", x=text_val_x, y=y_center_b, text=f"<b><span style='font-size:16px'>{format_yoy_text_func(sum_b)}</span></b>", showarrow=False, xanchor="left", yanchor="middle", font=dict(color="#FFFFFF")))

                                # Garis Penghubung & Badge Persentase
                                bracket_x = text_val_x + 0.09 
                                box_x = bracket_x + 0.06      
                                y_box_center = (y_center_a + y_center_b) / 2 

                                fig.add_shape(type="line", xref="paper", yref="paper", x0=bracket_x - 0.015, y0=y_center_a, x1=bracket_x, y1=y_center_a, line=dict(color="#FFFFFF", width=1.5, dash='dot'))
                                fig.add_shape(type="line", xref="paper", yref="paper", x0=bracket_x - 0.015, y0=y_center_b, x1=bracket_x, y1=y_center_b, line=dict(color="#FFFFFF", width=1.5, dash='dot'))
                                fig.add_shape(type="line", xref="paper", yref="paper", x0=bracket_x, y0=y_center_b, x1=bracket_x, y1=y_center_a, line=dict(color="#FFFFFF", width=1.5, dash='dot'))
                                fig.add_shape(type="line", xref="paper", yref="paper", x0=bracket_x, y0=y_box_center, x1=box_x - 0.035, y1=y_box_center, line=dict(color="#FFFFFF", width=1.5, dash='dot'))
                                
                                badge_color = "#00E676" if yoy_pct >= 0 else "#FF1744"
                                sign = "+" if yoy_pct > 0 else ""
                                
                                title_annotations.append(dict(
                                    xref="paper", yref="paper", x=box_x, y=y_box_center, 
                                    text=f"<span style='font-size:10px; color:#A0A0A0'><i>YoY YTD:</i></span><br><b><span style='color:{badge_color}; font-size:18px;'>{sign}{yoy_pct:,.2f}%</span></b>".replace(",", "X").replace(".", ",").replace("X", "."), 
                                    showarrow=False, xanchor="center", yanchor="middle", 
                                    font=dict(color="#333333", size=14), bgcolor="#FFFFFF", bordercolor=badge_color, borderwidth=2, borderpad=5
                                ))

                                fig.update_layout(
                                    height=720, 
                                    title="",
                                    paper_bgcolor='#002E5B', 
                                    plot_bgcolor='#002E5B',  
                                    margin=dict(t=240, b=40, l=10, r=20),
                                    legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5, font=dict(size=14, weight="bold", color="#FFFFFF")),
                                    hovermode="x unified",
                                    hoverlabel=dict(bgcolor="#FFFFFF", font_color="#002E5B"),
                                    annotations=title_annotations
                                )
                                fig.update_xaxes(showgrid=False, tickfont=dict(color="#FFFFFF", size=13, weight="bold"))
                                fig.update_yaxes(title_text=y_title, title_font=dict(color="#FFFFFF"), showgrid=True, gridcolor="rgba(255,255,255,0.15)", tickfont=dict(color="#FFFFFF"), rangemode="tozero")
                                return fig

                            st.markdown("<hr>", unsafe_allow_html=True)
                            
                            fig_trx = create_yoy_fig(df_a, df_b, 'Total_TRX_All', "Kali Transaksi", "Jumlah Transaksi (Kali)", is_trx=True)
                            st.plotly_chart(fig_trx, use_container_width=True, config={'displaylogo': False})
                            st.markdown("<br><br>", unsafe_allow_html=True)

                            fig_kwh = create_yoy_fig(df_a, df_b, 'Total_KWH_All', "kWh Transaksi", "Konsumsi Energi (kWh)")
                            st.plotly_chart(fig_kwh, use_container_width=True, config={'displaylogo': False})
                            st.markdown("<br><br>", unsafe_allow_html=True)

                            fig_rp = create_yoy_fig(df_a, df_b, 'Total_RP_All', "Rupiah kWh Transaksi", "Pendapatan (Rp)", is_rp=True)
                            st.plotly_chart(fig_rp, use_container_width=True, config={'displaylogo': False})

                    else:
                        st.info("💡 Grafik tren butuh kolom 'TAHUN' dan 'BULAN' di Google Sheet untuk ditampilkan.")

                with tab_pie:
                    st.markdown("##### 🍩 Porsi Penjualan kWh per ULP")
                    df_ulp = df_perf.groupby(ulp_col)['Total_kWh_Calc'].sum().reset_index()
                    fig_ulp = px.pie(df_ulp, values='Total_kWh_Calc', names=ulp_col, hole=0.45, color_discrete_sequence=px.colors.qualitative.Set2)
                    fig_ulp.update_traces(textposition='inside', textinfo='percent+label', marker=dict(line=dict(color="#FFFFFF", width=2)))
                    fig_ulp.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=20, b=20, l=10, r=10), font=dict(color="#333333"), showlegend=False)
                    st.plotly_chart(fig_ulp, use_container_width=True, config={'displaylogo': False})

                with tab_bar:
                    st.markdown("##### 🏆 Top 5 SPKLU (Berdasarkan Konsumsi kWh)")
                    df_top = df_perf.groupby(nama_spklu_col)['Total_kWh_Calc'].sum().reset_index()
                    df_top = df_top.sort_values('Total_kWh_Calc', ascending=True).tail(5)
                    
                    df_top['Label_Name'] = df_top[nama_spklu_col].apply(lambda x: f"<b>{x}</b>")
                    fig_top = px.bar(df_top, x='Total_kWh_Calc', y='Label_Name', orientation='h', color_discrete_sequence=["#00AFF0"])
                    
                    custom_texts = [f"{format_indo(v)} kWh" for v in df_top['Total_kWh_Calc']]
                    fig_top.update_traces(text=custom_texts, textposition='inside', textfont=dict(family="Inter", size=14, color="white", weight='bold'))
                    
                    fig_top.update_yaxes(showticklabels=False, title="")
                    fig_top.update_xaxes(showgrid=True, gridcolor="#EEEEEE", title="")
                    
                    fig_top.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                        margin=dict(t=20, b=20, l=480, r=10), font=dict(color="#333333")
                    )
                    
                    for i, val in enumerate(df_top[nama_spklu_col]):
                        fig_top.add_annotation(
                            xref="paper", x=0, xanchor="left", xshift=-470,
                            yref="y", y=i, yanchor="middle",
                            text=f"<b>{val}</b>",
                            font=dict(family="Inter", size=14, color="black"),
                            showarrow=False, align="left"
                        )
                        
                    st.plotly_chart(fig_top, use_container_width=True, config={'displaylogo': False})

                with tab_data:
                    st.markdown("##### 📋 Data Detail SPKLU")
                    df_display = df_spklu.copy()
                    for c in trx_cols + kwh_cols + rp_cols:
                        if c in df_display.columns:
                            if 'TRX' in c.upper():
                                df_display[c] = df_display[c].apply(lambda x: f"{int(x)}" if pd.notna(x) else "0")
                            else:
                                df_display[c] = df_display[c].apply(lambda x: format_indo(x) if pd.notna(x) else "0")
                    st.dataframe(df_display, use_container_width=True, height=400)

        except Exception as e:
            st.error(f"Gagal memproses data SPKLU: {e}")

def show_dil_dashboard():
    st.markdown("<div class='custom-header'><h2>Dashboard DIL</h2></div>", unsafe_allow_html=True)
    st.info("🚧 Halaman DIL masih kosong dan dalam tahap pengembangan.")

def show_ts_lpb_dashboard():
    st.markdown("<div class='custom-header'><h2>Dashboard TS LPB</h2></div>", unsafe_allow_html=True)
    st.info("🚧 Halaman TS LPB masih kosong dan dalam tahap pengembangan.")
            
def show_piutang_dashboard(piutang_indicators):
    st.markdown("<div class='custom-header'><h2>Dashboard Piutang</h2></div>", unsafe_allow_html=True)
    
    # Ambil indikator yang sedang aktif dari session_state
    selected_ind = st.session_state.radio_piutang if st.session_state.radio_piutang else piutang_indicators[0]
    
    with st.spinner("⏳ Mengambil data Piutang dari Google Sheet (Sheet: ROC PIUTANG)..."):
        df_piutang = load_piutang_from_gsheet()
        
    if df_piutang.empty:
        st.error("❌ Gagal mengambil data atau Sheet 'ROC PIUTANG' kosong.")
        return

    # Tampilkan fungsi sesuai dengan tombol menu yang diklik di sidebar
    if selected_ind == "REKAP DAYA DIATAS 16500 BELUM LUNAS > TGL 20":
        show_tabel_rekap_16500(df_piutang)
    elif selected_ind == "REKAP SALDO PIUTANG PELANGGAN UP3 BEKASI RPTL >=RP 1 JUTA":
        show_tabel_rekap_1juta(df_piutang)
    else:
        st.info("Pilih menu Piutang di sidebar untuk menampilkan data.")
        
    # Selalu tampilkan data mentah di bagian bawah
    st.markdown("---")
    show_piutang_data_mentah(df_piutang)

# ==========================================
# 9. MAIN EXECUTION
# ==========================================
def main():
    if 'active_menu' not in st.session_state:
        st.session_state.active_menu = 'KPI'

    df_raw_kpi = load_data()
    if df_raw_kpi is None or df_raw_kpi.empty:
        st.error("❌ Gagal terhubung ke Google Sheet! Pastikan file 'Raw Data Dashboard KN dan Pemasaran' sudah di-Share (Bagikan) ke email Service Account Anda dan Secrets di Streamlit Cloud sudah diatur.")
        df_kpi, ind_list_kpi = pd.DataFrame(), []
    else:
        df_kpi, _, _, _, ind_list_kpi = clean_data(df_raw_kpi)

    if 'comparison_data' not in st.session_state:
        st.session_state.comparison_data = pd.DataFrame(columns=["Label", "Tahun", "Bulan_Awal", "Bulan_Akhir", "ULP", "Indikator", "T", "R", "%"])
    if 'cc_data' not in st.session_state:
        st.session_state.cc_data = pd.DataFrame(columns=["Label", "Tahun", "Bulan_Awal", "Bulan_Akhir", "ULP", "Indikator", "T", "R", "%"])
    if 'line_data' not in st.session_state:
        st.session_state.line_data = pd.DataFrame(columns=["Label", "Tahun", "Bulan_Awal", "Bulan_Akhir", "ULP", "Indikator", "T", "R", "%"])

    custom_order_kpi = [
        "Penjualan Tenaga Listrik", "Transaksi PLN Mobile", "Penambahan Jumlah Pelanggan",
        "Penambahan Daya Tersambung", "Penambahan Pelanggan Produk Tematik",
        "Rata Rata Saldo Tgl 20 Non-Kogol 1 & 2", "Rata-Rata Saldo Akhir Bulan", "Pelunasan PRR"
    ]
    kpi_indicators = []
    for item in custom_order_kpi:
        if item in ind_list_kpi:
            kpi_indicators.append(item)
    for item in sorted(ind_list_kpi):
        if item not in kpi_indicators and "PIUTANG" not in item.upper() and "16500" not in item.upper():
            kpi_indicators.append(item)

    piutang_indicators = [
        "REKAP DAYA DIATAS 16500 BELUM LUNAS > TGL 20",
        "REKAP SALDO PIUTANG PELANGGAN UP3 BEKASI RPTL >=RP 1 JUTA"
    ]

    if 'radio_kpi' not in st.session_state:
        st.session_state.radio_kpi = kpi_indicators[0] if kpi_indicators else None
    if 'radio_piutang' not in st.session_state:
        st.session_state.radio_piutang = None

    sidebar_logo()

    with st.sidebar.expander("**KPI Kinerja Niaga**", expanded=(st.session_state.active_menu == 'KPI')):
        for item in kpi_indicators:
            is_active = (st.session_state.active_menu == 'KPI' and st.session_state.radio_kpi == item)
            btn_type = "primary" if is_active else "secondary"
            if st.button(item, key=f"btn_kpi_{item}", use_container_width=True, type=btn_type):
                st.session_state.active_menu = 'KPI'
                st.session_state.radio_kpi = item
                st.session_state.radio_piutang = None
                st.rerun()

    with st.sidebar.expander("**Piutang**", expanded=(st.session_state.active_menu == 'PIUTANG')):
        for item in piutang_indicators:
            is_active = (st.session_state.active_menu == 'PIUTANG' and st.session_state.radio_piutang == item)
            btn_type = "primary" if is_active else "secondary"
            if st.button(item, key=f"btn_piu_{item}", use_container_width=True, type=btn_type):
                st.session_state.active_menu = 'PIUTANG'
                st.session_state.radio_piutang = item
                st.session_state.radio_kpi = None
                st.rerun()

    with st.sidebar.expander("**Mind Map**", expanded=(st.session_state.active_menu == 'MIND_MAP')):
        is_active = (st.session_state.active_menu == 'MIND_MAP')
        btn_type = "primary" if is_active else "secondary"
        if st.button("Mind Map Kinerja", key="btn_mindmap", use_container_width=True, type=btn_type):
            st.session_state.active_menu = 'MIND_MAP'
            st.session_state.radio_kpi = None
            st.session_state.radio_piutang = None
            st.rerun()

    with st.sidebar.expander("**HCS**", expanded=(st.session_state.active_menu == 'HCS')):
        is_active = (st.session_state.active_menu == 'HCS')
        btn_type = "primary" if is_active else "secondary"
        if st.button("Dashboard HCS", key="btn_hcs", use_container_width=True, type=btn_type):
            st.session_state.active_menu = 'HCS'
            st.session_state.radio_kpi = None
            st.session_state.radio_piutang = None
            st.rerun()

    with st.sidebar.expander("**SPKLU**", expanded=(st.session_state.active_menu == 'SPKLU')):
        is_active = (st.session_state.active_menu == 'SPKLU')
        btn_type = "primary" if is_active else "secondary"
        if st.button("Dashboard SPKLU", key="btn_spklu", use_container_width=True, type=btn_type):
            st.session_state.active_menu = 'SPKLU'
            st.session_state.radio_kpi = None
            st.session_state.radio_piutang = None
            st.rerun()

    with st.sidebar.expander("**DIL**", expanded=(st.session_state.active_menu == 'DIL')):
        is_active = (st.session_state.active_menu == 'DIL')
        btn_type = "primary" if is_active else "secondary"
        if st.button("Dashboard DIL", key="btn_dil", use_container_width=True, type=btn_type):
            st.session_state.active_menu = 'DIL'
            st.session_state.radio_kpi = None
            st.session_state.radio_piutang = None
            st.rerun()

    with st.sidebar.expander("**TS LPB**", expanded=(st.session_state.active_menu == 'TS_LPB')):
        is_active = (st.session_state.active_menu == 'TS_LPB')
        btn_type = "primary" if is_active else "secondary"
        if st.button("Dashboard TS LPB", key="btn_ts_lpb", use_container_width=True, type=btn_type):
            st.session_state.active_menu = 'TS_LPB'
            st.session_state.radio_kpi = None
            st.session_state.radio_piutang = None
            st.rerun()

    # --- PUSAT ROUTING RAPI DAN BERSIH (ANTI DUPLIKASI) ---
    if st.session_state.active_menu == 'KPI':
        selected_ind = st.session_state.radio_kpi if st.session_state.radio_kpi else (kpi_indicators[0] if kpi_indicators else "Data Kosong")
        st.markdown(f"<div class='custom-header'><h2>{selected_ind}</h2></div>", unsafe_allow_html=True)

        tab1, tab2, tab3, tab4 = st.tabs(["📊 Column Vs Line", "📊 Column Vs Column", "📈 Trend Analysis", "⚡ Quick Graph Maker"])
        with tab1:
            if not df_kpi.empty:
                show_dashboard_kinerja(df_kpi, selected_ind)
        with tab2:
            if not df_kpi.empty:
                show_dashboard_cc(df_kpi, selected_ind)
        with tab3:
            if not df_kpi.empty:
                show_analisis_tren(df_kpi, selected_ind)
        with tab4:
            show_quick_graph()

    elif st.session_state.active_menu == 'MIND_MAP':
        show_mindmap_generator()

    elif st.session_state.active_menu == 'HCS':
        show_hcs_dashboard()

    elif st.session_state.active_menu == 'SPKLU':
        show_spklu_dashboard()

    elif st.session_state.active_menu == 'PIUTANG':
        try:
            show_piutang_dashboard(piutang_indicators)
        except NameError:
            st.warning("⚠️ Modul Piutang Dashboard belum terdefinisi/sedang dikembangkan.")

    elif st.session_state.active_menu == 'DIL':
        show_dil_dashboard()

    elif st.session_state.active_menu == 'TS_LPB':
        show_ts_lpb_dashboard()

if __name__ == "__main__":
    main()
