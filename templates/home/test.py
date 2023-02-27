from transformers import KeyBERTTokenizer

# Load the tokenizer
tokenizer = KeyBERTTokenizer.from_pretrained("all-mpnet/base-v2")

# Add the word "About" to the tokenizer
tokenizer.add_tokens(["About"])

# Add the word "University" to the tokenizer
tokenizer.add_tokens(["University"])

# Save the updated tokenizer to disk
# tokenizer.save_pretrained("/path/to/updated_tokenizer")

tokenizer.save_pretrained("updated_tokenizer.json", format='json')