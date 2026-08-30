import json

with open(r"c:\Users\ayush\OneDrive\Documents\GitHub\autonomous_document_intelligence_agent\evaluation\results\phase4_baseline_failure_analysis.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print("="*60)
print("PHASE 4 BASELINE FAILURE ANALYSIS BREAKDOWN")
print("="*60)

cat_counts = {}
field_counts = {}

for item in data:
    c = item["failure_category"]
    fn = item["field_name"]
    cat_counts[c] = cat_counts.get(c, 0) + 1
    field_counts[fn] = field_counts.get(fn, 0) + 1

print("\n--- 1. Failure Categories (Across Runs 1-3) ---")
for cat, cnt in sorted(cat_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"   - {cat:<55}: {cnt} mismatches ({cnt/3:.1f}/run, {cnt/len(data)*100:.1f}%)")

print("\n--- 2. Top Failure-Prone Fields ---")
for fn, cnt in sorted(field_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"   - {fn:<25}: {cnt} mismatches ({cnt/3:.1f}/run)")
