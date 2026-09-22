# -*- coding: utf-8 -*-
"""
A股新能源行业上市公司财务数据清洗
数据源：akshare（开源A股数据接口）
作者：周子豪
日期：2026-09-20
"""

import akshare as ak
import pandas as pd
import numpy as np
import os
import warnings
warnings.filterwarnings('ignore')


def get_new_energy_stocks():
    """获取A股新能源行业上市公司列表"""
    print("=" * 60)
    print("Step 1: 获取A股新能源行业上市公司列表")
    print("=" * 60)

    try:
        stock_list = ak.stock_zh_a_spot_em()
        print(f"获取A股股票列表：{len(stock_list)} 只")
    except Exception as e:
        print(f"stock_zh_a_spot_em接口异常，切换备用接口: {e}")
        stock_list = ak.stock_info_a_code_name()
        stock_list.columns = ['代码', '名称']

    # 关键词模糊匹配筛选新能源相关股票
    keywords = ['新能', '光伏', '锂电', '风电', '储能', '新能源', '电池', '充电',
                '太阳能', '氢能', '核电', '水电', '碳']
    mask = stock_list['名称'].str.contains('|'.join(keywords), na=False)
    new_energy_stocks = stock_list[mask].copy()

    # 排除ST股（特别处理股票，财务数据非常规）
    new_energy_stocks = new_energy_stocks[~new_energy_stocks['名称'].str.contains('ST', na=False)]

    if '代码' in new_energy_stocks.columns:
        new_energy_stocks = new_energy_stocks[['代码', '名称']].drop_duplicates()
    else:
        new_energy_stocks = new_energy_stocks[['code', 'name']].copy()
        new_energy_stocks.columns = ['代码', '名称']

    if len(new_energy_stocks) > 50:
        new_energy_stocks = new_energy_stocks.head(50)

    print(f"筛选结果：{len(new_energy_stocks)} 只新能源相关股票")
    print(new_energy_stocks.head(10).to_string(index=False))
    return new_energy_stocks


def get_financial_data(stock_list):
    """批量获取上市公司财务分析指标"""
    print("\n" + "=" * 60)
    print("Step 2: 批量获取财务报表数据")
    print("=" * 60)

    all_data = []
    success_count = 0
    fail_count = 0

    for idx, row in stock_list.iterrows():
        code = row['代码']
        name = row['名称']

        try:
            df = ak.stock_financial_analysis_indicator(symbol=code, start_year="2023")

            if df is not None and len(df) > 0:
                df = df.head(1)  # 取最新一期
                df['股票代码'] = code
                df['股票名称'] = name
                all_data.append(df)
                success_count += 1
                print(f"  [{success_count}/{len(stock_list)}] {name}({code}) - OK")
            else:
                fail_count += 1
                print(f"  [{success_count+fail_count}/{len(stock_list)}] {name}({code}) - 无数据")

        except Exception as e:
            fail_count += 1
            print(f"  [{success_count+fail_count}/{len(stock_list)}] {name}({code}) - 失败: {str(e)[:30]}")

    print(f"\n获取完成：成功 {success_count} 家，失败 {fail_count} 家")

    if all_data:
        raw_data = pd.concat(all_data, ignore_index=True)
        return raw_data
    else:
        print("错误：未获取到任何数据")
        return pd.DataFrame()


def clean_data(raw_data):
    """数据清洗：缺失值处理、异常值缩尾、单位统一、去重"""
    print("\n" + "=" * 60)
    print("Step 3: 数据清洗")
    print("=" * 60)

    df = raw_data.copy()
    print(f"原始数据：{df.shape[0]} 行 x {df.shape[1]} 列")

    # 3.1 删除缺失率>80%的列（保留标识列）
    missing_ratio = df.isnull().sum() / len(df)
    cols_to_drop = missing_ratio[missing_ratio > 0.8].index.tolist()
    cols_to_drop = [c for c in cols_to_drop if c not in ['股票代码', '股票名称']]
    df = df.drop(columns=cols_to_drop)
    print(f"  3.1 删除缺失率>80%的列：{len(cols_to_drop)} 列，剩余 {df.shape[1]} 列")

    # 3.2 中位数填补数值型缺失值（robust to outliers）
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    for col in numeric_cols:
        if df[col].isnull().sum() > 0:
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)
    print(f"  3.2 中位数填补：{len(numeric_cols)} 个数值列")

    # 3.3 IQR方法识别异常值 + Winsorize缩尾处理
    key_indicators = ['净资产收益率(%)', '销售毛利率(%)', '销售净利率(%)',
                      '资产负债率(%)', '流动比率', '存货周转率']

    for col in key_indicators:
        if col in df.columns:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 3 * IQR
            upper_bound = Q3 + 3 * IQR
            df[col] = df[col].clip(lower=lower_bound, upper=upper_bound)

    print(f"  3.3 Winsorize缩尾：{len(key_indicators)} 个关键指标")

    # 3.4 百分比类指标单位统一
    percent_cols = [c for c in df.columns if '(%)' in c or '率' in c]
    for col in percent_cols:
        if df[col].max() < 1:
            df[col] = df[col] * 100
    print(f"  3.4 单位统一：{len(percent_cols)} 个百分比指标")

    # 3.5 按股票代码去重
    before = len(df)
    df = df.drop_duplicates(subset=['股票代码'], keep='first')
    after = len(df)
    print(f"  3.5 去重：删除 {before - after} 行")

    print(f"\n清洗后数据：{df.shape[0]} 行 x {df.shape[1]} 列")
    return df


