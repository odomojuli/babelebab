import pandas as pd

# Replace 'your_file.txt' with the path to your .txt file
file_path = 'clean_lemmas_60k.txt'

# Load the .txt file into a pandas DataFrame
df = pd.read_csv(file_path, sep='\t', header=0)

# Display the DataFrame
print(df)

# Print unique column names
print(df.columns.unique())

# Extract the first 1000 values of the 'lemma' column
lemma_values = df['lemma'].head(1000)

# Write these values to a new .txt file
output_file_path = 'lemma_values.txt'
lemma_values.to_csv(output_file_path, index=False, header=False, sep='\t')

print(f"First 1000 values of 'lemma' column have been written to {output_file_path}")