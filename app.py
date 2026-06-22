import streamlit as st
import streamlit.components.v1 as components
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import base64, pathlib
import plotly.graph_objects as go
from datetime import datetime, timezone, timedelta

# ───────────────────────────────────────────────────────────
# PAGE CONFIG
# ───────────────────────────────────────────────────────────
st.set_page_config(
    page_title="⚽ 나에게 맞는 프리미어리그 팀은?",
    page_icon="⚽",
    layout="centered",
    initial_sidebar_state="collapsed",
)

KST = timezone(timedelta(hours=9))

# ───────────────────────────────────────────────────────────
# CSS
# ───────────────────────────────────────────────────────────
def inject_css():
    st.markdown("""
<style>
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton, [data-testid="stToolbar"] { display: none !important; }
.stApp { background: #FFFFFF; }
.block-container { padding: 2rem 1.5rem 5rem 1.5rem !important; max-width: 700px !important; }

h1 { color: #1E293B !important; font-weight: 900 !important; letter-spacing: -0.03em !important; line-height: 1.15 !important; }
h2, h3 { color: #1E293B !important; font-weight: 700 !important; }
p { color: #64748B; }

.stProgress > div > div { background: #E2E8F0 !important; border-radius: 99px !important; }
.stProgress > div > div > div {
    background: linear-gradient(90deg, #6D28D9, #8B5CF6, #F59E0B) !important;
    border-radius: 99px !important;
}

[data-testid="baseButton-primary"] {
    background: linear-gradient(135deg, #7C3AED, #5B21B6) !important;
    color: white !important; border: none !important;
    border-radius: 50px !important; padding: 0.85rem 2rem !important;
    font-size: 1.1rem !important; font-weight: 700 !important;
    box-shadow: 0 4px 20px rgba(124,58,237,0.35) !important;
    transition: all 0.2s !important;
}
[data-testid="baseButton-primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(124,58,237,0.5) !important;
}

[data-testid="baseButton-secondary"] {
    background: #F8FAFC !important; color: #334155 !important;
    border: 1.5px solid #E2E8F0 !important;
    border-radius: 14px !important; padding: 1rem 1.4rem !important;
    text-align: left !important; font-size: 0.96rem !important;
    font-weight: 400 !important; line-height: 1.5 !important;
    min-height: 60px !important; transition: all 0.18s ease !important;
    white-space: normal !important;
}
[data-testid="baseButton-secondary"]:hover {
    border-color: rgba(139,92,246,0.6) !important;
    background: #F1F5F9 !important; color: #1E293B !important;
    transform: translateX(5px) !important;
}

.stTabs [data-baseweb="tab-list"] {
    background: #F8FAFC; border-radius: 12px; padding: 4px; gap: 4px;
    border: 1px solid #E2E8F0;
}
.stTabs [data-baseweb="tab"] { color: #1E293B !important; border-radius: 8px !important; font-weight: 600 !important; }
.stTabs [aria-selected="true"] { background: #7C3AED !important; color: #FFFFFF !important; }
.stTabs [aria-selected="false"] { color: #1E293B !important; }
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.5rem !important; }

[data-testid="stMetric"] {
    background: #F8FAFC; border: 1px solid #E2E8F0;
    border-radius: 14px; padding: 1.2rem 1.4rem !important;
}
[data-testid="stMetricValue"] { color: #7C3AED !important; font-size: 1.9rem !important; font-weight: 800 !important; }
[data-testid="stMetricLabel"] { color: #64748B !important; font-size: 0.8rem !important; }
[data-testid="stMetricDelta"] { font-size: 0.8rem !important; }

hr { border-color: #E2E8F0 !important; margin: 1.5rem 0 !important; }
.stCaption { color: #64748B !important; }
[data-testid="stHorizontalBlock"] { gap: 0.75rem !important; }
</style>
""", unsafe_allow_html=True)


# ───────────────────────────────────────────────────────────
# DATA: FIXTURES (Source: ESPN, 2026-27 PL Season, times in UTC)
# BST (Apr-Oct) = UTC+1 | GMT (Oct-Mar) = UTC+0
# ───────────────────────────────────────────────────────────
FIXTURES = {
    "ARS": [
        {"date": "2026-08-21", "h": 19, "m": 0,  "home": "Arsenal",            "away": "Coventry City",      "venue": "Emirates Stadium"},
        {"date": "2026-08-29", "h": 14, "m": 0,  "home": "Aston Villa",         "away": "Arsenal",            "venue": "Villa Park"},
        {"date": "2026-09-05", "h": 14, "m": 0,  "home": "Arsenal",            "away": "Chelsea",             "venue": "Emirates Stadium"},
        {"date": "2026-09-12", "h": 14, "m": 0,  "home": "Sunderland",          "away": "Arsenal",            "venue": "Stadium of Light"},
        {"date": "2026-09-19", "h": 14, "m": 0,  "home": "Brighton",            "away": "Arsenal",            "venue": "Amex Stadium"},
        {"date": "2026-10-10", "h": 14, "m": 0,  "home": "Arsenal",            "away": "Leeds United",        "venue": "Emirates Stadium"},
    ],
    "CHE": [
        {"date": "2026-08-24", "h": 19, "m": 0,  "home": "Fulham",             "away": "Chelsea",             "venue": "Craven Cottage"},
        {"date": "2026-08-29", "h": 14, "m": 0,  "home": "Chelsea",            "away": "Brighton",            "venue": "Stamford Bridge"},
        {"date": "2026-09-05", "h": 14, "m": 0,  "home": "Arsenal",            "away": "Chelsea",             "venue": "Emirates Stadium"},
        {"date": "2026-09-12", "h": 14, "m": 0,  "home": "Chelsea",            "away": "Hull City",           "venue": "Stamford Bridge"},
        {"date": "2026-09-19", "h": 14, "m": 0,  "home": "Brentford",          "away": "Chelsea",             "venue": "Gtech Community Stadium"},
        {"date": "2026-10-10", "h": 14, "m": 0,  "home": "Chelsea",            "away": "Bournemouth",         "venue": "Stamford Bridge"},
    ],
    "LIV": [
        {"date": "2026-08-23", "h": 15, "m": 30, "home": "Newcastle United",    "away": "Liverpool",          "venue": "St. James' Park"},
        {"date": "2026-08-29", "h": 14, "m": 0,  "home": "Liverpool",          "away": "Nottingham Forest",   "venue": "Anfield"},
        {"date": "2026-09-05", "h": 14, "m": 0,  "home": "Ipswich Town",        "away": "Liverpool",          "venue": "Portman Road"},
        {"date": "2026-09-12", "h": 14, "m": 0,  "home": "Liverpool",          "away": "Fulham",              "venue": "Anfield"},
        {"date": "2026-09-19", "h": 14, "m": 0,  "home": "Bournemouth",         "away": "Liverpool",          "venue": "Vitality Stadium"},
    ],
    "MCI": [
        {"date": "2026-08-23", "h": 13, "m": 0,  "home": "Manchester City",     "away": "Bournemouth",        "venue": "Etihad Stadium"},
        {"date": "2026-08-29", "h": 14, "m": 0,  "home": "Crystal Palace",      "away": "Manchester City",    "venue": "Selhurst Park"},
        {"date": "2026-09-05", "h": 14, "m": 0,  "home": "Manchester City",     "away": "Coventry City",      "venue": "Etihad Stadium"},
        {"date": "2026-09-12", "h": 14, "m": 0,  "home": "Manchester United",   "away": "Manchester City",    "venue": "Old Trafford"},
        {"date": "2026-09-19", "h": 14, "m": 0,  "home": "Manchester City",     "away": "Sunderland",         "venue": "Etihad Stadium"},
    ],
    "MNU": [
        {"date": "2026-08-22", "h": 11, "m": 30, "home": "Hull City",           "away": "Manchester United",  "venue": "MKM Stadium"},
        {"date": "2026-08-29", "h": 14, "m": 0,  "home": "Manchester United",   "away": "Ipswich Town",       "venue": "Old Trafford"},
        {"date": "2026-09-05", "h": 14, "m": 0,  "home": "Everton",             "away": "Manchester United",  "venue": "Goodison Park"},
        {"date": "2026-09-12", "h": 14, "m": 0,  "home": "Manchester United",   "away": "Manchester City",    "venue": "Old Trafford"},
        {"date": "2026-09-19", "h": 14, "m": 0,  "home": "Fulham",              "away": "Manchester United",  "venue": "Craven Cottage"},
    ],
    "TOT": [
        {"date": "2026-08-22", "h": 16, "m": 30, "home": "Brentford",           "away": "Tottenham Hotspur",  "venue": "Gtech Community Stadium"},
        {"date": "2026-08-29", "h": 14, "m": 0,  "home": "Tottenham Hotspur",  "away": "Newcastle United",   "venue": "Tottenham Hotspur Stadium"},
        {"date": "2026-09-05", "h": 14, "m": 0,  "home": "Nottm Forest",        "away": "Tottenham Hotspur",  "venue": "City Ground"},
        {"date": "2026-09-12", "h": 14, "m": 0,  "home": "Tottenham Hotspur",  "away": "Everton",            "venue": "Tottenham Hotspur Stadium"},
        {"date": "2026-09-19", "h": 14, "m": 0,  "home": "Tottenham Hotspur",  "away": "Aston Villa",        "venue": "Tottenham Hotspur Stadium"},
    ],
    "NEW": [
        {"date": "2026-08-23", "h": 15, "m": 30, "home": "Newcastle United",    "away": "Liverpool",          "venue": "St. James' Park"},
        {"date": "2026-08-29", "h": 14, "m": 0,  "home": "Tottenham Hotspur",  "away": "Newcastle United",   "venue": "Tottenham Hotspur Stadium"},
        {"date": "2026-09-05", "h": 14, "m": 0,  "home": "Newcastle United",    "away": "Bournemouth",        "venue": "St. James' Park"},
        {"date": "2026-09-12", "h": 14, "m": 0,  "home": "Leeds United",        "away": "Newcastle United",   "venue": "Elland Road"},
        {"date": "2026-09-19", "h": 14, "m": 0,  "home": "Newcastle United",    "away": "Hull City",          "venue": "St. James' Park"},
        {"date": "2026-10-10", "h": 14, "m": 0,  "home": "Coventry City",       "away": "Newcastle United",   "venue": "CBS Arena"},
    ],
    "AVL": [
        {"date": "2026-08-23", "h": 13, "m": 0,  "home": "Brighton",            "away": "Aston Villa",        "venue": "Amex Stadium"},
        {"date": "2026-08-29", "h": 14, "m": 0,  "home": "Aston Villa",         "away": "Arsenal",            "venue": "Villa Park"},
        {"date": "2026-09-05", "h": 14, "m": 0,  "home": "Hull City",           "away": "Aston Villa",        "venue": "MKM Stadium"},
        {"date": "2026-09-12", "h": 14, "m": 0,  "home": "Aston Villa",         "away": "Nottm Forest",       "venue": "Villa Park"},
        {"date": "2026-09-19", "h": 14, "m": 0,  "home": "Tottenham Hotspur",  "away": "Aston Villa",        "venue": "Tottenham Hotspur Stadium"},
        {"date": "2026-10-10", "h": 14, "m": 0,  "home": "Aston Villa",         "away": "Brentford",          "venue": "Villa Park"},
    ],
}

