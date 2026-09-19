\
\
\
\
   
import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.enrichment_engine import ProductEnrichmentEngine, DELIVERY_HEADERS

def run_batch_processing(input_csv_path: str, output_csv_path: str) -> Dict[str, Any]:
    print(f"Starting batch enrichment on: {input_csv_path}")
    engine = ProductEnrichmentEngine()

    if not os.path.exists(input_csv_path):
        raise FileNotFoundError(f"Input file not found: {input_csv_path}")

    enriched_rows = []
    category_counts = {}
    brand_counts = {}
    high_confidence_count = 0
    needs_review_count = 0

    with open(input_csv_path, mode="r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for idx, raw_row in enumerate(reader, start=1):
            enriched = engine.enrich_record(raw_row, index=idx)
            enriched_rows.append(enriched)

            dept = enriched.get("Dept", "Other")
            category_counts[dept] = category_counts.get(dept, 0) + 1
            
            brand = enriched.get("BRAND_NAME", "Unbranded")
            brand_counts[brand] = brand_counts.get(brand, 0) + 1

            if enriched.get("_NEEDS_REVIEW") == "Yes":
                needs_review_count += 1
            else:
                high_confidence_count += 1

            if idx % 200 == 0 or idx == 1000:
                print(f"  Processed {idx} records...")

    with open(output_csv_path, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=DELIVERY_HEADERS, extrasaction="ignore")
        writer.writeheader()
        for row in enriched_rows:
            writer.writerow(row)

    print(f"\nSuccessfully wrote {len(enriched_rows)} enriched rows to: {output_csv_path}")

    stats = {
        "total_records": len(enriched_rows),
        "total_columns": len(DELIVERY_HEADERS),
        "high_confidence_count": high_confidence_count,
        "needs_review_count": needs_review_count,
        "confidence_rate_pct": round((high_confidence_count / len(enriched_rows)) * 100, 2),
        "top_categories": sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:6],
        "top_brands": sorted(brand_counts.items(), key=lambda x: x[1], reverse=True)[:6]
    }

    return stats

if __name__ == "__main__":
    input_file = "Unihack_ Sample Dataset - Input.csv"
    output_file = "UniHack_Final_Enriched_1000_Delivery.csv"
    stats = run_batch_processing(input_file, output_file)
    print("\nBatch Run Summary:")
    print(json.dumps(stats, indent=2))
