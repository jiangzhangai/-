import streamlit as st
import pandas as pd
import numpy as np
import os
import time
import hashlib
from btca_main import BTCA存储器, BTCA调度器

# --- 1. 页面配置与适配 CSS ---
st.set_page_config(page_title="仿生思维克隆系统", layout="wide", page_icon="🧬")

st.markdown("""
<style>
/* 基础背景：改为浅灰色径向渐变 */
.stApp { 
    background: radial-gradient(circle at 50% 50%, #f8fafc 0%, #e2e8f0 100%); 
    color: #1e293b;
}

/* 侧边栏样式：深灰蓝背景，保持对比度 */
[data-testid="stSidebar"] { 
    background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%) !important;
    border-right: 1px solid #cbd5e1;
}

/* 手机端适配 */
@media (max-width: 768px) {
    [data-testid="stSidebar"] { min-width: 100% !important; }
}

/* 指标卡片：浅色底 + 深色文字 */
.metric-card { 
    background: rgba(255, 255, 255, 0.2); 
    border: 1px solid #94a3b8; 
    border-left: 4px solid #3b82f6;
    border-radius: 4px; 
    padding: 10px; 
    margin-bottom: 8px;
}
.metric-label { color: #64748b; font-size: 0.65rem; text-transform: uppercase; font-weight: 600; }
.metric-value { 
    color: #0f172a; font-size: 1.1rem; font-weight: 800; 
    font-family: 'JetBrains Mono', monospace; 
}
.status-normal { color: #059669 !important; } /* 森林绿 */
.status-danger { color: #dc2626 !important; } /* 警示红 */

/* 重置按钮 */
div.stButton > button:first-child {
    background: #f1f5f9;
    color: #475569;
    border: 1px solid #cbd5e1;
    font-size: 0.7rem;
    display: block;
    margin: 10px auto;
}

/* 输入框区域：改为浅灰色背景 */
[data-testid="stChatInput"] {
    background-color: #f1f5f9 !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 8px;
}

/* 对话区：浅灰色背景框 + 深色文字 */
[data-testid="stChatMessage"] { 
    background-color: #ffffff !important; 
    border: 1px solid #e2e8f0 !important; 
    border-radius: 8px !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}
[data-testid="stChatMessage"] p { color: #334155 !important; }

/* 调整标题颜色 */
h1, h2, h3, .stCaption { color: #0f172a !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. 核心引擎初始化 ---
@st.cache_resource
def init_engine():
    return BTCA调度器(os.environ.get("OPENAI_API_KEY", ""))

调度器 = init_engine()

def get_storage_size():
    path = "btca_memory"
    if not os.path.exists(path): return "0 KB"
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            total_size += os.path.getsize(os.path.join(dirpath, f))
    return f"{total_size / 1024:.1f} KB"

if "messages" not in st.session_state: st.session_state.messages = []
if "stress_level" not in st.session_state: st.session_state.stress_level = 0.0
if "phase" not in st.session_state: st.session_state.phase = 0.0

# --- 3. 处理输入 ---
if prompt := st.chat_input("注入刺激问题..."):
    st.session_state.stress_level = min(len(prompt) / 40, 5.0)
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.pending_run = prompt

# --- 4. 侧边栏 ---
with st.sidebar:
    st.markdown("<div style='color:#38bdf8; font-weight:bold; font-size:0.9rem; margin-bottom:15px;'>● BTCS CORE TERMINAL</div>", unsafe_allow_html=True)
    体征 = 调度器.存储.状态 
    
    def metric_box(label, value, status="normal", b_color="#3b82f6"):
        c_class = "status-normal" if status=="normal" else "status-danger"
        st.markdown(f'<div class="metric-card" style="border-left-color:{b_color}"><div class="metric-label">{label}</div><div class="metric-value {c_class}">{value}</div></div>', unsafe_allow_html=True)

    metric_box("核心端粒 (TELOMERE)", f"{体征['端粒剩余']:.4f}")
    metric_box("能量储备 (ENERGY)", f"{int(体征['能量储备'])} TKS", b_color="#0ea5e9")
    
    c1, c2 = st.columns(2)
    with c1:
        metric_box("生命轮次", f"R-{体征['总轮次']}", b_color="#6366f1")
        metric_box("异常偏离", f"{体征['异常计数']} ERR", "danger" if 体征['异常计数']>0 else "normal", "#ef4444")
        metric_box("存储负载", get_storage_size(), b_color="#10b981")
    with c2:
        metric_box("DMA版本", f"V{体征['DMA版本']}", b_color="#f59e0b")
        metric_box("抗体活性", f"{len(调度器.存储.抗体库)} ACT", b_color="#a855f7")
        metric_box("逻辑熵增", f"+{(体征['异常计数']*1.2)+(100-体征['端粒剩余'])/10:.2f} G", b_color="#f43f5e")

    if st.button("🔄 重置体征", use_container_width=True):
        调度器.存储.状态 = BTCA存储器._初始状态()
        调度器.存储.保存状态()
        st.session_state.messages = []
        st.rerun()

# --- 5. 主界面 ---
st.markdown("### 仿生思维克隆系统")

# 动态波形图：深色线条适应浅色背景
t_val = 体征['端粒剩余'] / 100
stress = st.session_state.stress_level
st.session_state.phase += 0.15 
x = np.linspace(0, 10, 120)
y = np.sin(x * (1 + stress) + st.session_state.phase) * t_val
y += np.random.randn(120) * (0.01 + stress * 0.08) 

# 展示波形图
st.line_chart(pd.DataFrame(y, columns=['Thinking Waveform']), height=160)

st.markdown("<p style='font-size:0.7rem; color:#94a3b8; margin-top:20px;'>THOUGHT STREAM ACCESS | SACT PROTOCOL ACTIVE</p>", unsafe_allow_html=True)

chat_container = st.container()
with chat_container:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

if "pending_run" in st.session_state:
    current_prompt = st.session_state.pop("pending_run")
    with chat_container:
        with st.chat_message("assistant"):
            with st.spinner("思维解旋中..."):
                回复, _ = 调度器.运行推演周期(current_prompt)
                st.markdown(回复)
                st.session_state.messages.append({"role": "assistant", "content": 回复})
                st.rerun()
