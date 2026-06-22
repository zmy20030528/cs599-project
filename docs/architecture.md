# 系统架构说明

本文件是便于评阅的入口；可执行架构决策、时序图和数据契约见 [Architecture Spec](architecture-spec.md)，产品验收见 [Product Spec](product-spec.md)，接口见 [API Spec](api-spec.md)。

核心拓扑：`START → Fetcher → [Quant | News | Risk] → CIO → Memory → END`。

