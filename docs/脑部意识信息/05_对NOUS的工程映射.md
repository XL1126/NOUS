# 对 NOUS 的工程映射

> 文献/生物学 → 代码。防止“读了很多却落不到模块”。

---

## 映射表

| 科学来源 | 机制 | NOUS 模块 | 状态 |
|----------|------|-----------|------|
| Baars / Dehaene GNW | 竞争→点火→广播→可报告 | `workspace/global_ws.py` + `consciousness/core.py` figure | 已有，待更严 |
| Block A/P 意识 | 访问 vs 现象代理 | figure=access；presence/vividness=proxy | 已有 |
| Tononi IIT（代理） | 整合-分化 | `core._integration` | 已有（非真 Φ） |
| Casali PCI | 复杂度 | 历史上的压缩率思路；可加强 | 可加强 |
| Friston/Clark PP | 预测误差/惊讶 | `predictive/model.py` | 已有（线性） |
| Seth 在场感 | 预测性自我 | presence + body | 已有 |
| Damasio/Barrett | 躯体标记/构造情绪 | `soma/body.py` + feeling_label | 已有 |
| Craig 内感受 | 身体状态上行 | Soma vector | 已有 |
| Sterling 异稳态 | 设定点漂移 | `set_point` demand | 已有 |
| Sherman core/matrix | 丘脑双通道 | 认知层近似；未全生物化 | 部分 |
| TRN 门控 | 侧抑制 | SpikeRace + workspace | 部分 |
| Buzsáki 睡眠/SWR | 离线重组 | `dream.py` + consolidate | 已有 |
| Tulving 记忆 | 情景/语义 | `memory/systems.py` | 已有 |
| James 意识流 | 连续当下 | specious + stream_link | 已有 |
| 胡塞尔时间意识 | retention/now/protention | 仅 specious 窗 | **缺口 P0** |
| 反思前我思 | 最小自我 | min_self 标量 | **缺口 P0→自我极点** |
| Graziano 注意 schema | 知道自己注意什么 | `AttentionSchema` | 已有 |
| Fleming 元认知 | 置信 | MetaCognition | 已有 |
| Eliasmith SPA | 语义指针 | `concepts/space.py` | 已有 |
| 构式语法 | 非 LM 语言 | `language/constructions.py` | 已有 |
| 自创生 | 自我维持 | `consciousness/autopoiesis.py` | 已有 |
| 主动推理 | 行动减惊讶 | ActionLoop | 已有 |

---

## 缺口（P0）实现草案

### 1. 自我极点 SelfPole

```text
self_vec = sticky vector (slow drift)
about_world = encode(focus)
experience = bind(self_vec, about_world)  # “我经验 X”
```

报告模板变为：`我正意识到 X`，其中“我”始终来自 self_vec。

### 2. 时间拓扑

```text
retention:  last 1–3 abouts (衰减)
now:        current about
protention: predicted next abouts (来自预测模型)
```

意识流不再只是列表，而是有方向的轨迹。

### 3. 严格访问

```text
if ignition < θ:  preconscious only
else:             figure = top-k broadcast
```

---

## 测试应增加

- 存在 about 永不为空
- figure 非空 ⇔ ignition 高
- min_self 长程单调上升（有教学时）
- sleep 后 stream_link 不崩溃
- fork 后 self_vec 有继承但可漂移

---

## 冗余清理清单

- 减少重复报告路径（phen 与 core 已同步，勿双写逻辑）
- 不要再为每个关键词加固定句
- 状态报告合并到 first_person + 少量数值
