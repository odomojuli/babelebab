import pandas as pd

# Replace 'your_file.txt' with the path to your .txt file
file_path = 'clean_lemmas_60k.txt'

# Load the .txt file into a pandas DataFrame
df = pd.read_csv(file_path, sep='\t', header=0)

# Specify the output file path for CSV
output_csv_path = 'clean_lemmas_60k.csv'

# Write the entire DataFrame to a CSV file
df.to_csv(output_csv_path, index=False, sep=',')

print(f"Entire DataFrame has been written to {output_csv_path}")