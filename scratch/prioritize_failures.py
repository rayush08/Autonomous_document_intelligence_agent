import json

with open(r"c:\Users\ayush\OneDrive\Documents\GitHub\autonomous_document_intelligence_agent\evaluation\results\field_failure_matrix.json", "r", encoding="utf-8") as f:
    matrix = json.load(f)

field_counts = {}
domain_counts = {}
cat_counts = {}
doc_counts = {}

for item in matrix:
    fname = item["field_name"]
    dom = item["domain"]
    cat = item["primary_category"]
    doc = item["document_id"]
    
    field_counts[fname] = field_counts.get(fname, 0) + 1
    domain_counts[dom] = domain_counts.get(dom, 0) + 1
    cat_counts[cat] = cat_counts.get(cat, 0) + 1
    doc_counts[doc] = doc_counts.get(doc, 0) + 1

print("="*60)
print("TOP FAILURE SOURCES BY IMPACT")
print("="*60)

print("\n--- 1. Failure Count by Field Name (Top 8) ---")
for fn, c in sorted(field_counts.items(), key=lambda x: x[1], reverse=True)[:8]:
    print(f"   - {fn:<24}: {c} mismatches")

print("\n--- 2. Failure Count by Domain ---")
for dom, c in domain_counts.items():
    print(f"   - {dom:<24}: {c} mismatches")

print("\n--- 3. Failure Count by Category ---")
for cat, c in sorted(cat_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"   - {cat:<45}: {c} mismatches")

print("\n--- 4. Failure Count by Document ---")
for doc, c in sorted(doc_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"   - {doc:<12}: {c} mismatches")
