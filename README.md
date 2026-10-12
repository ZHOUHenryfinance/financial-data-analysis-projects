# 财务数据分析项目 | Python + Stata

> 上海对外经贸大学 资产评估专硕 周子豪

## 项目1：A股新能源行业上市公司财务数据清洗（Python）

- **工具**：Python 3.12 + akshare + pandas + numpy
- **功能**：获取新能源行业上市公司财务指标数据，完成缺失值中位数填补、IQR异常值Winsorize缩尾处理、百分比单位统一、按股票代码去重
- **输出**：清洗后数据集（CSV/Excel）+ 分析报告
- **文件**：`financial_data_cleaning.py`

## 项目2：研发投入与企业绩效OLS回归分析（Stata）

- **工具**：Stata 19 MP
- **功能**：OLS回归分析研发投入对ROA/ROE的影响，含3组稳健性检验
- **模型**：`ROA = β0 + β1×RD_intensity + β2×Debt_ratio + β3×Firm_size + ε`
- **稳健性检验**：更换自变量、更换因变量、异方差稳健标准误
- **文件**：`rd_performance_regression.do` + `sample_data.csv`

## 数据说明

- 项目1：通过 akshare 公开接口获取A股新能源行业上市公司财务指标（2023年最新一期），清洗、去重后得到47家样本，输出为 `cleaned_financial_data.csv`。
- 项目2：`sample_data.csv` 中公司名称已做匿名化处理（XN_NewEnergy_XX 编号形式），回归分析代码可基于该数据完整复现。
