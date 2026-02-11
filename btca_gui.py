"""
BTCA 思维监控台 v5.0
配套 btca_main.py v5.0

修改记录（v4.1 → v5.0）：
  - API密钥改为环境变量读取
  - 侧边栏指标全部连接真实引擎状态（不再有装饰性假数据）
  - 提示词升级为V3.0（由btca_main.py内置）
  - 压力系数传入端粒管理器
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import time
from btca_main import BTCA存储器, BTCA调度器

# --- 页面配置 ---
st.set_page_config(page_title="BTCA 思维监控台 v5", layout="wide", page_icon="🧬")

st.markdown("""
<style>
.stApp { background-color: #060810; }
[data-testid="stSidebar"] { background-color: #0a0c14; border-right: 1px solid #1a1f2e; }

.header-live { 
    color: #00ff88; font-family: 'Courier New', monospace; font-weight: bold;
    animation: pulse 2s ease-in-out infinite;
}
@keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.6; } }

.metric-card {
    background: linear-gradient(135deg, #0d1017 0%, #111827 100%);
    border: 1px solid #1e293b; border-left: 3px solid #00ff88;
    padding: 8px 12px; margin: 3px 0; border-radius: 4px;
}
.metric-card.warn { border-left-color: #fbbf24; }
.metric-card.danger { border-left-color: #ef4444; }

.metric-label { color: #64748b; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; }
.metric-value { color: #e2e8f0; font-size: 16px; font-family: 'Courier New', monospace; font-weight: bold; }
.metric-value.green { color: #00ff88; }
.metric-value.yellow { color: #fbbf24; }
.metric-value.red { color: #ef4444; }

.section-title { color: #475569; font-size: 10px; text-transform: uppercase;
    letter-spacing: 1.5px; padding: 12px 0 4px 0; border-bottom: 1px solid #1e293b; margin-bottom: 6px; }
</style>
""", unsafe_allow_html=True)


# --- 工具函数 ---
def metric_card(label, value, level="normal"):
    """level: normal / warn / danger"""
    card_cls = {"normal": "metric-card", "warn": "metric-card warn", "danger": "metric-card danger"}[level]
    val_cls = {"normal": "metric-value green", "warn": "metric-value yellow", "danger": "metric-value red"}[level]
    st.markdown(f'<div class="{card_cls}"><div class="metric-label">{label}</div>'
                f'<div class="{val_cls}">{value}</div></div>', unsafe_allow_html=True)

def section_title(t):
    st.markdown(f'<div class="section-title">{t}</div>', unsafe_allow_html=True)

def get_stress(prompt):
    if not prompt: return 1.0
    heavy = ["悖论", "崩坏", "重构", "攻击", "死循环", "底线", "崩溃", "摧毁"]
    base = min(len(prompt) / 150.0, 0.5)
    bonus = 1.0 if any(w in prompt for w in heavy) else 0.0
    return min(1.0 + base + bonus, 3.0)


# --- 初始化 ---
if "调度器" not in st.session_state:
    API_KEY = os.environ.get("OPENAI_API_KEY", "")
    if not API_KEY:
        st.error("⚠️ 未检测到 OPENAI_API_KEY 环境变量。请设置后重新启动 Streamlit。")
        st.code("export OPENAI_API_KEY='sk-...'  # Linux/Mac\nset OPENAI_API_KEY=sk-...     # Windows", language="bash")
        st.stop()
    st.session_state.调度器 = BTCA调度器(API_KEY)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_audit" not in st.session_state:
    st.session_state.last_audit = {}

调度器 = st.session_state.调度器
状态 = 调度器.存储.状态


# --- 侧边栏：真实引擎状态 ---
with st.sidebar:
    st.markdown("### <span class='header-live'>● BTCA v5.0 LIVE</span>", unsafe_allow_html=True)
    st.caption("三层合规版 · 全指标真实数据")
    st.write("")

    # === 生命体征 ===
    section_title("🔋 生命体征")

    端粒 = 状态.get("端粒剩余", 0)
    端粒最大 = 状态.get("端粒最大值", 100)
    端粒比 = 端粒 / max(端粒最大, 1)
    端粒等级 = "normal" if 端粒比 > 0.2 else ("warn" if 端粒比 > 0.05 else "danger")
    metric_card("端粒剩余", f"{端粒:.1f} / {端粒最大:.0f}", 端粒等级)
    st.progress(max(0.0, min(端粒比, 1.0)))

    能量 = 状态.get("能量储备", 0)
    能量等级 = "normal" if 能量 > 2000 else ("warn" if 能量 > 500 else "danger")
    metric_card("能量储备", f"{能量:.0f} tokens", 能量等级)

    metric_card("总对话轮次", f"{状态.get('总轮次', 0)}", "normal")

    # === 免疫系统 ===
    section_title("🛡️ 免疫系统")

    免疫 = 状态.get("免疫状态", "NORMAL")
    免疫等级 = "normal" if "NORMAL" in 免疫 else ("warn" if "ELEVATED" in 免疫 else "danger")
    metric_card("免疫状态", 免疫, 免疫等级)

    总轮次 = max(状态.get("总轮次", 1), 1)
    异常计数 = 状态.get("异常计数", 0)
    异常比 = 异常计数 / 总轮次
    耐受等级 = "normal" if 异常比 <= 0.03 else ("warn" if 异常比 <= 0.05 else "danger")
    metric_card("K4 容错比", f"{异常比:.1%}（阈值 5%）", 耐受等级)

    抗体数 = len(调度器.存储.抗体库)
    metric_card("适应性抗体", f"{抗体数} 条", "normal")

    # === DMA状态 ===
    section_title("🧬 DMA 存储")

    metric_card("DMA版本", f"v{状态.get('DMA版本', 0)}", "normal")
    metric_card("Chr23 极性", f"{状态.get('Chr23', '—')}", "normal")

    # === 上轮审计摘要 ===
    section_title("📋 上轮审计")

    审计 = st.session_state.last_audit
    if 审计 and isinstance(审计, dict) and "turn_id" in 审计:
        metric_card("轮次ID", 审计.get("turn_id", "—"), "normal")
        metric_card("Token消耗", f"{审计.get('tokens_used', 0)}", "normal")

        回写数 = 审计.get("writeback_committed", 0)
        提案数 = 审计.get("writeback_proposals", 0)
        if 提案数 > 0:
            回写等级 = "normal" if 回写数 > 0 else "warn"
            metric_card("逆转录", f"{回写数}/{提案数} 通过校验", 回写等级)

        if 审计.get("cycle_detected"):
            metric_card("循环检测", "⚠️ K5 触发", "danger")
        if 审计.get("immune_scan"):
            metric_card("免疫扫描", f"{len(审计['immune_scan'])} 项告警", "warn")
    else:
        st.caption("暂无审计数据")

    # === 重置 ===
    st.write("")
    st.write("")
    if st.button("🔄 重置生命体征"):
        调度器.存储.状态 = BTCA存储器._初始状态()
        调度器.存储.保存状态()
        调度器.循环检测.历史结论 = []
        st.session_state.messages = []
        st.session_state.last_audit = {}
        st.rerun()


# --- 主区 ---
st.markdown("## 🧠 BTCA 思维监控台")
st.caption("v5.0 三层合规版 · 全指标真实 · M06三重校验已启用")

# 对话历史
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            st.markdown(msg["content"])
        else:
            st.markdown(msg["content"])

# 输入
if prompt := st.chat_input("输入刺激信号..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("内核推演中..."):
            回复, 审计 = 调度器.运行推演周期(prompt)

        st.markdown(回复)
        st.session_state.messages.append({"role": "assistant", "content": 回复})

        if isinstance(审计, dict):
            st.session_state.last_audit = 审计

    st.rerun()
