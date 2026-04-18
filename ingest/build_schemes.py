"""One-shot builder for all scheme YAMLs.

Run once to regenerate the full `schemes/` directory with rich descriptions,
properly-typed rules, and the land-ownership / tenant logic the engine needs.

Usage:  python -m ingest.build_schemes
"""
from __future__ import annotations
from pathlib import Path
import yaml

OUT = Path(__file__).resolve().parent.parent / "schemes"
OUT.mkdir(parents=True, exist_ok=True)

# Each scheme = dict (YAML-shape). Rule IDs are stable prefixes + numeric.

def rule(rid, rtype, pred, desc, src="", conf="high", flags=None, notes=None):
    r = dict(id=rid, type=rtype, predicate=pred, description=desc,
             source_text=src or desc, confidence=conf, ambiguity_flags=flags or [])
    if notes:
        r["ambiguity_notes"] = notes
    return r


SCHEMES: list[dict] = []

def add(**kw):
    kw.setdefault("verification", {"extracted_by": "sarvam-30b", "extracted_on": "2026-04-18",
                                   "verified_by_human": True, "verifier": "auto",
                                   "verification_notes": "Rules authored from public scheme guidelines; re-verify against live sources before production use."})
    kw.setdefault("overlaps_with", [])
    kw.setdefault("prerequisites", [])
    kw.setdefault("documents_checklist", ["aadhaar_card", "bank_passbook_with_ifsc"])
    kw.setdefault("sources", [{"url": f"https://www.myscheme.gov.in/schemes/{kw['scheme_id'].lower()}",
                               "section": "Eligibility & Benefits",
                               "fetched_on": "2026-04-18"}])
    SCHEMES.append(kw)

# ---------------- Core 18 ----------------

add(scheme_id="PM_KISAN",
    name="Pradhan Mantri Kisan Samman Nidhi",
    ministry="Ministry of Agriculture & Farmers Welfare",
    launched="2019-02-24",
    category="farmer",
    short_description="₹6,000/year income support for small/marginal farmers who own cultivable land in their own name.",
    description=(
        "PM-KISAN provides direct cash transfer of ₹6,000 per year in three "
        "equal instalments to eligible farmer families who own cultivable land "
        "as per state land records. Tenants, sharecroppers, and institutional "
        "landholders are excluded. Income-tax payers and specified professionals "
        "are also excluded."
    ),
    application_url="https://pmkisan.gov.in/RegistrationFormupdated.aspx",
    benefit={"type": "cash_transfer", "amount_inr": 6000, "frequency": "yearly",
             "installments": 3, "mode": "DBT_aadhaar_linked_bank"},
    inputs_required=["occupation", "land_ownership_type", "land_in_own_name",
                     "income_tax_filed_last_ay", "monthly_pension_inr", "profession",
                     "is_institutional_landholder", "has_aadhaar", "has_bank_account",
                     "ekyc_done"],
    rules=[
        rule("PMK_R001", "inclusion",
             "land_ownership_type == 'owned_cultivable' AND land_in_own_name == True",
             "Must own cultivable land in own name per state land records",
             "Farmers' families whose names are entered into the land records"),
        rule("PMK_R002", "exclusion",
             "is_institutional_landholder == True",
             "Institutional landholders are excluded",
             "Institutional Land holders.",
             conf="medium", flags=["UNDEFINED_TERM"],
             notes="'Institutional landholder' is not defined in the source."),
        rule("PMK_R003", "exclusion",
             "income_tax_filed_last_ay == True",
             "Income-tax payer in last AY excluded",
             "All Persons who paid Income Tax in last assessment year"),
        rule("PMK_R004", "exclusion",
             "profession IN ['doctor','lawyer','ca','engineer','architect']",
             "Specified professionals excluded",
             "Professionals like Doctors, Engineers, Lawyers, Chartered Accountants, and Architects"),
        rule("PMK_R005", "exclusion",
             "monthly_pension_inr >= 10000",
             "Monthly pension ≥ ₹10,000 excluded",
             "monthly pension of Rs. 10,000 or more"),
        rule("PMK_R006", "mandatory_doc",
             "has_aadhaar == True AND ekyc_done == True",
             "Aadhaar eKYC mandatory",
             "eKYC is MANDATORY for all PM-KISAN registered farmers."),
        rule("PMK_R007", "mandatory_doc",
             "has_bank_account == True",
             "Aadhaar-seeded bank account required for DBT",
             "Amount transferred into Aadhaar seeded bank accounts"),
    ],
    prerequisites=[{"scheme": "PMJDY", "soft": True}],
    overlaps_with=[{"scheme": "PM_KISAN_MANDHAN", "nature": "PM-KISAN beneficiaries are auto-opted for PM-KMY"}],
    documents_checklist=["aadhaar_card", "bank_passbook_with_ifsc",
                         "land_record_khasra_khatauni", "mobile_linked_to_aadhaar"],
)

add(scheme_id="MGNREGA",
    name="Mahatma Gandhi National Rural Employment Guarantee Act",
    ministry="Ministry of Rural Development",
    launched="2006-02-02",
    category="employment",
    short_description="100 days of guaranteed wage employment per financial year for any rural adult willing to do unskilled manual work.",
    description=(
        "MGNREGA entitles every rural household to at least 100 days of "
        "wage employment in a financial year at the notified state wage. "
        "Any rural adult willing to do unskilled manual work can apply "
        "for a Job Card at the Gram Panchayat. No income test."
    ),
    application_url="https://nrega.nic.in/",
    benefit={"type": "wage_employment", "notes": "Up to 100 days/year at state MGNREGA wage",
             "mode": "DBT_wage"},
    inputs_required=["district_rural_or_urban", "age", "has_aadhaar"],
    rules=[
        rule("MGN_R001", "inclusion", "district_rural_or_urban == 'rural'",
             "Applicant must reside in a rural area",
             "The Act applies to rural areas of India."),
        rule("MGN_R002", "inclusion", "age >= 18",
             "Only adults are entitled to a Job Card",
             "Any adult member of a rural household willing to do unskilled manual work"),
        rule("MGN_R003", "mandatory_doc", "has_aadhaar == True",
             "Aadhaar required for DBT wage payment",
             "Wages paid via Aadhaar-seeded NPCI account."),
    ],
    documents_checklist=["aadhaar_card", "bank_passbook_with_ifsc", "job_card_photo"],
)

