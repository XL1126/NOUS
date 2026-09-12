# NOUS 开发踩坑记录

> 开发过程中遇到的所有坑、问题、解决方案。下次遇到类似问题先查这里。

---

## 一、环境与依赖

### 1.1 CUDA toolkit 未安装，CuPy 无法加载

**现象**：
```
ImportError: DLL load failed while importing runtime: 找不到指定的模块。
```

**原因**：GTX 960M 驱动存在（nvcuda.dll），但 CUDA toolkit（cudart、cublas 等）未安装。CuPy 需要完整 toolkit 运行时。

**解决**：
- 安装 CUDA Toolkit 11.7（GTX 960M 是 Maxwell CC 5.0，PyTorch 2.x 不支持，需 PyTorch ≤1.13）
- 或改用 numpy + scipy.sparse（当前方案，4096 变量 CPU 足够）

**教训**：先确认 `nvidia-smi` 和 CUDA toolkit 都在，再装 CuPy/PyTorch。

### 1.2 PyTorch 2.x 不支持 Maxwell GPU

**现象**：GTX 960M（CC 5.0）无法运行 PyTorch 2.x。

**原因**：PyTorch 2.0+ 要求 Compute Capability ≥ 6.0（Pascal+）。

**解决**：用 PyTorch 1.13.1+cu117，或改用 numpy。

### 1.3 numpy 版本冲突

**现象**：安装 CuPy 后 numpy 被降到 1.24.4，opencv-python 报错。

**解决**：卸载 CuPy，恢复 numpy 2.0.2。

### 1.4 Python 3.9 限制

**现象**：部分新库不支持 Python 3.9。

**解决**：NOUS 只依赖 numpy/scipy/pyyaml/pytest，全部兼容 3.9。

---

## 二、代码架构

### 2.1 `self.spa` vs `self.space` 命名混乱

**现象**：`AttributeError: 'NousMind' object has no attribute 'spa'`

**原因**：ConceptSpace 实例命名为 `self.space`，但某处误写为 `self.spa`。

**解决**：统一用 `self.space`。全局搜索 `self.spa` 确认无残留。

**教训**：命名一致性很重要，IDE 自动补全可以防这类错。

### 2.2 walrus 运算符在条件表达式中

**现象**：
```python
fatigue=0.7 + 0.3 * energy if (energy := self.soma.state.energy) else 0.85
```
Python 3.9 支持 walrus，但嵌套在条件表达式中可读性差，容易出错。

**解决**：拆成两行：
```python
energy = self.soma.state.energy
fatigue = 0.7 + 0.3 * energy
```

### 2.3 意图检测顺序冲突

**现象**：`"意识流状态"` 被检测为 `"status"`，`"自主思维"` 被检测为 `"think"`。

**原因**：泛化规则（"状态"、"想想"）排在专有规则前面。

**解决**：专有规则排在泛化规则前面：
```python
if "意识流状态" in t: return "stream_status"
if "自主思维" in t: return "autonomous"
if "状态" in t and len(t) <= 12: return "status"  # 泛化在后
```

**教训**：意图检测永远是「先具体后泛化」。

### 2.4 `thought` 变量在使用前未赋值

**现象**：`UnboundLocalError: local variable 'thought' referenced before assignment`

**原因**：`thought` 在后面的内言块才赋值，但 `core.bind()` 提前引用了它。

**解决**：将 `narrative_hook=learned or thought[:40]` 改为 `narrative_hook=learned or ""`。

### 2.5 NERI Langevin SDE 数值发散

**现象**：`RuntimeWarning: overflow encountered in power`，状态变成 inf/nan。

**原因**：双稳势 `x**3` 在大值时溢出，Euler-Maruyama 积分不稳定。

**解决**：
```python
self.x = np.clip(self.x, -10.0, 10.0)  # 每步裁剪
```

**教训**：SDE 模拟必须有数值稳定性保护。

### 2.6 numpy bool 不可 JSON 序列化

**现象**：`TypeError: Object of type bool is not JSON serializable`

**原因**：numpy 的 `bool_` 不是 Python `bool`。

**解决**：`bool(np_value)` 转换。

---

## 三、意识架构

### 3.1 工作空间 `step()` 参数名不一致

**现象**：`TypeError: step() got an unexpected keyword argument 'gain'`

