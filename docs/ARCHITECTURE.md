# NOUS 架构

## 闭合循环

```
        ┌─────────────────────────────────────────┐
        │                 SOMA                     │
        │  energy/sleep/stress/social/curiosity    │
        │  attention_gain · learning_gain · policy │
        └───────────────┬─────────────────────────┘
                        │ 驱动 / 增益
                        ▼
用户话语 → tokenize → ConceptSpace(512) → PredictiveModel(误差/新颖)
                        │                        │
                        ▼                        │
              GlobalWorkspace 竞争/点火/广播 ◄────┘
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
     MemoryBank      Goals/Self    Language
     WM/EP/Sem       Meta/Other    Construction
     Proc/Auto       InnerSpeech   Generator
          │             │             │
          └─────────────┴──────┬──────┘
                               ▼
                            回复 + 学习写回
```

## 模块

| 路径 | 职责 |
|------|------|
| `src/soma/body.py` | 身体、异稳态、事件、策略、构造情绪 |
| `src/concepts/space.py` | 语义指针、角色填充图 |
| `src/workspace/global_ws.py` | 竞争点火与广播 |
| `src/predictive/model.py` | 预测误差与新颖度 |
| `src/memory/systems.py` | 五类记忆 + 巩固 |
| `src/language/constructions.py` | 分词/意图/构式生成 |
| `src/self_model/meta.py` | 目标/元认知/自我/他者/内言 |
| `src/knowledge/seed.py` | 种子知识 |
| `src/mind.py` | **NousMind** 总集成 |

## 与 Transformer 的区别

- 无注意力语言模型、无梯度续写
- 语言=构式槽位 + 概念检索 + 组合
- 学习=在线绑定 + 强化程序权重 + 巩固，不是反向传播

## 意识声明

实现的是**可报告工作空间 + 预测 + 自我维护 + 目标/内言**的功能代理。
不声称现象意识。