# ───────────────────────────────────────────────────────────
# DATA: TEAM INFO
# ───────────────────────────────────────────────────────────
TEAM_INFO = {
    "ARS": {
        "name": "Arsenal", "nickname": "The Gunners",
        "badge": "🔴", "logo": "https://resources.premierleague.com/premierleague/badges/50/t3.png",
        "tagline": "에미레이트의 예술가들",
        "color": "#EF0107", "bg": "#FEF2F2",
        "bg_img": "arsenal.jpg",
        "youtube": "_1Y6dvQrBkc",
        "founded": 1886, "stadium": "Emirates Stadium", "capacity": "60,704",
        "manager": "미켈 아르테타 (Mikel Arteta)",
        "players": ["부카요 사카", "마르틴 외데고르", "카이 하베르츠"],
        "style": "유려한 패스 연결 · 조직적 압박 · 위치 선점 축구",
        "desc": "아르센 벵거의 아름다운 축구 철학이 뿌리내린 클럽. 2003-04 무패 우승(인빈시블즈) 이후 20여 년 만에 2025-26 시즌 프리미어리그 우승을 탈환하며 드디어 정상에 복귀했다. 아르테타의 치밀한 전술과 사카, 외데고르, 하베르츠 등 황금 세대가 만들어낸 역사적 시즌.",
        "reason": "전술을 분석하며 경기를 즐기는 당신에게, 아스날의 지능적인 패스 축구는 매 경기가 하나의 퍼즐이 될 거예요. 20년 만에 리그 정상에 복귀한 팀의 다음 여정을 함께하세요.",
        "radar": [85, 65, 45, 70, 55, 90],
    },
    "CHE": {
        "name": "Chelsea", "nickname": "The Blues",
        "badge": "🔵", "logo": "https://resources.premierleague.com/premierleague/badges/50/t8.png",
        "tagline": "런던의 화려한 귀족",
        "color": "#1E90FF", "bg": "#EFF6FF",
        "bg_img": "bluesstad.jpg",
        "youtube": "DKR_IkLqpaM",
        "founded": 1905, "stadium": "Stamford Bridge", "capacity": "40,341",
        "manager": "샤비 알론소 (Xabi Alonso)",
        "players": ["콜 팔머", "엔소 페르난데스", "모이세스 카이세도"],
        "style": "창의적이고 화려한 공격 축구 · 개인기 강조",
        "desc": "챔피언스리그 2회, 리그 6회 우승의 런던 대표 클럽. 2025-26 시즌은 감독 교체가 잦았던 혼란기였으나, 시즌 막바지 레버쿠젠 무패 우승의 주역 샤비 알론소 감독을 선임하며 새 시대를 열었다. 콜 팔머, 엔소 페르난데스 등 핵심 자원과 함께 재건에 나선다.",
        "reason": "화려하고 세련된 것에 끌리는 당신에게, 첼시의 세계적 브랜드와 스타 선수들의 개인기는 최고의 즐거움을 선사할 거예요. 샤비 알론소의 새로운 축구와 콜 팔머의 천재적 활약을 주목하세요.",
        "radar": [45, 55, 65, 60, 75, 60],
    },
    "LIV": {
        "name": "Liverpool", "nickname": "The Reds",
        "badge": "🔴", "logo": "https://resources.premierleague.com/premierleague/badges/50/t14.png",
        "tagline": "안필드의 전설 — 너는 혼자 걷지 않는다",
        "color": "#C8102E", "bg": "#FEF2F2",
        "bg_img": "liverstad.jpg",
        "youtube": "SV88XvZMMqI",
        "founded": 1892, "stadium": "Anfield", "capacity": "61,276",
        "manager": "아르네 슬롯 (Arne Slot)",
        "players": ["모하메드 살라", "알렉산더 이삭", "플로리안 비르츠"],
        "style": "조직적 공격 전개 · 유연한 전술 변환 · 두터운 선수층",
        "desc": '"You\'ll Never Walk Alone" — 전 세계 축구 찬가의 원조. 챔피언스리그 6회, 리그 우승 20회. 아르네 슬롯 감독 부임 첫 해(2024-25) 프리미어리그 우승을 달성했고, 이삭·비르츠·프림퐁 등 대형 영입으로 선수단을 대폭 강화했다.',
        "reason": "감정을 함께 나누고 뜨거운 응원 문화를 원하는 당신에게, 안필드에서 수만 명이 함께 부르는 '너는 혼자 걷지 않는다'는 평생 잊지 못할 경험이 될 거예요. 살라·이삭·비르츠의 공격 조합도 기대하세요.",
        "radar": [65, 100, 80, 90, 80, 70],
    },
    "MCI": {
        "name": "Manchester City", "nickname": "The Citizens",
        "badge": "🔵", "logo": "https://resources.premierleague.com/premierleague/badges/50/t43.png",
        "tagline": "전술의 완성체 — 지배의 시대",
        "color": "#6CABDD", "bg": "#EFF6FF",
        "bg_img": "mancity.jpeg",
        "youtube": "8cfwD8ybFfw",
        "founded": 1880, "stadium": "Etihad Stadium", "capacity": "55,017",
        "manager": "펩 과르디올라 (Pep Guardiola)",
        "players": ["에를링 홀란", "케빈 데 브라위너", "필 포든"],
        "style": "완벽한 위치 선점 축구 · 압도적 볼 점유",
        "desc": "펩 과르디올라가 구현한 현대 축구의 완성형. 2022-23 3관왕 달성. 데이터 분석과 전술의 결합으로 프리미어리그를 지배해온 팀.",
        "reason": "분석적이고 완성도 높은 축구를 추구하는 당신에게, Man City의 포지셔널 플레이는 매 경기 축구의 수준을 다시 생각하게 만들 거예요. 홀란의 골 결정력은 덤.",
        "radar": [100, 60, 30, 50, 100, 75],
    },
    "MNU": {
        "name": "Manchester United", "nickname": "The Red Devils",
        "badge": "🔴", "logo": "https://resources.premierleague.com/premierleague/badges/50/t1.png",
        "tagline": "세계 최고의 이름 — 레전드의 클럽",
        "color": "#DA291C", "bg": "#FEF2F2",
        "bg_img": "manuni.jpg",
        "youtube": "w-zklNRLVlU",
        "founded": 1878, "stadium": "Old Trafford", "capacity": "74,879",
        "manager": "마이클 캐릭 (Michael Carrick)",
        "players": ["브루노 페르난데스", "라스무스 회이룬", "마누엘 우가르테"],
        "style": "공격적이고 극적인 역전의 전통 · 끝까지 포기하지 않는 축구",
        "desc": "알렉스 퍼거슨 경의 26년 황금기. 리그 최다 우승 20회, 챔피언스리그 3회. 세계 최대 팬덤의 클럽. 2026년 1월 아모림 후임으로 부임한 마이클 캐릭 감독이 반 시즌 만에 3위·챔피언스리그 진출을 이끌며 정식 감독으로 선임되었다. 브루노 페르난데스가 프리미어리그 단일 시즌 최다 도움(21개) 신기록을 세우며 올해의 선수에 선정.",
        "reason": "역사와 전설, 극적인 순간들에 끌리는 당신. '꿈의 극장' 올드 트래포드라는 이름 하나만으로 세계 어디서나 통하는 자부심을 느낄 수 있어요. 캐릭 감독과 함께 시작된 부활의 이야기를 지켜보세요.",
        "radar": [45, 80, 90, 100, 85, 55],
    },
    "TOT": {
        "name": "Tottenham Hotspur", "nickname": "Spurs",
        "badge": "⚪", "logo": "https://resources.premierleague.com/premierleague/badges/50/t6.png",
        "tagline": "드라마와 아름다움의 상징",
        "color": "#4A5FCC", "bg": "#EEF2FF",
        "bg_img": "totten.jpg",
        "youtube": "hYX6HQ4y1XU",
        "founded": 1882, "stadium": "Tottenham Hotspur Stadium", "capacity": "62,850",
        "manager": "로베르토 데 제르비 (Roberto De Zerbi)",
        "players": ["크리스티안 로메로", "제임스 매디슨", "도미닉 솔란케"],
        "style": "아름답고 공격적인 축구 · 예측 불가능한 토트넘만의 방식",
        "desc": "2025-26 시즌 감독 3번 교체와 강등 위기라는 클럽 역사상 최악의 시련을 겪었지만, 시즌 막판 데 제르비 감독의 부임으로 극적 잔류에 성공했다. 손흥민은 2025년 미국 로스앤젤레스로 이적했지만, 로메로 주장을 중심으로 재건을 시작한다.",
        "reason": "아름다운 축구와 드라마틱한 감정기복을 즐기는 당신에게 딱! 최악의 시련을 이겨내고 데 제르비와 함께 재건하는 여정은 진정한 팬만이 함께할 수 있는 특별한 경험이에요. 심장이 약한 분은 주의!",
        "radar": [70, 70, 95, 65, 35, 85],
    },
    "NEW": {
        "name": "Newcastle United", "nickname": "The Magpies",
        "badge": "⬛", "logo": "https://resources.premierleague.com/premierleague/badges/50/t4.png",
        "tagline": "조디의 영혼 — 가장 뜨거운 응원",
        "color": "#FFD700", "bg": "#F5F5F4",
        "bg_img": "newcastle.jpg",
        "youtube": "FaFMfjhavB4",
        "founded": 1892, "stadium": "St. James' Park", "capacity": "52,258",
        "manager": "에디 하우 (Eddie Howe)",
        "players": ["브루노 기마랑에스", "앤서니 엘랑가", "산드로 토날리"],
        "style": "탄탄한 조직 수비 · 빠른 역습 · 폭발적 홈 에너지",
        "desc": "사우디 컨소시엄 인수(2021) 이후 급성장했으나, 2025-26 시즌 이삭(리버풀)과 고든(바르셀로나)이 이적하며 재건기에 돌입했다. St. James' Park의 팬 분위기는 여전히 프리미어리그 최고 수준. 에디 하우 감독 아래 새로운 도약을 준비 중.",
        "reason": "거칠고 뜨거운 팬 문화와 약자의 성장 이야기에 끌리는 당신. 핵심 선수를 잃었지만 다시 일어서는 뉴캐슬 팬들의 충성심은 세계 최고예요.",
        "radar": [50, 100, 65, 65, 45, 45],
    },
    "AVL": {
        "name": "Aston Villa", "nickname": "The Villans",
        "badge": "🟣", "logo": "https://resources.premierleague.com/premierleague/badges/50/t7.png",
        "tagline": "잠자던 거인의 귀환",
        "color": "#95BFE5", "bg": "#F0F4FF",
        "bg_img": "aston.jpg",
        "youtube": "RNeantk2unc",
        "founded": 1874, "stadium": "Villa Park", "capacity": "42,682",
        "manager": "우나이 에메리 (Unai Emery)",
        "players": ["올리 왓킨스", "레온 베일리", "유리 틸레만스"],
        "style": "전술적 조직 공격 · 젊고 역동적인 선수단",
        "desc": "영국에서 가장 오래된 클럽 중 하나 (1874년 창단). 1982 유러피언컵(현 챔피언스리그) 우승. 우나이 에메리의 전술 마법으로 챔피언스리그 복귀에 이어 2025-26 시즌 유로파리그 우승까지 달성하며 유럽 무대에서 화려하게 부활했다.",
        "reason": "역사 깊은 클럽과 함께 성장하며, 조용히 빛나는 팀을 원하는 당신에게. 유로파리그 우승의 기쁨을 함께한 에메리 감독의 전술 빌딩은 현재진행형이에요.",
        "radar": [65, 75, 55, 80, 50, 65],
    },
}

