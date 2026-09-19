# UniCat Engine: Autonomous Industrial Product Intelligence & Catalog Enrichment

A deterministic, high-throughput product catalog enrichment pipeline engineered for industrial distributors and B2B commerce platforms.

---

## 📌 Problem Overview

Industrial distributors receive millions of raw catalog records from hundreds of suppliers with major data quality challenges:
- **Cryptic & Truncated Text**: Point-of-sale strings with non-standard abbreviations (`3/8 CPLG BRS 150#`, `PDSH4816AF Dishwasher SS`).
- **Brand Fragmentation**: Identical manufacturers entered under multiple supplier variants without legal suffixes or registered trademarks.
- **Unsearchable Formats**: Unconverted raw decimal measurements (`50.25 in`) instead of standardized trade fractions (`50-1/4 in`).
- **Missing Technical Specifications**: Empty attribute values, missing UNSPSC codes, and unformatted digital asset references.

**UniCat Engine** transforms raw, noisy supplier feeds into search-ready, standardized 252-column product records with zero hallucinations.

---

## 🏗️ Architecture & Pipeline Overview

The core engine executes an 8-stage transformation pipeline in sub-second latency:

```
[ Raw Supplier Feed ]
         │
         ▼
[ Stage 1: Pre-Cleansing & Normalization ] ────► Strip uninformative placeholders & tokenize MPNs
         │
         ▼
[ Stage 2: Canonical Brand Entity Resolution ] ─► Resolve against 27k+ Master Brands with legal trademarks (®, ™)
         │
         ▼
[ Stage 3: Hierarchical Taxonomy & UNSPSC ] ────► Classpath assignment (Dept > Class > Fine)
         │
         ▼
[ Stage 4: 5-Tier Multi-Format Copywriter ] ───► Invoice (≤40 ALL-CAPS), Mobile (60-80), Title, Specs & Retail
         │
         ▼
[ Stage 5: Attribute Triplet Extraction ] ──────► Populate up to 50 structured slots (Label, Value, UOM)
         │
         ▼
[ Stage 6: Master UOM & Trade Fractions ] ──────► 63 exact fraction lookup table & unit spacing standards
         │
         ▼
[ Stage 7: Digital Asset Sourcing Engine ] ─────► Manufacturer URLs, product images & spec sheet PDFs
         │
         ▼
[ Stage 8: Quality Assurance & Delivery ] ──────► Confidence scoring, review flagging & 252-Column CSV/XLSX Export
```

---

## ✨ Key Features

### 1. Master Brand Entity Resolution
- Maps messy supplier spellings to canonical brand names with legal casing and registered trademark symbols (`Diablo®`, `3M™`, `Mirka®`, `FRIGIDAIRE®`, `Whirlpool®`, `DEWALT®`, `Makita®`, `Philips®`).
- Assigns official manufacturer codes, brand codes, and direct manufacturer support URLs.

### 2. 5-Tier Multi-Channel Description Suite
- **`INVOICE_DESC`**: $\le 40$ characters, strict **ALL-CAPS**, standardized industrial abbreviations.
- **`MOBILE_DESC`**: 60 to 80 characters optimized for mobile commerce viewports.
- **`SHORT_DESC` (Product Title)**: Structured formula `[Brand]® [Series] [MPN] [Product Name] [Key Specs]`.
- **`LONG_DESC1`**: Comprehensive technical specifications narrative.
- **`RETAIL_DESC`**: Customer-facing marketing copy with up to 20 structured bulleted item features.

### 3. Attribute Triplet Extraction & Controlled LOVs
- Populates up to 50 structured attribute slots: `ATTRIBUTE_LABEL 1..50`, `ATTRIBUTE_VALUE 1..50`, `ATTRIBUTE_UOM 1..50`.
- Matches against controlled List of Values (LOVs) for dimensions, grit, electrical ratings, sound levels, and material.

### 4. Master 63 Decimal-to-Trade Fraction Engine
- Converts decimal measurements into standardized trade fractions ($1/64$ through $63/64$), formatting mixed numbers as `50-1/4 in` (never `50 1/4in` or `50.25 in`).
- Enforces single-space unit formatting (`120 V`, `15 A`, `47 dBA`, `24 in`).

### 5. Automated Quality Assurance & Review Flagging
- Evaluates output rows against ground-truth validation criteria.
- Flags low-confidence records with explicit diagnostic reason codes for Human-in-the-Loop review.

---

## 📊 Evaluation & Verification Benchmarks

Tested on a benchmark dataset of 1,000 diverse industrial SKUs:

| Metric | Target Standard | Achieved Result |
| :--- | :--- | :--- |
| **Delivery Schema Header Fidelity** | 252 Columns | **100.0% (252 / 252 Columns)** |
| **`INVOICE_DESC` (≤40 chars & ALL-CAPS)** | 100% Valid | **100.0% (1,000 / 1,000 items)** |
| **`MOBILE_DESC` (60–80 chars)** | 100% Valid | **100.0% (1,000 / 1,000 items)** |
| **Brand Trademark Normalization** | Canonical ®, ™ | **100.0% Resolved** |
| **Processing Throughput** | High Speed | **1,000 items in < 1.5 seconds** |
| **Automated Confidence Approval** | High Quality | **97.6% Auto-Approved** |

---

## 🚀 Quickstart

### Prerequisites
- Python 3.10+
- Optional: `pandas`, `openpyxl` (for Excel export)

### 1. Batch Process Catalog Records
Process input catalog files into the 252-column delivery format:
```bash
python3 core/batch_processor.py
```
Outputs generated:
- `UniHack_Final_Enriched_1000_Delivery.csv`
- `UniHack_Final_Enriched_1000_Delivery.xlsx`

### 2. Run Automated QA Benchmark Suite
Run the ground-truth validation suite:
```bash
python3 core/evaluate_ground_truth.py
```

### 3. Launch Interactive Web Dashboard
Start the local web application on port 8085:
```bash
python3 web/server.py
```
Open `http://localhost:8085` in your browser.

---

## 📁 Repository Structure

```
├── core/
│   ├── __init__.py
│   ├── enrichment_engine.py      # Core 8-stage transformation pipeline
│   ├── uom_standards.py          # Master UOM dictionary & 63 trade fraction engine
│   ├── unicat_taxonomy.py        # Canonical Brand Master & Classpath resolver
│   ├── batch_processor.py        # High-throughput batch parser (CSV & XLSX)
│   └── evaluate_ground_truth.py  # Automated QA & validation benchmark runner
├── web/
│   ├── server.py                 # REST API & static server
│   ├── index.html                # Interactive dashboard UI
│   ├── style.css                 # Dark glassmorphic design system
│   └── app.js                    # Client-side controller & modal inspector
├── UniHack_Final_Enriched_1000_Delivery.csv   # Standardized 252-column output dataset
├── UniHack_Final_Enriched_1000_Delivery.xlsx  # Excel delivery workbook
├── Unihack_ Expected Output - Delivery Format.csv # Delivery schema reference
├── Unihack_ Sample Dataset - Input.csv           # Raw input dataset
└── README.md
```

---

## 📄 License
MIT License.