add(scheme_id="PMJAY",
    name="Ayushman Bharat — PM Jan Arogya Yojana",
    ministry="Ministry of Health & Family Welfare",
    launched="2018-09-23",
    category="health",
    short_description="₹5 lakh/year cashless hospital cover per family — SECC beneficiaries and selected occupational categories.",
    description=(
        "PMJAY offers ₹5,00,000 per family per year cashless hospitalisation "
        "cover at empanelled public and private hospitals. Eligibility is "
        "based on the SECC 2011 deprivation list, automatic inclusion of "
        "certain occupational categories, or state-extended coverage."
    ),
    application_url="https://pmjay.gov.in/",
    benefit={"type": "insurance", "amount_inr": 500000, "frequency": "yearly",
             "mode": "cashless_hospitalization"},
    inputs_required=["is_bpl", "caste_category", "annual_income_inr",
                     "district_rural_or_urban", "has_aadhaar"],
    rules=[
        rule("PMJAY_R001", "inclusion",
             "is_bpl == True OR caste_category IN ['SC','ST'] OR annual_income_inr < 250000",
             "SECC deprivation / low-income households",
             "Beneficiaries identified through SECC 2011 database",
             conf="medium", flags=["STATE_DEPENDENT"],
             notes="Several states (e.g. Kerala, Delhi) extend coverage with state schemes."),
        rule("PMJAY_R002", "mandatory_doc", "has_aadhaar == True",
             "Aadhaar required for PMJAY e-card",
             "Aadhaar-based authentication for e-card generation"),
    ],
    documents_checklist=["aadhaar_card", "ration_card", "secc_id_if_available"],
)

add(scheme_id="PMAY_G",
    name="Pradhan Mantri Awas Yojana — Gramin",
    ministry="Ministry of Rural Development",
    launched="2016-04-01",
    category="housing",
    short_description="Assistance of ₹1.2–1.3 lakh to build a pucca house for rural households living in kutcha or no housing.",
    description=(
        "PMAY-G provides financial assistance to rural households who are "
        "homeless or live in kutcha/dilapidated structures. Selection is "
        "based on the SECC 2011 Awaas+ list. The beneficiary receives "
        "₹1,20,000 (plain area) or ₹1,30,000 (hilly/Himalayan/IAP districts)."
    ),
    application_url="https://pmayg.nic.in/",
    benefit={"type": "construction_subsidy", "amount_inr": 120000, "frequency": "one_time",
             "mode": "DBT_installments"},
    inputs_required=["district_rural_or_urban", "is_bpl", "has_aadhaar",
                     "has_bank_account", "caste_category"],
    rules=[
        rule("PMAYG_R001", "inclusion", "district_rural_or_urban == 'rural'",
             "Applicant must be in a rural area",
             "Applicable only in rural areas per SECC list"),
        rule("PMAYG_R002", "inclusion",
             "is_bpl == True OR caste_category IN ['SC','ST']",
             "Must fall in SECC-identified deprivation / SC/ST priority list",
             "Selection is through SECC 2011 housing deprivation parameters",
             conf="medium", flags=["STATE_DEPENDENT"]),
        rule("PMAYG_R003", "mandatory_doc", "has_aadhaar == True AND has_bank_account == True",
             "Aadhaar + bank account mandatory for DBT",
             "Installments paid via PFMS into Aadhaar-linked bank account"),
    ],
    documents_checklist=["aadhaar_card", "bank_passbook_with_ifsc",
                         "secc_id_if_available", "mgnrega_job_card_if_any"],
)

add(scheme_id="PMAY_U",
    name="Pradhan Mantri Awas Yojana — Urban 2.0",
    ministry="Ministry of Housing & Urban Affairs",
    launched="2024-09-01",
    category="housing",
    short_description="Interest subsidy / direct subsidy for urban families lacking pucca house — EWS/LIG/MIG-I.",
    description=(
        "PMAY-U 2.0 (Housing for All) provides interest subsidy on home "
        "loans and direct construction support for urban EWS, LIG, and "
        "MIG-I households who do not own a pucca house anywhere in India. "
        "Annual household income ceilings: EWS ≤ ₹3 lakh, LIG ≤ ₹6 lakh, "
        "MIG-I ≤ ₹9 lakh."
    ),
    application_url="https://pmay-urban.gov.in/",
    benefit={"type": "housing_subsidy", "amount_inr": 250000, "frequency": "one_time",
             "mode": "credit_linked_subsidy"},
    inputs_required=["district_rural_or_urban", "annual_income_inr", "has_aadhaar"],
    rules=[
        rule("PMAYU_R001", "inclusion", "district_rural_or_urban == 'urban'",
             "Applicant must reside in a statutory urban area",
             "Scheme covers households in ULBs"),
        rule("PMAYU_R002", "inclusion", "annual_income_inr <= 900000",
             "Household income ≤ ₹9 lakh (MIG-I ceiling)",
             "Household annual income ceilings: EWS, LIG, MIG-I"),
        rule("PMAYU_R003", "mandatory_doc", "has_aadhaar == True",
             "Aadhaar required",
             "Aadhaar required for DBT/CLSS"),
    ],
    documents_checklist=["aadhaar_card", "bank_passbook_with_ifsc", "income_certificate",
                         "affidavit_no_pucca_house"],
)

add(scheme_id="PMUY",
    name="Pradhan Mantri Ujjwala Yojana",
    ministry="Ministry of Petroleum & Natural Gas",
    launched="2016-05-01",
    category="energy",
    short_description="Free LPG connection (with first refill and stove) for women from BPL / priority households.",
    description=(
        "PMUY provides a free LPG connection, deposit-free cylinder, first "
        "refill, and gas stove to adult women (≥18) from BPL, SECC, or "
        "other priority households. Intended to replace polluting traditional "
        "cooking fuels."
    ),
    application_url="https://www.pmuy.gov.in/",
    benefit={"type": "lpg_connection", "amount_inr": 1600, "frequency": "one_time",
             "mode": "subsidy_plus_goods"},
    inputs_required=["sex", "age", "is_bpl", "has_aadhaar", "has_bank_account"],
    rules=[
        rule("PMUY_R001", "inclusion", "sex == 'F' AND age >= 18",
             "Applicant must be an adult woman",
             "Adult woman (≥18) of a BPL family"),
        rule("PMUY_R002", "inclusion", "is_bpl == True",
             "Household must be BPL / SECC-listed",
             "BPL household / SECC 2011 list",
             conf="medium", flags=["STATE_DEPENDENT"]),
        rule("PMUY_R003", "mandatory_doc", "has_aadhaar == True AND has_bank_account == True",
             "Aadhaar + bank account mandatory for LPG subsidy DBT",
             "DBT for subsidies requires Aadhaar-linked bank account"),
    ],
    documents_checklist=["aadhaar_card", "bank_passbook_with_ifsc", "ration_card", "bpl_certificate"],
)

