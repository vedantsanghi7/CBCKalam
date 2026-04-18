# Edge Case Evaluation Results

> Engine evaluated **10 adversarial profiles** against **30 schemes**.

---

## Widow Who Recently Remarried (Leela, 38)

**ID:** `P01_leela_remarried_widow`  
**Adversarial Angle:** Tests whether widow-specific pension schemes correctly disqualify a widow who has remarried, despite still having BPL status. Exercises the tension between is_widow=true and remarried status.

| Status | Count |
|--------|-------|
| ✅ QUALIFIES | 19 |
| 🟡 ALMOST_QUALIFIES | 1 |
| ❌ DOES_NOT_QUALIFY | 10 |
| ❓ UNCERTAIN | 0 |

### ✅ Qualifies

- **Atal Pension Yojana** (`APY`) — confidence: 75% | missing: income_tax_filed_last_ay
- **Indira Gandhi National Disability Pension Scheme** (`IGNDPS`) — confidence: 56% | missing: is_disabled
- **Mahatma Gandhi National Rural Employment Guarantee Act** (`MGNREGA`) — confidence: 100%
- **Pradhan Mantri MUDRA Yojana** (`MUDRA`) — confidence: 100%
- **Deendayal Antyodaya Yojana — National Rural Livelihoods Mission** (`NRLM`) — confidence: 75%
- **National Family Benefit Scheme (NSAP)** (`NSAP_NFBS`) — confidence: 100%
- **Pradhan Mantri Kisan Samman Nidhi** (`PM_KISAN`) — confidence: 12% | missing: land_ownership_type, land_in_own_name, income_tax_filed_last_ay
- **PM Kisan Maan-Dhan Yojana** (`PM_KISAN_MANDHAN`) — confidence: 50% | missing: land_ownership_type, land_in_own_name, income_tax_filed_last_ay
- **PM Shram Yogi Maan-Dhan** (`PM_SYM`) — confidence: 60% | missing: govt_employee_status, income_tax_filed_last_ay
- **Pradhan Mantri Awas Yojana — Gramin** (`PMAY_G`) — confidence: 67%
- **Ayushman Bharat — PM Jan Arogya Yojana** (`PMJAY`) — confidence: 50%
- **Pradhan Mantri Jan Dhan Yojana** (`PMJDY`) — confidence: 100%
- **Pradhan Mantri Jeevan Jyoti Bima Yojana** (`PMJJBY`) — confidence: 100%
- **Pradhan Mantri Kaushal Vikas Yojana 4.0** (`PMKVY`) — confidence: 100%
- **Pradhan Mantri Matru Vandana Yojana** (`PMMVY`) — confidence: 56% | missing: is_pregnant
- **Pradhan Mantri Suraksha Bima Yojana** (`PMSBY`) — confidence: 100%
- **Pradhan Mantri Ujjwala Yojana** (`PMUY`) — confidence: 67%
- **Sukanya Samriddhi Yojana** (`SSY`) — confidence: 25% | missing: has_daughter_under_10
- **Stand-Up India** (`STANDUP_INDIA`) — confidence: 100%

### 🟡 Almost Qualifies

- **Pradhan Mantri Awas Yojana — Urban 2.0** (`PMAY_U`) — confidence: 100%

### ❌ Does Not Qualify (showing 5 of 10)

- **Annapurna Scheme (NSAP)** (`ANNAPURNA`) — confidence: 100%
- **Deen Dayal Upadhyaya Grameen Kaushalya Yojana** (`DDU_GKY`) — confidence: 100%
- **Indira Gandhi National Old Age Pension Scheme** (`IGNOAPS`) — confidence: 100%
- **Indira Gandhi National Widow Pension Scheme** (`IGNWPS`) — confidence: 100%
- **Kisan Credit Card** (`KCC`) — confidence: 100% | missing: land_ownership_type

---

## Landless Tenant Farmer (Ramesh, 42)

**ID:** `P02_ramesh_tenant_farmer`  
**Adversarial Angle:** Ramesh works on leased land. PM-KISAN requires "cultivable land held", so his ownership type "lease" should trigger ALMOST_QUALIFIES for PM-KISAN but still qualify for MGNREGA and KCC.

