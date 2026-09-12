# nengo_spa.algebras — Nengo SPA 代数模块文档

## 基本信息

- **原始链接**：https://www.nengo.ai/nengo-spa/v1.3.0/modules/nengo_spa.algebras.html
- **文档类型**：Python库API文档（技术文档）
- **库名称**：Nengo SPA（Semantic Pointer Architecture，语义指针架构）
- **版本**：v1.3.0
- **模块路径**：nengo_spa.algebras
- **官方网站**：https://www.nengo.ai/nengo-spa/
- **可用版本**：latest、v1.3.0、v1.2.0、v1.1.1、v1.1.0

## 模块概述

`nengo_spa.algebras` 模块定义了Nengo SPA中使用的代数系统。语义指针（Semantic Pointers）是高维向量，通过**叠加**（superposition）和**绑定**（binding）两种基本操作来表示和操作符号结构。

该模块导出以下代数实现：

| 类名 | 描述 |
|---|---|
| `base.AbstractAlgebra` | 代数的抽象基类 |
| `base.CommonProperties` | 代数中向量公共属性的常量定义 |
| `base.ElementSidedness` | 特殊元素属性在二元运算中成立的侧（左/右/双侧） |
| `hrr_algebra.HrrAlgebra` | 全息约简表征（HRR）代数 |
| `hrr_algebra.HrrProperties` | HrrAlgebra支持的向量属性 |
| `vtb_algebra.VtbAlgebra` | 向量导出变换绑定（VTB）代数 |
| `vtb_algebra.VtbProperties` | VtbAlgebra支持的向量属性 |
| `tvtb_algebra.TvtbAlgebra` | 转置向量导出变换绑定（TVTB）代数 |
| `tvtb_algebra.TvtbProperties` | TvtbAlgebra支持的向量属性 |

## 基类（Base classes）

### ElementSidedness 枚举

```python
class nengo_spa.algebras.base.ElementSidedness(value)
```

基类：`enum.Enum`

特殊元素属性在二元运算中成立的侧。

- `LEFT = 'left'`：左侧
- `RIGHT = 'right'`：右侧
- `TWO_SIDED = 'two-sided'`：双侧

### AbstractAlgebra 抽象基类

```python
class nengo_spa.algebras.base.AbstractAlgebra
```

基类：`object`

代数的抽象基类。自定义代数可通过实现此抽象基类的接口来定义。

#### 核心方法

**1. `is_valid_dimensionality(d)`**
- 检查d是否为有效的向量维度
- 参数：d（int）— 维度
- 返回：bool，d是否为有效维度

**2. `create_vector(d, properties, *, rng=None)`**
- 创建满足给定向量属性的向量
- 参数：
  - d（int）— 向量维度
  - properties — 向量需满足的属性定义（建议使用str的set或list，利用CommonProperties中定义的常量）
  - rng（numpy.random.RandomState，可选）— 用于创建向量的随机数生成器
- 返回：ndarray，具有所需属性的随机向量

**3. `make_unitary(v)`**
- 基于向量v返回酉向量（unitary vector）
- 酉向量不会改变其绑定向量的长度
- 参数：v（(d,) ndarray）— 基础向量
- 返回：ndarray，酉向量

**4. `superpose(a, b)`**
- 返回a和b的叠加
- 通常是逐元素加法
- 参数：a（(d,) ndarray）、b（(d,) ndarray）
- 返回：(d,) ndarray

**5. `bind(a, b)`**
- 返回a和b的绑定
- 结果向量在大多数情况下应与两个输入都不相似
- 参数：a（(d,) ndarray）、b（(d,) ndarray）
- 返回：(d,) ndarray

**6. `binding_power(v, exponent)`**
- 返回v的绑定幂
- 正指数：将v绑定自身(exponent-1)次
- 负指数：近似逆绑定自身
- 特殊指数：-1返回近似逆，0返回恒等向量，1返回v本身
- 默认实现仅支持整数指数，需要代数有左恒等元
- 参数：v（(d,) ndarray）、exponent（int或float）
- 返回：(d,) ndarray