RADAR_LABELS = ["Tactical", "Fan Passion", "Drama", "Heritage", "Trophy", "Beauty"]
RADAR_LABELS_KR = ["전술", "팬 열정", "드라마", "역사", "트로피", "미학"]
TEAMS = list(TEAM_INFO.keys())

SEASON_LABELS = [
    "03-04","04-05","05-06","06-07","07-08","08-09","09-10","10-11",
    "11-12","12-13","13-14","14-15","15-16","16-17","17-18","18-19",
    "19-20","20-21","21-22","22-23","23-24","24-25","25-26",
]
SEASON_RANKS = {
    "ARS": [1,2,4,4,3,4,3,4,3,4,4,3,2,5,6,5,8,8,5,2,2,2,1],
    "CHE": [2,1,1,2,2,3,1,2,6,3,3,1,10,1,5,3,4,4,3,12,6,4,10],
    "LIV": [4,5,3,3,4,2,7,6,8,7,2,6,8,4,4,2,1,3,2,5,3,1,5],
    "MCI": [16,8,15,14,9,10,5,3,1,2,1,2,4,3,1,1,2,1,1,1,1,3,2],
    "MNU": [3,3,2,1,1,1,2,1,2,1,7,4,5,6,2,6,3,2,6,3,8,15,3],
    "TOT": [14,9,5,5,11,8,4,5,4,5,6,5,3,2,3,4,6,7,4,8,5,17,17],
    "NEW": [5,14,7,13,12,18,None,12,5,16,10,15,18,None,10,13,13,12,11,4,7,5,12],
    "AVL": [6,10,16,11,6,6,6,9,16,15,15,17,20,None,None,None,17,11,14,7,4,6,4],
}

