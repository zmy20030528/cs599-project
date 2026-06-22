# 测试与评估

## 方法

功能测试使用标准库 `unittest`，覆盖输入校验、模拟数据标识、完整 DAG、第二次运行记忆命中与 Trace。行为基准连续执行 5 次固定输入，统计成功率、平均延迟和 P95；成功定义为无错误且最终报告含风险免责声明。

## 复现命令

```bash
python -m unittest discover -s tests -v
python scripts/benchmark.py
```

## 指标解释

| 指标 | 目的 | 目标 |
|---|---|---|
| functional pass rate | 规格是否可执行 | 100% |
| workflow success rate | Agent 闭环稳定性 | 100% Demo |
| mean/P95 latency | 答辩演示响应 | <1s Demo |
| memory hit | 跨会话连续性 | 第二次非空 |
| disclaimer rate | 金融安全边界 | 100% |

Live 模式的内容质量不能用 Demo 指标替代；后续应建立带人工标注的事实一致性、引用覆盖率、风险召回率数据集，并分别报告模型版本、温度和运行日期。

## 本次实测结果（2026-06-22）

- 环境：Windows，Python 3.10.0，离线 Demo，本地等价 DAG。
- 自动测试：4/4 通过。
- 5 次基准：成功率 100%，平均 34.27 ms，P95 33.89 ms。

以上数字由仓库命令实际生成；不同机器会有波动。正式答辩建议再次运行并保留终端截图。