**7. `invert(v, sidedness=TWO_SIDED)`**
- 反转向量v
- 向量绑定其逆将得到恒等向量
- 某些代数可能仅在特定侧有逆
- 参数：v（(d,) ndarray）、sidedness（ElementSidedness，可选）
- 返回：(d,) ndarray

**8. `get_binding_matrix(v, swap_inputs=False)`**
- 返回与固定向量绑定的变换矩阵
- 参数：v（(d,) ndarray）、swap_inputs（bool，可选）— 默认v成为右操作数，设为True则v成为左操作数
- 返回：(d, d) ndarray

**9. `get_inversion_matrix(d, sidedness=TWO_SIDED)`**
- 返回反转向量的变换矩阵
- 参数：d（int）、sidedness（ElementSidedness，可选）
- 返回：(d, d) ndarray

**10. `implement_superposition(n_neurons_per_d, d, n)`**
- 实现向量叠加的神经网络
- 参数：n_neurons_per_d（int）、d（int）、n（int）— 要叠加的向量数
- 返回：tuple (net, inputs, output)

**11. `implement_binding(n_neurons_per_d, d, unbind_left, unbind_right)`**
- 实现向量绑定的神经网络
- 参数：n_neurons_per_d（int）、d（int）、unbind_left（bool）、unbind_right（bool）
- 返回：tuple (net, inputs, output)

**12. `sign(v)`**
- 返回v的符号（由代数定义）
- 类似于复数的符号：绑定两个同号向量产生"正"向量
- 可能有多种负号类型
- 如果代数支持分数绑定幂，应对所有"非负"向量支持，对"负"向量不支持
- 参数：v（(d,) ndarray）
- 返回：AbstractSign

**13. `abs(v)`**
- 返回v的绝对向量（由代数定义）
- 应是与输入向量相关的"正"向量
- 默认实现要求代数的可能符号对应代数中的实际向量
- 参数：v（(d,) ndarray）
- 返回：(d,) ndarray

**14. `absorbing_element(d, sidedness=TWO_SIDED)`**
- 返回维度d的标准吸收元
- 吸收元绑定另一向量时产生自身的缩放版本
- 标准吸收元是范数为1的吸收元
- 参数：d（int）、sidedness（ElementSidedness，可选）
- 返回：(d,) ndarray

**15. `identity_element(d, sidedness=TWO_SIDED)`**
- 返回维度d的恒等元
- 恒等元不改变其绑定的向量
- 参数：d（int）、sidedness（ElementSidedness，可选）
- 返回：(d,) ndarray

**16. `negative_identity_element(d, sidedness=TWO_SIDED)`**
- 返回维度d的负恒等元
- 负恒等元仅改变其绑定向量的符号
- 参数：d（int）、sidedness（ElementSidedness，可选）
- 返回：(d,) ndarray

**17. `zero_element(d, sidedness=TWO_SIDED)`**
- 返回维度d的零元
- 零元绑定另一向量时产生自身
- 参数：d（int）、sidedness（ElementSidedness，可选）
- 返回：(d,) ndarray

### AbstractSign 抽象基类

```python
class nengo_spa.algebras.base.AbstractSign
```

基类：`abc.ABC`

为代数实现符号的抽象基类。

- `is_positive()`：返回符号是否为正
- `is_negative()`：返回符号是否为负
- `is_zero()`：返回符号是否既非正也非负（即零）但是确定的
- `is_indefinite()`：返回符号是否既非正也非负也非零
- `to_vector(d)`：返回代数中对应符号的向量

### GenericSign 类

```python
class nengo_spa.algebras.base.GenericSign(sign)
```

基类：`AbstractSign`

通用符号实现。参数sign取值为-1、0、1或None（None用于不确定符号）。

### CommonProperties 类

```python
class nengo_spa.algebras.base.CommonProperties
```

基类：`object`

代数中向量公共属性的常量定义。用于代数间的最佳互操作性。