| Status | Count |
|--------|-------|
| ✅ QUALIFIES | 15 |
| 🟡 ALMOST_QUALIFIES | 2 |
| ❌ DOES_NOT_QUALIFY | 13 |
| ❓ UNCERTAIN | 0 |

### ✅ Qualifies

- **Indira Gandhi National Disability Pension Scheme** (`IGNDPS`) — confidence: 56% | missing: is_disabled
- **Indira Gandhi National Widow Pension Scheme** (`IGNWPS`) — confidence: 56% | missing: is_widow
- **Kisan Credit Card** (`KCC`) — confidence: 67%
- **Mahatma Gandhi National Rural Employment Guarantee Act** (`MGNREGA`) — confidence: 100%
- **Pradhan Mantri MUDRA Yojana** (`MUDRA`) — confidence: 100%
- **National Family Benefit Scheme (NSAP)** (`NSAP_NFBS`) — confidence: 100%
- **Pradhan Mantri Awas Yojana — Gramin** (`PMAY_G`) — confidence: 67%
- **Pradhan Mantri Fasal Bima Yojana** (`PMFBY`) — confidence: 100%
- **Ayushman Bharat — PM Jan Arogya Yojana** (`PMJAY`) — confidence: 50%
- **Pradhan Mantri Jan Dhan Yojana** (`PMJDY`) — confidence: 100%
- **Pradhan Mantri Jeevan Jyoti Bima Yojana** (`PMJJBY`) — confidence: 100%
- **Pradhan Mantri Kaushal Vikas Yojana 4.0** (`PMKVY`) — confidence: 100%
- **Pradhan Mantri Suraksha Bima Yojana** (`PMSBY`) — confidence: 100%
- **Sukanya Samriddhi Yojana** (`SSY`) — confidence: 25% | missing: has_daughter_under_10
- **Stand-Up India** (`STANDUP_INDIA`) — confidence: 100%

### 🟡 Almost Qualifies

- **Pradhan Mantri Kisan Samman Nidhi** (`PM_KISAN`) — confidence: 37% | missing: land_in_own_name, monthly_pension_inr, profession
- **Pradhan Mantri Awas Yojana — Urban 2.0** (`PMAY_U`) — confidence: 100%

### ❌ Does Not Qualify (showing 5 of 13)

- **Annapurna Scheme (NSAP)** (`ANNAPURNA`) — confidence: 100%
- **Atal Pension Yojana** (`APY`) — confidence: 100%
- **Deen Dayal Upadhyaya Grameen Kaushalya Yojana** (`DDU_GKY`) — confidence: 100%
- **Indira Gandhi National Old Age Pension Scheme** (`IGNOAPS`) — confidence: 100%
- **National Means-cum-Merit Scholarship Scheme** (`NMMSS`) — confidence: 100%

---

## Aadhaar-Only, No Bank Account (Sushila, 28)

**ID:** `P03_sushila_no_bank`  
**Adversarial Angle:** Most schemes require both Aadhaar + bank account. Sushila has Aadhaar but no bank account. This should recommend PMJDY first (bank account opening) and mark insurance/pension schemes as ALMOST_QUALIFIES.

| Status | Count |
|--------|-------|
| ✅ QUALIFIES | 5 |
| 🟡 ALMOST_QUALIFIES | 16 |
| ❌ DOES_NOT_QUALIFY | 9 |
| ❓ UNCERTAIN | 0 |

### ✅ Qualifies

- **Pradhan Mantri Awas Yojana — Urban 2.0** (`PMAY_U`) — confidence: 100%
- **Ayushman Bharat — PM Jan Arogya Yojana** (`PMJAY`) — confidence: 50%
- **Pradhan Mantri Jan Dhan Yojana** (`PMJDY`) — confidence: 100%
- **Pradhan Mantri Kaushal Vikas Yojana 4.0** (`PMKVY`) — confidence: 100%
- **Sukanya Samriddhi Yojana** (`SSY`) — confidence: 25% | missing: has_daughter_under_10

### 🟡 Almost Qualifies

