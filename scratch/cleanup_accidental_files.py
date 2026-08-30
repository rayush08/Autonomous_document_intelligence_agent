import os

root_dir = r"c:\Users\ayush\OneDrive\Documents\GitHub\autonomous_document_intelligence_agent"

for fname in os.listdir(root_dir):
    fpath = os.path.join(root_dir, fname)
    if fname == "tatus" or "e 7" in fname or fname.startswith("e 7"):
        try:
            os.remove(fpath)
            print(f"Removed accidental file successfully.")
        except Exception as e:
            print(f"Failed to remove accidental file: {e}")