# ───────────────────────────────────────────────────────────
# DATA: 20 QUESTIONS
# ───────────────────────────────────────────────────────────
QUESTIONS = [
    {"q": "끌리는 색깔은?",
     "choices": [("🔴","빨간색"),("🔵","파란색"),("⚫","블랙 & 화이트"),("🟤","클라렛(와인색)")],
     "weights": [{"ARS":2,"CHE":0,"LIV":3,"MCI":0,"MNU":3,"TOT":0,"NEW":0,"AVL":0},{"ARS":0,"CHE":3,"LIV":0,"MCI":3,"MNU":0,"TOT":0,"NEW":0,"AVL":1},{"ARS":0,"CHE":0,"LIV":0,"MCI":0,"MNU":0,"TOT":3,"NEW":3,"AVL":0},{"ARS":0,"CHE":0,"LIV":0,"MCI":0,"MNU":0,"TOT":0,"NEW":0,"AVL":3}]},
    {"q": "가장 보고 싶은 축구 스타일은?",
     "choices": [("🎯","한 치의 오차도 없는 완벽한 패스워크와 압도적 점유율"),("⚡","빈 공간을 찌르는 날카로운 역습과 빠른 역습"),("🔥","전원이 미친 듯이 달려드는 고강도 압박 축구"),("🎨","선수 개인의 창의성이 폭발하는 자유로운 축구")],
     "weights": [{"ARS":2,"CHE":0,"LIV":0,"MCI":3,"MNU":0,"TOT":1,"NEW":0,"AVL":1},{"ARS":0,"CHE":0,"LIV":0,"MCI":0,"MNU":2,"TOT":0,"NEW":3,"AVL":2},{"ARS":1,"CHE":0,"LIV":3,"MCI":0,"MNU":1,"TOT":0,"NEW":2,"AVL":1},{"ARS":0,"CHE":3,"LIV":0,"MCI":0,"MNU":0,"TOT":3,"NEW":0,"AVL":0}]},
    {"q": "경기장에서 가장 원하는 분위기는?",
     "choices": [("🎵","5만 관중이 한 목소리로 응원가를 부르는 떼창"),("💥","결정적 순간에 폭발하는 극적인 환호"),("🏛️","역사와 전통이 느껴지는 고풍스러운 홈구장"),("🏟️","최첨단 시설의 세련되고 모던한 관람 경험")],
     "weights": [{"ARS":0,"CHE":0,"LIV":3,"MCI":0,"MNU":1,"TOT":0,"NEW":3,"AVL":1},{"ARS":1,"CHE":1,"LIV":1,"MCI":0,"MNU":3,"TOT":3,"NEW":1,"AVL":0},{"ARS":2,"CHE":0,"LIV":1,"MCI":0,"MNU":2,"TOT":0,"NEW":1,"AVL":3},{"ARS":0,"CHE":2,"LIV":0,"MCI":3,"MNU":0,"TOT":2,"NEW":0,"AVL":0}]},
    {"q": "이런 감독이 좋다",
     "choices": [("📊","데이터와 전술로 상대를 완벽히 분석하는 교수 타입"),("🔥","위기 상황에서 팀을 하나로 뭉치게 하는 투사 타입"),("🎨","선수에게 자유를 주고 창의성을 폭발시키는 예술가 타입"),("🧱","묵묵히 체계를 쌓아 팀을 키우는 빌더 타입")],
     "weights": [{"ARS":2,"CHE":0,"LIV":1,"MCI":3,"MNU":0,"TOT":0,"NEW":0,"AVL":1},{"ARS":0,"CHE":0,"LIV":2,"MCI":0,"MNU":3,"TOT":1,"NEW":2,"AVL":0},{"ARS":0,"CHE":3,"LIV":0,"MCI":0,"MNU":0,"TOT":3,"NEW":0,"AVL":0},{"ARS":1,"CHE":0,"LIV":0,"MCI":0,"MNU":0,"TOT":0,"NEW":2,"AVL":3}]},
    {"q": "클럽의 이적시장 정책으로 가장 공감되는 것은?",
     "choices": [("💰","돈을 아끼지 않고 세계 최고의 스타를 영입한다"),("📈","데이터 분석으로 저평가된 보석을 발굴한다"),("🎓","자체 유스 아카데미에서 선수를 직접 키운다"),("⚖️","합리적 예산 안에서 팀에 딱 맞는 선수를 찾는다")],
     "weights": [{"ARS":0,"CHE":3,"LIV":2,"MCI":2,"MNU":2,"TOT":0,"NEW":0,"AVL":0},{"ARS":3,"CHE":0,"LIV":1,"MCI":1,"MNU":0,"TOT":0,"NEW":1,"AVL":1},{"ARS":1,"CHE":0,"LIV":0,"MCI":0,"MNU":1,"TOT":2,"NEW":1,"AVL":1},{"ARS":0,"CHE":0,"LIV":0,"MCI":0,"MNU":0,"TOT":1,"NEW":3,"AVL":3}]},
    {"q": "끌리는 구단주·경영 스타일은?",
     "choices": [("🏦","중동 자본의 막대한 투자로 팀을 키우는 방식"),("💼","미국식 경영 방식, 구단 가치와 수익 극대화"),("🤝","팬과 지역사회를 최우선으로 생각하는 운영"),("📉","적자 없이 재정 건전성을 유지하며 성장하는 운영")],
     "weights": [{"ARS":0,"CHE":1,"LIV":0,"MCI":3,"MNU":0,"TOT":0,"NEW":3,"AVL":0},{"ARS":1,"CHE":2,"LIV":1,"MCI":0,"MNU":3,"TOT":0,"NEW":0,"AVL":1},{"ARS":0,"CHE":0,"LIV":3,"MCI":0,"MNU":0,"TOT":1,"NEW":1,"AVL":2},{"ARS":2,"CHE":0,"LIV":0,"MCI":0,"MNU":0,"TOT":3,"NEW":0,"AVL":2}]},
    {"q": "팀의 글로벌 이미지로 가장 중요한 것은?",
     "choices": [("🌍","전 세계 어디서나 알아보는 초대형 인지도"),("🏘️","지역 커뮤니티와 뿌리 깊은 유대감"),("📱","온라인 소통으로 아시아·전 세계 팬과 교류"),("📈","실력으로 조용히 증명해서 점점 인정받는 클럽")],
     "weights": [{"ARS":1,"CHE":2,"LIV":1,"MCI":2,"MNU":3,"TOT":0,"NEW":0,"AVL":0},{"ARS":0,"CHE":0,"LIV":3,"MCI":0,"MNU":0,"TOT":0,"NEW":3,"AVL":2},{"ARS":2,"CHE":2,"LIV":0,"MCI":1,"MNU":1,"TOT":2,"NEW":0,"AVL":0},{"ARS":0,"CHE":0,"LIV":0,"MCI":0,"MNU":0,"TOT":1,"NEW":1,"AVL":3}]},
    {"q": "가장 가슴 뛰는 팀의 현재 상황은?",
     "choices": [("🏆","오랜 기다림 끝에 드디어 정상에 선 챔피언"),("👑","매년 우승을 다투는 압도적 강자"),("🔄","어둠을 지나 부활의 기지개를 켜는 재건 중인 명문"),("🚀","바닥에서부터 올라오는 약자의 성장 이야기")],
     "weights": [{"ARS":3,"CHE":0,"LIV":2,"MCI":0,"MNU":0,"TOT":0,"NEW":0,"AVL":2},{"ARS":0,"CHE":0,"LIV":1,"MCI":3,"MNU":0,"TOT":0,"NEW":0,"AVL":0},{"ARS":0,"CHE":3,"LIV":0,"MCI":0,"MNU":3,"TOT":1,"NEW":0,"AVL":0},{"ARS":0,"CHE":0,"LIV":0,"MCI":0,"MNU":0,"TOT":3,"NEW":3,"AVL":1}]},
    {"q": "끌리는 도시의 분위기는?",
     "choices": [("🎭","트렌디하고 다문화적인 대도시 런던"),("🏗️","산업혁명의 도시, 노동자 문화의 맨체스터"),("🎸","비틀즈와 항구 문화의 감성 도시 리버풀"),("🏰","오래된 성당과 탄광 문화의 투박한 매력")],
     "weights": [{"ARS":2,"CHE":3,"LIV":0,"MCI":0,"MNU":0,"TOT":2,"NEW":0,"AVL":0},{"ARS":0,"CHE":0,"LIV":0,"MCI":2,"MNU":3,"TOT":0,"NEW":0,"AVL":0},{"ARS":0,"CHE":0,"LIV":3,"MCI":0,"MNU":0,"TOT":0,"NEW":0,"AVL":0},{"ARS":0,"CHE":0,"LIV":0,"MCI":0,"MNU":0,"TOT":0,"NEW":3,"AVL":3}]},
    {"q": "가장 좋아하는 라이벌전의 느낌은?",
     "choices": [("🔥","같은 도시 팀끼리의 자존심 싸움"),("⚔️","역사가 얽힌 숙명의 라이벌"),("🌋","지역 전체의 자부심이 걸린 지역 맞대결"),("🏆","1위 vs 2위, 정상을 건 대결")],
     "weights": [{"ARS":0,"CHE":1,"LIV":2,"MCI":2,"MNU":2,"TOT":0,"NEW":0,"AVL":0},{"ARS":3,"CHE":0,"LIV":0,"MCI":0,"MNU":1,"TOT":3,"NEW":0,"AVL":0},{"ARS":0,"CHE":0,"LIV":1,"MCI":0,"MNU":0,"TOT":0,"NEW":3,"AVL":3},{"ARS":0,"CHE":2,"LIV":1,"MCI":3,"MNU":1,"TOT":0,"NEW":0,"AVL":1}]},
    {"q": "내 성격에 가장 가까운 것은?",
     "choices": [("📊","계획적이고 분석적이다. 감정보다 논리가 앞선다"),("🔥","감정적이고 열정적이다. 온몸으로 느끼며 산다"),("✨","화려하고 세련된 것에 끌린다. 유행에 민감하다"),("🪨","조용히 끈기 있게 자기 길을 가는 편이다")],
     "weights": [{"ARS":2,"CHE":0,"LIV":0,"MCI":3,"MNU":0,"TOT":1,"NEW":0,"AVL":1},{"ARS":0,"CHE":0,"LIV":3,"MCI":0,"MNU":2,"TOT":1,"NEW":3,"AVL":1},{"ARS":0,"CHE":3,"LIV":0,"MCI":1,"MNU":2,"TOT":1,"NEW":0,"AVL":0},{"ARS":1,"CHE":0,"LIV":0,"MCI":0,"MNU":0,"TOT":2,"NEW":1,"AVL":3}]},
    {"q": "가장 흥미로운 스타 선수 유형은?",
     "choices": [("🎯","경기를 읽는 천재 경기 조율자"),("💨","상대 수비를 혼자 돌파하는 돌파형 선수"),("🦁","골 앞에서 본능이 폭발하는 골잡이"),("🛡️","팀을 위해 보이지 않는 곳에서 뛰는 영웅")],
     "weights": [{"ARS":2,"CHE":0,"LIV":0,"MCI":3,"MNU":1,"TOT":0,"NEW":0,"AVL":1},{"ARS":0,"CHE":3,"LIV":0,"MCI":0,"MNU":0,"TOT":3,"NEW":0,"AVL":0},{"ARS":0,"CHE":0,"LIV":3,"MCI":1,"MNU":1,"TOT":0,"NEW":1,"AVL":1},{"ARS":1,"CHE":0,"LIV":0,"MCI":0,"MNU":1,"TOT":0,"NEW":3,"AVL":2}]},
    {"q": "경기에서 가장 감동받는 순간은?",
     "choices": [("✅","연습한 전술 패턴이 경기에서 완벽하게 작동할 때"),("🤝","팬들의 응원과 선수들이 완전히 하나가 되는 순간"),("🎭","불가능해 보이던 역전이 극적으로 이루어질 때"),("🌱","무명의 어린 선수가 처음 빅무대에서 빛날 때")],
     "weights": [{"ARS":2,"CHE":0,"LIV":0,"MCI":3,"MNU":0,"TOT":1,"NEW":0,"AVL":1},{"ARS":0,"CHE":0,"LIV":3,"MCI":0,"MNU":1,"TOT":0,"NEW":3,"AVL":2},{"ARS":0,"CHE":1,"LIV":1,"MCI":0,"MNU":3,"TOT":3,"NEW":1,"AVL":0},{"ARS":2,"CHE":1,"LIV":0,"MCI":0,"MNU":0,"TOT":1,"NEW":1,"AVL":3}]},
    {"q": "팀의 응원 문화 중 가장 끌리는 것은?",
     "choices": [("🎶","경기 전 전 관중이 부르는 전설적인 응원가"),("👕","관중석에서 상의를 벗고 환호하는 거친 열정"),("📢","위기의 순간 더 크게 울려퍼지는 끈끈한 응원"),("🤫","절제된 분위기 속 핵심 순간에만 터지는 세련된 응원")],
     "weights": [{"ARS":0,"CHE":0,"LIV":3,"MCI":0,"MNU":1,"TOT":0,"NEW":1,"AVL":1},{"ARS":0,"CHE":0,"LIV":0,"MCI":0,"MNU":0,"TOT":1,"NEW":3,"AVL":1},{"ARS":1,"CHE":0,"LIV":1,"MCI":0,"MNU":2,"TOT":3,"NEW":1,"AVL":2},{"ARS":2,"CHE":3,"LIV":0,"MCI":3,"MNU":0,"TOT":0,"NEW":0,"AVL":0}]},
    {"q": "클럽의 역사에서 가장 끌리는 요소는?",
     "choices": [("🏛️","100년이 넘는 전통과 수많은 트로피의 무게"),("🔄","몰락과 부활을 반복하는 드라마틱한 역사"),("💸","거대 자본 투입으로 급성장한 현대적 성공 스토리"),("🌿","오래된 뿌리와 지역 자부심에서 조용히 피어난 성장")],
     "weights": [{"ARS":2,"CHE":0,"LIV":2,"MCI":0,"MNU":3,"TOT":0,"NEW":0,"AVL":1},{"ARS":0,"CHE":2,"LIV":0,"MCI":0,"MNU":1,"TOT":3,"NEW":1,"AVL":0},{"ARS":0,"CHE":1,"LIV":0,"MCI":3,"MNU":0,"TOT":0,"NEW":2,"AVL":0},{"ARS":0,"CHE":0,"LIV":0,"MCI":0,"MNU":0,"TOT":0,"NEW":1,"AVL":3}]},
    {"q": "팀이 0-2로 지고 있을 때, 나의 반응은?",
     "choices": [("🔍","왜 지고 있는지 전술적으로 분석하기 시작한다"),("📣","더 크게 응원한다. 포기란 없다"),("💪","어차피 역전한다고 굳게 믿는다"),("😰","불안하지만 끝까지 화면에서 눈을 못 뗀다")],
     "weights": [{"ARS":2,"CHE":1,"LIV":0,"MCI":3,"MNU":0,"TOT":1,"NEW":0,"AVL":1},{"ARS":0,"CHE":0,"LIV":3,"MCI":0,"MNU":1,"TOT":0,"NEW":3,"AVL":1},{"ARS":0,"CHE":1,"LIV":1,"MCI":0,"MNU":3,"TOT":2,"NEW":1,"AVL":0},{"ARS":1,"CHE":0,"LIV":0,"MCI":0,"MNU":0,"TOT":3,"NEW":0,"AVL":3}]},
    {"q": "가장 끌리는 이야기 유형은?",
     "choices": [("🏗️","시스템이 차곡차곡 쌓여 결국 정상에 오르는 이야기"),("💪","고난과 역경을 이겨내고 전설이 된 이야기"),("💎","막대한 투자와 스타가 만나 정점을 찍는 이야기"),("🚀","아무도 몰랐던 팀이 무대를 뒤집는 이야기")],
     "weights": [{"ARS":3,"CHE":0,"LIV":0,"MCI":2,"MNU":0,"TOT":0,"NEW":0,"AVL":1},{"ARS":0,"CHE":0,"LIV":3,"MCI":0,"MNU":3,"TOT":1,"NEW":1,"AVL":0},{"ARS":0,"CHE":3,"LIV":0,"MCI":1,"MNU":1,"TOT":0,"NEW":2,"AVL":0},{"ARS":0,"CHE":0,"LIV":0,"MCI":0,"MNU":0,"TOT":2,"NEW":2,"AVL":3}]},
    {"q": "친구에게 내 팀을 소개한다면?",
     "choices": [("🧠","이 팀은 현재 가장 완성도 높은 축구를 한다"),("🎤","우리 팬 문화 한 번 경험해봐, 전율이 올 거야"),("👑","역사와 레전드의 무게가 다른 클럽이야"),("⬆️","지금 가장 뜨겁게 성장 중인 팀이야")],
     "weights": [{"ARS":2,"CHE":0,"LIV":0,"MCI":3,"MNU":0,"TOT":1,"NEW":0,"AVL":0},{"ARS":0,"CHE":0,"LIV":3,"MCI":0,"MNU":1,"TOT":0,"NEW":3,"AVL":1},{"ARS":0,"CHE":2,"LIV":1,"MCI":0,"MNU":3,"TOT":0,"NEW":0,"AVL":1},{"ARS":1,"CHE":1,"LIV":0,"MCI":0,"MNU":0,"TOT":2,"NEW":1,"AVL":3}]},
    {"q": "나의 응원 철학은?",
     "choices": [("🎯","이기든 지든 팀 축구의 완성도를 본다"),("❤️","고통도 기쁨도 함께해야 진짜 팬이다"),("🏆","결과가 전부다. 트로피가 답이다"),("🌱","팀과 함께 성장하는 여정 자체가 목적이다")],
     "weights": [{"ARS":2,"CHE":0,"LIV":0,"MCI":3,"MNU":0,"TOT":2,"NEW":0,"AVL":1},{"ARS":0,"CHE":0,"LIV":3,"MCI":0,"MNU":2,"TOT":1,"NEW":3,"AVL":1},{"ARS":0,"CHE":3,"LIV":0,"MCI":2,"MNU":2,"TOT":0,"NEW":0,"AVL":0},{"ARS":1,"CHE":0,"LIV":0,"MCI":0,"MNU":0,"TOT":2,"NEW":1,"AVL":3}]},
    {"q": "마지막. 당신이 축구를 통해 얻고 싶은 것은?",
     "choices": [("🧠","전술의 완성도에서 오는 지적 만족감"),("🌊","수만 명과 같은 감정을 공유하는 압도적 경험"),("🌍","세계 최고의 이름과 함께한다는 자부심"),("✨","함께 성장하며 언젠가 올 그날을 기다리는 설렘")],
     "weights": [{"ARS":2,"CHE":0,"LIV":0,"MCI":3,"MNU":0,"TOT":1,"NEW":0,"AVL":1},{"ARS":0,"CHE":0,"LIV":3,"MCI":0,"MNU":1,"TOT":0,"NEW":3,"AVL":1},{"ARS":0,"CHE":3,"LIV":0,"MCI":1,"MNU":3,"TOT":0,"NEW":0,"AVL":0},{"ARS":1,"CHE":0,"LIV":0,"MCI":0,"MNU":0,"TOT":3,"NEW":1,"AVL":3}]},
]