- **Atal Pension Yojana** (`APY`) — confidence: 100%
- **Deen Dayal Upadhyaya Grameen Kaushalya Yojana** (`DDU_GKY`) — confidence: 75%
- **Indira Gandhi National Disability Pension Scheme** (`IGNDPS`) — confidence: 56% | missing: is_disabled
- **Mahatma Gandhi National Rural Employment Guarantee Act** (`MGNREGA`) — confidence: 100%
- **Pradhan Mantri MUDRA Yojana** (`MUDRA`) — confidence: 100%
- **Deendayal Antyodaya Yojana — National Rural Livelihoods Mission** (`NRLM`) — confidence: 75%
- **National Family Benefit Scheme (NSAP)** (`NSAP_NFBS`) — confidence: 100%
- **Pradhan Mantri Kisan Samman Nidhi** (`PM_KISAN`) — confidence: 24% | missing: land_ownership_type, land_in_own_name, monthly_pension_inr
- **PM Kisan Maan-Dhan Yojana** (`PM_KISAN_MANDHAN`) — confidence: 75% | missing: land_ownership_type, land_in_own_name
- **PM Shram Yogi Maan-Dhan** (`PM_SYM`) — confidence: 80% | missing: govt_employee_status
- **Pradhan Mantri Awas Yojana — Gramin** (`PMAY_G`) — confidence: 67%
- **Pradhan Mantri Jeevan Jyoti Bima Yojana** (`PMJJBY`) — confidence: 100%
- **Pradhan Mantri Matru Vandana Yojana** (`PMMVY`) — confidence: 56% | missing: is_pregnant
- **Pradhan Mantri Suraksha Bima Yojana** (`PMSBY`) — confidence: 100%
- **Pradhan Mantri Ujjwala Yojana** (`PMUY`) — confidence: 67%
- **Stand-Up India** (`STANDUP_INDIA`) — confidence: 100%

### ❌ Does Not Qualify (showing 5 of 9)

- **Annapurna Scheme (NSAP)** (`ANNAPURNA`) — confidence: 100%
- **Indira Gandhi National Old Age Pension Scheme** (`IGNOAPS`) — confidence: 100%
- **Indira Gandhi National Widow Pension Scheme** (`IGNWPS`) — confidence: 100% | missing: is_widow
- **Kisan Credit Card** (`KCC`) — confidence: 100% | missing: land_ownership_type
- **National Means-cum-Merit Scholarship Scheme** (`NMMSS`) — confidence: 100%

---

## Transgender Individual (Ayesha, 35)

**ID:** `P04_ayesha_transgender`  
**Adversarial Angle:** Ayesha identifies as transgender (sex='other'). Schemes like PMMVY require sex='F' explicitly. Tests whether the engine correctly marks gender-specific schemes as DOES_NOT_QUALIFY vs. UNCERTAIN. Also tests is_pregnant=true with sex='other'.

| Status | Count |
|--------|-------|
| ✅ QUALIFIES | 14 |
| 🟡 ALMOST_QUALIFIES | 3 |
| ❌ DOES_NOT_QUALIFY | 13 |
| ❓ UNCERTAIN | 0 |

### ✅ Qualifies

- **Atal Pension Yojana** (`APY`) — confidence: 75% | missing: income_tax_filed_last_ay
- **Indira Gandhi National Disability Pension Scheme** (`IGNDPS`) — confidence: 56% | missing: is_disabled
- **Pradhan Mantri MUDRA Yojana** (`MUDRA`) — confidence: 100%
- **National Family Benefit Scheme (NSAP)** (`NSAP_NFBS`) — confidence: 100%
- **Pradhan Mantri Kisan Samman Nidhi** (`PM_KISAN`) — confidence: 12% | missing: land_ownership_type, land_in_own_name, income_tax_filed_last_ay
- **PM Kisan Maan-Dhan Yojana** (`PM_KISAN_MANDHAN`) — confidence: 50% | missing: land_ownership_type, land_in_own_name, income_tax_filed_last_ay
- **PM Shram Yogi Maan-Dhan** (`PM_SYM`) — confidence: 60% | missing: govt_employee_status, income_tax_filed_last_ay
- **Pradhan Mantri Awas Yojana — Urban 2.0** (`PMAY_U`) — confidence: 100%
- **Ayushman Bharat — PM Jan Arogya Yojana** (`PMJAY`) — confidence: 50%
- **Pradhan Mantri Jan Dhan Yojana** (`PMJDY`) — confidence: 100%
- **Pradhan Mantri Jeevan Jyoti Bima Yojana** (`PMJJBY`) — confidence: 100%
- **Pradhan Mantri Kaushal Vikas Yojana 4.0** (`PMKVY`) — confidence: 100%
- **Pradhan Mantri Suraksha Bima Yojana** (`PMSBY`) — confidence: 100%
- **Sukanya Samriddhi Yojana** (`SSY`) — confidence: 25% | missing: has_daughter_under_10

