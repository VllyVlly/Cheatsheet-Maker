from parsing.jsonformat import ExtractedItem


def classify(client, md, model="gemini-3.6-flash"):
    response = client.models.generate_content(
        model=model,
        contents=f"Extract and classify content from this lecture material:\n\n{md}",
        config={
            "response_mime_type": "application/json",
            "response_schema": list[ExtractedItem],
        },
    )
    return response.parsed
