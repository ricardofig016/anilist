from icecream import ic


def get_preferences(user_data, media_data):
    preferences = {}

    qualitative_attributes = ["type", "format", "country", "source"]
    quantitative_attributes = [
        "year",
        "episodes",
        "chapters",
        "averageScore",
        "popularity",
    ]
    list_attributes = ["genres", "studios"]
    dict_attributes = ["tags"]

    for attribute in qualitative_attributes + quantitative_attributes:
        # ic(attribute)
        values = []
        scores = []
        for entry in user_data:
            value = find_value_from_id(entry["id"], attribute, media_data)
            score = entry["score"]
            if value and score > 0:
                # ic(value, score)
                values.append(value)
                scores.append(score)
        if attribute in qualitative_attributes:
            # for key, value in get_qualitative_preference(values, scores).items():
            #    preferences[f"{attribute}.{key}"] = value
            preferences[attribute] = get_qualitative_preference(values, scores)
        else:
            preferences[attribute] = get_quantitative_preference(values, scores)
    return preferences


def find_value_from_id(id, key, media_data):
    # binary search
    low, high = 0, len(media_data) - 1

    while low <= high:
        mid = (low + high) // 2
        mid_entry = media_data[mid]

        if mid_entry["id"] == id:
            return mid_entry[key]
        elif mid_entry["id"] < id:
            low = mid + 1
        else:
            high = mid - 1

    return None


def get_qualitative_preference(values, scores):
    if len(values) == 0:  # len(values)==len(scores)
        return {}

    min_score = min(scores)
    max_score = max(scores)
    score_range = max_score - min_score

    if score_range == 0:
        return {}

    preference = {value: 0 for value in values}
    for value, score in zip(values, scores):
        score_index = (score - min_score) / score_range * 2 - 1
        preference[value] += score_index

    for key, value in preference.items():
        preference[key] = round(preference[key] / values.count(key), 2)

    return preference


def get_quantitative_preference(values, scores):
    if len(values) < 2:
        return {}

    sorted_values = sorted(values)
    n = len(values)
    median = (
        (sorted_values[(n // 2) - 1] + sorted_values[n // 2]) / 2
        if n % 2 == 0
        else sorted_values[n // 2]
    )
    median = int(round(median, 0))

    qualitative_values = [
        f"<{median}" if value < median else f">{median}" for value in values
    ]

    return get_qualitative_preference(qualitative_values, scores)


if __name__ == "__main__":
    pass
