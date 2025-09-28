import requests

def fetch_amazon_product(asin, country="US"):
    url = "https://real-time-amazon-data.p.rapidapi.com/product-details"
    headers = {
        "x-rapidapi-host": "real-time-amazon-data.p.rapidapi.com",
        "x-rapidapi-key": "b5add04a2amsh97b53fc17139a3ep11f058jsn6a762af25aea"
    }
    params = {"asin": asin, "country": country}
    try:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        return {
            "title": data.get("product_title", ""),
            "reviews": [r.get("review_text", "") for r in data.get("reviews", [])]
        }
    except Exception as e:
        return {"error": str(e)}