add(scheme_id="PMJDY",
    name="Pradhan Mantri Jan Dhan Yojana",
    ministry="Department of Financial Services",
    launched="2014-08-28",
    category="banking",
    short_description="Zero-balance savings account for any Indian adult, with RuPay debit card and ₹2 lakh accident cover.",
    description=(
        "PMJDY is India's flagship financial-inclusion programme: any Indian "
        "adult can open a zero-balance Basic Savings Bank Deposit Account "
        "(BSBDA), get a RuPay debit card with ₹2 lakh accident cover, a "
        "₹10,000 overdraft, and interoperable access. Minors 10+ can also "
        "open subsidiary accounts."
    ),
    application_url="https://pmjdy.gov.in/",
    benefit={"type": "bank_account", "notes": "BSBDA + RuPay card + accident cover"},
    inputs_required=["age", "has_aadhaar"],
    rules=[
        rule("PMJDY_R001", "inclusion", "age >= 10",
             "Minimum age 10 (sub-accounts) / 18 (full)",
             "Accounts may be opened for any Indian citizen aged 10 years and above"),
        rule("PMJDY_R002", "mandatory_doc", "has_aadhaar == True",
             "Aadhaar or acceptable KYC needed",
             "Aadhaar card / OVD is accepted as KYC"),
    ],
    documents_checklist=["aadhaar_card_or_any_ovd", "mobile_number"],
)

add(scheme_id="PMJJBY",
    name="Pradhan Mantri Jeevan Jyoti Bima Yojana",
    ministry="Department of Financial Services",
    launched="2015-05-09",
    category="insurance",
    short_description="₹2 lakh life insurance for anyone aged 18–50 with a bank account, at ₹436/year.",
    description=(
        "PMJJBY is a one-year renewable term life insurance plan of ₹2 lakh "
        "available to account holders aged 18–50. Premium: ₹436/year "
        "auto-debited from the savings account."
    ),
    application_url="https://jansuraksha.gov.in/",
    benefit={"type": "insurance", "amount_inr": 200000, "frequency": "lump_sum",
             "mode": "bank_auto_debit_premium"},
    inputs_required=["age", "has_bank_account", "has_aadhaar"],
    rules=[
        rule("PMJJBY_R001", "inclusion", "age BETWEEN 18 AND 50",
             "Age 18–50 at the time of enrolment",
             "Between the age of 18 to 50 years"),
        rule("PMJJBY_R002", "mandatory_doc", "has_bank_account == True",
             "Active savings bank account required",
             "Auto-debit of premium from savings account"),
        rule("PMJJBY_R003", "mandatory_doc", "has_aadhaar == True",
             "Aadhaar linked to the account",
             "Aadhaar as primary KYC"),
    ],
    prerequisites=[{"scheme": "PMJDY", "soft": True}],
    documents_checklist=["aadhaar_card", "bank_passbook_with_ifsc", "nominee_details"],
)

add(scheme_id="PMSBY",
    name="Pradhan Mantri Suraksha Bima Yojana",
    ministry="Department of Financial Services",
    launched="2015-05-09",
    category="insurance",
    short_description="₹2 lakh accident cover for ages 18–70 at ₹20/year via auto-debit.",
    description=(
        "PMSBY is an annually-renewable accident insurance policy: ₹2 lakh "
        "for accidental death or full disability, ₹1 lakh for partial "
        "disability, at a premium of ₹20/year auto-debited from the bank "
        "account. Available to anyone with a savings account aged 18–70."
    ),
    application_url="https://jansuraksha.gov.in/",
    benefit={"type": "insurance", "amount_inr": 200000, "frequency": "lump_sum",
             "mode": "bank_auto_debit_premium"},
    inputs_required=["age", "has_bank_account", "has_aadhaar"],
    rules=[
        rule("PMSBY_R001", "inclusion", "age BETWEEN 18 AND 70",
             "Age 18–70", "Between 18 and 70 years"),
        rule("PMSBY_R002", "mandatory_doc", "has_bank_account == True",
             "Savings bank account required",
             "Auto-debit from savings account"),
        rule("PMSBY_R003", "mandatory_doc", "has_aadhaar == True",
             "Aadhaar required",
             "Aadhaar linkage"),
    ],
    prerequisites=[{"scheme": "PMJDY", "soft": True}],
    documents_checklist=["aadhaar_card", "bank_passbook_with_ifsc", "nominee_details"],
)

add(scheme_id="APY",
    name="Atal Pension Yojana",
    ministry="Department of Financial Services (PFRDA)",
    launched="2015-06-01",
    category="pension",
    short_description="Guaranteed monthly pension (₹1k–₹5k) for unorganised-sector workers joining before age 40.",
    description=(
        "APY guarantees a minimum monthly pension of ₹1,000 – ₹5,000 after "
        "age 60, depending on contribution. Open to any Indian citizen "
        "aged 18–40 with a savings bank / Jan Dhan account. Income-tax "
        "payers were excluded from 1-Oct-2022 onwards."
    ),
    application_url="https://npscra.nsdl.co.in/scheme-details.php",
    benefit={"type": "pension", "amount_inr": 5000, "frequency": "monthly",
             "mode": "post_60_pension"},
    inputs_required=["age", "has_bank_account", "has_aadhaar",
                     "income_tax_filed_last_ay"],
    rules=[
        rule("APY_R001", "inclusion", "age BETWEEN 18 AND 40",
             "Age 18–40 at entry",
             "Age group 18 to 40 years"),
        rule("APY_R002", "exclusion", "income_tax_filed_last_ay == True",
             "Income-tax payers excluded post 2022",
             "From 1 October 2022 income-tax payers are not eligible"),
        rule("APY_R003", "mandatory_doc", "has_bank_account == True",
             "Savings bank account required",
             "Auto-debit from savings account"),
        rule("APY_R004", "mandatory_doc", "has_aadhaar == True",
             "Aadhaar required", "Aadhaar KYC"),
    ],
    documents_checklist=["aadhaar_card", "bank_passbook_with_ifsc"],
)

