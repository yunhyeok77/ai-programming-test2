import pandas as pd


def 정제(df):
	# 점수가 비어 있는 행을 삭제한다.
	df = df.dropna(subset=["점수"]).copy()
	print("점수 비어 있는 행 삭제 후:", len(df))

	# 모든 열이 완전히 같은 행은 하나만 남긴다.
	df = df.drop_duplicates()
	print("완전히 같은 행 중복 제거 후:", len(df))

	# 반과 과목의 앞뒤 공백을 제거한다.
	df["반"] = df["반"].astype("string").str.strip()
	df["과목"] = df["과목"].astype("string").str.strip()
	print("반과 과목 공백 제거 후:", len(df))

	# 점수가 정수가 아니거나 0~100 범위를 벗어난 행을 삭제한다.
	scores = pd.to_numeric(df["점수"], errors="coerce")
	valid = scores.between(0, 100) & scores.mod(1).eq(0)
	df = df.loc[valid].copy()
	df["점수"] = scores.loc[df.index].astype(int)
	print("점수 유효성 검사 후:", len(df))

	return df


df = pd.read_csv("scores_2026.csv")
print(정제(df))
df = 정제(df)




print("#1.필터링 프롬포트 결과 ")


df_math = df[df['과목'] == '수학']
print("수학 과목 행 수:", len(df))



print("2.그룹화")


# '반'별 점수 평균
class_score_avg = df.groupby('반')['점수'].mean()
print("반별 점수 평균:")
print(class_score_avg)

# '과목'과 '반'별 점수 평균
subject_class_score_avg = df.groupby(['과목', '반'])['점수'].mean()
print("과목 및 반별 점수 평균:")
print(subject_class_score_avg)




print("3.통계")
class_score_summary = df.groupby('반')['점수'].agg(
	개수='count',
	평균='mean',
	중앙값='median',
	최댓값='max'
).round(2)
print("반별 점수 요약:")
print(class_score_summary)


print("합계일치")
print(df.groupby("반")["점수"].sum().sum())  # 7484.0
print(df["점수"].sum())  # 7484.0


print(df.groupby("반")["점수"].count().sum())  # 100
print(len(df))  # 100

print("스팟 체크")
print(df[(df["반"]=="1반") & (df["과목"]=="수학")]["점수"])
