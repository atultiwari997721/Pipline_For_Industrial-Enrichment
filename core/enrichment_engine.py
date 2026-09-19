\
\
\
   
import re
import csv
import os
import sys
from typing import Dict, List, Any, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.uom_standards import normalize_uom, decimal_to_trade_fraction, format_dimension_string
from core.unicat_taxonomy import resolve_brand, resolve_taxonomy

DELIVERY_HEADERS = [
    "MFR URL", "Ref URL 1", "Ref URL 2", "Ref URL 3", "Ref URL 4", "Ref URL 5",
    "PART_NUMBER", "Dept", "Class", "Fine", "SKU - MY_PART_NUMBER",
    "Mfg_Part_Num", "Part_Desc", "E1_Brand", "Unilog_Brand", "DIB_Brand", "Part_Manuf",
    "MANUFACTURER_NAME", "BRAND_NAME", "TRADE_NAME", "MANUFACTURER_PART_NUMBER",
    "ALTERNATE_PART_NUMBER", "Classpath", "MOBILE_DESC", "INVOICE_DESC",
    "SHORT_DESC", "LONG_DESC1", "RETAIL_DESC", "MARKETING_DESCRIPTION",
    "ITEM_FEATURES_1", "ITEM_FEATURES_2", "ITEM_FEATURES_3", "ITEM_FEATURES_4",
    "ITEM_FEATURES_5", "ITEM_FEATURES_6", "ITEM_FEATURES_7", "ITEM_FEATURES_8",
    "ITEM_FEATURES_9", "ITEM_FEATURES_10", "ITEM_FEATURES_11", "ITEM_FEATURES_12",
    "ITEM_FEATURES_13", "ITEM_FEATURES_14", "ITEM_FEATURES_15", "ITEM_FEATURES_16",
    "ITEM_FEATURES_17", "ITEM_FEATURES_18", "ITEM_FEATURES_19", "ITEM_FEATURES_20",
    "With", "Standard/Approvals", "Prop 65", "Application", "Includes", "Product Name"
]

for i in range(1, 51):
    DELIVERY_HEADERS.extend([f"ATTRIBUTE_LABEL {i}", f"ATTRIBUTE_VALUE {i}", f"ATTRIBUTE_UOM {i}"])

DELIVERY_HEADERS.extend([
    "UPC", "EAN", "GTIN", "UNSPSC", "Warranty", "List Price", "Selling Qty",
    "Selling UOM", "Standard Packaging Information", "LENGTH", "LENGTH_UOM",
    "HEIGHT", "HEIGHT_UOM", "WIDTH", "WIDTH_UOM", "WEIGHT", "WEIGHT_UOM",
    "VOLUME", "VOLUME_UOM", "Product Image", "Alternate Image 1", "Alternate Image 2",
    "Alternate Image 3", "Alternate Image 4", "SDS", "SDS_1", "Warranty Information",
    "Catalog", "Specification Sheet", "Instruction/Installation Manual",
    "Service Manual", "Owners/User Manual", "Line Drawing", "MTR", "RoHS",
    "Full Engineering Drawing", "Energy Star Guide", "Technical Bulletin",
    "Submittal", "Compatibility Chart", "Size Chart", "Product Label/Insert",
    "Video Link", "Video Link 1", "Country Of Origin", "Discontinued",
    "Actual Image (Yes/No)"
])

def clean_placeholders(val: Optional[str]) -> str:
                                                                                  
    if not val:
        return ""
    s = str(val).strip()
    if s in ["-- Unbranded --", "-- No Unilog Brand --", "-- No DIB Brand --", "-", "None", "null"]:
        return ""
    return s

class ProductEnrichmentEngine:
    def __init__(self):
        self.headers = DELIVERY_HEADERS

    def parse_attributes_from_description(self, mpn: str, desc: str, raw_manuf: str) -> Dict[str, Any]:
\
\
           
        extracted = {
            "series": "",
            "model": mpn,
            "grit": "",
            "dimension": "",
            "width": "",
            "length": "",
            "diameter": "",
            "pack_qty": "",
            "material": "",
            "color": "",
            "finish": "",
            "voltage": "",
            "amperage": "",
            "wash_cycles": "",
            "sound_level": "",
            "mounting": "",
            "approvals": "",
            "features": []
        }

        d_lower = desc.lower()

        grit_match = re.search(r'\b(p\d{2,4}|\d{2,4}\s*grit)\b', d_lower)
        if grit_match:
            g = grit_match.group(1).upper()
            extracted["grit"] = g
            extracted["features"].append(f"{g} Grit Rating for optimal surface preparation")

        dim_match = re.search(r'(\d+[\d/\.\-]*\s*["\']?\s*[xX]\s*\d+[\d/\.\-]*\s*["\']?)', desc)
        if dim_match:
            raw_dim = dim_match.group(1).strip()
            formatted_dim = format_dimension_string(raw_dim)
            extracted["dimension"] = formatted_dim
            extracted["features"].append(f"Dimensions: {formatted_dim}")
            
            parts = re.split(r'[xX]', raw_dim)
            if len(parts) == 2:
                w_str = parts[0].strip().replace('"', '')
                l_str = parts[1].strip().replace('"', '')
                extracted["width"] = f"{w_str} in"
                extracted["length"] = f"{l_str} in"
        else:
            dia_match = re.search(r'(\d+[\d/\.\-]*)\s*["\']\s*(?:dia|disc|\b)', desc)
            if dia_match:
                extracted["diameter"] = f"{dia_match.group(1).strip()} in"

        pack_match = re.search(r'(\d+)\s*(?:pc|disc/box|pk|pack|box|count)\b', d_lower)
        if pack_match:
            extracted["pack_qty"] = pack_match.group(1)
            extracted["features"].append(f"Package Quantity: {pack_match.group(1)}")

        if "cubitron ii" in d_lower or "cubitron" in d_lower:
            extracted["series"] = "Cubitron™ II"
            extracted["material"] = "Precision-Shaped Ceramic Grain"
        elif "diablo" in d_lower:
            extracted["series"] = "Diablo Series"
            extracted["material"] = "Premium Ceramic Blend"
        elif "hiolit" in d_lower:
            extracted["series"] = "HIOLIT Series"
            extracted["material"] = "Aluminum Oxide"
        elif "abranet" in d_lower:
            extracted["series"] = "Abranet Series"
            extracted["material"] = "Mesh Aluminum Oxide"
        elif "stikit" in d_lower:
            extracted["series"] = "Stikit™ 775L"
            extracted["material"] = "Film Backing"
        elif "professional" in d_lower:
            extracted["series"] = "Professional Series"
        elif "eco" in d_lower:
            extracted["series"] = "Eco Series"

        volt_match = re.search(r'(\d+)\s*v(?:olts?|ac)?\b', d_lower)
        if volt_match:
            extracted["voltage"] = volt_match.group(1)

        amp_match = re.search(r'(\d+)\s*a(?:mps?|mperes?)?\b', d_lower)
        if amp_match:
            extracted["amperage"] = amp_match.group(1)

        sound_match = re.search(r'(\d+)\s*(?:dba|db)\b', d_lower)
        if sound_match:
            extracted["sound_level"] = sound_match.group(1)

        cycle_match = re.search(r'(\d+)\s*(?:wash\s*cycle|cycles?)\b', d_lower)
        if cycle_match:
            extracted["wash_cycles"] = cycle_match.group(1)

        if "ss" in d_lower.split() or "sst" in d_lower.split() or "stainless" in d_lower:
            extracted["material"] = "Stainless Steel"
            extracted["finish"] = "Stainless Steel"
            extracted["color"] = "Stainless Steel"
        elif "brass" in d_lower or "brs" in d_lower:
            extracted["material"] = "Brass"
        elif "pvc" in d_lower:
            extracted["material"] = "PVC"

        if "cleanboost" in d_lower:
            extracted["features"].append("CleanBoost™ Technology for deep sanitization")
        if "leak detection" in d_lower:
            extracted["features"].append("Integrated Leak Detection System")
        if "3rd rack" in d_lower or "third rack" in d_lower:
            extracted["features"].append("Dedicated 3rd Rack for extra utensil capacity")

        return extracted

    def build_invoice_desc(self, taxonomy: dict, brand: dict, mpn: str, desc: str, attrs: dict) -> str:
\
\
           
        prod_abbr = taxonomy["fine"].upper()
        if "DISHWASHER" in prod_abbr:
            prod_abbr = "DISHWASHER"
        elif "SANDING BELTS" in prod_abbr or "SANDING BELT" in prod_abbr:
            prod_abbr = "SND BLT"
        elif "FILM DISCS" in prod_abbr or "SANDING DISCS" in prod_abbr:
            prod_abbr = "SND DISC"

        specs = []
        if attrs.get("mounting"):
            specs.append(attrs["mounting"].upper())
        if attrs.get("wash_cycles"):
            specs.append(f"{attrs['wash_cycles']}")
        if attrs.get("grit"):
            specs.append(attrs["grit"])
        if attrs.get("dimension"):
            d_clean = attrs["dimension"].replace(" in", "").replace(" ", "").upper()
            specs.append(d_clean)
        elif attrs.get("diameter"):
            specs.append(attrs["diameter"].replace(" in", "IN").upper())
        if attrs.get("finish") == "Stainless Steel" or "ss" in desc.lower():
            specs.append("SST")
        if attrs.get("voltage"):
            specs.append(f"{attrs['voltage']}V")
        if attrs.get("amperage"):
            specs.append(f"{attrs['amperage']}A")
        if attrs.get("sound_level"):
            specs.append(f"{attrs['sound_level']}DBA")
        if attrs.get("pack_qty"):
            specs.append(f"{attrs['pack_qty']}PK")

        inv = f"{prod_abbr} {' '.join(specs)}".strip()
        if len(inv) > 40:
            inv = inv[:40]
        return inv.upper()

    def build_mobile_desc(self, brand: dict, taxonomy: dict, mpn: str, attrs: dict) -> str:
\
\
           
        parts = [brand["mfr_name"].replace(", Inc.", "").replace(" Company", "").strip(), brand["brand_name"].replace("®", "").replace("™", "")]
        parts.append(taxonomy["product_name"])
        if attrs.get("series"):
            parts.append(attrs["series"])
        parts.append(mpn)
        if attrs.get("grit"):
            parts.append(attrs["grit"])
        if attrs.get("dimension"):
            parts.append(attrs["dimension"])

        mobile = ", ".join([p for p in parts if p])
        if len(mobile) > 80:
            mobile = mobile[:77] + "..."
        elif len(mobile) < 60:
                                                        
            mobile = f"{mobile}, {taxonomy['class_name']}"
            if len(mobile) > 80:
                mobile = mobile[:80]
        return mobile

    def build_short_desc(self, brand: dict, taxonomy: dict, mpn: str, attrs: dict) -> str:
\
\
           
        parts = [brand["brand_name"]]
        if attrs.get("series"):
            parts.append(attrs["series"])
        parts.append(mpn)
        parts.append(taxonomy["product_name"])

        specs = []
        if attrs.get("grit"):
            specs.append(f"{attrs['grit']} Grit")
        if attrs.get("dimension"):
            specs.append(attrs["dimension"])
        elif attrs.get("diameter"):
            specs.append(f"{attrs['diameter']} Dia")
        if attrs.get("finish"):
            specs.append(attrs["finish"])
        if attrs.get("pack_qty"):
            specs.append(f"{attrs['pack_qty']}-Pack")

        if specs:
            parts.append(", ".join(specs))

        return " ".join([p for p in parts if p])

    def build_long_desc(self, brand: dict, taxonomy: dict, mpn: str, attrs: dict) -> str:
\
\
           
        items = [f"{brand['brand_name']} {taxonomy['product_name']}"]
        if attrs.get("series"):
            items.append(attrs["series"])
        if attrs.get("grit"):
            items.append(f"{attrs['grit']} Grit")
        if attrs.get("material"):
            items.append(attrs["material"])
        if attrs.get("dimension"):
            items.append(attrs["dimension"])
        if attrs.get("voltage"):
            items.append(f"{attrs['voltage']} V")
        if attrs.get("amperage"):
            items.append(f"{attrs['amperage']} A")
        if attrs.get("sound_level"):
            items.append(f"{attrs['sound_level']} dBA Sound Level")
        if attrs.get("finish"):
            items.append(attrs["finish"])
        if attrs.get("pack_qty"):
            items.append(f"Package of {attrs['pack_qty']}")

        return ", ".join([it for it in items if it])

    def enrich_record(self, raw_row: Dict[str, Any], index: int = 1) -> Dict[str, Any]:
\
\
           
        mpn = clean_placeholders(raw_row.get("Mfg_Part_Num", ""))
        desc = clean_placeholders(raw_row.get("Part_Desc", ""))
        e1_brand = clean_placeholders(raw_row.get("E1_Brand", ""))
        unilog_brand = clean_placeholders(raw_row.get("Unilog_Brand", ""))
        dib_brand = clean_placeholders(raw_row.get("DIB_Brand", ""))
        part_manuf = clean_placeholders(raw_row.get("Part_Manuf", ""))

        brand_info = resolve_brand(part_manuf, desc, e1_brand)
        tax_info = resolve_taxonomy(desc)
        attrs = self.parse_attributes_from_description(mpn, desc, part_manuf)

        invoice_desc = self.build_invoice_desc(tax_info, brand_info, mpn, desc, attrs)
        mobile_desc = self.build_mobile_desc(brand_info, tax_info, mpn, attrs)
        short_desc = self.build_short_desc(brand_info, tax_info, mpn, attrs)
        long_desc = self.build_long_desc(brand_info, tax_info, mpn, attrs)
        retail_desc = short_desc
        marketing_desc = f"Engineered for heavy-duty industrial and commercial applications, the {brand_info['brand_name']} {mpn} delivers superior durability, precision performance, and maximum uptime."

        clean_mpn_url = re.sub(r'[^a-zA-Z0-9_\-]', '', mpn)
        mfr_url = brand_info["mfr_url_template"].format(mpn=clean_mpn_url) if brand_info.get("mfr_url_template") else ""
        brand_clean_slug = re.sub(r'[^a-zA-Z0-9]', '', brand_info['brand_name'].replace("®", "").replace("™", "").upper())

        out = {h: "" for h in self.headers}

        out["MFR URL"] = mfr_url
        out["PART_NUMBER"] = str(20000000 + index)
        out["Dept"] = tax_info["dept"]
        out["Class"] = tax_info["class_name"]
        out["Fine"] = tax_info["fine"]
        out["SKU - MY_PART_NUMBER"] = str(1500000 + index)
        out["Mfg_Part_Num"] = mpn
        out["Part_Desc"] = desc
        out["E1_Brand"] = raw_row.get("E1_Brand", "-- Unbranded --")
        out["Unilog_Brand"] = raw_row.get("Unilog_Brand", "-- No Unilog Brand --")
        out["DIB_Brand"] = raw_row.get("DIB_Brand", "-- No DIB Brand --")
        out["Part_Manuf"] = raw_row.get("Part_Manuf", "")
        out["MANUFACTURER_NAME"] = brand_info["mfr_name"]
        out["BRAND_NAME"] = brand_info["brand_name"]
        out["MANUFACTURER_PART_NUMBER"] = mpn
        out["Classpath"] = tax_info["classpath"]
        out["MOBILE_DESC"] = mobile_desc
        out["INVOICE_DESC"] = invoice_desc
        out["SHORT_DESC"] = short_desc
        out["LONG_DESC1"] = long_desc
        out["RETAIL_DESC"] = retail_desc
        out["MARKETING_DESCRIPTION"] = marketing_desc

        for f_idx, feat in enumerate(attrs["features"][:20], start=1):
            out[f"ITEM_FEATURES_{f_idx}"] = feat

        out["Product Name"] = tax_info["product_name"]
        out["UNSPSC"] = tax_info["unspsc"]
        out["Selling Qty"] = "1"
        out["Selling UOM"] = "EA"

        attr_triplets = []
        if attrs.get("series"):
            attr_triplets.append(("Series", attrs["series"], ""))
        if attrs.get("model"):
            attr_triplets.append(("Model", attrs["model"], ""))
        if attrs.get("grit"):
            attr_triplets.append(("Grit", attrs["grit"], ""))
        if attrs.get("dimension"):
            attr_triplets.append(("Size", attrs["dimension"], ""))
        if attrs.get("diameter"):
            attr_triplets.append(("Diameter", attrs["diameter"].replace(" in", ""), "in"))
        if attrs.get("width"):
            attr_triplets.append(("Width", attrs["width"].replace(" in", ""), "in"))
        if attrs.get("length"):
            attr_triplets.append(("Length", attrs["length"].replace(" in", ""), "in"))
        if attrs.get("pack_qty"):
            attr_triplets.append(("Package Quantity", attrs["pack_qty"], "pk"))
        if attrs.get("material"):
            attr_triplets.append(("Material", attrs["material"], ""))
        if attrs.get("finish"):
            attr_triplets.append(("Finish", attrs["finish"], ""))
        if attrs.get("voltage"):
            attr_triplets.append(("Voltage Rating", attrs["voltage"], "V"))
        if attrs.get("amperage"):
            attr_triplets.append(("Amperage Rating", attrs["amperage"], "A"))
        if attrs.get("sound_level"):
            attr_triplets.append(("Sound Level", attrs["sound_level"], "dBA"))
        if attrs.get("wash_cycles"):
            attr_triplets.append(("Number of Wash Cycles", attrs["wash_cycles"], ""))

        for a_idx, (label, val, uom) in enumerate(attr_triplets[:50], start=1):
            out[f"ATTRIBUTE_LABEL {a_idx}"] = label
            out[f"ATTRIBUTE_VALUE {a_idx}"] = val
            out[f"ATTRIBUTE_UOM {a_idx}"] = uom

        out["Product Image"] = f"{brand_clean_slug}_{clean_mpn_url}.jpg"
        out["Alternate Image 1"] = f"{brand_clean_slug}_{clean_mpn_url}_1.jpg"
        out["Alternate Image 2"] = f"{brand_clean_slug}_{clean_mpn_url}_2.jpg"
        out["Specification Sheet"] = f"{brand_clean_slug}_{clean_mpn_url}_Specification_Sheet.pdf"
        out["Instruction/Installation Manual"] = f"{brand_clean_slug}_{clean_mpn_url}_Installation_Manual.pdf"
        out["Actual Image (Yes/No)"] = "Yes"

        confidence = 100
        review_reasons = []
        if len(invoice_desc) > 40:
            confidence -= 20
            review_reasons.append("Invoice description exceeds 40 chars")
        if not attrs.get("grit") and not attrs.get("dimension") and not attrs.get("voltage"):
            confidence -= 15
            review_reasons.append("Low extracted attribute density")
        if brand_info["mfr_name"] == "Generic Industrial":
            confidence -= 25
            review_reasons.append("Unresolved brand entity")

        out["_CONFIDENCE_SCORE"] = max(confidence, 45)
        out["_NEEDS_REVIEW"] = "Yes" if confidence < 75 else "No"
        out["_REVIEW_REASONS"] = "; ".join(review_reasons) if review_reasons else "All rules satisfied"

        return out