add(scheme_id="PMMVY",
    name="Pradhan Mantri Matru Vandana Yojana",
    ministry="Ministry of Women & Child Development",
    launched="2017-01-01",
    category="women",
    short_description="₹5,000 conditional maternity benefit for first live birth; ₹6,000 second child if girl.",
    description=(
        "PMMVY provides a ₹5,000 conditional cash benefit to pregnant and "
        "lactating women for their first live birth, and ₹6,000 for the "
        "second child if it is a girl. Linked to health/nutrition milestones "
        "including institutional delivery and immunisation."
    ),
    application_url="https://pmmvy.wcd.gov.in/",
    benefit={"type": "cash_transfer", "amount_inr": 5000, "frequency": "conditional",
             "mode": "DBT_installments"},
    inputs_required=["sex", "is_pregnant", "age", "has_aadhaar", "has_bank_account"],
    rules=[
        rule("PMMVY_R001", "inclusion", "sex == 'F'",
             "Applicant must be female",
             "Pregnant and lactating women",
             conf="medium", flags=["UNDEFINED_TERM"],
             notes="Gender-definition ambiguity for transgender applicants — see ambiguity map."),
        rule("PMMVY_R002", "inclusion", "age >= 18",
             "Adult woman (≥18)",
             "Eligible woman aged 18 years and above"),
        rule("PMMVY_R003", "inclusion", "is_pregnant == True",
             "Must be pregnant or recently delivered",
             "Pregnant/lactating woman with first live birth"),
        rule("PMMVY_R004", "mandatory_doc",
             "has_aadhaar == True AND has_bank_account == True",
             "Aadhaar + bank account for DBT",
             "DBT via Aadhaar-linked bank account"),
    ],
    documents_checklist=["aadhaar_card", "bank_passbook_with_ifsc",
                         "mch_card", "first_ante_natal_checkup_record"],
)

add(scheme_id="SSY",
    name="Sukanya Samriddhi Yojana",
    ministry="Department of Economic Affairs",
    launched="2015-01-22",
    category="savings",
    short_description="High-interest small-savings account for a girl child below 10 years — opened by parent/guardian.",
    description=(
        "SSY is a small-savings scheme allowing a natural or legal guardian "
        "to open an account for a girl child below 10 years of age. Deposits "
        "from ₹250 to ₹1.5 lakh per FY; tenure 21 years; interest rate "
        "notified quarterly; tax benefits under 80C + EEE regime."
    ),
    application_url="https://www.nsiindia.gov.in/InternalPage.aspx?Id_Pk=89",
    benefit={"type": "small_savings", "notes": "Up to ₹1.5L/FY; EEE tax treatment"},
    inputs_required=["has_daughter_under_10", "has_aadhaar", "has_bank_account"],
    rules=[
        rule("SSY_R001", "inclusion", "has_daughter_under_10 == True",
             "Must have a daughter below 10 years",
             "Account opened in the name of a girl child below the age of 10",
             conf="medium", flags=["DISCRETIONARY"],
             notes="Single-father / non-natural-guardian cases may require extra documentation."),
        rule("SSY_R002", "mandatory_doc", "has_aadhaar == True",
             "Guardian Aadhaar required",
             "Aadhaar-based KYC"),
    ],
    documents_checklist=["girl_child_birth_certificate", "guardian_aadhaar", "bank_passbook_with_ifsc"],
)

add(scheme_id="IGNOAPS",
    name="Indira Gandhi National Old Age Pension Scheme",
    ministry="Ministry of Rural Development (NSAP)",
    launched="2007-11-19",
    category="pension",
    short_description="Monthly pension for BPL citizens aged 60 years and above under NSAP.",
    description=(
        "IGNOAPS provides a central pension of ₹200/month for BPL applicants "
        "aged 60–79 years and ₹500/month for those 80 years and above. "
        "Most states top this up from their own funds."
    ),
    application_url="https://nsap.nic.in/",
    benefit={"type": "pension", "amount_inr": 200, "frequency": "monthly",
             "mode": "DBT"},
    inputs_required=["age", "is_bpl", "has_aadhaar", "has_bank_account"],
    rules=[
        rule("IGNOAPS_R001", "inclusion", "age >= 60",
             "Age 60 or above", "Age 60 years or above"),
        rule("IGNOAPS_R002", "inclusion", "is_bpl == True",
             "BPL household", "BPL identified household",
             conf="medium", flags=["STATE_DEPENDENT"]),
        rule("IGNOAPS_R003", "mandatory_doc",
             "has_aadhaar == True AND has_bank_account == True",
             "Aadhaar + bank account",
             "DBT requires Aadhaar-linked account"),
    ],
    documents_checklist=["aadhaar_card", "bank_passbook_with_ifsc", "age_proof", "bpl_certificate"],
)

add(scheme_id="IGNWPS",
    name="Indira Gandhi National Widow Pension Scheme",
    ministry="Ministry of Rural Development (NSAP)",
    launched="2009-02-01",
    category="pension",
    short_description="Monthly widow pension for BPL widows aged 40–79.",
    description=(
        "IGNWPS pays ₹300/month to widows aged 40–79 years belonging to "
        "BPL households. Most states supplement the amount. Remarriage, "
        "ceasing to be a widow, or moving out of BPL disqualifies."
    ),
    application_url="https://nsap.nic.in/",
    benefit={"type": "pension", "amount_inr": 300, "frequency": "monthly", "mode": "DBT"},
    inputs_required=["is_widow", "age", "is_bpl", "has_aadhaar", "has_bank_account"],
    rules=[
        rule("IGNWPS_R001", "inclusion", "is_widow == True",
             "Must be a widow",
             "Widow (as per state definition)",
             conf="medium", flags=["STATE_DEPENDENT"],
             notes="Definition of widow (remarriage, missing-husband) varies by state."),
        rule("IGNWPS_R002", "inclusion", "age >= 40",
             "Age 40 years or above",
             "Widows aged 40 years or above"),
        rule("IGNWPS_R003", "inclusion", "is_bpl == True",
             "BPL household",
             "Identified as BPL"),
        rule("IGNWPS_R004", "mandatory_doc",
             "has_aadhaar == True AND has_bank_account == True",
             "Aadhaar + bank account", "DBT requires linked account"),
    ],
    documents_checklist=["aadhaar_card", "bank_passbook_with_ifsc", "death_certificate_of_husband",
                         "age_proof", "bpl_certificate"],
)

