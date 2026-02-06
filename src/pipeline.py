import json
from typing import Iterable
from openai import OpenAI
import instructor
from schemas import RentalSchema
from validation import validate_rental
from issues import sort_issues, is_valid
from dotenv import load_dotenv
import argparse
import os
load_dotenv()

def extract_one(client, text: str) -> RentalSchema:
    """
    Extract rental schema fields from text using GPT.
    
    Args:
        client: Instructor-wrapped OpenAI client
        text: Input text to extract rental information from
        
    Returns:
        RentalSchema: Extracted rental data
    """
    return client.chat.completions.create(
        model="gpt-5-nano",
        messages=[
            {"role": "system", "content": "Extract the fields defined in the schema from the text."},
            {"role": "user", "content": text}
        ],
        response_model=RentalSchema
    )
    
def run_pipeline(texts: Iterable[str]) -> list[dict]:
    """
    Process multiple rental listing texts through extraction and validation pipeline.
    
    Args:
        texts: Iterable of rental listing texts
        
    Returns:
        list[dict]: List of results with extracted data and validation issues
    """
    client = instructor.from_openai(OpenAI())
    results: list[dict] = []
    
    # Process each text and collect results
    for idx, text in enumerate(texts, start=1):
        schema = extract_one(client, text)
        issues = sort_issues(validate_rental(schema))
        results.append({
            "id": idx,
            "text": text,
            "valid": is_valid(issues),
            "issues": [i.__dict__ for i in issues],
            "extracted": schema.model_dump(),
        })
        
    return results

def load_listings_from_txt(path: str) -> list[str]:
    """  
    Loads listings from a text file.
    Listings are seperated by one or more lines
    """
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()
        
    listings = [block.strip() for block in raw.split("\n\n") if block.strip()]
    return listings
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LLM extraction + deterministic validation pipeline")
    parser.add_argument("--in", dest="in_path", default=os.path.join("examples", "listings.txt"),
                        help="Path to input .txt file (listings separated by blank lines)")
    parser.add_argument("--out", dest="out_path", default=os.path.join("out", "out.json"),
                        help="Path to output JSON file")
    args = parser.parse_args()

    texts = load_listings_from_txt(args.in_path)
    out = run_pipeline(texts)

    os.makedirs(os.path.dirname(args.out_path), exist_ok=True)
    with open(args.out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print(f"Wrote {args.out_path}")
    print("Total listings:", len(out))
    print("Valid:", sum(1 for r in out if r["valid"]))
    print("With issues:", sum(1 for r in out if len(r["issues"]) > 0))