- `UNITARY = 'unitary'`：酉向量不改变其绑定向量的长度
- `POSITIVE = 'positive'`：正向量不改变其绑定向量的符号；正向量允许分数绑定幂

---

## 全息约简表征（HRR）代数

### HrrAlgebra 类

```python
class nengo_spa.algebras.hrr_algebra.HrrAlgebra
```

基类：`AbstractAlgebra`

全息约简表征（Holographic Reduced Representations, HRRs）代数。

- 使用逐元素加法进行叠加
- 使用**圆卷积**（circular convolution）进行绑定，带有近似逆

圆卷积c的定义：
```
c[i] = Σ_j a[j] · b[i-j]
```
其中b的负索引回绕到向量末尾。

也可在傅里叶域中计算：
```
c = DFT⁻¹( DFT(a) ⊙ DFT(b) )
```
其中DFT是离散傅里叶变换算子，DFT⁻¹是其逆变换。

圆卷积作为绑定操作是**结合的、交换的、分配的**。

更多信息参见：Plate, Tony A. *Holographic Reduced Representation: Distributed Representation for Cognitive Structures*. Stanford, CA: CSLI Publications, 2003.

#### HRR方法详情

- **`is_valid_dimensionality(d)`**：所有正数都是有效维度
- **`create_vector(d, properties, *, rng=None)`**：properties为HrrProperties中定义的常量集合
- **`invert(v, sidedness=TWO_SIDED)`**：sidedness参数无效，因为HRR代数是交换的，逆是双侧的。逆将圆卷积变为圆相关，即A*B*~B近似等于A。示例：向量[1,2,3,4,5]的逆是[1,5,4,3,2]
- **`binding_power(v, exponent)`**：支持分数绑定幂。特殊指数：-1返回近似逆，0返回恒等向量，1返回v本身。对于整数指数和酉向量，v^a ⊛ v^b = v^(a+b)、(v^a)^b = v^(ab)成立
- **`absorbing_element(d)`**：圆卷积的吸收元是向量(1,1,…,1)^T/√d
- **`identity_element(d)`**：圆卷积的恒等元是向量(1,0,…,0)^T
- **`negative_identity_element(d)`**：圆卷积的负恒等元是向量(-1,0,…,0)^T
- **`zero_element(d)`**：圆卷积的零元是零向量

### HrrSign 类

```python
class nengo_spa.algebras.hrr_algebra.HrrSign(dc_sign, nyquist_sign)
```

基类：`AbstractSign`

表示HRR代数中的符号。

- 对于奇数维度，符号等于向量傅里叶表示中DC分量的符号
- 对于偶数维度，符号由DC分量和奈奎斯特频率的符号构成
- 总共有四个子符号（排除零）
- 整体符号为正当且仅当DC分量为正且奈奎斯特分量非负
- 绑定两个同子符号的语义指针产生正语义指针

**HRR绑定符号结果表**（仅给出上三角，因为矩阵是对称的）：

| 符号 (DC, Nyquist) | + (+1,+1) | − (+1,-1) | − (-1,+1) | − (−1,−1) | (0,0) |
|---|---|---|---|---|---|
| + (+1,+1) | + (+1,+1) | − (+1,-1) | − (−1,+1) | − (−1,−1) | (0,0) |
| − (+1,-1) | | + (1,+1) | − (−1,−1) | − (−1,+1) | (0,0) |
| − (−1,+1) | | | + (1,+1) | − (+1,-1) | (0,0) |
| − (−1,−1) | | | | + (1,+1) | (0,0) |
| (0,0) | | | | | (0,0) |

**符号对应向量表**：

| DC符号 | Nyquist符号 | 向量 |
|---|---|---|
| 1 | 1 | [1, 0, 0, …]（恒等） |
| 1 | -1 | [0, 1, 0, 0, …] |
| -1 | 1 | [0, -1, 0, …] |
| -1 | -1 | [-1, 0, 0, 0, …]（负恒等） |
| 0 | 0 | [0, 0, 0, …]（零） |