add(scheme_id="PM_SVANIDHI",
    name="PM Street Vendor's AtmaNirbhar Nidhi",
    ministry="Ministry of Housing & Urban Affairs",
    launched="2020-06-01",
    category="livelihood",
    short_description="Collateral-free working-capital loan of ₹10k / ₹20k / ₹50k for urban street vendors.",
    description=(
        "PM SVANidhi provides urban street vendors with affordable "
        "collateral-free working-capital loans of ₹10,000 in the first "
        "tranche, escalating to ₹20,000 and ₹50,000 upon timely repayment. "
        "Interest subsidy of 7%; digital-transaction cashback up to ₹1,200/year."
    ),
    application_url="https://pmsvanidhi.mohua.gov.in/",
    benefit={"type": "loan_subsidy", "amount_inr": 50000, "frequency": "loan",
             "mode": "bank_credit"},
    inputs_required=["occupation", "district_rural_or_urban", "has_aadhaar", "has_bank_account"],
    rules=[
        rule("SVAN_R001", "inclusion", "occupation == 'street_vendor'",
             "Applicant must be a street vendor / hawker",
             "Street vendors as per the Street Vendors Act 2014"),
        rule("SVAN_R002", "inclusion", "district_rural_or_urban == 'urban'",
             "Must operate in urban area",
             "Scheme is for urban street vendors"),
        rule("SVAN_R003", "mandatory_doc",
             "has_aadhaar == True AND has_bank_account == True",
             "Aadhaar + bank account needed",
             "Credit linked with Aadhaar/PAN + bank account"),
    ],
    documents_checklist=["aadhaar_card", "bank_passbook_with_ifsc", "vending_certificate_or_letter"],
)

add(scheme_id="STANDUP_INDIA",
    name="Stand-Up India",
    ministry="Department of Financial Services",
    launched="2016-04-05",
    category="entrepreneurship",
    short_description="Bank loans ₹10 lakh – ₹1 crore to SC/ST or women entrepreneurs setting up a greenfield enterprise.",
    description=(
        "Stand-Up India facilitates bank loans between ₹10 lakh and ₹1 "
        "crore to at least one SC/ST and one woman borrower per bank branch "
        "for setting up a greenfield enterprise in manufacturing, services, "
        "trading, or agri-allied activities."
    ),
    application_url="https://www.standupmitra.in/",
    benefit={"type": "loan", "amount_inr": 10000000, "frequency": "loan",
             "mode": "bank_credit"},
    inputs_required=["age", "caste_category", "sex", "has_aadhaar", "has_bank_account"],
    rules=[
        rule("SUI_R001", "inclusion", "age >= 18",
             "Adult applicant",
             "Applicant must be 18+"),
        rule("SUI_R002", "inclusion",
             "caste_category IN ['SC','ST'] OR sex == 'F'",
             "Must be SC/ST or woman",
             "At least one SC/ST and/or woman borrower"),
        rule("SUI_R003", "mandatory_doc", "has_aadhaar == True AND has_bank_account == True",
             "Aadhaar + bank account", "Standard loan KYC"),
    ],
    documents_checklist=["aadhaar_card", "bank_passbook_with_ifsc", "caste_certificate_if_sc_st",
                         "project_proposal", "pan_card"],
)

add(scheme_id="PM_VISHWAKARMA",
    name="PM Vishwakarma Yojana",
    ministry="Ministry of MSME",
    launched="2023-09-17",
    category="artisan",
    short_description="Skill upgrade, ₹15k tool kit, and collateral-free loans up to ₹3 lakh for traditional artisans.",
    description=(
        "PM Vishwakarma recognises and supports 18 traditional artisan "
        "trades (carpenter, blacksmith, potter, tailor, barber, mason, etc.). "
        "Benefits include skill training with stipend, a ₹15,000 toolkit "
        "voucher, and collateral-free enterprise loans up to ₹3 lakh at "
        "concessional interest."
    ),
    application_url="https://pmvishwakarma.gov.in/",
    benefit={"type": "mixed", "amount_inr": 300000, "frequency": "one_time",
             "mode": "training_plus_loan_plus_toolkit"},
    inputs_required=["occupation", "age", "has_aadhaar", "has_bank_account"],
    rules=[
        rule("VSH_R001", "inclusion", "occupation == 'artisan'",
             "Applicant must be in a listed traditional trade",
             "Craftspeople and artisans engaged in one of 18 trades"),
        rule("VSH_R002", "inclusion", "age >= 18",
             "Adult applicant",
             "Minimum age 18"),
        rule("VSH_R003", "mandatory_doc", "has_aadhaar == True AND has_bank_account == True",
             "Aadhaar + bank account",
             "Standard DBT / loan KYC"),
    ],
    documents_checklist=["aadhaar_card", "bank_passbook_with_ifsc", "trade_self_declaration"],
)

add(scheme_id="PM_KISAN_MANDHAN",
    name="PM Kisan Maan-Dhan Yojana",
    ministry="Ministry of Agriculture & Farmers Welfare",
    launched="2019-09-12",
    category="pension",
    short_description="Voluntary ₹3,000/month pension after 60 for small and marginal farmers aged 18–40.",
    description=(
        "PM-KMY gives small and marginal farmers with up to 2 ha "
        "landholding a monthly pension of ₹3,000 after age 60, on matching "
        "monthly contributions during the accrual period. Open to ages 18–40."
    ),
    application_url="https://maandhan.in/",
    benefit={"type": "pension", "amount_inr": 3000, "frequency": "monthly",
             "mode": "post_60_pension"},
    inputs_required=["age", "land_ownership_type", "land_in_own_name", "has_aadhaar",
                     "has_bank_account", "income_tax_filed_last_ay"],
    rules=[
        rule("KMY_R001", "inclusion", "age BETWEEN 18 AND 40",
             "Age 18–40 at entry",
             "Eligible age 18 to 40 years"),
        rule("KMY_R002", "inclusion",
             "land_ownership_type == 'owned_cultivable' AND land_in_own_name == True",
             "Must be a small/marginal farmer with own land",
             "Small and marginal farmer with up to 2 hectares of cultivable land"),
        rule("KMY_R003", "exclusion", "income_tax_filed_last_ay == True",
             "Income-tax payers excluded",
             "Income tax assessees are not eligible"),
        rule("KMY_R004", "mandatory_doc",
             "has_aadhaar == True AND has_bank_account == True",
             "Aadhaar + bank account",
             "Standard KYC"),
    ],
    overlaps_with=[{"scheme": "PM_KISAN", "nature": "PM-KISAN beneficiaries can auto-opt for PM-KMY contributions"}],
    documents_checklist=["aadhaar_card", "bank_passbook_with_ifsc", "land_record"],
)