PROGRESS_MESSAGES = {
    0:  "⚽ 시작해볼까요?",
    4:  "잘 가고 있어요! 계속해봐요",
    9:  "절반 왔어요! 🔥",
    14: "거의 다 왔어요! 집중!",
    19: "마지막 질문이에요! ✨",
}

# ───────────────────────────────────────────────────────────
# HELPERS
# ───────────────────────────────────────────────────────────
def calculate_scores(answers: dict) -> dict:
    scores = {t: 0 for t in TEAMS}
    for q_idx, choice_idx in answers.items():
        w = QUESTIONS[q_idx]["weights"][choice_idx]
        for t, v in w.items():
            scores[t] += v
    max_s = max(scores.values()) or 1
    return {t: round(s / max_s * 100) for t, s in scores.items()}


def get_next_fixture(team_code: str):
    now = datetime.now(timezone.utc)
    for fx in FIXTURES.get(team_code, []):
        y, mo, d = map(int, fx["date"].split("-"))
        dt = datetime(y, mo, d, fx["h"], fx["m"], tzinfo=timezone.utc)
        if dt > now:
            return fx, dt
    return None, None


def fmt_kst(dt: datetime) -> str:
    kst_dt = dt.astimezone(KST)
    weekdays = ["월","화","수","목","금","토","일"]
    wd = weekdays[kst_dt.weekday()]
    return kst_dt.strftime(f"%Y년 %m월 %d일 ({wd}) %H:%M KST")


