import os
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GOLD_DIR = os.path.join(BASE_DIR, "evaluation", "gold")


def run_medium_integrity_check():
    """Verify Medium-difficulty structural integrity against docs/dataset_strategy.md."""
    results = {}
    
    # ----------------------------------------------------
    # GOV-M-01 AUDIT
    # ----------------------------------------------------
    gov_m01_path = os.path.join(GOLD_DIR, "GOV-M-01.json")
    with open(gov_m01_path, 'r', encoding='utf-8') as f:
        m01 = json.load(f)
        
    m01_benefits = m01['benefit_amount']['value']
    m01_null_fields = [k for k, v in m01.items() if isinstance(v, dict) and v.get('verification_status') == 'not_found']
    
    results['GOV-M-01'] = {
        "multi_component_benefits": isinstance(m01_benefits, list) and len(m01_benefits) >= 3,
        "multi_condition_eligibility": bool(m01['target_beneficiaries']['value'] and m01['academic_criteria']['value']),
        "genuinely_missing_fields": m01_null_fields,
        "integrity_passed": isinstance(m01_benefits, list) and 'income_criteria' in m01_null_fields and 'age_criteria' in m01_null_fields
    }

    # ----------------------------------------------------
    # GOV-M-02 AUDIT
    # ----------------------------------------------------
    gov_m02_path = os.path.join(GOLD_DIR, "GOV-M-02.json")
    with open(gov_m02_path, 'r', encoding='utf-8') as f:
        m02 = json.load(f)
        
    m02_benefits = m02['benefit_amount']['value']
    m02_null_fields = [k for k, v in m02.items() if isinstance(v, dict) and v.get('verification_status') == 'not_found']
    m02_category = m02['category_criteria']['value']
    
    has_4_components = isinstance(m02_benefits, list) and len(m02_benefits) == 4
    has_female_quota = any('female' in str(c).lower() or 'girl' in str(c).lower() for c in (m02_category if isinstance(m02_category, list) else [m02_category]))
    
    results['GOV-M-02'] = {
        "four_component_financial_package": has_4_components,
        "category_income_institution_conditions": bool(m02['income_criteria']['value'] and m02['education_level']['value']),
        "female_quota_verified": has_female_quota,
        "genuinely_missing_fields": m02_null_fields,
        "integrity_passed": has_4_components and has_female_quota and 'age_criteria' in m02_null_fields and 'domicile_criteria' in m02_null_fields
    }

    # ----------------------------------------------------
    # GOV-M-03 AUDIT
    # ----------------------------------------------------
    gov_m03_path = os.path.join(GOLD_DIR, "GOV-M-03.json")
    with open(gov_m03_path, 'r', encoding='utf-8') as f:
        m03 = json.load(f)
        
    m03_benefits = m03['benefit_amount']['value']
    m03_null_fields = [k for k, v in m03.items() if isinstance(v, dict) and v.get('verification_status') == 'not_found']
    m03_docs = m03['required_documents']['value']
    
    # Check page numbers in evidence
    page_locators = []
    for k, v in m03.items():
        if isinstance(v, dict) and 'evidence' in v:
            for ev in v['evidence']:
                loc = ev.get('locator', {})
                if loc and loc.get('page') is not None:
                    page_locators.append(loc['page'])
                    
    has_page_locators = len(page_locators) > 0
    has_phased_docs = isinstance(m03_docs, list) and len(m03_docs) >= 5
    
    results['GOV-M-03'] = {
        "multi_tier_capacity_cfa_table": isinstance(m03_benefits, list) and len(m03_benefits) >= 3,
        "phased_document_requirements": has_phased_docs,
        "pdf_page_level_extraction": has_page_locators,
        "distinct_page_numbers_referenced": list(set(page_locators)),
        "genuinely_missing_fields": m03_null_fields,
        "integrity_passed": has_page_locators and 'education_level' in m03_null_fields and 'income_criteria' in m03_null_fields
    }

    print("==========================================")
    print("MEDIUM DIFFICULTY INTEGRITY VERIFICATION")
    print("==========================================")
    for doc_id, res in results.items():
        status_str = "✅ PASSED INTEGRITY" if res['integrity_passed'] else "❌ FAILED INTEGRITY"
        print(f"[{doc_id}] {status_str}")
        for k, v in res.items():
            if k != 'integrity_passed':
                print(f"   -> {k}: {v}")

    return results


if __name__ == "__main__":
    run_medium_integrity_check()

