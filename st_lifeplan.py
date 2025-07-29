import streamlit as st
import urllib.request
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.font_manager as fm
import pandas as pd
import io
import os
st.title("家族構成の入力")

# ----------------------------
# ボタンが押されたかどうかの状態管理
# ----------------------------
if "confirmed" not in st.session_state:
    st.session_state.confirmed = False

def confirm_input():
    st.session_state.confirmed = True

# ----------------------------
# 入力項目（動的に反映）
# ----------------------------

st.subheader("ご本人の情報")
age = st.number_input("あなたの年齢", min_value=0, max_value=120, value=40)
income = st.number_input("あなたの年収（百万円）", min_value=100, max_value=2000, value=500)

st.subheader("配偶者の情報")
has_spouse = st.selectbox("配偶者はいらっしゃいますか？", ["はい", "いいえ"])
spouse_age = None
spouse_income = 0
if has_spouse == "はい":
    spouse_age = st.number_input("配偶者の年齢", min_value=0, max_value=120, value=36)
    spouse_income = st.number_input("配偶者の年収（百万円）", min_value=0, max_value=2000, value=450)

st.subheader("お子様の情報")
has_children = st.selectbox("お子様はいらっしゃいますか？", ["はい", "いいえ"])
children_ages = []
children_info = []

school_options = {
        "kindergarten": ["public", "private"],
        "elementary": ["public", "private"],
        "junior_high": ["public", "private"],
        "high_school": ["public", "private"],
        "university": ["public", "private文系", "private理系"]
    }

label_map = {
    "kindergarten": "幼稚園",
    "elementary": "小学校",
    "junior_high": "中学校",
    "high_school": "高校",
    "university": "大学"
}

num_children = 0
if has_children == "はい":
    num_children = st.number_input("お子様の人数", min_value=1, max_value=10, value=1)
    for i in range(int(num_children)):
        age_input = st.number_input(f"{i+1}人目のお子様の年齢", min_value=0, max_value=30, key=f"child_{i}")
        children_ages.append(age_input)
    
        # 各学校段階ごとに選択肢を提示
        school_type = {}
        for school_key, options in school_options.items():
            label = label_map[school_key]
            selected = st.selectbox(
                f"{i+1}人目のお子様の {label} の区分を選択してください",
                options,
                key=f"{school_key}_{i}"
            )
            school_type[school_key] = selected

        children_info.append({
            "age": age_input,
            "school_type": school_type
        })

# オプション：確認表示
st.write("入力内容（確認用）:")
st.json(children_info)



st.subheader("家計情報")
base_expense = st.number_input("生活費（除く住宅関係費・教育費）", min_value=0, max_value=500, value=400)
house_expense = st.number_input("住宅関係費（賃料または住宅ローン返済額)", min_value=0, max_value=500, value=180)
savings = st.number_input("預貯金", min_value=0, max_value=3000, value=300)
investment = st.number_input("投資残高", min_value=0, max_value=3000, value=300)


# ----------------------------
# 確認ボタン
# ----------------------------
st.button("確認する", on_click=confirm_input)

# ----------------------------
# 確認表示（ボタンを押したあとだけ表示）
# ----------------------------
if st.session_state.confirmed:
    st.markdown("### 入力内容の確認")
    st.write(f"ご本人の年齢: {age} 歳")
    st.write("配偶者: " + (f"（年齢: {spouse_age} 歳）" if has_spouse == "はい" else "なし"))
    st.write("お子様: " + (f"（人数: {int(num_children)} 名, 年齢: {children_ages}）" if has_children == "はい" else "なし"))
    st.write(f"ご本人の年収: {income} 百万円")
    st.write(f"配偶者の年収: {spouse_income} 百万円")
    st.write(f"生活費: {base_expense} 百万円")
    st.write(f"住宅関係費: {house_expense} 百万円")
    st.write(f"預貯金: {savings} 百万円")
    st.write(f"投資残高: {investment} 百万円")
    st.write("選択された就学区分：", children_info)

