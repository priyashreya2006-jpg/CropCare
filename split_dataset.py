import pandas as pd
from sklearn.model_selection import train_test_split
from pathlib import Path

# Load dataset labels
df = pd.read_csv("dataset/labels.csv")

# First split: 70% training, 30% temporary
train_df, temp_df = train_test_split(
    df,
    test_size=0.30,
    random_state=42,
    stratify=df["label"]
)

# Second split: 15% validation, 15% testing
val_df, test_df = train_test_split(
    temp_df,
    test_size=0.50,
    random_state=42,
    stratify=temp_df["label"]
)

# Create output folder
output_dir = Path("dataset/splits")
output_dir.mkdir(parents=True, exist_ok=True)

# Save CSV files
train_df.to_csv(output_dir / "train.csv", index=False)
val_df.to_csv(output_dir / "validation.csv", index=False)
test_df.to_csv(output_dir / "test.csv", index=False)

print("Dataset splitting completed!")
print("Training images:", len(train_df))
print("Validation images:", len(val_df))
print("Testing images:", len(test_df))

print("\nCategories in each dataset:")
print("Training:", train_df["label"].nunique())
print("Validation:", val_df["label"].nunique())
print("Testing:", test_df["label"].nunique())