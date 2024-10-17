import requests
import httpx
from fastapi import HTTPException
from app.schema.pincode_details import pincode_get_response

response_data = []

async def get_location_details_by_pincode(pincode: str) -> dict:
    api_url = f"https://api.postalpincode.in/pincode/{pincode}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url)
            response = response.json()
        if response[0]["Status"] == "Success":
            status = True
            for each in response[0]["PostOffice"]:
                response_data.append(
                    pincode_get_response(country=each["Country"], state=each["State"], district=each["District"],
                                         location=each["Name"], pincode=each["Pincode"])
                )
        else:
            status = "Invalid"

    except requests.exceptions as e:
        status = "Error"
        status += "divide Error =>" + e

    return {"status": status, "data": response_data}