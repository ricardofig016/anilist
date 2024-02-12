from icecream import ic


def get_recommendations(user_data, media_data, preferences):
    recommendations = []

    # Array of ids of the media the user has given a score
    # The expected score will not be calculated for these media
    user_data_ids = [
        user_media["id"] for user_media in user_data if user_media["score"] != 0
    ]

    # Updated media_data without the media from user_data_ids
    media_data = [media for media in media_data if media["id"] not in user_data_ids]

    for media in media_data:
        expected_score = sum(calc_expected_scores(media, preferences).values())

        title = media["title"]["english"]
        if not title:
            title = media["title"]["romaji"]

        media_rec = {
            "id": media["id"],
            "title": title,
            "expectedScore": round(expected_score, 2),
            "media_info": media,
        }
        recommendations.append(media_rec)

    return sorted(recommendations, key=lambda x: x["expectedScore"], reverse=True)


def calc_expected_scores(media, preferences):
    expected_scores = {}

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

    for attribute in qualitative_attributes:
        if (
            preferences[attribute]
            and media[attribute]
            and media[attribute] in preferences[attribute]
        ):
            expected_score = preferences[attribute][media[attribute]]
            expected_scores[f"{attribute}.{media[attribute]}"] = expected_score

    for attribute in quantitative_attributes:
        if preferences[attribute] and media[attribute]:
            # Number used to divide the quantitative values in 2 preferences (median)
            pivot = int(next(iter(preferences[attribute]))[1:])
            if media[attribute] < pivot:
                expected_score = preferences[attribute][f"<{pivot}"]
                expected_scores[f"{attribute}.<{pivot}"] = expected_score
            else:
                expected_score = preferences[attribute][f">{pivot}"]
                expected_scores[f"{attribute}.>{pivot}"] = expected_score

    for attribute in list_attributes:
        if preferences[attribute] and media[attribute]:
            for media_list_element in media[attribute]:
                if media_list_element in preferences[attribute]:
                    expected_score = preferences[attribute][media_list_element]
                    expected_scores[f"{attribute}.{media_list_element}"] = (
                        expected_score
                    )

    for attribute in dict_attributes:
        if preferences[attribute] and media[attribute]:
            for media_dict in media[attribute]:
                if media_dict["name"] in preferences[attribute]:
                    rank = media_dict["rank"] / 100
                    expected_score = preferences[attribute][media_dict["name"]] * rank
                    expected_scores[f"{attribute}.{media_dict['name']}"] = (
                        expected_score
                    )

    weighted_expected_scores = calc_weighted_expected_scores(expected_scores)

    # Use this to get expected scores information about a media from an id
    if media["id"] == 0:
        ic(
            expected_scores,
            weighted_expected_scores,
            sum(weighted_expected_scores.values()),
        )

    return weighted_expected_scores


def calc_weighted_expected_scores(expected_scores):
    # Weights can be changed to favor certain attributes
    attribute_weights = [
        ("format", 1),
        ("source", 1),
        ("year", 1),
        ("episodes", 1),
        ("chapters", 1),
        ("averageScore", 1),
        ("popularity", 1),
        ("country", 1),
        ("studios", 1),
        ("type", 1),
        ("genres", 2),
        ("tags", 2),
    ]
    weighted_expected_scores = {}
    for attribute, weight in attribute_weights:
        attribute_expected_scores = [
            value for key, value in expected_scores.items() if key.startswith(attribute)
        ]
        if attribute_expected_scores:
            average = sum(attribute_expected_scores) / len(attribute_expected_scores)
            weighted_expected_scores[f"{attribute}"] = average * weight

    return weighted_expected_scores