### 🟡 Almost Qualifies

- **Deen Dayal Upadhyaya Grameen Kaushalya Yojana** (`DDU_GKY`) — confidence: 75%
- **Mahatma Gandhi National Rural Employment Guarantee Act** (`MGNREGA`) — confidence: 100%
- **Pradhan Mantri Awas Yojana — Gramin** (`PMAY_G`) — confidence: 67%

### ❌ Does Not Qualify (showing 5 of 13)

- **Annapurna Scheme (NSAP)** (`ANNAPURNA`) — confidence: 100%
- **Indira Gandhi National Old Age Pension Scheme** (`IGNOAPS`) — confidence: 100%
- **Indira Gandhi National Widow Pension Scheme** (`IGNWPS`) — confidence: 100% | missing: is_widow
- **Kisan Credit Card** (`KCC`) — confidence: 100% | missing: land_ownership_type
- **National Means-cum-Merit Scholarship Scheme** (`NMMSS`) — confidence: 100%

---

## Husband Missing 7+ Years (Meena, 45)

**ID:** `P05_meena_missing_husband`  
**Adversarial Angle:** Meena's husband has been missing for 7 years. She may be legally considered a widow by court decree but has no death certificate. Tests UNKNOWN handling for is_widow — the engine should flag this as UNCERTAIN rather than force a True/False.

| Status | Count |
|--------|-------|
| ✅ QUALIFIES | 17 |
| 🟡 ALMOST_QUALIFIES | 1 |
| ❌ DOES_NOT_QUALIFY | 12 |
| ❓ UNCERTAIN | 0 |

### ✅ Qualifies

- **Indira Gandhi National Disability Pension Scheme** (`IGNDPS`) — confidence: 56% | missing: is_disabled
- **Indira Gandhi National Widow Pension Scheme** (`IGNWPS`) — confidence: 75%
- **Mahatma Gandhi National Rural Employment Guarantee Act** (`MGNREGA`) — confidence: 100%
- **Pradhan Mantri MUDRA Yojana** (`MUDRA`) — confidence: 100%
- **Deendayal Antyodaya Yojana — National Rural Livelihoods Mission** (`NRLM`) — confidence: 75%
- **National Family Benefit Scheme (NSAP)** (`NSAP_NFBS`) — confidence: 100%
- **Pradhan Mantri Kisan Samman Nidhi** (`PM_KISAN`) — confidence: 12% | missing: land_ownership_type, land_in_own_name, income_tax_filed_last_ay
- **Pradhan Mantri Awas Yojana — Gramin** (`PMAY_G`) — confidence: 67%
- **Ayushman Bharat — PM Jan Arogya Yojana** (`PMJAY`) — confidence: 50%
- **Pradhan Mantri Jan Dhan Yojana** (`PMJDY`) — confidence: 100%
- **Pradhan Mantri Jeevan Jyoti Bima Yojana** (`PMJJBY`) — confidence: 100%
- **Pradhan Mantri Kaushal Vikas Yojana 4.0** (`PMKVY`) — confidence: 100%
- **Pradhan Mantri Matru Vandana Yojana** (`PMMVY`) — confidence: 56% | missing: is_pregnant
- **Pradhan Mantri Suraksha Bima Yojana** (`PMSBY`) — confidence: 100%
- **Pradhan Mantri Ujjwala Yojana** (`PMUY`) — confidence: 67%
- **Sukanya Samriddhi Yojana** (`SSY`) — confidence: 25% | missing: has_daughter_under_10
- **Stand-Up India** (`STANDUP_INDIA`) — confidence: 100%

