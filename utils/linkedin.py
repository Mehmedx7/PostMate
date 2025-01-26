import requests
from config import LINKEDIN_CLIENT_ID, LINKEDIN_CLIENT_SECRET, LINKEDIN_REDIRECT_URI

# Step 1: Generate Authorization URL
def get_linkedin_auth_url():
    return f"https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id={LINKEDIN_CLIENT_ID}&redirect_uri={LINKEDIN_REDIRECT_URI}&scope=w_member_social"

# Step 2: Exchange Code for Access Token
def get_linkedin_access_token(code):
    url = "https://www.linkedin.com/oauth/v2/accessToken"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": LINKEDIN_REDIRECT_URI,
        "client_id": LINKEDIN_CLIENT_ID,
        "client_secret": LINKEDIN_CLIENT_SECRET
    }
    response = requests.post(url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(f"Failed to get access token: {response.text}")

# Step 3: Post to LinkedIn
def post_to_linkedin(content, image_path=None, access_token=None):
    if not access_token:
        raise Exception("Access token is required to post to LinkedIn.")

    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "author": "urn:li:person:YOUR_LINKEDIN_USER_ID",  # Replace with your LinkedIn URN
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": content
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    if image_path:
        # Upload image to LinkedIn
        media_url = "https://api.linkedin.com/v2/assets?action=registerUpload"
        media_payload = {
            "registerUploadRequest": {
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                "owner": "urn:li:person:YOUR_LINKEDIN_USER_ID",  # Replace with your LinkedIn URN
                "serviceRelationships": [
                    {
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent"
                    }
                ]
            }
        }
        media_response = requests.post(media_url, headers=headers, json=media_payload)
        if media_response.status_code != 200:
            raise Exception(f"Failed to register image upload: {media_response.text}")

        upload_url = media_response.json()["value"]["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
        asset_id = media_response.json()["value"]["asset"]

        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
        upload_response = requests.put(upload_url, data=image_data)
        if upload_response.status_code != 201:
            raise Exception(f"Failed to upload image: {upload_response.text}")

        payload["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "IMAGE"
        payload["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [
            {
                "status": "READY",
                "description": {
                    "text": "Image description"
                },
                "media": asset_id,
                "title": {
                    "text": "Image title"
                }
            }
        ]

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 201:
        raise Exception(f"Failed to post to LinkedIn: {response.text}")
    print("Posted to LinkedIn successfully!")