import pytest

from load_scores import load_scores


def _write_csv(tmp_path, contents):
	path = tmp_path / "scores.csv"
	path.write_text(contents, encoding="utf-8")
	return path


def test_load_scores_keeps_valid_rows_and_ignores_header_and_blank_lines(tmp_path):
	path = _write_csv(tmp_path, "name,score\nAlice,90\n\n Bob , 75 \n")

	assert load_scores(path) == ([('Alice', 90), ('Bob', 75)], [])


@pytest.mark.parametrize(
	("row", "reason"),
	[
		("only-one-column", "열 개수가 2가 아님"),
		("extra,column,here", "열 개수가 2가 아님"),
		(",80", "이름이 비어 있음"),
		("Alice,", "점수가 비어 있음"),
		("Alice,eighty", "점수가 정수가 아님"),
		("Alice,10.5", "점수가 정수가 아님"),
		("Alice,-1", "점수가 0~100 밖"),
		("Alice,101", "점수가 0~100 밖"),
	],
)
def test_load_scores_records_invalid_rows(tmp_path, row, reason):
	path = _write_csv(tmp_path, f"name,score\n{row}\n")

	kept, skipped = load_scores(path)

	assert kept == []
	assert skipped == [(2, row, reason)]


@pytest.mark.parametrize("score", [0, 100])
def test_load_scores_accepts_score_boundaries(tmp_path, score):
	path = _write_csv(tmp_path, f"name,score\nBoundary,{score}\n")

	assert load_scores(path) == ([('Boundary', score)], [])


def test_load_scores_preserves_line_numbers_when_skipping_blank_lines(tmp_path):
	path = _write_csv(tmp_path, "name,score\nA,101\n\nB,nope\n")

	kept, skipped = load_scores(path)

	assert kept == []
	assert skipped == [
		(2, "A,101", "점수가 0~100 밖"),
		(4, "B,nope", "점수가 정수가 아님"),
	]


def test_load_scores_raises_for_missing_file(tmp_path):
	with pytest.raises(FileNotFoundError):
		load_scores(tmp_path / "missing.csv")