### 🟡 Almost Qualifies

- **Pradhan Mantri Awas Yojana — Urban 2.0** (`PMAY_U`) — confidence: 100%

### ❌ Does Not Qualify (showing 5 of 12)

- **Annapurna Scheme (NSAP)** (`ANNAPURNA`) — confidence: 100%
- **Atal Pension Yojana** (`APY`) — confidence: 100% | missing: income_tax_filed_last_ay
- **Deen Dayal Upadhyaya Grameen Kaushalya Yojana** (`DDU_GKY`) — confidence: 100%
- **Indira Gandhi National Old Age Pension Scheme** (`IGNOAPS`) — confidence: 100%
- **Kisan Credit Card** (`KCC`) — confidence: 100% | missing: land_ownership_type

---

## Divorced Father Raising Daughter (Arjun, 44)

**ID:** `P06_arjun_single_father`  
**Adversarial Angle:** SSY (Sukanya Samriddhi) is for "girl child" parents. Arjun is a divorced single father with a daughter under 10. Tests whether the engine correctly qualifies him despite the scheme's common association with mothers specifically.

| Status | Count |
|--------|-------|
| ✅ QUALIFIES | 7 |
| 🟡 ALMOST_QUALIFIES | 5 |
| ❌ DOES_NOT_QUALIFY | 18 |
| ❓ UNCERTAIN | 0 |

### ✅ Qualifies

- **Pradhan Mantri MUDRA Yojana** (`MUDRA`) — confidence: 100%
- **Pradhan Mantri Awas Yojana — Urban 2.0** (`PMAY_U`) — confidence: 100%
- **Pradhan Mantri Jan Dhan Yojana** (`PMJDY`) — confidence: 100%
- **Pradhan Mantri Jeevan Jyoti Bima Yojana** (`PMJJBY`) — confidence: 100%
- **Pradhan Mantri Kaushal Vikas Yojana 4.0** (`PMKVY`) — confidence: 100%
- **Pradhan Mantri Suraksha Bima Yojana** (`PMSBY`) — confidence: 100%
- **Sukanya Samriddhi Yojana** (`SSY`) — confidence: 50%

### 🟡 Almost Qualifies

- **Indira Gandhi National Disability Pension Scheme** (`IGNDPS`) — confidence: 56% | missing: is_disabled
- **Indira Gandhi National Widow Pension Scheme** (`IGNWPS`) — confidence: 56% | missing: is_widow
- **Mahatma Gandhi National Rural Employment Guarantee Act** (`MGNREGA`) — confidence: 100%
- **National Family Benefit Scheme (NSAP)** (`NSAP_NFBS`) — confidence: 100%
- **Pradhan Mantri Kisan Samman Nidhi** (`PM_KISAN`) — confidence: 24% | missing: land_ownership_type, land_in_own_name, monthly_pension_inr

### ❌ Does Not Qualify (showing 5 of 18)

- **Annapurna Scheme (NSAP)** (`ANNAPURNA`) — confidence: 100%
- **Atal Pension Yojana** (`APY`) — confidence: 100%
- **Deen Dayal Upadhyaya Grameen Kaushalya Yojana** (`DDU_GKY`) — confidence: 100%
- **Indira Gandhi National Old Age Pension Scheme** (`IGNOAPS`) — confidence: 100%
- **Kisan Credit Card** (`KCC`) — confidence: 100% | missing: land_ownership_type

---

## Exact Age Boundary — Just Turned 18 (Ravi)

**ID:** `P07_boundary_age_18`  
**Adversarial Angle:** Ravi is exactly 18. Multiple schemes have age >= 18 or BETWEEN 18 AND X rules. Tests that boundary values are handled inclusively (>=, not >). Should qualify for PMJJBY, PMSBY, MGNREGA, APY, PM-SVANidhi, etc.

| Status | Count |
|--------|-------|
| ✅ QUALIFIES | 18 |
| 🟡 ALMOST_QUALIFIES | 1 |
| ❌ DOES_NOT_QUALIFY | 11 |
| ❓ UNCERTAIN | 0 |

