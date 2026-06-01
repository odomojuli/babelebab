import argparse
import os


def split_file_into_chunks(input_file, lines_per_chunk=1000):
    """
    Splits a file into smaller files with a specified number of lines each.

    Parameters:
        input_file (str): The path to the input file.
        lines_per_chunk (int): The number of lines per chunk. Default is 1000.

    Returns:
        None
    """
    # Extract the base name of the input file
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    
    # Create a directory named after the input file
    output_dir = os.path.join(os.path.dirname(input_file), base_name)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")

    # Open the input file
    with open(input_file, 'r') as file:
        lines = file.readlines()

    # Calculate the total number of chunks
    total_chunks = len(lines) // lines_per_chunk + (1 if len(lines) % lines_per_chunk != 0 else 0)

    # Write each chunk to a separate file in the created directory
    for i in range(total_chunks):
        start_line = i * lines_per_chunk
        end_line = min((i + 1) * lines_per_chunk - 1, len(lines) - 1)
        chunk_lines = lines[start_line: end_line + 1]
        chunk_file_path = os.path.join(output_dir, f"{base_name}_{start_line}-{end_line}.txt")
        
        with open(chunk_file_path, 'w') as chunk_file:
            chunk_file.writelines(chunk_lines)
        
        print(f"Created {chunk_file_path} with {len(chunk_lines)} lines")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Split a text file into smaller chunks.")
    parser.add_argument("input_file", help="Path to the input text file.")
    parser.add_argument("--lines", type=int, default=1000, help="Number of lines per chunk (default: 1000).")

    args = parser.parse_args()
    
    split_file_into_chunks(args.input_file, args.lines)