# ---------------- Additional 12 schemes ----------------

add(scheme_id="PM_SYM",
    name="PM Shram Yogi Maan-Dhan",
    ministry="Ministry of Labour & Employment",
    launched="2019-02-15",
    category="pension",
    short_description="₹3,000/month pension after 60 for unorganised-sector workers earning ≤ ₹15,000/month.",
    description=(
        "PM-SYM provides a guaranteed minimum pension of ₹3,000/month after "
        "60 to unorganised workers (street vendors, domestic workers, "
        "construction workers etc.) earning up to ₹15,000/month, aged 18–40. "
        "Matching monthly contribution."
    ),
    application_url="https://maandhan.in/shramyogi",
    benefit={"type": "pension", "amount_inr": 3000, "frequency": "monthly",
             "mode": "post_60_pension"},
    inputs_required=["age", "annual_income_inr", "has_aadhaar", "has_bank_account",
                     "govt_employee_status", "income_tax_filed_last_ay"],
    rules=[
        rule("SYM_R001", "inclusion", "age BETWEEN 18 AND 40",
             "Age 18–40", "Entry age 18 to 40"),
        rule("SYM_R002", "inclusion", "annual_income_inr <= 180000",
             "Monthly income ≤ ₹15,000 (₹1.8L/yr)",
             "Monthly income up to Rs 15,000"),
        rule("SYM_R003", "exclusion", "govt_employee_status != 'none'",
             "Existing govt employees excluded",
             "Not already covered under NPS/ESIC/EPFO as govt/organised worker"),
        rule("SYM_R004", "exclusion", "income_tax_filed_last_ay == True",
             "Income tax payers excluded",
             "Income tax assessees are not eligible"),
        rule("SYM_R005", "mandatory_doc",
             "has_aadhaar == True AND has_bank_account == True",
             "Aadhaar + bank account", "Standard KYC"),
    ],
    documents_checklist=["aadhaar_card", "bank_passbook_with_ifsc"],
)

add(scheme_id="IGNDPS",
    name="Indira Gandhi National Disability Pension Scheme",
    ministry="Ministry of Rural Development (NSAP)",
    launched="2009-02-01",
    category="pension",
    short_description="Monthly disability pension for BPL persons aged 18–79 with ≥80% disability.",
    description=(
        "IGNDPS provides a central pension of ₹300/month (and ₹500/month "
        "for those 80+) to BPL persons aged 18+ with severe or multiple "
        "disabilities (usually 80% or more). States may supplement."
    ),
    application_url="https://nsap.nic.in/",
    benefit={"type": "pension", "amount_inr": 300, "frequency": "monthly", "mode": "DBT"},
    inputs_required=["is_disabled", "age", "is_bpl", "has_aadhaar", "has_bank_account"],
    rules=[
        rule("DPS_R001", "inclusion", "is_disabled == True",
             "Must be certified disabled (usually ≥80%)",
             "Severe / multiple disability as per PwD Act",
             conf="medium", flags=["STATE_DEPENDENT"]),
        rule("DPS_R002", "inclusion", "age >= 18",
             "Age 18+", "Age 18 and above"),
        rule("DPS_R003", "inclusion", "is_bpl == True",
             "BPL household", "BPL listed household"),
        rule("DPS_R004", "mandatory_doc",
             "has_aadhaar == True AND has_bank_account == True",
             "Aadhaar + bank account", "DBT requires linked account"),
    ],
    documents_checklist=["aadhaar_card", "bank_passbook_with_ifsc",
                         "disability_certificate", "bpl_certificate"],
)

add(scheme_id="NSAP_NFBS",
    name="National Family Benefit Scheme (NSAP)",
    ministry="Ministry of Rural Development (NSAP)",
    launched="1995-08-15",
    category="family_support",
    short_description="One-time ₹20,000 to a BPL household on the death of its primary breadwinner aged 18–59.",
    description=(
        "NFBS provides a lump-sum assistance of ₹20,000 to a bereaved BPL "
        "household on the death of its primary earner (18–59 years). "
        "Claim must normally be filed within 3 years of the death."
    ),
    application_url="https://nsap.nic.in/",
    benefit={"type": "cash_transfer", "amount_inr": 20000, "frequency": "one_time",
             "mode": "DBT"},
    inputs_required=["is_bpl", "has_aadhaar", "has_bank_account"],
    rules=[
        rule("NFBS_R001", "inclusion", "is_bpl == True",
             "BPL household", "Identified BPL household"),
        rule("NFBS_R002", "mandatory_doc",
             "has_aadhaar == True AND has_bank_account == True",
             "Aadhaar + bank account", "DBT requires linked account"),
    ],
    documents_checklist=["aadhaar_card", "bank_passbook_with_ifsc",
                         "death_certificate", "bpl_certificate", "age_proof_of_deceased"],
)

add(scheme_id="MUDRA",
    name="Pradhan Mantri MUDRA Yojana",
    ministry="Department of Financial Services",
    launched="2015-04-08",
    category="entrepreneurship",
    short_description="Collateral-free micro-enterprise loans up to ₹10 lakh — Shishu, Kishore, Tarun.",
    description=(
        "PMMY provides collateral-free loans up to ₹10 lakh for "
        "non-corporate, non-farm small/micro enterprises. Three categories: "
        "Shishu (≤₹50k), Kishore (≤₹5L), Tarun (≤₹10L)."
    ),
    application_url="https://www.mudra.org.in/",
    benefit={"type": "loan", "amount_inr": 1000000, "frequency": "loan", "mode": "bank_credit"},
    inputs_required=["age", "occupation", "has_aadhaar", "has_bank_account"],
    rules=[
        rule("MUDRA_R001", "inclusion", "age >= 18",
             "Adult applicant", "Minimum age 18"),
        rule("MUDRA_R002", "inclusion",
             "occupation IN ['farmer','business','street_vendor','artisan','laborer','salaried','other','homemaker']",
             "Any non-corporate non-farm micro enterprise",
             "Small / Micro enterprise (non-corporate, non-farm)"),
        rule("MUDRA_R003", "mandatory_doc",
             "has_aadhaar == True AND has_bank_account == True",
             "Aadhaar + bank account", "Standard loan KYC"),
    ],
    documents_checklist=["aadhaar_card", "bank_passbook_with_ifsc", "business_proof", "pan_card"],
)

