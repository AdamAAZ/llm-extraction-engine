from __future__ import annotations
from schemas import RentalSchema
from config import ConfidenceThresholds, PricePolicy, BedroomsRange, BathroomsRange
from issues import Issue

def validate_confidence(
    extracted_field,
    field_name: str,
    conf: ConfidenceThresholds = ConfidenceThresholds()
) -> list[Issue]:
    """
    Validates extracted field confidence against configured thresholds.
    
    Checks if confidence meets minimum standards and creates error or warning 
    issues if thresholds are not met.

    Args:
        extracted_field: The specific field to validate
        field_name (str): The name of the field
        conf (ConfidenceThresholds, optional): Configured confidence thresholds. 
            Defaults to ConfidenceThresholds().

    Returns:
        list[Issue]: List of issues related to confidence validation
    """
    issues: list[Issue] = []
    
    # Skip validation if field value is missing
    if extracted_field.value is None:
        return issues

    # Check confidence level against thresholds
    c = extracted_field.confidence
    if c < conf.error:
        # Confidence below error threshold
        issues.append(Issue(
            field=field_name,
            severity="error",
            message=(f"Error-level confidence ({c:.2f} < {conf.error}); manual review required.")
        ))
    elif c < conf.warn:
        # Confidence below warning threshold
        issues.append(Issue(
            field=field_name,
            severity="warning",
            message=(f"Low confidence ({c:.2f} < {conf.warn}); manual review recommended.")
        ))
    return issues

def validate_range(
    extracted_field,
    field_name: str,
    min_v: float,
    max_v: float
) -> list[Issue]:
    """
    Validates that extracted field value falls within acceptable range.

    Args:
        extracted_field: The field to be validated
        field_name (str): The name of the field
        min_v (float): Lower bound of valid range (inclusive)
        max_v (float): Upper bound of valid range (inclusive)

    Returns:
        list[Issue]: List of issues if value is outside range
    """
    issues: list[Issue] = []
    
    # Skip validation if field value is missing
    if extracted_field.value is None:
        return issues
    
    # Check if value is within acceptable range
    v = extracted_field.value
    if v < min_v or v > max_v:
        issues.append(Issue(
            field=field_name,
            severity="error",
            message=f"{field_name} {v} is outside expected range [{min_v}, {max_v}]."
        ))
    return issues


# Rental listing specific validators (thin wrappers around generic validators)

def validate_price(
    price_field,
    bedrooms_value: int | None,
    conf: ConfidenceThresholds = ConfidenceThresholds(),
    policy: PricePolicy = PricePolicy(),
) -> list[Issue]:
    issues: list[Issue] = []
    if price_field.value is None:
        return issues

    max_p = policy.max_for_bedrooms(bedrooms_value)

    issues.extend(validate_range(price_field, "price_monthly", policy.min_price, max_p))
    issues.extend(validate_confidence(price_field, "price_monthly", conf))
    return issues

def validate_bedrooms(
    beds_field,
    conf: ConfidenceThresholds = ConfidenceThresholds(),
    beds_range: BedroomsRange = BedroomsRange(),
) -> list[Issue]:
    """Validates bedroom count field against range and confidence thresholds."""
    issues: list[Issue] = []
    issues.extend(validate_range(beds_field, "bedrooms", beds_range.min, beds_range.max))
    issues.extend(validate_confidence(beds_field, "bedrooms", conf))
    return issues

def validate_bathrooms(
    baths_field,
    conf: ConfidenceThresholds = ConfidenceThresholds(),
    baths_range: BathroomsRange = BathroomsRange(),
) -> list[Issue]:
    """Validates bathroom count field against range and confidence thresholds."""
    issues: list[Issue] = []
    issues.extend(validate_range(baths_field, "bathrooms", baths_range.min, baths_range.max))
    issues.extend(validate_confidence(baths_field, "bathrooms", conf))
    return issues
    
def validate_string_field(
    string_field,
    field_name: str,
    conf: ConfidenceThresholds = ConfidenceThresholds()
) -> list[Issue]:
    """
    Validates string field against confidence thresholds.
    
    String fields are only validated for confidence; no range validation applied.
    
    Args:
        string_field: The string field to validate
        field_name (str): The name of the field
        conf (ConfidenceThresholds, optional): Confidence thresholds. 
            Defaults to ConfidenceThresholds().
    
    Returns:
        list[Issue]: List of confidence-related issues
    """
    return validate_confidence(string_field, field_name, conf)

def validate_rental(
    schema: RentalSchema,
    conf: ConfidenceThresholds = ConfidenceThresholds(),
    beds_range: BedroomsRange = BedroomsRange(),
    baths_range: BathroomsRange = BathroomsRange()
) -> list[Issue]:
    """
    Validates entire rental listing schema.
    
    Runs all field-specific validators and aggregates issues.

    Args:
        schema (RentalSchema): The extracted rental data to validate
        conf (ConfidenceThresholds, optional): Confidence thresholds. 
            Defaults to ConfidenceThresholds().
        price_range (PriceRange, optional): Valid price range. 
            Defaults to PriceRange().
        beds_range (BedroomsRange, optional): Valid bedroom count range. 
            Defaults to BedroomsRange().
        baths_range (BathroomsRange, optional): Valid bathroom count range. 
            Defaults to BathroomsRange().

    Returns:
        list[Issue]: Aggregated list of all validation issues found
    """
    issues = []
    issues.extend(validate_price(schema.price_monthly, schema.bedrooms.value, conf))
    issues.extend(validate_bedrooms(schema.bedrooms, conf, beds_range))
    issues.extend(validate_bathrooms(schema.bathrooms, conf, baths_range))
    issues.extend(validate_string_field(schema.address, "address", conf))
    issues.extend(validate_string_field(schema.utilities_text, "utilities_text", conf))
    return issues