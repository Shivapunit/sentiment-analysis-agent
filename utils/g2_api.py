import requests

def fetch_g2_vendors(query):
    url = "https://g2-products-reviews-users2.p.rapidapi.com/vendor/autocomplete"
    headers = {
        "x-rapidapi-host": "g2-products-reviews-users2.p.rapidapi.com",
        "x-rapidapi-key": "b5add04a2amsh97b53fc17139a3ep11f058jsn6a762af25aea"
    }
    try:
        response = requests.get(url, headers=headers, params={"Query": query})
        return response.json().get("vendors", [])
    except Exception as e:
        return {"error": str(e)}