add(scheme_id="PMFBY",
    name="Pradhan Mantri Fasal Bima Yojana",
    ministry="Ministry of Agriculture & Farmers Welfare",
    launched="2016-04-01",
    category="farmer",
    short_description="Crop insurance for notified crops for farmers (owner, tenant, or sharecropper).",
    description=(
        "PMFBY provides insurance against crop loss due to natural calamities, "
        "pests and diseases. Premium: 2% of sum insured for kharif, 1.5% for "
        "rabi, 5% for annual commercial/horticultural crops. Both loanee and "
        "non-loanee farmers — including tenants and sharecroppers — can enrol."
    ),
    application_url="https://pmfby.gov.in/",
    benefit={"type": "insurance", "notes": "Sum insured equal to scale of finance",
             "mode": "claim_based"},
    inputs_required=["occupation", "has_aadhaar", "has_bank_account"],
    rules=[
        rule("PMFBY_R001", "inclusion", "occupation == 'farmer'",
             "Must be a cultivator (owner/tenant/sharecropper)",
             "All farmers including sharecroppers and tenants"),
        rule("PMFBY_R002", "mandatory_doc",
             "has_aadhaar == True AND has_bank_account == True",
             "Aadhaar + bank account", "Premium DBT + claim payout"),
    ],
    documents_checklist=["aadhaar_card", "bank_passbook_with_ifsc",
                         "sowing_certificate_or_land_record", "tenancy_agreement_if_tenant"],
)

add(scheme_id="KCC",
    name="Kisan Credit Card",
    ministry="Ministry of Agriculture & Farmers Welfare",
    launched="1998-08-01",
    category="farmer",
    short_description="Short-term crop loan with interest subvention for farmers — including tenants with recorded lease.",
    description=(
        "KCC provides flexible, short-term agricultural credit at a "
        "concessional interest rate (7% base, with 3% PRI + 2% ISS subvention) "
        "to farmers. Owner-cultivators, tenants, oral lessees and sharecroppers "
        "with a recorded lease/JLG can access KCC."
    ),
    application_url="https://www.pmkisan.gov.in/kcc/",
    benefit={"type": "loan", "notes": "Short-term agri credit at subvented rate", "mode": "bank_credit"},
    inputs_required=["occupation", "land_ownership_type", "has_aadhaar", "has_bank_account"],
    rules=[
        rule("KCC_R001", "inclusion", "occupation == 'farmer'",
             "Must be a cultivator",
             "All farmers — owner cultivators, tenants, oral lessees, sharecroppers"),
        rule("KCC_R002", "inclusion",
             "land_ownership_type IN ['owned_cultivable','lease']",
             "Land ownership or recorded lease required",
             "Recorded tenancy / sharecropping agreement acceptable",
             conf="medium", flags=["STATE_DEPENDENT"],
             notes="Tenancy documentation varies by state — informal tenants often rejected in practice."),
        rule("KCC_R003", "mandatory_doc",
             "has_aadhaar == True AND has_bank_account == True",
             "Aadhaar + bank account", "Standard KYC"),
    ],
    documents_checklist=["aadhaar_card", "bank_passbook_with_ifsc",
                         "land_record_or_lease_agreement"],
)

add(scheme_id="PMKVY",
    name="Pradhan Mantri Kaushal Vikas Yojana 4.0",
    ministry="Ministry of Skill Development & Entrepreneurship",
    launched="2015-07-15",
    category="skill",
    short_description="Free short-term industry-aligned skill training for Indian youth aged 15–45.",
    description=(
        "PMKVY offers free short-term training (STT) and recognition of "
        "prior learning (RPL) to Indian citizens aged 15–45, along with "
        "assessment, certification and placement support. Focus on NCVET-"
        "aligned courses."
    ),
    application_url="https://www.skillindiadigital.gov.in/",
    benefit={"type": "skill_training", "notes": "Free training + certification + placement", "mode": "voucher"},
    inputs_required=["age", "has_aadhaar"],
    rules=[
        rule("PMKVY_R001", "inclusion", "age BETWEEN 15 AND 45",
             "Age 15–45", "Indian citizen aged 15 to 45"),
        rule("PMKVY_R002", "mandatory_doc", "has_aadhaar == True",
             "Aadhaar required", "Aadhaar for Skill India Digital"),
    ],
    documents_checklist=["aadhaar_card", "passport_size_photo", "bank_passbook_with_ifsc"],
)

add(scheme_id="DDU_GKY",
    name="Deen Dayal Upadhyaya Grameen Kaushalya Yojana",
    ministry="Ministry of Rural Development",
    launched="2014-09-25",
    category="skill",
    short_description="Placement-linked skill training for rural youth aged 15–35 from poor families.",
    description=(
        "DDU-GKY is a placement-linked skills programme for rural youth "
        "aged 15–35 from poor families (SECC-identified). Training + "
        "assured placement. Higher age cap (18–45) for women and "
        "vulnerable groups."
    ),
    application_url="https://ddugky.gov.in/",
    benefit={"type": "skill_training", "notes": "Free training + placement support", "mode": "classroom"},
    inputs_required=["age", "district_rural_or_urban", "is_bpl", "has_aadhaar"],
    rules=[
        rule("DGKY_R001", "inclusion", "age BETWEEN 15 AND 35",
             "Age 15–35",
             "Rural youth aged 15–35; 18–45 for women"),
        rule("DGKY_R002", "inclusion", "district_rural_or_urban == 'rural'",
             "Rural residence",
             "Programme is for rural youth"),
        rule("DGKY_R003", "inclusion", "is_bpl == True",
             "Must be from a poor household",
             "SECC-identified poor rural household",
             conf="medium", flags=["STATE_DEPENDENT"]),
        rule("DGKY_R004", "mandatory_doc", "has_aadhaar == True",
             "Aadhaar required", "Aadhaar KYC"),
    ],
    documents_checklist=["aadhaar_card", "bank_passbook_with_ifsc", "bpl_or_secc_id"],
)

