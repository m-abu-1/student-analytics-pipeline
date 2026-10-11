"""
BIT B.Tech Cohort 2026 Synthetic Dataset Generator
Modeled for Bannari Amman Institute of Technology (Autonomous / Anna University / NAAC & NBA Accredited)

Generates realistic academic records for 200 students across 5 core engineering subjects (1000 total records)
with embedded statistical correlations, subject difficulty biases, and intentional data anomalies for testing
the Stage 1-3 Sanitation and Audit Pipeline.
"""

import numpy as np
import pandas as pd


def generate_bit_cohort_data(
    num_students: int = 200, seed: int = 42
) -> pd.DataFrame:
    np.random.seed(seed)

    student_ids = [f"2026BIT{1000 + i}" for i in range(num_students)]

    first_names = [
        "Aravind",
        "Ananya",
        "Balaji",
        "Deepak",
        "Divya",
        "Gokul",
        "Hari",
        "Harini",
        "Karthik",
        "Kavya",
        "Manoj",
        "Meena",
        "Naveen",
        "Nithya",
        "Pranav",
        "Priya",
        "Rahul",
        "Rithika",
        "Sanjay",
        "Sneha",
        "Surya",
        "Swetha",
        "Varun",
        "Vidyut",
        "Yashwanth",
    ]
    last_names = [
        "Subramanian",
        "Ramanathan",
        "Krishnan",
        "Murugan",
        "Srinivasan",
        "Natarajan",
        "Sundaram",
        "Chandrasekar",
        "Venkatesh",
        "Balasubramanian",
        "Vijayraghavan",
        "Rajagopal",
        "Ganesan",
        "Senthil",
        "Kannan",
    ]

    names = [
        f"{np.random.choice(first_names)} {np.random.choice(last_names)}"
        for _ in range(num_students)
    ]

    subjects = [
        ("CS301", "Data Structures and Algorithms"),
        ("CS302", "Operating Systems Architecture"),
        ("EC301", "Digital Signal Processing"),
        ("MA301", "Linear Algebra and Probability Theory"),
        ("CS303", "Database Management Systems"),
    ]

    difficulty_offsets = {
        "CS301": 6.5,
        "CS302": 1.5,
        "EC301": 12.0,
        "MA301": 14.5,
        "CS303": -3.0,
    }

    records = []

    for sid, name in zip(student_ids, names):
        base_academic_ability = np.random.normal(68.0, 11.5)
        base_attendance_discipline = np.random.normal(81.0, 9.5)

        for sub_code, sub_title in subjects:
            att_val = float(
                np.clip(
                    base_attendance_discipline + np.random.normal(0, 4.5),
                    40.0,
                    100.0,
                )
            )

            diff = difficulty_offsets[sub_code]
            score_val = base_academic_ability - diff + (att_val - 75.0) * 0.38
            score_val += np.random.normal(0, 7.5)
            score_val = float(np.clip(score_val, 12.0, 100.0))

            records.append({
                "Register_No": sid,
                "Full_Name": name,
                "Subject_Code": sub_code,
                "Subject_Title": sub_title,
                "Attendance_%": round(att_val, 1),
                "Score": round(score_val, 1),
                "Max_Marks": 100,
                "Academic_Semester": 4,
            })

    df = pd.DataFrame(records)

    # Inject intentional dataset anomalies for pipeline audit testing

    # Anomaly 1: Attendance out of bounds (> 100%)
    df.loc[12, "Attendance_%"] = 118.5

    # Anomaly 2: Marks obtained exceeding maximum marks
    df.loc[45, "Score"] = 122.0

    # Anomaly 3: Negative marks obtained
    df.loc[88, "Score"] = -15.0

    # Anomaly 4: Non-numeric / String entry in numeric score field
    df.loc[120, "Score"] = "ABSENT_EXP"

    # Anomaly 5: Missing Critical Identifier (Register No)
    df.loc[210, "Register_No"] = np.nan

    # Anomaly 6: Duplicate (student_id, subject_id, semester) entry
    dup_row = df.iloc[300].copy()
    df = pd.concat([df, pd.DataFrame([dup_row])], ignore_index=True)

    return df


if __name__ == "__main__":
    output_filename = "BIT_BTech_Cohort_2026.csv"
    dataset = generate_bit_cohort_data(num_students=200)
    dataset.to_csv(output_filename, index=False)
    print(f"[SUCCESS] Synthetic dataset generated: {output_filename}")
    print(
        f"[INFO] Total Records: {len(dataset)} | Unique Students: 200 |"
        " Core Subjects: 5"
    )