### HrrProperties 类

```python
class nengo_spa.algebras.hrr_algebra.HrrProperties
```

基类：`object`

HrrAlgebra支持的向量属性。
- `UNITARY = 'unitary'`
- `POSITIVE = 'positive'`

---

## 向量导出变换绑定（VTB）代数

### VtbAlgebra 类

```python
class nengo_spa.algebras.vtb_algebra.VtbAlgebra
```

基类：`AbstractAlgebra`

向量导出变换绑定（Vector-derived Transformation Binding, VTB）代数。

VTB使用逐元素加法进行叠加。绑定操作B(x, y)定义为：

```
B(x, y) := V_y · x
```

其中V_y是由y导出的分块对角矩阵：
```
V_y = d^(1/4) · [ y_1    y_2    …  y_d'    ]
                [ y_d'+1 y_d'+2 …  y_2d'   ]
                [ ⋮      ⋮      ⋱  ⋮       ]
                [ y_d-d'+1 y_d-d'+2 … y_d  ]
```
共d'个块，且d'² = d。

y的近似逆y⁺通过置换元素使得V_{y⁺} = V_y^T。

**注意**：VTB要求向量维度为完全平方数。

VTB绑定操作**既不结合也不交换**。此外，仅有右逆和右恒等元。通过转置V_y矩阵，可获得密切相关的TvtbAlgebra（转置VTB）代数，它具有双侧恒等元和逆。

更多信息参见：
- Gosmann, Jan, and Chris Eliasmith (2019). Vector-derived transformation binding: an improved binding operation for deep symbol-like processing in neural networks. *Neural computation* 31.5, 849-869.
- Jan Gosmann (2018). An Integrated Model of Context, Short-Term, and Long-Term Memory. UWSpace.

#### VTB方法详情

- **`is_valid_dimensionality(d)`**：所有完全平方数是有效维度
- **`create_vector(d, properties, *, rng=None)`**：创建正向量需要SciPy
- **`invert(v, sidedness=RIGHT)`**：VTB仅有右逆。自版本1.2.0起弃用默认sidedness=TWO_SIDED
- **`binding_power(v, exponent)`**：支持正向量的分数绑定幂（需要SciPy）。注意：VTB代数的绑定幂**不满足**通常的幂运算性质：B(v^a, v^b) = v^(a+b)不成立，(v^a)^b = v^(ab)不成立
- **`get_swapping_matrix(d)`**：获取在绑定状态中交换操作数的矩阵
- **`absorbing_element(d)`**：VTB除零向量外无吸收元，始终抛出NotImplementedError
- **`identity_element(d, sidedness=RIGHT)`**：VTB仅有右恒等元
- **`negative_identity_element(d, sidedness=RIGHT)`**：VTB仅有右负恒等元
- **`zero_element(d)`**：零向量

### VtbSign 类

```python
class nengo_spa.algebras.vtb_algebra.VtbSign(sign)
```

基类：`GenericSign`

表示VtbAlgebra中的符号。符号取决于从向量导出的绑定矩阵的对称性和正/负定性：
- 所有非对称矩阵的符号是不确定的
- 如果矩阵特征值有不同符号，符号也是不确定的
- 对称正定（负定）绑定矩阵对应正（负）符号
- 所有特征值等于0时符号也为0

### VtbProperties 类

```python
class nengo_spa.algebras.vtb_algebra.VtbProperties
```

基类：`object`

VtbAlgebra支持的向量属性。
- `UNITARY = 'unitary'`
- `POSITIVE = 'positive'`

---

## 转置向量导出变换绑定（TVTB）代数

### TvtbAlgebra 类

```python
class nengo_spa.algebras.tvtb_algebra.TvtbAlgebra
```

基类：`AbstractAlgebra`

转置向量导出变换绑定（Transposed Vector-derived Transformation Binding, TVTB）代数。

TVTB使用逐元素加法进行叠加。绑定操作B(x, y)定义为：

