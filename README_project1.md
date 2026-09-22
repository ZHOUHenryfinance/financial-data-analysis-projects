# A股新能源行业上市公司财务数据清洗

## 项目概述

使用Python + akshare开源接口，批量获取A股新能源行业50家上市公司财务指标数据，完成数据清洗全流程（缺失值处理、异常值缩尾、单位统一、去重），输出可用于审计分析和回归建模的干净数据集。

## 技术栈

- Python 3.12
- akshare（A股开源数据接口）
- pandas（数据处理）
- numpy（数值计算）
- openpyxl（Excel导出）

## 数据清洗流程

| 步骤 | 方法 | 说明 |
|------|------|------|
| 缺失值处理 | 中位数填补 | 对数值型列用中位数填补，避免极端值干扰 |
| 异常值处理 | IQR + Winsorize缩尾 | 对6个关键财务指标用四分位距识别异常值，用边界值替换 |
| 单位统一 | 百分比格式校准 | 检查百分比类指标是否为小数格式，统一为百分比 |
| 去重 | 按股票代码去重 | 确保每家公司唯一 |

## 关键财务指标

- 净资产收益率 ROE (%)
- 销售毛利率 (%)
- 销售净利率 (%)
- 资产负债率 (%)
- 流动比率
- 存货周转率

## 输出文件

| 文件 | 说明 |
|------|------|
| `financial_data_cleaning.py` | 源代码 |
| `cleaned_financial_data.csv` | 清洗后数据集（CSV格式） |
| `cleaned_financial_data.xlsx` | 清洗后数据集（Excel格式） |
| `analysis_report.txt` | 数据分析报告 |

## 运行方式

```bash
pip install akshare pandas numpy openpyxl
python financial_data_cleaning.py
```

## 应用场景

- **审计风险评估**：高负债率 + 低ROE组合可标识为高风险客户
- **资产估值参考**：行业均值可作为可比公司估值法的基准数据