def export_data(cleaned_data, output_dir='.'):
    """导出清洗后数据集（CSV + Excel）"""
    print("\n" + "=" * 60)
    print("Step 4: 导出数据集")
    print("=" * 60)

    csv_path = os.path.join(output_dir, 'cleaned_financial_data.csv')
    cleaned_data.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print(f"  CSV: {csv_path}")

    xlsx_path = os.path.join(output_dir, 'cleaned_financial_data.xlsx')
    cleaned_data.to_excel(xlsx_path, index=False)
    print(f"  Excel: {xlsx_path}")

    return csv_path, xlsx_path


def generate_report(cleaned_data):
    """生成分析报告"""
    print("\n" + "=" * 60)
    print("Step 5: 分析报告")
    print("=" * 60)

    report_lines = []
    report_lines.append("=" * 60)
    report_lines.append("A股新能源行业上市公司财务数据分析报告")
    report_lines.append("=" * 60)
    report_lines.append(f"样本数量：{len(cleaned_data)} 家上市公司")
    report_lines.append(f"数据来源：akshare")
    report_lines.append(f"清洗步骤：缺失值中位数填补、IQR缩尾处理、单位统一、去重")
    report_lines.append("")

    key_cols = ['净资产收益率(%)', '销售毛利率(%)', '销售净利率(%)',
                '资产负债率(%)', '流动比率']

    for col in key_cols:
        if col in cleaned_data.columns:
            mean_val = cleaned_data[col].mean()
            median_val = cleaned_data[col].median()
            std_val = cleaned_data[col].std()
            report_lines.append(f"{col}：均值{mean_val:.2f}，中位数{median_val:.2f}，标准差{std_val:.2f}")

    report_lines.append("")
    report_lines.append("主要发现：")
    report_lines.append("1. 盈利能力：通过ROE和销售净利率评估新能源上市公司整体盈利水平。")
    report_lines.append("2. 财务风险：资产负债率反映杠杆水平，流动比率反映短期偿债能力。")
    report_lines.append("3. 数据质量：IQR缩尾处理剔除极端值，中位数填补缺失值，")
    report_lines.append("   确保数据集可用于后续回归分析或审计底稿验证。")
    report_lines.append("")
    report_lines.append("应用场景：")
    report_lines.append("- 审计风险评估：高负债率+低ROE组合可标识为高风险客户")
    report_lines.append("- 资产估值参考：行业均值可作为可比公司估值法的基准数据")
    report_lines.append("=" * 60)

    report_text = '\n'.join(report_lines)
    print(report_text)

    report_path = 'analysis_report.txt'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_text)
    print(f"\n报告已保存：{report_path}")
    return report_text


def main():
    print("=" * 60)
    print("A股新能源行业上市公司财务数据清洗")
    print("工具：Python + akshare")
    print("=" * 60 + "\n")

    stock_list = get_new_energy_stocks()
    raw_data = get_financial_data(stock_list)

    if raw_data.empty:
        print("未获取到数据，程序结束")
        return

    cleaned_data = clean_data(raw_data)
    csv_path, xlsx_path = export_data(cleaned_data)
    generate_report(cleaned_data)

    print("\n项目完成，输出文件：")
    print("  1. financial_data_cleaning.py - 源代码")
    print("  2. cleaned_financial_data.csv - 清洗后数据集")
    print("  3. cleaned_financial_data.xlsx - 清洗后数据集（Excel）")
    print("  4. analysis_report.txt - 分析报告")


if __name__ == '__main__':
    main()
