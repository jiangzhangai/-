import streamlit as st
import pandas as pd
import numpy as np
import os
import time
import hashlib
from btca_main import BTCA存储器, BTCA调度器

# --- 1. 页面配置与手机端适配 CSS ---
st.set_page_config(page_title="仿生思维克隆系统", layout="wide", page_icon="🧬")

st.markdown("""
<style>
/* 基础背景：径向渐变深空黑 */
.stApp { 
    background: radial-gradient(circle at 50% 50%, #0d1117 0%, #060810 100%); 
}

/* 侧边栏样式：响应式适配 */
[data-testid="stSidebar"] { 
    background: linear-gradient(180deg, #0a0f1e 0%, #05070a 100%) !important;
    border-right: 1px solid #1e293b;
}

/* 手机端特定优化：当屏幕宽度小于768px时 */
@media (max-width: 768px) {
    [data-testid="stSidebar"] { min-width: 100% !important; }
    .metric-value { font-size: 0.9rem !important; }
    .stMarkdown h3 { font-size: 1.2rem !important; }
}

/* 指标卡片：高亮文字 + 带颜色的背景框 */
.metric-card { 
    background: rgba(30, 41, 59, 0.5); 
    border: 1px solid #334155; 
    border-left: 4px solid #00ff88;
    border-radius: 4px; 
    padding: 10px; 
    margin-bottom: 8px;
}
.metric-label { color: #94a3b8; font-size: 0.65rem; text-transform: uppercase; font-weight: 600; }
.metric-value { 
    color: #ffffff; font-size: 1.1rem; font-weight: 800; 
    font-family: 'JetBrains Mono', monospace; 
    text-shadow: 0 0 8px rgba(255, 255, 255, 0.2);
}
.status-normal { color: #00ff88 !important; }
.status-danger { color: #ff4b4b !important; }

/* 微缩化重置按钮 */
div.stButton > button:first-child {
    background: rgba(31, 41, 55, 0.6);
    color: #94a3b8;
    border: 1px solid #374151;
    font-size: 0.7rem;
    padding: 4px 12px;
    height: auto;
    width: auto !important;
    margin: 10px auto;
    display: block;
}
div.stButton > button:hover { border-color: #ff4b4b; color: #ff4b4b; }

/* 对话区样式：带标题感和边框 */
[data-testid="stChatMessage"] { 
    background-color: rgba(17, 25, 40, 0.7) !important; 
    border: 1px solid #1e293b !important; 
    border-radius: 8px !important;
    margin-bottom: 1rem !important;
}
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

# 状态初始化
if "messages" not in st.session_state: st.session_state.messages = []
if "stress_level" not in st.session_state: st.session_state.stress_level = 0.0
if "phase" not in st.session_state: st.session_state.phase = 0.0

# --- 3. 处理用户输入 ---
if prompt := st.chat_input("注入刺激问题..."):
    st.session_state.stress_level = min(len(prompt) / 40, 5.0)
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.pending_run = prompt

# --- 4. 侧边栏：15项高亮指标矩阵 ---
with st.sidebar:
    st.markdown("<div style='color:#00ff88; font-weight:bold; font-size:0.9rem; margin-bottom:15px;'>● BTCS CORE TERMINAL</div>", unsafe_allow_html=True)
    体征 = 调度器.存储.状态 
    
    def metric_box(label, value, status="normal", b_color="#00ff88"):
        c_class = "status-normal" if status=="normal" else "status-danger"
        st.markdown(f'<div class="metric-card" style="border-left-color:{b_color}"><div class="metric-label">{label}</div><div class="metric-value {c_class}">{value}</div></div>', unsafe_allow_html=True)

    metric_box("核心端粒 (TELOMERE)", f"{体征['端粒剩余']:.4f}")
    metric_box("能量储备 (ENERGY)", f"{int(体征['能量储备'])} TKS", b_color="#00d1ff")
    
    c1, c2 = st.columns(2)
    with c1:
        metric_box("生命轮次", f"R-{体征['总轮次']}", b_color="#3b82f6")
        metric_box("异常偏离", f"{体征['异常计数']} ERR", "danger" if 体征['异常计数']>0 else "normal", "#ef4444")
        metric_box("代谢活跃", f"{(体征['能量储备']/10000)*100:.1f}%", b_color="#00d1ff")
        metric_box("衰减斜率", "-0.052/T", b_color="#64748b")
        metric_box("抗体活性", f"{len(调度器.存储.抗体库)} ACT", b_color="#a855f7")
        metric_box("存储负载", get_storage_size(), b_color="#10b981")
    with c2:
        metric_box("DMA版本", f"V{体征['DMA版本']}", b_color="#f59e0b")
        metric_box("遗传向量", f"Chr-{体征['Chr23']}", b_color="#ec4899")
        db_hash = hashlib.md5(str(体征['端粒剩余']).encode()).hexdigest()[:6]
        metric_box("内存快照", f"#{db_hash}", b_color="#06b6d4")
        metric_box("校验级别", "M06-HIGH", b_color="#10b981")
        metric_box("碎片热度", f"{min(体征['DMA版本']*2.5, 100):.1f}%", b_color="#fb923c")
        metric_box("逻辑熵增", f"+{(体征['异常计数']*1.2)+(100-体征['端粒剩余'])/10:.2f} G", b_color="#f43f5e")

    if st.button("🔄 重置体征", use_container_width=False):
        调度器.存储.状态 = BTCA存储器._初始状态()
        调度器.存储.保存状态()
        st.session_state.messages = []
        st.session_state.stress_level = 0.0
        st.rerun()

# --- 5. 主界面 ---
st.markdown("### 🧠 仿生思维克隆监控终端")

# 动态波形图
t_val = 体征['端粒剩余'] / 100
stress = st.session_state.stress_level
st.session_state.phase += 0.15 
x = np.linspace(0, 10, 120)
y = np.sin(x * (1 + stress) + st.session_state.phase) * t_val
y += np.random.randn(120) * (0.01 + stress * 0.08) 
st.line_chart(pd.DataFrame(y, columns=['Thinking Waveform']), height=160)

st.markdown("<p style='font-size:0.7rem; color:#475569; margin-top:20px;'>THOUGHT STREAM ACCESS | SACT PROTOCOL ACTIVE</p>", unsafe_allow_html=True)

# 对话容器
chat_container = st.container()
with chat_container:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# 执行逻辑推演
if "pending_run" in st.session_state:
    current_prompt = st.session_state.pop("pending_run")
    with chat_container:
        with st.chat_message("assistant"):
            with st.spinner("思维解旋中..."):
                回复, _ = 调度器.运行推演周期(current_prompt)
                st.markdown(回复)
                st.session_state.messages.append({"role": "assistant", "content": 回复})
                st.rerun()