### ✅ Qualifies

- **Atal Pension Yojana** (`APY`) — confidence: 100%
- **Deen Dayal Upadhyaya Grameen Kaushalya Yojana** (`DDU_GKY`) — confidence: 75%
- **Indira Gandhi National Disability Pension Scheme** (`IGNDPS`) — confidence: 56% | missing: is_disabled
- **Mahatma Gandhi National Rural Employment Guarantee Act** (`MGNREGA`) — confidence: 100%
- **Pradhan Mantri MUDRA Yojana** (`MUDRA`) — confidence: 100%
- **National Means-cum-Merit Scholarship Scheme** (`NMMSS`) — confidence: 100%
- **National Family Benefit Scheme (NSAP)** (`NSAP_NFBS`) — confidence: 100%
- **Pradhan Mantri Kisan Samman Nidhi** (`PM_KISAN`) — confidence: 24% | missing: land_ownership_type, land_in_own_name, monthly_pension_inr
- **PM Kisan Maan-Dhan Yojana** (`PM_KISAN_MANDHAN`) — confidence: 75% | missing: land_ownership_type, land_in_own_name
- **PM Shram Yogi Maan-Dhan** (`PM_SYM`) — confidence: 80% | missing: govt_employee_status
- **Pradhan Mantri Awas Yojana — Gramin** (`PMAY_G`) — confidence: 67%
- **Ayushman Bharat — PM Jan Arogya Yojana** (`PMJAY`) — confidence: 50%
- **Pradhan Mantri Jan Dhan Yojana** (`PMJDY`) — confidence: 100%
- **Pradhan Mantri Jeevan Jyoti Bima Yojana** (`PMJJBY`) — confidence: 100%
- **Pradhan Mantri Kaushal Vikas Yojana 4.0** (`PMKVY`) — confidence: 100%
- **Pradhan Mantri Suraksha Bima Yojana** (`PMSBY`) — confidence: 100%
- **Sukanya Samriddhi Yojana** (`SSY`) — confidence: 25% | missing: has_daughter_under_10
- **Stand-Up India** (`STANDUP_INDIA`) — confidence: 100%

### 🟡 Almost Qualifies

- **Pradhan Mantri Awas Yojana — Urban 2.0** (`PMAY_U`) — confidence: 100%

### ❌ Does Not Qualify (showing 5 of 11)

- **Annapurna Scheme (NSAP)** (`ANNAPURNA`) — confidence: 100%
- **Indira Gandhi National Old Age Pension Scheme** (`IGNOAPS`) — confidence: 100%
- **Indira Gandhi National Widow Pension Scheme** (`IGNWPS`) — confidence: 100% | missing: is_widow
- **Kisan Credit Card** (`KCC`) — confidence: 100% | missing: land_ownership_type
- **Deendayal Antyodaya Yojana — National Rural Livelihoods Mission** (`NRLM`) — confidence: 100%

---

## High-Income Farmer Filing Taxes (Pradeep, 55)

**ID:** `P08_wealthy_farmer`  
**Adversarial Angle:** Pradeep is a farmer with high income who files taxes. PM-KISAN explicitly excludes income-tax filers. Tests the exclusion-rule logic — he should DOES_NOT_QUALIFY for PM-KISAN despite being a farmer with own land. Should still qualify for KCC and PMFBY.

| Status | Count |
|--------|-------|
| ✅ QUALIFIES | 7 |
| 🟡 ALMOST_QUALIFIES | 5 |
| ❌ DOES_NOT_QUALIFY | 18 |
| ❓ UNCERTAIN | 0 |

### ✅ Qualifies

- **Kisan Credit Card** (`KCC`) — confidence: 67%
- **Mahatma Gandhi National Rural Employment Guarantee Act** (`MGNREGA`) — confidence: 100%
- **Pradhan Mantri MUDRA Yojana** (`MUDRA`) — confidence: 100%
- **Pradhan Mantri Fasal Bima Yojana** (`PMFBY`) — confidence: 100%
- **Pradhan Mantri Jan Dhan Yojana** (`PMJDY`) — confidence: 100%
- **Pradhan Mantri Suraksha Bima Yojana** (`PMSBY`) — confidence: 100%
- **Sukanya Samriddhi Yojana** (`SSY`) — confidence: 25% | missing: has_daughter_under_10

