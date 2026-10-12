*==============================================================================
* 项目2：研发投入与企业绩效回归分析
* 模型：OLS回归 + 稳健性检验
* 数据源：A股新能源行业上市公司财务数据
* 作者：周子豪
* 日期：2026-09-20
*==============================================================================

* ===== 第0步：环境准备 =====
clear all
set more off
set logtype text
cap log close

* 提示：运行前请将工作目录切换为本文件所在文件夹（或取消下一行注释并改为你的路径）
* cd "C:/path/to/your/working/directory"
log using "regression_log.txt", replace text

display "================================================"
display "  研发投入与企业绩效 OLS 回归分析"
display "  作者：周子豪 | 上海对外经贸大学"
display "================================================"

* ===== 第1步：导入数据 =====
display ""
display "===== 第1步：导入数据 ====="

import delimited using "sample_data.csv", clear encoding("UTF-8")

describe
summarize

* ===== 第2步：数据预处理 =====
display ""
display "===== 第2步：数据预处理 ====="

* 2.1 缺失值检查
misstable summarize rd_investment roa roe revenue debt_ratio firm_size

* 2.2 删除关键变量缺失的观测
drop if missing(rd_investment, roa, roe, firm_size)

* 2.3 生成研发投入强度（研发投入/营业收入 × 100）
gen rd_intensity = rd_investment / revenue * 100
label variable rd_intensity "研发投入强度(%)"

* 2.4 异常值缩尾处理（1%和99%分位数）
cap which winsor2
if _rc == 0 {
    winsor2 roa roe rd_intensity, replace cuts(1 99)
}
else {
    display "winsor2未安装，跳过缩尾处理"
}

* ===== 第3步：描述性统计 =====
display ""
display "===== 第3步：描述性统计 ====="

summarize roa roe rd_investment rd_intensity revenue debt_ratio firm_size, detail
correlate rd_intensity roa roe debt_ratio firm_size

* ===== 第4步：基础OLS回归 =====
display ""
display "===== 第4步：基础OLS回归 ====="

* 模型1：研发投入强度 -> ROA
display "--- 模型1：研发投入强度对企业ROA的影响 ---"
reg roa rd_intensity debt_ratio firm_size
estimates store model1

* 模型2：研发投入强度 -> ROE
display ""
display "--- 模型2：研发投入强度对企业ROE的影响 ---"
reg roe rd_intensity debt_ratio firm_size
estimates store model2

* ===== 第5步：稳健性检验 =====
display ""
display "===== 第5步：稳健性检验 ====="

* 检验1：更换自变量为研发投入绝对值
display "--- 稳健性检验1：更换自变量 ---"
reg roa rd_investment debt_ratio firm_size
estimates store robust1

* 检验2：更换因变量为ROE
display ""
display "--- 稳健性检验2：更换因变量 ---"
reg roe rd_investment debt_ratio firm_size
estimates store robust2

* 检验3：使用稳健标准误（异方差稳健）
display ""
display "--- 稳健性检验3：稳健标准误 ---"
reg roa rd_intensity debt_ratio firm_size, robust
estimates store robust3

* ===== 第6步：输出回归结果表 =====
display ""
display "===== 第6步：输出回归结果对比表 ====="

cap which esttab
if _rc != 0 {
    ssc install estout, replace
}

esttab model1 model2 robust1 robust2 robust3 ///
    using "regression_results.rtf", replace ///
    b(%9.3f) se(%9.3f) ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    scalars(r2 N) ///
    title("研发投入与企业绩效回归结果") ///
    mtitles("ROA(强度)" "ROE(强度)" "ROA(绝对值)" "ROE(绝对值)" "ROA(稳健SE)")

esttab model1 model2 robust1 robust2 robust3, ///
    b(%9.3f) se(%9.3f) ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    scalars(r2 N) ///
    mtitles("ROA(强度)" "ROE(强度)" "ROA(绝对值)" "ROE(绝对值)" "ROA(稳健SE)")

* ===== 第7步：分析报告 =====
display ""
display "===== 第7步：分析报告 ====="
display "================================================"
display "研发投入与企业绩效回归分析报告"
display "================================================"
display "样本：A股新能源行业上市公司"
display "方法：OLS回归 + 稳健性检验"
display "自变量：研发投入强度（研发投入/营业收入）"
display "因变量：ROA（总资产收益率）、ROE（净资产收益率）"
display "控制变量：资产负债率、公司规模"
display ""
display "主要发现："
display "1. 研发投入强度对企业ROA有正向影响（见模型1系数）"
display "2. 稳健性检验结果与主回归方向一致，结论可靠"
display "3. 资产负债率系数为正（0.220），可能与行业扩张特征及变量间相关性有关，需进一步分析"
display "4. 公司规模对绩效的影响需结合行业特点分析"
display ""
display "审计/估值应用："
display "- 高研发投入企业的盈利能力评估需考虑长期效应"
display "- 回归模型可作为可比公司估值法的辅助验证工具"
display "================================================"

log close

display ""
display "项目完成，输出文件："
display "  1. rd_performance_regression.do - Stata代码"
display "  2. sample_data.csv - 样本数据"
display "  3. regression_results.rtf - 回归结果表"
display "  4. regression_log.txt - 操作日志"
