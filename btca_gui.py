import streamlit as st
import pandas as pd
import numpy as np
import os
import time
import hashlib
from btca_main import BTCA存储器, BTCA调度器

# --- 页面配置 ---
st.set_page_config(page_title="仿生思维克隆系统", layout="wide", page_icon="🧬")

# 核心 CSS 增强：注入色彩与边框逻辑
st.markdown("""
<style>
.stApp { background: radial-gradient(circle at 50% 50%, #0d1117 0%, #060810 100%); }

/* 侧边栏样式 */
[data-testid="stSidebar"] { 
    background: linear-gradient(180deg, #0a0f1e 0%, #05070a 100%) !important;
    border-right: 1px solid #1e293b;
    min-width: 350px !important; 
}

/* 指标卡片：增强高亮文字与色彩 */
.metric-card { 
    background: rgba(30, 41, 59, 0.4); 
    border: 1px solid #334155; 
    border-left: 4px solid #00ff88;
    border-radius: 4px; 
    padding: 8px 10px; 
    margin-bottom: 8px;
}
.metric-label { color: #94a3b8; font-size: 0.65rem; text-transform: uppercase; }
.metric-value { 
    color: #ffffff; font-size: 1rem; font-weight: 800; 
    font-family: 'JetBrains Mono', monospace; 
}
.status-normal { color: #00ff88 !important; }
.status-danger { color: #ff4b4b !important; }

/* 微缩化重置按钮 */
div.stButton > button:first-child {
    background: rgba(31, 41, 55, 0.8);
    color: #94a3b8;
    border: 1px solid #374151;
    font-size: 0.7rem;
    padding: 2px 10px;
    height: auto;
    width: auto !important; /* 使其不再撑满全行 */
    margin: 0 auto;
    display: block;
}
div.stButton > button:hover {
    border-color: #ff4b4b;
    color: #ff4b4b;
}

/* 恢复对话区边框和标题感 */
[data-testid="stChatMessage"] { 
    background-color: rgba(17, 25, 40, 0.7) !important; 
    border: 1px solid #1e293b !important; 
    border-radius: 8px !important;
    margin-bottom: 1rem !important;
}
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def init_engine():
    return BTCA调度器(os.environ.get("OPENAI_API_KEY", ""))

调度器 = init_engine()

# 获取真实存储数据的函数
def get_storage_size():
    path = "btca_memory"
    if not os.path.exists(path): return "0 KB"
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return f"{total_size / 1024:.1f} KB"

# 状态初始化
if "messages" not in st.session_state: st.session_state.messages = []
if "last_audit" not in st.session_state: st.session_state.last_audit = {}
if "stress_level" not in st.session_state: st.session_state.stress_level = 0.0
if "phase" not in st.session_state: st.session_state.phase = 0.0

# --- 处理用户输入 ---
if prompt := st.chat_input("注入刺激问题..."):
    new_stress = min(len(prompt) / 50, 6.0)
    st.session_state.stress_level = max(st.session_state.stress_level, new_stress)
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.pending_run = prompt

# --- 侧边栏：15项高亮指标 ---
with st.sidebar:
    st.markdown("<div style='color:#00ff88; font-weight:bold; font-size:0.9rem;'>● BTCS CORE METRICS</div>", unsafe_allow_html=True)
    体征 = 调度器.存储.状态 
    
    def metric_card(label, value, status="normal", border_color="#00ff88"):
        color_class = "status-normal" if status=="normal" else "status-danger"
        st.markdown(f"""
            <div class="metric-card" style="border-left-color: {border_color}">
                <div class="metric-label">{label}</div>
                <div class="metric-value {color_class}">{value}</div>
            </div>
        """, unsafe_allow_html=True)

    # 核心指标
    metric_card("核心端粒 (TELOMERE)", f"{体征['端粒剩余']:.4f}", border_color="#00ff88")
    metric_card("能量储备 (ENERGY)", f"{int(体征['能量储备'])} TKS", border_color="#00d1ff")
    
    # 指标矩阵
    cols = st.columns(2)
    with cols[0]:
        metric_card("生命轮次", f"R-{体征['总轮次']}", border_color="#3b82f6")
        metric_card("异常偏离", f"{体征['异常计数']} ERR", "danger" if 体征['异常计数']>0 else "normal", "#ef4444")
        metric_card("代谢活跃度", f"{(体征['能量储备']/10000)*100:.1f}%", border_color="#00d1ff")
        metric_card("衰减斜率", "-0.052/T", border_color="#64748b")
        metric_card("抗体活性", f"{len(调度器.存储.抗体库)} ACT", border_color="#a855f7")
        # 新增真实指标 15
        metric_card("存储池负载", get_storage_size(), border_color="#10b981")
    with cols[1]:
        metric_card("DMA 版本", f"V{体征['DMA版本']}", border_color="#f59e0b")
        metric_card("遗传向量", f"Chr-{体征['Chr23']}", border_color="#ec4899")
        db_hash = hashlib.md5(str(体征['端粒剩余']).encode()).hexdigest()[:6]
        metric_card("内存快照", f"#{db_hash}", border_color="#06b6d4")
        metric_card("校验级别", "M06-HIGH", border_color="#10b981")
        metric_card("碎片热度", f"{min(体征['DMA版本']*2.5, 100):.1f}%", border_color="#fb923c")
        metric_card("逻辑熵增", f"+{(体征['异常计数']*1.2)+(100-体征['端粒剩余'])/10:.2f} G", border_color="#f43f5e")

    st.write("")
    # 微缩化按钮
    if st.button("🔄 重置体征", use_container_width=False):
        调度器.存储.状态 = BTCA存储器._初始状态()
        调度器.存储.保存状态()
        st.session_state.messages = []
        st.session_state.stress_level = 0.0
        st.toast("系统已初始化", icon="🧬")
        st.rerun()

# --- 主区 ---
st.markdown("### 🧠 仿生思维克隆监控终端")

# === 动态波形图 ===
t_val = 体征['端粒剩余'] / 100
stress = st.session_state.stress_level
st.session_state.phase += 0.15 
x = np.linspace(0, 10, 120)
y = np.sin(x * (1 + stress) + st.session_state.phase) * t_val
y += np.random.randn(120) * (0.01 + stress * 0.08) 
st.line_chart(pd.DataFrame(y, columns=['Thinking Waveform']), height=150)

# 对话展示：带标题与边框
st.write("---")
st.markdown("<p style='font-size:0.7rem; color:#475569;'>THOUGHT STREAM ACCESS</p>", unsafe_allow_html=True)

chat_container = st.container()
with chat_container:
    for msg in st.session_state.messages:
        # 对话区现在有了内置的角色标题和背景框
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# 执行推演逻辑
if "pending_run" in st.session_state:
    current_prompt = st.session_state.pop("pending_run")
    with chat_container:
        with st.chat_message("assistant"):
            with st.spinner("思维解旋中..."):
                回复, 审计日志 = 调度器.运行推演周期(current_prompt)
                st.markdown(回复)
                st.session_state.messages.append({"role": "assistant", "content": 回复})
                st.rerun()