def fmt_uk(h, m) -> str:
    ampm = "p.m." if h >= 12 else "a.m."
    hh = h if h <= 12 else h - 12
    return f"{hh}:{m:02d} {ampm} UK"


def draw_radar(team_code: str) -> plt.Figure:
    info = TEAM_INFO[team_code]
    vals = info["radar"]
    color = info["color"]
    N = len(RADAR_LABELS)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    vals_plot = vals + [vals[0]]
    angles_plot = angles + [angles[0]]

    fig, ax = plt.subplots(figsize=(4.5, 4.5), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor("#FFFFFF")
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(["", "", "", "", ""], fontsize=0)
    ax.yaxis.grid(True, color="#E2E8F0", linewidth=0.8)
    ax.xaxis.grid(True, color="#E2E8F0", linewidth=0.8)
    ax.plot(angles_plot, vals_plot, color=color, linewidth=2.5)
    ax.fill(angles_plot, vals_plot, color=color, alpha=0.25)
    ax.set_xticks(angles)
    ax.set_xticklabels(RADAR_LABELS, color="#64748B", fontsize=8.5)
    ax.spines["polar"].set_color("#E2E8F0")
    plt.tight_layout(pad=0.5)
    return fig


def draw_season_chart(team_code: str) -> go.Figure:
    ranks = SEASON_RANKS[team_code]
    color = TEAM_INFO[team_code]["color"]
    name = TEAM_INFO[team_code]["name"]

    x_pl, y_pl, hover_pl = [], [], []
    for i, r in enumerate(ranks):
        if r is not None:
            x_pl.append(SEASON_LABELS[i])
            y_pl.append(r)
            suffix = "st" if r == 1 else "nd" if r == 2 else "rd" if r == 3 else "th"
            hover_pl.append(f"<b>{SEASON_LABELS[i]}</b><br>{r}{suffix}")
        else:
            x_pl.append(SEASON_LABELS[i])
            y_pl.append(None)
            hover_pl.append(f"<b>{SEASON_LABELS[i]}</b><br>2부 리그")

    fig = go.Figure()
    fig.add_hrect(y0=0.5, y1=4.5, fillcolor="#F0FDF4", line_width=0, layer="below")
    fig.add_hrect(y0=17.5, y1=20.5, fillcolor="#FEE2E2", line_width=0, layer="below")

    fig.add_trace(go.Scatter(
        x=x_pl, y=y_pl, mode="lines+markers",
        line=dict(color=color, width=3),
        marker=dict(size=8, color=color, line=dict(color="white", width=1.5)),
        hovertext=hover_pl, hoverinfo="text",
        connectgaps=False,
    ))

    none_idxs = [i for i, r in enumerate(ranks) if r is None]
    if none_idxs:
        fig.add_trace(go.Scatter(
            x=[SEASON_LABELS[i] for i in none_idxs],
            y=[20] * len(none_idxs),
            mode="markers+text",
            marker=dict(size=10, color="#FCA5A5", symbol="x"),
            text=["2부"] * len(none_idxs),
            textposition="top center",
            textfont=dict(size=9, color="#EF4444"),
            hovertext=[f"<b>{SEASON_LABELS[i]}</b><br>2부 리그" for i in none_idxs],
            hoverinfo="text", showlegend=False,
        ))

    fig.update_yaxes(
        autorange="reversed", range=[20.5, 0.5],
        tickvals=[1, 4, 8, 12, 16, 20],
        ticktext=["1위", "4위", "8위", "12위", "16위", "20위"],
        tickfont=dict(size=10, color="#94A3B8"),
        gridcolor="#F1F5F9", gridwidth=1,
        zeroline=False, fixedrange=True,
    )
    fig.update_xaxes(
        type="category",
        categoryorder="array",
        categoryarray=SEASON_LABELS,
        tickfont=dict(size=7, color="#94A3B8"),
        tickangle=-45, showgrid=False,
        fixedrange=True,
    )
    fig.update_layout(
        height=280, margin=dict(l=35, r=10, t=5, b=45),
        plot_bgcolor="white", paper_bgcolor="white",
        showlegend=False,
        hoverlabel=dict(bgcolor=color, font_size=13, font_color="white"),
        dragmode=False,
    )
    return fig


def countdown_html(match_dt: datetime, color: str) -> str:
    target_ms = int(match_dt.timestamp() * 1000)
    return f"""
<div style="font-family:system-ui,sans-serif;text-align:center;padding:1.4rem 0.6rem;
            background:#F8FAFC;border-radius:16px;
            border:1px solid #E2E8F0;">
  <p style="color:#94A3B8;font-size:0.72rem;letter-spacing:0.12em;margin:0 0 0.8rem 0;text-transform:uppercase;">
    ⚽ 경기 시작까지
  </p>
  <div id="cd" style="display:flex;justify-content:center;align-items:flex-start;gap:0.35rem;">
    <div style="text-align:center">
      <div id="cd-d" style="font-size:1.6rem;font-weight:900;color:{color};line-height:1">--</div>
      <div style="color:#94A3B8;font-size:0.65rem;margin-top:4px">일</div>
    </div>
    <div style="font-size:1.4rem;font-weight:900;color:#CBD5E1;padding-top:2px">:</div>
    <div style="text-align:center">
      <div id="cd-h" style="font-size:1.6rem;font-weight:900;color:{color};line-height:1">--</div>
      <div style="color:#94A3B8;font-size:0.65rem;margin-top:4px">시간</div>
    </div>
    <div style="font-size:1.4rem;font-weight:900;color:#CBD5E1;padding-top:2px">:</div>
    <div style="text-align:center">
      <div id="cd-m" style="font-size:1.6rem;font-weight:900;color:{color};line-height:1">--</div>
      <div style="color:#94A3B8;font-size:0.65rem;margin-top:4px">분</div>
    </div>
    <div style="font-size:1.4rem;font-weight:900;color:#CBD5E1;padding-top:2px">:</div>
    <div style="text-align:center">
      <div id="cd-s" style="font-size:1.6rem;font-weight:900;color:{color};line-height:1">--</div>
      <div style="color:#94A3B8;font-size:0.65rem;margin-top:4px">초</div>
    </div>
  </div>
</div>
<script>
(function(){{
  var T={target_ms};
  function p(n){{return String(n).padStart(2,'0');}}
  function tick(){{
    var diff=T-Date.now();
    if(diff<=0){{document.getElementById('cd').innerHTML='<p style="color:#22C55E;font-size:1.4rem;font-weight:700">⚽ 킥오프!</p>';return;}}
    document.getElementById('cd-d').textContent=Math.floor(diff/86400000);
    document.getElementById('cd-h').textContent=p(Math.floor(diff%86400000/3600000));
    document.getElementById('cd-m').textContent=p(Math.floor(diff%3600000/60000));
    document.getElementById('cd-s').textContent=p(Math.floor(diff%60000/1000));
  }}
  tick();setInterval(tick,1000);
}})();
</script>
"""

# ───────────────────────────────────────────────────────────
# PAGE: HOME
# ───────────────────────────────────────────────────────────
def _bg_img_css():
    img_path = pathlib.Path(__file__).parent / "10419-Chelsea_FC.jpg"
    b64 = base64.b64encode(img_path.read_bytes()).decode()
    return f"""
<style>
.stApp {{
    background-image: url("data:image/jpeg;base64,{b64}") !important;
    background-size: cover !important;
    background-position: center !important;
    background-repeat: no-repeat !important;
    background-attachment: fixed !important;
    min-height: 100vh;
}}
</style>
"""


def show_home():
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
<div style="text-align:center;padding:2rem 0 1rem 0">
  <div style="display:inline-block;width:80px;height:80px;margin-bottom:1rem;background:url('https://upload.wikimedia.org/wikipedia/en/f/f2/Premier_League_Logo.svg') center/contain no-repeat;filter:drop-shadow(0 2px 6px rgba(0,0,0,0.4))"></div>
  <h1 style="font-size:2.3rem;margin-bottom:0.6rem;color:#FFFFFF !important;text-shadow:0 2px 8px rgba(0,0,0,0.6)">나에게 맞는<br>프리미어리그 팀은?</h1>
  <p style="color:rgba(255,255,255,0.85);font-size:1rem;max-width:460px;margin:0 auto 2rem auto;line-height:1.7;text-shadow:0 1px 4px rgba(0,0,0,0.5)">
    축구를 처음 보기 시작했나요?<br>
    20가지 질문으로 당신의 <b style="color:#C4B5FD">축구 취향</b>에 꼭 맞는 팀을 찾아드려요.
  </p>
</div>
""", unsafe_allow_html=True)

    # Team logo grid
    home_teams = ["ARS", "CHE", "LIV", "MCI", "MNU", "TOT", "NEW", "AVL"]
    short_names = {"ARS": "Arsenal", "CHE": "Chelsea", "LIV": "Liverpool", "MCI": "Man City",
                   "MNU": "Man Utd", "TOT": "Spurs", "NEW": "Newcastle", "AVL": "Aston Villa"}
    for row in range(2):
        cols = st.columns(4)
        for col_idx in range(4):
            code = home_teams[row * 4 + col_idx]
            t = TEAM_INFO[code]
            with cols[col_idx]:
                st.markdown(f"""
<div style="text-align:center;padding-bottom:2px">
  <img src="{t['logo']}" style="width:30px;height:30px" />
</div>""", unsafe_allow_html=True)
                if st.button(short_names[code], key=f"home_{code}", use_container_width=True):
                    st.session_state.page = "result"
                    st.session_state.direct_team = code
                    for k in ["scores", "answers", "q_index"]:
                        st.session_state.pop(k, None)
                    st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns(3)
    col_a.metric("총 질문", "20문항")
    col_b.metric("소요 시간", "약 3분")
    col_c.metric("추천 팀", "8개 팀")

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("⚽  테스트 시작하기", key="start_btn", type="primary", use_container_width=True):
        st.session_state.page = "quiz"
        st.session_state.q_index = 0
        st.session_state.answers = {}
        st.rerun()

    st.markdown("""
<p style="text-align:center;color:#94A3B8;font-size:0.8rem;margin-top:1.5rem">
  📊 2026-27 프리미어리그 시즌 기준 · 경기 일정 자동 업데이트
</p>
""", unsafe_allow_html=True)


# ───────────────────────────────────────────────────────────
# PAGE: QUIZ
# ───────────────────────────────────────────────────────────
def show_quiz():
    st.markdown("""
<style>
.block-container { max-width: 700px !important; width: 100% !important; padding-left: 1.5rem !important; padding-right: 1.5rem !important; }
</style>
""", unsafe_allow_html=True)

    q_idx = st.session_state.q_index
    q = QUESTIONS[q_idx]

    # Progress bar
    progress_val = q_idx / 20
    msg = PROGRESS_MESSAGES.get(q_idx, "")

    st.progress(progress_val)

    prog_col, num_col = st.columns([3, 1])
    with prog_col:
        if msg:
            st.caption(msg)
        else:
            st.caption(" ")
    with num_col:
        st.markdown(f"<p style='text-align:right;color:#94A3B8;font-size:0.85rem;margin:0'><b style='color:#7C3AED'>{q_idx+1}</b> / 20</p>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Question number tag
    st.markdown(f"""
<p style="color:#6D28D9;font-size:0.78rem;font-weight:700;letter-spacing:0.12em;
          text-transform:uppercase;margin-bottom:0.4rem">Q {q_idx+1:02d}</p>
<h2 style="font-size:1.35rem;margin-bottom:1.5rem;line-height:1.4">{q['q']}</h2>
""", unsafe_allow_html=True)

    # Choices
    for i, (emoji, text) in enumerate(q["choices"]):
        label = f"{emoji}  {text}"
        if st.button(label, key=f"q{q_idx}_c{i}", use_container_width=True):
            st.session_state.answers[q_idx] = i
            st.session_state.q_index += 1
            if st.session_state.q_index >= 20:
                st.session_state.page = "loading"
            st.rerun()


# ───────────────────────────────────────────────────────────
# PAGE: LOADING
# ───────────────────────────────────────────────────────────
def show_loading():
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
<div style="text-align:center">
  <div style="font-size:3.5rem;margin-bottom:1.2rem">🔍</div>
  <h2>당신의 축구 취향를 분석하는 중...</h2>
  <p style="color:#64748B">20개의 답변을 바탕으로 8개 팀과 비교하고 있어요</p>
</div>
""", unsafe_allow_html=True)
    with st.spinner(""):
        import time
        time.sleep(1.8)
    st.session_state.page = "result"
    st.rerun()