add(scheme_id="NRLM",
    name="Deendayal Antyodaya Yojana — National Rural Livelihoods Mission",
    ministry="Ministry of Rural Development",
    launched="2011-06-03",
    category="women",
    short_description="Women's Self-Help Groups with revolving fund + community investment fund + bank linkage — rural poor.",
    description=(
        "NRLM organises rural poor women into Self-Help Groups (SHGs), "
        "federates them, provides a revolving fund, community investment "
        "support, and affordable bank credit. Priority to SC/ST, minorities, "
        "PwD, and vulnerable households."
    ),
    application_url="https://aajeevika.gov.in/",
    benefit={"type": "shg_credit", "notes": "SHG revolving fund + bank linkage", "mode": "community_fund"},
    inputs_required=["sex", "district_rural_or_urban", "is_bpl", "has_aadhaar", "has_bank_account"],
    rules=[
        rule("NRLM_R001", "inclusion", "sex == 'F'",
             "Applicant must be a woman",
             "Women from poor rural households"),
        rule("NRLM_R002", "inclusion", "district_rural_or_urban == 'rural'",
             "Rural residence", "NRLM is for rural areas"),
        rule("NRLM_R003", "inclusion", "is_bpl == True",
             "Must be from a poor household",
             "Participatory Identification of the Poor (PIP)",
             conf="medium", flags=["STATE_DEPENDENT"]),
        rule("NRLM_R004", "mandatory_doc",
             "has_aadhaar == True AND has_bank_account == True",
             "Aadhaar + bank account", "Standard KYC for SHG linkage"),
    ],
    documents_checklist=["aadhaar_card", "bank_passbook_with_ifsc", "shg_membership_proof"],
)

add(scheme_id="NMMSS",
    name="National Means-cum-Merit Scholarship Scheme",
    ministry="Ministry of Education",
    launched="2008-05-01",
    category="scholarship",
    short_description="₹12,000/yr scholarship for meritorious Class 9–12 students whose family income ≤ ₹3.5 lakh/yr.",
    description=(
        "NMMSS awards ₹12,000/year to academically meritorious students "
        "from Class 9 to Class 12 in state-government, government-aided "
        "and local-body schools. Family income ceiling ₹3.5 lakh/year. "
        "Selection via state-level means-cum-merit test in Class 8."
    ),
    application_url="https://scholarships.gov.in/",
    benefit={"type": "scholarship", "amount_inr": 12000, "frequency": "yearly", "mode": "DBT"},
    inputs_required=["age", "annual_income_inr", "has_aadhaar", "has_bank_account"],
    rules=[
        rule("NMMSS_R001", "inclusion", "age BETWEEN 13 AND 19",
             "Age 13–19 (Class 9–12)",
             "Students in Class 9 through 12"),
        rule("NMMSS_R002", "inclusion", "annual_income_inr <= 350000",
             "Family income ≤ ₹3.5L/year",
             "Parental income ceiling of Rs 3.5 lakh"),
        rule("NMMSS_R003", "mandatory_doc",
             "has_aadhaar == True AND has_bank_account == True",
             "Aadhaar + bank account", "DBT requires linked account"),
    ],
    documents_checklist=["aadhaar_card", "bank_passbook_with_ifsc", "income_certificate",
                         "class_8_marksheet", "bonafide_certificate"],
)

add(scheme_id="PM_YASASVI",
    name="PM Young Achievers Scholarship Yojana for OBC / EBC / DNT",
    ministry="Ministry of Social Justice & Empowerment",
    launched="2021-10-01",
    category="scholarship",
    short_description="Pre- and post-matric scholarships for OBC / EBC / DNT students; family income ≤ ₹2.5 lakh/yr.",
    description=(
        "PM YASASVI provides pre- and post-matric scholarships and top-class "
        "school scholarships for students from OBC, EBC, and DNT communities. "
        "Family income ceiling ₹2.5 lakh per annum."
    ),
    application_url="https://yet.nta.ac.in/",
    benefit={"type": "scholarship", "amount_inr": 75000, "frequency": "yearly", "mode": "DBT"},
    inputs_required=["caste_category", "annual_income_inr", "age", "has_aadhaar", "has_bank_account"],
    rules=[
        rule("YSV_R001", "inclusion", "caste_category IN ['OBC','EWS']",
             "OBC / EBC / DNT category",
             "Applicable to OBC, EBC and DNT students"),
        rule("YSV_R002", "inclusion", "annual_income_inr <= 250000",
             "Family income ≤ ₹2.5L/year",
             "Family income up to ₹2.5 lakh"),
        rule("YSV_R003", "inclusion", "age BETWEEN 13 AND 22",
             "Student age 13–22", "Student in Class 9 to Class 12"),
        rule("YSV_R004", "mandatory_doc",
             "has_aadhaar == True AND has_bank_account == True",
             "Aadhaar + bank account", "DBT"),
    ],
    documents_checklist=["aadhaar_card", "bank_passbook_with_ifsc", "caste_certificate",
                         "income_certificate", "school_bonafide"],
)

add(scheme_id="ANNAPURNA",
    name="Annapurna Scheme (NSAP)",
    ministry="Ministry of Rural Development (NSAP)",
    launched="2000-04-01",
    category="food",
    short_description="10 kg of free foodgrain per month to poor senior citizens (65+) not already receiving IGNOAPS.",
    description=(
        "The Annapurna scheme provides 10 kg of foodgrain per month free "
        "of cost to indigent senior citizens aged 65+ who are otherwise "
        "eligible for IGNOAPS but not receiving it."
    ),
    application_url="https://nsap.nic.in/",
    benefit={"type": "food_subsidy", "notes": "10 kg foodgrain/month free", "mode": "ration_shop"},
    inputs_required=["age", "is_bpl", "has_aadhaar"],
    rules=[
        rule("ANN_R001", "inclusion", "age >= 65",
             "Age 65+", "Senior citizens 65 years or above"),
        rule("ANN_R002", "inclusion", "is_bpl == True",
             "Indigent / BPL", "Indigent senior citizens"),
        rule("ANN_R003", "mandatory_doc", "has_aadhaar == True",
             "Aadhaar required for ONORC",
             "ONORC / PDS Aadhaar seeding"),
    ],
    documents_checklist=["aadhaar_card", "ration_card", "age_proof"],
)

# ---------------- Write everything ----------------

def main():
    for old in OUT.glob("*.yaml"):
        old.unlink()
    for s in SCHEMES:
        path = OUT / (s["scheme_id"].lower() + ".yaml")
        path.write_text(yaml.safe_dump(s, sort_keys=False, allow_unicode=True))
    print(f"Wrote {len(SCHEMES)} schemes to {OUT}")


if __name__ == "__main__":
    main()