### 🟡 Almost Qualifies

- **Indira Gandhi National Disability Pension Scheme** (`IGNDPS`) — confidence: 56% | missing: is_disabled
- **Indira Gandhi National Widow Pension Scheme** (`IGNWPS`) — confidence: 56% | missing: is_widow
- **National Family Benefit Scheme (NSAP)** (`NSAP_NFBS`) — confidence: 100%
- **Pradhan Mantri Kisan Samman Nidhi** (`PM_KISAN`) — confidence: 24% | missing: land_in_own_name, monthly_pension_inr, profession
- **Pradhan Mantri Awas Yojana — Urban 2.0** (`PMAY_U`) — confidence: 100%

### ❌ Does Not Qualify (showing 5 of 18)

- **Annapurna Scheme (NSAP)** (`ANNAPURNA`) — confidence: 100%
- **Atal Pension Yojana** (`APY`) — confidence: 100%
- **Deen Dayal Upadhyaya Grameen Kaushalya Yojana** (`DDU_GKY`) — confidence: 100%
- **Indira Gandhi National Old Age Pension Scheme** (`IGNOAPS`) — confidence: 100%
- **National Means-cum-Merit Scholarship Scheme** (`NMMSS`) — confidence: 100%

---

## 70-Year-Old Without Any Pension (Kamla Devi)

**ID:** `P09_elderly_no_pension`  
**Adversarial Angle:** Tests upper age boundaries. At 70, Kamla exceeds PMJJBY's max age (50) and APY's max (40) but should strongly qualify for IGNOAPS (old-age pension), Annapurna (food), and NSAP/NFBS. Verifies that exceeding scheme age limits correctly results in DOES_NOT_QUALIFY.

| Status | Count |
|--------|-------|
| ✅ QUALIFIES | 17 |
| 🟡 ALMOST_QUALIFIES | 1 |
| ❌ DOES_NOT_QUALIFY | 12 |
| ❓ UNCERTAIN | 0 |

### ✅ Qualifies

- **Annapurna Scheme (NSAP)** (`ANNAPURNA`) — confidence: 100%
- **Indira Gandhi National Disability Pension Scheme** (`IGNDPS`) — confidence: 56% | missing: is_disabled
- **Indira Gandhi National Old Age Pension Scheme** (`IGNOAPS`) — confidence: 67%
- **Indira Gandhi National Widow Pension Scheme** (`IGNWPS`) — confidence: 75%
- **Mahatma Gandhi National Rural Employment Guarantee Act** (`MGNREGA`) — confidence: 100%
- **Pradhan Mantri MUDRA Yojana** (`MUDRA`) — confidence: 100%
- **Deendayal Antyodaya Yojana — National Rural Livelihoods Mission** (`NRLM`) — confidence: 75%
- **National Family Benefit Scheme (NSAP)** (`NSAP_NFBS`) — confidence: 100%
- **Pradhan Mantri Kisan Samman Nidhi** (`PM_KISAN`) — confidence: 37% | missing: land_ownership_type, land_in_own_name, profession
- **Pradhan Mantri Awas Yojana — Gramin** (`PMAY_G`) — confidence: 67%
- **Ayushman Bharat — PM Jan Arogya Yojana** (`PMJAY`) — confidence: 50%
- **Pradhan Mantri Jan Dhan Yojana** (`PMJDY`) — confidence: 100%
- **Pradhan Mantri Matru Vandana Yojana** (`PMMVY`) — confidence: 56% | missing: is_pregnant
- **Pradhan Mantri Suraksha Bima Yojana** (`PMSBY`) — confidence: 100%
- **Pradhan Mantri Ujjwala Yojana** (`PMUY`) — confidence: 67%
- **Sukanya Samriddhi Yojana** (`SSY`) — confidence: 25% | missing: has_daughter_under_10
- **Stand-Up India** (`STANDUP_INDIA`) — confidence: 100%

### 🟡 Almost Qualifies

- **Pradhan Mantri Awas Yojana — Urban 2.0** (`PMAY_U`) — confidence: 100%

