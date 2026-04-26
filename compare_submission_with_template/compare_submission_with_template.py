import pandas as pd
import os

REQUIRED_COLUMNS = ["row_id", "label", "score"]


def compare_submission_with_template(submission_path, template_path):
    submission = pd.read_csv(submission_path)
    template = pd.read_csv(template_path)
    try:
        is_int_csv_check = os.path.basename(submission_path).replace('.csv','')
    except:
        print('ERROR: Your file name is: ', os.path.basename(submission_path))
        print('NAME YOUR SUBMISSIONS BASED ON ORDER OF SUBMISSION: 1.CSV, 2.CSV, ..., 10.CSV')

    print("Checking columns...")

    # Check columns exist
    for col in REQUIRED_COLUMNS:
        assert col in submission.columns, f"ERROR: Missing required column: {col}, ADD THAT COLUMN!"

    # Warn if extra columns
    extra_cols = set(submission.columns) - set(REQUIRED_COLUMNS)
    if extra_cols:
        print(f"WARNING: Extra columns found: {extra_cols}, but this is ok.")

    print("Checking row_id consistency...")

    # Check same length
    assert len(submission) == len(template), \
        f"Length mismatch: submission={len(submission)}, template={len(template)}"
    submission = submission.sort_values(['row_id'], ascending=True).reset_index(drop=True)
    template = template.sort_values(['row_id'], ascending=True).reset_index(drop=True)

    # Check exact match
    if not submission["row_id"].equals(template["row_id"]):
        mismatch_idx = submission["row_id"] != template["row_id"]
        print("ERROR: row_id mismatch detected! THIS WILL NOT WORK FOR SCORING YOUR SOLUTION!")
        print("First mismatches:")
        print(pd.DataFrame({
            "submission": submission["row_id"][mismatch_idx],
            "template": template["row_id"][mismatch_idx]
        }).head())

        assert False, "row_id values do not match template"

    print("Checking value ranges...")

    # Label check
    # Identify the values that are NOT in the set [0, 1]
    invalid_label = submission.loc[~submission["label"].isin([0, 1]), "label"]

    if not invalid_label.empty:
        print("WARNING: label column contains values other than 0/1")
        print("Labels outside 0,1 range:")
        print(invalid_label.unique().tolist())


    # Score check
    invalid_scores = submission.loc[~(submission["score"] >= 0) & (submission["score"] <= 1), "score"]

    if not invalid_scores.empty:
        print("WARNING: score values out of [0,1] range")
        print("Scores outside 0,1 range:")
        print(invalid_scores.tolist())

    print("All checks passed ✅")


import argparse


def main():
    parser = argparse.ArgumentParser(
        description="Compare a submission CSV with a template CSV."
    )
    
    parser.add_argument(
        "--submission_path",
        type=str,
        required=True,
        help="Path to the submission CSV file"
    )
    
    parser.add_argument(
        "--template_path",
        type=str,
        required=True,
        help="Path to the template CSV file"
    )

    args = parser.parse_args()

    compare_submission_with_template(
        submission_path=args.submission_path,
        template_path=args.template_path
    )

"""
python compare_submission_with_template.py \
    --submission_path submissions/raw/25/baseline_model_results.csv \
        --template_path submissions/raw/26/nasumicni_1.csv
"""
if __name__ == "__main__":
    main()