```
B(x, y) := V_y^T · x
```

其中V_y与VTB中定义相同，但使用其转置V_y^T。

y的近似逆y⁺通过置换元素使得V_{y⁺} = V_y^T。

**注意**：TVTB要求向量维度为完全平方数。

TVTB绑定操作**既不结合也不交换**。但与VTB不同，TVTB具有**双侧恒等元和逆**。其他属性与VTB等价。

#### TVTB方法详情

- **`is_valid_dimensionality(d)`**：所有完全平方数是有效维度
- **`create_vector(d, properties, *, rng=None)`**：创建正向量需要SciPy
- **`invert(v, sidedness=TWO_SIDED)`**：TVTB的逆是双侧的，sidedness参数无效
- **`binding_power(v, exponent)`**：支持正向量的分数绑定幂（需要SciPy）。对于整数指数，B(v^a, v^b) = v^(a+b)和(v^a)^b = v^(ab)成立（技术上对正酉向量也成立，但唯一这样的向量是恒等向量）
- **`absorbing_element(d)`**：TVTB除零向量外无吸收元，始终抛出NotImplementedError
- **`identity_element(d, sidedness=TWO_SIDED)`**：TVTB的恒等元是双侧的
- **`negative_identity_element(d, sidedness=TWO_SIDED)`**：TVTB的负恒等元是双侧的
- **`zero_element(d)`**：零向量

### TvtbSign 类

```python
class nengo_spa.algebras.tvtb_algebra.TvtbSign(sign)
```

基类：`GenericSign`

表示TvtbAlgebra中的符号。与VtbSign相同，符号取决于绑定矩阵的对称性和正/负定性。

### TvtbProperties 类

```python
class nengo_spa.algebras.tvtb_algebra.TvtbProperties
```

基类：`object`

TvtbAlgebra支持的向量属性。
- `UNITARY = 'unitary'`
- `POSITIVE = 'positive'`

---

## 三种代数对比总结

| 特性 | HRR | VTB | TVTB |
|---|---|---|---|
| 绑定操作 | 圆卷积 | V_y·x | V_y^T·x |
| 结合性 | 是 | 否 | 否 |
| 交换性 | 是 | 否 | 否 |
| 分配性 | 是 | 是 | 是 |
| 有效维度 | 所有正数 | 完全平方数 | 完全平方数 |
| 恒等元 | 双侧 | 仅右侧 | 双侧 |
| 逆 | 双侧 | 仅右侧 | 双侧 |
| 吸收元 | 有 | 无（除零） | 无（除零） |
| 分数绑定幂 | 支持 | 支持（正向量） | 支持（正向量） |
| 绑定幂运算性质 | 满足（整数/酉向量） | 不满足 | 满足（整数） |
| 符号类型 | DC+Nyquist双分量 | 基于矩阵对称性/定性 | 基于矩阵对称性/定性 |

## 关键结论

1. `nengo_spa.algebras` 模块为Nengo语义指针架构提供了三种代数实现：HRR（全息约简表征）、VTB（向量导出变换绑定）和TVTB（转置VTB）。
2. 所有代数都继承自`AbstractAlgebra`抽象基类，定义了叠加、绑定、反转、绑定幂、恒等元、吸收元、零元、符号等统一接口。
3. HRR使用圆卷积，是结合且交换的，支持所有正维度，具有双侧恒等元和逆。
4. VTB和TVTB使用向量导出的矩阵变换，既不结合也不交换，要求维度为完全平方数；VTB仅有右侧恒等元和逆，TVTB具有双侧恒等元和逆。
5. 每种代数都支持酉向量（unitary）和正向量（positive）两种属性，正向量允许分数绑定幂。
6. 代数可通过`implement_superposition`和`implement_binding`方法直接在Nengo神经网络中实现，支持神经形态计算。
7. 该模块是语义指针架构（SPA）的核心数学基础，用于在高维向量空间中表示和操作符号结构，是认知建模范式的关键组件。