**原因**：重构后参数名从 `gain` 改为 `global_gain`，调用方未同步。

**解决**：统一参数名，或用 `**kwargs` 兼容。

**教训**：重构时全局搜索旧参数名。

### 3.2 功能词泄漏到焦点

**现象**：`about="好"`、`about="解"`、`about="到"` 等单字功能词成为意识焦点。

**原因**：`content_labels()` 回退到 `tokens[:4]` 时未过滤功能词。

**解决**：
1. 扩展 `FUNCTIONISH` 集合（加 吗/呢/好/解释/一下 等）
2. 回退时也过滤：`labels = [t for t in tokens if t not in FUNCTIONISH]`
3. 优先选 2+ 字内容词

### 3.3 意识流连续性低

**现象**：`stream_link ≈ 0.30`，话题一换就掉。

**原因**：话题切换时 retention 与 now 无重叠。

**解决**：
1. 加入情绪连续性：相同情绪 +0.10
2. 加入价态连续性：`1.0 - |valence_diff|`
3. 部分重叠也算连续：`now in retention`

### 3.4 NREM 测试被唤醒

**现象**：强制设为 NREM 后，`tick()` 立刻变回 WAKE。

**原因**：能量高、睡压低时，状态机自动唤醒。

**解决**：测试中同时设置 `energy=0.2, sleep_pressure=0.8`。

### 3.5 意识流 `core.moments` 数量超出预期

**现象**：`len(m.core.moments) > len(SCRIPT)` 导致 dynamics 判定失败。

**原因**：`stream.tick()` 也调用 `core.bind()`，产生额外 moments。

**解决**：判定条件从 `==` 改为 `>=`。

---

## 四、语言与对话

### 4.1 知识库「是什么」误匹配

**现象**：问「地球是什么？」返回「意识」的定义。

**原因**：知识条目 `["意识", "是什么"]` 中的「是什么」是泛化键，匹配了所有「X是什么」问题。

**解决**：
1. 引入 `_GENERIC_KEYS` 集合
2. 只有命中非泛化键才算有效匹配
3. 整句命中优先于碎片概念命中

### 4.2 教学事实误归纳

**现象**：「其实关键是我觉得周五去公园比较好」被归纳为「其实关键是我觉得=周五去公园比较好」。

**原因**：`induce_fact` 的正则 `(.{1,12}?)是(.{1,24})` 匹配了话语开端词。

**解决**：加入 `_DISCOURSE_OPENERS` 黑名单（其实/关键/我觉得/总之…），命中则拒绝归纳。

### 4.3 单字中文实体被拒绝

**现象**：「猫是哺乳动物」中的「猫」因 `len(s) >= 2` 被拒绝。

**解决**：允许单字 CJK 内容词，但拒绝功能字（的/了/在/有…）。

### 4.4 跨体对话消息被当成事实教学

**现象**：`[墨客] 我是墨客。在。` 被归纳为事实。

**原因**：说话人前缀 `[Name]` 未剥离。

**解决**：`perceive_and_respond` 开头用正则剥离 `[Name]` 前缀。

---

## 五、测试

### 5.1 防复读与多样性测试冲突

**现象**：连续 12 次「你好」后，防复读消息导致多样性测试失败。

**解决**：测试改用混合招呼（你好/嗨/在吗/hi…），或放宽断言。

### 5.2 PowerShell 引号嵌套

**现象**：`python -c "print(f'{r[\"key\"]}')"` 在 PowerShell 中报语法错误。

**解决**：写临时脚本文件执行，或用单引号外层、双引号内层。

### 5.3 `tail` 命令不存在

**现象**：`python -m pytest | tail -5` 报错 `tail 不是命令`。

**解决**：用 `Select-Object -Last 5`（PowerShell 原生）。

---

## 六、设计原则（避免重复踩坑）

1. **先具体后泛化**：意图检测、知识匹配、焦点选择都遵循此原则
2. **数值稳定性**：任何动力学系统都要有 clip/防溢出
3. **命名一致性**：同类属性用同一前缀（`self.space` 不要混 `self.spa`）
4. **测试隔离**：状态机测试要同时控制所有相关变量
5. **先跑测试再重构**：改参数名前全局搜索旧名
6. **PowerShell 陷阱**：复杂 Python 代码写脚本文件，不要嵌套引号
