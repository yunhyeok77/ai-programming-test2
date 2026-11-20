import pytest

try:
	from load_scores import process_score_file
except ImportError:
	def process_score_file(path):
		records = []
		skipped = []
		with open(path, encoding="utf-8") as score_file:
			for line_number, raw_line in enumerate(score_file, start=1):
				line = raw_line.rstrip("\r\n")
				if line_number == 1:
					continue
				parts = line.split(",")
				if len(parts) != 2 or not parts[0].strip():
					skipped.append((line_number, line))
					continue
				try:
					score = int(parts[1])
				except ValueError:
					skipped.append((line_number, line))
					continue
				if not 0 <= score <= 100:
					skipped.append((line_number, line))
					continue
				records.append((parts[0], score))
		return records, skipped


def test_process_score_file_skips_header_and_returns_valid_records(tmp_path):
	score_file = tmp_path / "scores.txt"
	score_file.write_text("name,score\nAlice,90\nBob,75\n", encoding="utf-8")

	records, skipped = process_score_file(score_file)

	assert records == [("Alice", 90), ("Bob", 75)]
	assert skipped == []


@pytest.mark.parametrize(
	("line", "line_number"),
	[
		("NoScore", 2),
		("Alice,abc", 3),
		("Bob,-1", 4),
		("Carol,101", 5),
		(",50", 6),
	],
)
def test_process_score_file_skips_invalid_lines_and_reports_line_numbers(
	tmp_path, line, line_number
):
	score_file = tmp_path / "scores.txt"
	lines = ["name,score", "Valid,0", "Valid2,100"]
	while len(lines) < line_number - 1:
		lines.append("Extra,50")
	lines.insert(line_number - 1, line)
	score_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

	records, skipped = process_score_file(score_file)

	assert ("Valid", 0) in records
	assert ("Valid2", 100) in records
	assert (line_number, line) in skipped


def test_process_score_file_reports_missing_file(tmp_path):
	with pytest.raises(FileNotFoundError):
		process_score_file(tmp_path / "missing.txt")


def test_process_score_file_reports_unreadable_file(tmp_path, monkeypatch):
	score_file = tmp_path / "scores.txt"
	score_file.write_text("name,score\nAlice,90\n", encoding="utf-8")

	def deny_read(*args, **kwargs):
		raise PermissionError("permission denied")

	monkeypatch.setattr("builtins.open", deny_read)
	with pytest.raises(PermissionError):
		process_score_file(score_file)


def test_process_score_file_with_header_only_returns_empty_results(tmp_path):
	score_file = tmp_path / "scores.txt"
	score_file.write_text("name,score\n", encoding="utf-8")

	assert process_score_file(score_file) == ([], [])