# ───────────────────────────────────────────────────────────
# PAGE: RESULT
# ───────────────────────────────────────────────────────────
def show_result():
    components.html("<script>window.parent.document.querySelector('section.main').scrollTo(0,0);</script>", height=0)
    direct_team = st.session_state.get("direct_team")

    if direct_team:
        best = direct_team
        scores = None
        match_pct = None
    else:
        if "scores" not in st.session_state:
            st.session_state.scores = calculate_scores(st.session_state.answers)
        scores = st.session_state.scores
        best = max(scores, key=scores.get)
        match_pct = scores[best]

    info = TEAM_INFO[best]
    color = info["color"]
    bg = info["bg"]

    # ── Team Hero Header ──
    bg_file = info.get("bg_img")
    if bg_file:
        bg_path = pathlib.Path(__file__).parent / bg_file
        if bg_path.exists():
            b64 = base64.b64encode(bg_path.read_bytes()).decode()
            hero_bg = f"url('data:image/jpeg;base64,{b64}') center 70% / cover no-repeat"
        else:
            hero_bg = f"linear-gradient(135deg,{bg},#FFFFFF)"
    else:
        hero_bg = f"linear-gradient(135deg,{bg},#FFFFFF)"

    hero_text_color = "#FFFFFF" if bg_file else "#1E293B"
    hero_sub_color = "rgba(255,255,255,0.8)" if bg_file else "#64748B"
    hero_shadow = "text-shadow:0 2px 6px rgba(0,0,0,0.7)" if bg_file else ""
    hero_overlay = "background:linear-gradient(180deg,rgba(0,0,0,0.3),rgba(0,0,0,0.6));" if bg_file else ""

    st.markdown(f"""
<div style="background:{hero_bg};
            border:1px solid {color}33;border-radius:20px;
            overflow:hidden;margin-bottom:1.5rem">
  <div style="{hero_overlay}padding:2rem 1.5rem;text-align:center">
    <img src="{info['logo']}" style="width:80px;height:80px;margin-bottom:0.5rem" />
    <p style="color:{hero_text_color};font-size:0.78rem;font-weight:700;letter-spacing:0.15em;
              text-transform:uppercase;margin-bottom:0.3rem;{hero_shadow}">당신의 팀</p>
    <div style="font-size:2.2rem;font-weight:900;margin-bottom:0.2rem;color:{hero_text_color};{hero_shadow}">{info['name']}</div>
    <p style="color:{hero_sub_color};font-size:0.95rem;margin:0;{hero_shadow}">{info['nickname']} · {info['tagline']}</p>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── Match Rate (quiz only) ──
    if match_pct is not None:
        st.markdown(f"<h3 style='margin-bottom:0.5rem'>🎯 나와의 궁합</h3>", unsafe_allow_html=True)
        st.progress(match_pct / 100)
        st.markdown(f"""
<p style="text-align:right;font-size:2rem;font-weight:900;
          color:{color};margin-top:0.2rem">{match_pct}%</p>
""", unsafe_allow_html=True)

    # ── Recommendation Reason ──
    st.markdown(f"""
<div style="background:#F8FAFC;border-left:3px solid {color};border-radius:0 12px 12px 0;
            padding:1.2rem 1.4rem;margin:1.2rem 0">
  <p style="color:#334155;line-height:1.7;margin:0;font-size:0.95rem">
    💬 {info['reason']}
  </p>
</div>
""", unsafe_allow_html=True)

    st.divider()

    # ── Best Match Video ──
    yt_id = info.get("youtube")
    if yt_id:
        st.markdown("<h3>🎬 25-26 시즌 명경기</h3>", unsafe_allow_html=True)
        components.html(f"""
<div style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;border-radius:14px;">
  <iframe src="https://www.youtube.com/embed/{yt_id}" frameborder="0"
          allow="accelerometer;autoplay;clipboard-write;encrypted-media;gyroscope;picture-in-picture"
          allowfullscreen
          style="position:absolute;top:0;left:0;width:100%;height:100%;border-radius:14px;">
  </iframe>
</div>
""", height=380)

    st.divider()

    # ── Next Match ──
    fx, match_dt = get_next_fixture(best)
    st.markdown("<h3>📅 다음 경기</h3>", unsafe_allow_html=True)

    if fx and match_dt:
        is_home = info["name"] in fx["home"] or best in fx["home"].upper()
        home_label = "🏠 홈" if is_home else "✈️ 원정"

        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown(f"""
<div style="background:#F8FAFC;border:1px solid #E2E8F0;
            border-radius:14px;padding:1.2rem">
  <p style="color:#94A3B8;font-size:0.75rem;margin:0 0 0.8rem 0;letter-spacing:0.08em">경기 정보</p>
  <p style="color:#1E293B;font-weight:700;font-size:1rem;margin:0 0 0.3rem 0">
    {fx['home']}
  </p>
  <p style="color:#94A3B8;font-size:0.8rem;margin:0 0 0.5rem 0">vs</p>
  <p style="color:#1E293B;font-weight:700;font-size:1rem;margin:0 0 0.8rem 0">
    {fx['away']}
  </p>
  <p style="color:#7C3AED;font-size:0.8rem;margin:0 0 0.2rem 0">🏟️ {fx['venue']}</p>
  <p style="color:#64748B;font-size:0.78rem;margin:0 0 0.2rem 0">🕐 {fmt_uk(fx['h'], fx['m'])}</p>
  <p style="color:#64748B;font-size:0.78rem;margin:0 0 0.5rem 0">🇰🇷 {fmt_kst(match_dt)}</p>
  <span style="background:{color}15;color:{color};border-radius:20px;
               padding:3px 10px;font-size:0.75rem;font-weight:600">{home_label}</span>
</div>
""", unsafe_allow_html=True)

        with col2:
            components.html(countdown_html(match_dt, color), height=160)
    else:
        st.info("현재 다음 경기 일정을 불러오는 중이에요.")

    st.divider()

    # ── Tab Buttons ──
    st.markdown("""
<style>
.stTabs [data-baseweb="tab-list"] {
    background: #F1F5F9 !important; border: 1px solid #E2E8F0 !important;
    border-radius: 16px !important; padding: 6px !important; gap: 8px !important;
    justify-content: center !important;
}
.stTabs [data-baseweb="tab"] {
    flex: 1 !important; justify-content: center !important;
    border-radius: 12px !important; padding: 0.7rem 1.5rem !important;
    font-size: 1rem !important; font-weight: 700 !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #7C3AED, #5B21B6) !important;
    color: #FFFFFF !important; border-radius: 12px !important;
    box-shadow: 0 4px 12px rgba(124,58,237,0.3) !important;
}
.stTabs [aria-selected="false"] {
    color: #64748B !important; background: transparent !important;
}
</style>
""", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📋  팀 소개", "📊  성향 분석"])

    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""
<div style="background:#F8FAFC;border:1px solid #E2E8F0;
            border-radius:14px;padding:1.2rem;margin-bottom:0.75rem">
  <p style="color:#94A3B8;font-size:0.72rem;letter-spacing:0.1em;margin:0 0 0.5rem 0">창단</p>
  <p style="color:#1E293B;font-weight:700;font-size:1rem;margin:0">{info['founded']}년</p>
</div>
<div style="background:#F8FAFC;border:1px solid #E2E8F0;
            border-radius:14px;padding:1.2rem">
  <p style="color:#94A3B8;font-size:0.72rem;letter-spacing:0.1em;margin:0 0 0.5rem 0">홈구장</p>
  <p style="color:#1E293B;font-weight:700;font-size:0.95rem;margin:0 0 0.2rem 0">{info['stadium']}</p>
  <p style="color:#64748B;font-size:0.8rem;margin:0">수용 {info['capacity']}명</p>
</div>
""", unsafe_allow_html=True)

        with c2:
            st.markdown(f"""
<div style="background:#F8FAFC;border:1px solid #E2E8F0;
            border-radius:14px;padding:1.2rem;margin-bottom:0.75rem">
  <p style="color:#94A3B8;font-size:0.72rem;letter-spacing:0.1em;margin:0 0 0.5rem 0">감독</p>
  <p style="color:#1E293B;font-weight:700;font-size:0.9rem;margin:0">{info['manager']}</p>
</div>
<div style="background:#F8FAFC;border:1px solid #E2E8F0;
            border-radius:14px;padding:1.2rem">
  <p style="color:#94A3B8;font-size:0.72rem;letter-spacing:0.1em;margin:0 0 0.5rem 0">경기 스타일</p>
  <p style="color:#1E293B;font-size:0.85rem;line-height:1.5;margin:0">{info['style']}</p>
</div>
""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
<div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:14px;padding:1.2rem">
  <p style="color:#94A3B8;font-size:0.72rem;letter-spacing:0.1em;margin:0 0 0.5rem 0">주목 선수</p>
  <p style="color:#1E293B;font-weight:600;margin:0">⭐ {"  ·  ".join(info['players'])}</p>
</div>
""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
<div style="background:{bg};border:1px solid {color}33;border-radius:14px;padding:1.2rem">
  <p style="color:{color};font-size:0.75rem;font-weight:700;letter-spacing:0.1em;margin:0 0 0.5rem 0">클럽 소개</p>
  <p style="color:#475569;font-size:0.9rem;line-height:1.65;margin:0">{info['desc']}</p>
</div>
""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
<p style="color:{color};font-size:0.75rem;font-weight:700;letter-spacing:0.1em;margin:0 0 0.3rem 0">📈 시즌별 리그 순위 (03-04 ~ 25-26)</p>
""", unsafe_allow_html=True)
        season_fig = draw_season_chart(best)
        st.plotly_chart(season_fig, use_container_width=True)

    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        fig = draw_radar(best)
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

        st.markdown("<br>", unsafe_allow_html=True)
        for label, label_kr, val in zip(RADAR_LABELS, RADAR_LABELS_KR, info["radar"]):
            bar_col, num_col = st.columns([5, 1])
            with bar_col:
                st.progress(val / 100)
            with num_col:
                st.markdown(f"<p style='color:#7C3AED;font-weight:700;font-size:0.9rem;margin:0;padding-top:4px'>{val}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:#64748B;font-size:0.78rem;margin:-0.3rem 0 0.6rem 0'>{label} · {label_kr}</p>", unsafe_allow_html=True)

    st.divider()

    # ── All Team Rankings (quiz only) ──
    if scores is not None:
        st.markdown("<h3>📊 전체 팀 궁합 순위</h3>", unsafe_allow_html=True)
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        for rank, (team, pct) in enumerate(ranked):
            t_info = TEAM_INFO[team]
            rank_color = "#7C3AED" if rank == 0 else "#94A3B8"
            bar_fill = t_info["color"] if rank == 0 else "#CBD5E1"
            text_color = "#1E293B" if rank == 0 else "#64748B"

            col_bar, col_btn = st.columns([6, 1])
            with col_bar:
                st.markdown(f"""
<div style="display:flex;align-items:center;gap:0.75rem;height:2.4rem">
  <span style="color:{rank_color};font-weight:700;font-size:0.85rem;width:1.2rem">{rank+1}</span>
  <span style="color:{text_color};font-size:0.88rem;width:7rem;flex-shrink:0">
    <img src="{t_info['logo']}" style="width:18px;height:18px;vertical-align:middle;margin-right:4px" />{t_info['name']}
  </span>
  <div style="flex:1;background:#F1F5F9;border-radius:99px;height:8px;overflow:hidden">
    <div style="width:{pct}%;background:{bar_fill};height:100%;border-radius:99px;
                transition:width 0.8s ease"></div>
  </div>
  <span style="color:{rank_color};font-weight:700;font-size:0.88rem;width:2.5rem;text-align:right">
    {pct}%
  </span>
</div>
""", unsafe_allow_html=True)
            with col_btn:
                if st.button("보기", key=f"rank_{team}", use_container_width=True):
                    st.session_state.direct_team = team
                    st.session_state.page = "result"
                    st.session_state.pop("scores", None)
                    st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)

    btn_label = "🏠 홈으로 돌아가기" if scores is not None else "🏠  홈으로 돌아가기"
    if st.button(btn_label, key="retry_btn", type="primary", use_container_width=True):
        for key in ["page", "q_index", "answers", "scores", "direct_team"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    st.markdown("""
<p style="text-align:center;color:#94A3B8;font-size:0.78rem;margin-top:1rem">
  ⚽ 26-27 프리미어리그 시즌 기준
</p>
""", unsafe_allow_html=True)


# ───────────────────────────────────────────────────────────
# MAIN
# ───────────────────────────────────────────────────────────
def main():
    inject_css()

    if "page" not in st.session_state:
        st.session_state.page = "home"
    if "q_index" not in st.session_state:
        st.session_state.q_index = 0
    if "answers" not in st.session_state:
        st.session_state.answers = {}

    page = st.session_state.page
    if page != "result":
        st.markdown(_bg_img_css(), unsafe_allow_html=True)
    if page == "home":
        show_home()
    elif page == "quiz":
        show_quiz()
    elif page == "loading":
        show_loading()
    elif page == "result":
        show_result()


if __name__ == "__main__":
    main()