### ❌ Does Not Qualify (showing 5 of 12)

- **Atal Pension Yojana** (`APY`) — confidence: 100%
- **Deen Dayal Upadhyaya Grameen Kaushalya Yojana** (`DDU_GKY`) — confidence: 100%
- **Kisan Credit Card** (`KCC`) — confidence: 100% | missing: land_ownership_type
- **National Means-cum-Merit Scholarship Scheme** (`NMMSS`) — confidence: 100%
- **PM Kisan Maan-Dhan Yojana** (`PM_KISAN_MANDHAN`) — confidence: 100% | missing: land_ownership_type, land_in_own_name

---

## Urban Street Vendor Without PAN (Firoz, 32)

**ID:** `P10_urban_street_vendor`  
**Adversarial Angle:** Firoz is a street vendor — prime target for PM-SVANidhi. But he lacks a PAN card. Tests whether missing optional documents don't block qualification. He should also be eligible for Mudra, PMJJBY, PMSBY. Verifies occupation-based routing works correctly for 'street_vendor'.

| Status | Count |
|--------|-------|
| ✅ QUALIFIES | 15 |
| 🟡 ALMOST_QUALIFIES | 3 |
| ❌ DOES_NOT_QUALIFY | 12 |
| ❓ UNCERTAIN | 0 |

### ✅ Qualifies

- **Atal Pension Yojana** (`APY`) — confidence: 100%
- **Indira Gandhi National Disability Pension Scheme** (`IGNDPS`) — confidence: 56% | missing: is_disabled
- **Pradhan Mantri MUDRA Yojana** (`MUDRA`) — confidence: 100%
- **National Family Benefit Scheme (NSAP)** (`NSAP_NFBS`) — confidence: 100%
- **Pradhan Mantri Kisan Samman Nidhi** (`PM_KISAN`) — confidence: 24% | missing: land_ownership_type, land_in_own_name, monthly_pension_inr
- **PM Kisan Maan-Dhan Yojana** (`PM_KISAN_MANDHAN`) — confidence: 75% | missing: land_ownership_type, land_in_own_name
- **PM Street Vendor's AtmaNirbhar Nidhi** (`PM_SVANIDHI`) — confidence: 100%
- **PM Shram Yogi Maan-Dhan** (`PM_SYM`) — confidence: 80% | missing: govt_employee_status
- **Pradhan Mantri Awas Yojana — Urban 2.0** (`PMAY_U`) — confidence: 100%
- **Ayushman Bharat — PM Jan Arogya Yojana** (`PMJAY`) — confidence: 50%
- **Pradhan Mantri Jan Dhan Yojana** (`PMJDY`) — confidence: 100%
- **Pradhan Mantri Jeevan Jyoti Bima Yojana** (`PMJJBY`) — confidence: 100%
- **Pradhan Mantri Kaushal Vikas Yojana 4.0** (`PMKVY`) — confidence: 100%
- **Pradhan Mantri Suraksha Bima Yojana** (`PMSBY`) — confidence: 100%
- **Sukanya Samriddhi Yojana** (`SSY`) — confidence: 25% | missing: has_daughter_under_10

### 🟡 Almost Qualifies

- **Deen Dayal Upadhyaya Grameen Kaushalya Yojana** (`DDU_GKY`) — confidence: 75%
- **Mahatma Gandhi National Rural Employment Guarantee Act** (`MGNREGA`) — confidence: 100%
- **Pradhan Mantri Awas Yojana — Gramin** (`PMAY_G`) — confidence: 67%

### ❌ Does Not Qualify (showing 5 of 12)

- **Annapurna Scheme (NSAP)** (`ANNAPURNA`) — confidence: 100%
- **Indira Gandhi National Old Age Pension Scheme** (`IGNOAPS`) — confidence: 100%
- **Indira Gandhi National Widow Pension Scheme** (`IGNWPS`) — confidence: 100% | missing: is_widow
- **Kisan Credit Card** (`KCC`) — confidence: 100% | missing: land_ownership_type
- **National Means-cum-Merit Scholarship Scheme** (`NMMSS`) — confidence: 100%

