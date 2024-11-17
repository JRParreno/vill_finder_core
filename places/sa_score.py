def get_sa_score(value: float) -> str:
   # Validate input value: it should be between 0 and 5, inclusive.
    if not (0 <= value <= 5):
        return "Invalid input, must be equal or greater than zero and less than or equal to 5"

    
    # Define the ranges and corresponding string values
    ranges = [
        (4.5, 5.0, "Very Positive"),
        (3.5, 4.5, "Positive"),
        (2.5, 3.5, "Neutral"),
        (1.5, 2.5, "Negative"),
        (0.0, 1.5, "Very Negative")
    ]
    
    # Check the value against the defined ranges
    for low, high, sentiment in ranges:
        if low <= value <= high:
            return sentiment
