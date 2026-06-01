import argparse
import os


def split_file_into_char_chunks(input_file, chars_per_chunk=280):
    """
    Splits a file into smaller files with a specified number of characters each.

    Parameters:
        input_file (str): The path to the input file.
        chars_per_chunk (int): The number of characters per chunk. Default is 280.

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
        content = file.read()

    # Calculate the total number of chunks
    total_chunks = len(content) // chars_per_chunk + (1 if len(content) % chars_per_chunk != 0 else 0)

    # Write each chunk to a separate file in the created directory
    for i in range(total_chunks):
        start_char = i * chars_per_chunk
        end_char = min((i + 1) * chars_per_chunk, len(content))
        chunk_content = content[start_char: end_char]
        chunk_file_path = os.path.join(output_dir, f"{base_name}_{start_char}-{end_char - 1}.txt")
        
        with open(chunk_file_path, 'w') as chunk_file:
            chunk_file.write(chunk_content)
        
        print(f"Created {chunk_file_path} with {len(chunk_content)} characters")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Split a text file into smaller chunks based on character limits.")
    parser.add_argument("input_file", help="Path to the input text file.")
    parser.add_argument("--chars", type=int, default=280, help="Number of characters per chunk (default: 280).")

    args = parser.parse_args()
    
    split_file_into_char_chunks(args.input_file, args.chars)