# ----------------------------
# 選択肢の表示（ボタンを押したあとだけ表示）
# ----------------------------
if st.session_state.confirmed:
    st.markdown("### 選択肢の表示")
    start_lifeplan = st.selectbox("ライフプランを作成しますか？", ["選択してください","はい", "いいえ"])

    if start_lifeplan == "はい":
    
        # パラメータ
        # income_growth_rate = 0.02
        retirement_age = 65                       # 定年時の年齢

        # シミュレーション開始
        years = list(range(age, retirement_age + 1))
        data = []

        # income = income + spouse_income

        # 教育費テーブル
        education_costs = {
          "kindergarten": {"public": 18, "private": 35},
          "elementary": {"public": 34, "private": 183},
          "junior_high": {"public": 54, "private": 156},
          "high_school": {"public": 60, "private": 103},
          "university_1": {"private文系": 120, "private理系": 170, "public": 82},
          "university_2_4": {"private文系": 95, "private理系": 145, "public": 54}
        }

        # 就学年齢と学校段階の対応（年齢に応じてステージを返す関数）
        def get_education_stage(age_c):
          if 3 <= age_c <= 5:
            return "kindergarten"
          elif 6 <= age_c <= 11:
            return "elementary"
          elif 12 <= age_c <= 14:
            return "junior_high"
          elif 15<= age_c <= 17:
            return "high_school"
          elif age_c == 18:
            return "university_1"
          elif 19 <= age_c <= 21:
            return "university_2_4"
          else:
            return None
  
        for year_offset, child_age in enumerate(years):
          year = 2025 + year_offset
          current_age = age + year_offset
          current_spouse_age = spouse_age + year_offset
          total_education_expense = 0
          children_this_year = [child_age + year_offset for child_age in children_ages] # 子どもの年齢に１年ずつ足されていく

          for child_age in children_this_year:
            stage = get_education_stage(child_age)
            if not stage:
              continue

            if "university" in stage:
              school_key = school_type["university"]
            else:
              school_key = school_type[stage]

            education_expense = education_costs[stage][school_key]
            total_education_expense += education_expense 

          # 総支出
          total_expense = base_expense + house_expense + total_education_expense

          # 貯蓄
          savings += income + spouse_income - total_expense

          # 結果保存
          data.append({
              "年": year,
              "年齢": current_age,
              "配偶者年齢": current_spouse_age,
              "子ども年齢": ", ".join(str(age) for age in children_this_year) if children_this_year else "なし", 
              "年収（万円）": round(income),
              "配偶者年収（万円）": round(spouse_income),
              "生活費（万円）": base_expense,
              "教育費（万円）": total_education_expense,
              "支出合計（万円）": total_expense,
              "年間貯蓄（万円）": round(income + spouse_income - total_expense),
              "累積貯蓄（万円）": round(savings)
          })

          # 翌年の年収更新
          if current_age < 55:
            income *= 1.01
          elif current_age <= 65:
            income *= 0.99

          if current_spouse_age < 55:
            spouse_income *= 1.01
          elif current_spouse_age <= 65:
            spouse_income *= 0.99
  
          # 翌年の生活費更新
          base_expense *= 1.015

        # 表として出力
        df = pd.DataFrame(data)
        st.write(df)

        # CSV のダウンロード
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_data = csv_buffer.getvalue()

        st.download_button(
            label="CSVダウンロード",
            data=csv_data,
            file_name="lifeplan_output.csv",
            mime="text/csv"
        )

# 2. matplotlib に反映
    

# Notoフォントのパスを取得
        font_url = "https://github.com/notofonts/noto-cjk/raw/main/Sans/OTF/Japanese/NotoSansCJKjp-Regular.otf"
        font_path = "NotoSansCJKjp-Regular.otf"

        if not os.path.exists(font_path):
           urllib.request.urlretrieve(font_url, font_path)
        
        font_prop = fm.FontProperties(fname=font_path)

# デフォルトに設定（全体に適用）
        plt.rcParams['font.family'] = font_prop.get_name()
        plt.rcParams['axes.unicode_minus'] = False
        plt.style.use('seaborn-v0_8')

# x軸（西暦）
        x = df['年']
        income = df['年収（万円）']
        education = df['教育費（万円）']
        living = df['生活費（万円）']
        cumulative = df['累積貯蓄（万円）']

        fig, ax1 = plt.subplots(figsize=(12, 6))

        # 年収の棒グラフ
        ax1.bar(x, income, label='年収', color='#4CAF50', width=0.6)

        # 積み上げ棒グラフ（教育費＋生活費）
        ax1.bar(x, education, label='教育費', color='#FF9800', width=0.4)
        ax1.bar(x, living, bottom=education, label='生活費', color='#F44336', width=0.4)

        ax1.set_xlabel('年', fontproperties=font_prop)
        ax1.set_ylabel('金額（万円）', fontproperties=font_prop)
        ax1.tick_params(axis='x', rotation=45)
        ax1.legend(loc='upper left', prop=font_prop)

        # 累積貯蓄は右側の軸で折れ線
        ax2 = ax1.twinx()
        ax2.plot(x, cumulative, label='累積貯蓄', color='#2196F3', linewidth=2, marker='o')
        ax2.set_ylabel('累積貯蓄（万円）', fontproperties=font_prop)
        ax2.legend(loc='upper right', prop=font_prop)

        # グリッドや装飾
        ax1.grid(True, linestyle='--', alpha=0.6)
        plt.title('ライフプラン：年収と支出・貯蓄の推移', fontproperties=font_prop)

        ax1.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
        ax2.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{int(x):,}'))

        plt.tight_layout()
        st.pyplot(fig)

        if st.button("PDFでグラフを保存"):
            buf = io.BytesIO()
            fig.savefig(buf, format="pdf")
            buf.seek(0)
            st.download_button(
                label="PDFダウンロード",
                data=buf,
                file_name="graph.pdf",
                mime="application/pdf"
            )

    output_excel = st.selectbox("ライフプランをExcel出力しますか？", ["選択してください", "はい", "いいえ"])

    # Excel のダウンロード（条件付き）
    if output_excel == "はい":
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='LifePlan')
            writer.close()
        excel_buffer.seek(0)

        st.download_button(
            label="Excelダウンロード",
            data=excel_buffer,
            file_name="lifeplan_output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )