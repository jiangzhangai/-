# BTCA v5.0 仿生思维克隆系统（三层合规版）

## 相对 v4.1 的修改清单

| # | 问题 | 修复 |
|---|------|------|
| ① | API密钥硬编码 | 改为环境变量 `OPENAI_API_KEY` |
| ② | 逆转录无校验（DMA可被污染）| 新增 M06 RLT三重校验器 |
| ③ | 免疫系统仅3个关键词 | 升级为5模式先天库 + 适应性抗体学习 + K4 Treg 5%耐受 |
| ④ | 端粒衰减过慢（永不耗尽）| 校准为每轮0.05（约2000轮合理寿命）|
| ⑤ | GUI仪表盘24项假数据 | 全部替换为真实引擎状态 |
| ⑥ | 提示词未对齐V3.0 | 内置三层合规版自然语言提示词 |

额外新增：
- M07 审计日志（JSON Lines落盘）
- M10 循环检测器（K5执行面）
- 端粒状态机（HEALTHY → WARNING → CRITICAL → TERMINATED）
- 优雅降级（无API密钥时清晰报错）

## 启动方式

### 1. 安装依赖
```bash
pip install openai chromadb streamlit
```

### 2. 设置 API 密钥
```bash
# Linux / Mac
export OPENAI_API_KEY='sk-proj-...'

# Windows CMD
set OPENAI_API_KEY=sk-proj-...

# Windows PowerShell
$env:OPENAI_API_KEY = "sk-proj-..."
```

### 3A. 命令行模式
```bash
python btca_main.py
```

### 3B. Web监控台模式
```bash
streamlit run btca_gui.py
```

## 文件结构

```
practices_v5/
├── btca_main.py          # Ⅲ层外部引擎（后端）
├── btca_gui.py           # Streamlit Web前端
├── README.md             # 本文件
└── btca_memory/          # 持久化数据（自动生成）
    ├── btca_state.json   # 生命体征
    ├── audit_log.jsonl   # 审计日志
    ├── antibodies.json   # 适应性抗体库
    └── (chromadb files)  # DMA向量数据库
```

## 三层合规对照

| 层级 | 职责 | 实现位置 |
|------|------|----------|
| Ⅰ 生命蓝图 | 设计原则（中心法则、公理） | 文档，不写入代码 |
| Ⅱ 判断内核 | K1-K6原则面 + ATCG推演 | `SYSTEM_PROMPT_V3`（发送给GPT）|
| Ⅲ 系统组件 | 状态管理 + K规则执行面 | `btca_main.py` 全部类 |
