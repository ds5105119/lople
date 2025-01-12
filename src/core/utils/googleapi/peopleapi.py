import requests


def get_google_userinfo(access_token: str):
    """
    Fetches user information from Google People API using the provided access

    Args:
        access_token (str): The OAuth2 access token for Google API authentication,
            which authorizes access to the user's profile information.

    Returns:
        dict: A JSON response containing the user's information retrieved from
            the Google People API.


    """
    url = "https://people.googleapis.com/v1/people/me"
    params = {
        "personFields": "names,emailAddresses,genders,birthdays,photos"
    }
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch user info: {response.status_code}, {response.text}")
