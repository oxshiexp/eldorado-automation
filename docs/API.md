# Eldorado.gg Seller API Documentation

## Overview
Eldorado.gg provides a Seller API for automating listings, pricing, and delivery. This document covers the API integration used in this automation tool.

## Getting API Access

1. **Become a Verified Seller**
   - Visit: https://www.eldorado.gg/become-seller
   - Complete verification process
   - Access seller dashboard

2. **Generate API Key**
   - Navigate to Settings > API Access
   - Click "Generate New API Key"
   - Save your key securely (it won't be shown again)

## API Endpoints

### Base URL
```
https://api.eldorado.gg/v1
```

### Authentication
All requests require Bearer token authentication:
```
Authorization: Bearer YOUR_API_KEY
```

### Key Endpoints

#### 1. Create Listing
```http
POST /listings
Content-Type: application/json

{
  "game": "osrs",
  "category": "gold",
  "server": "Any",
  "price_per_unit": 0.45,
  "stock": 1000,
  "min_quantity": 10,
  "max_quantity": 10000,
  "delivery_time": "1-15 minutes",
  "description": "Fast delivery, 24/7 available"
}
```

#### 2. Update Listing
```http
PUT /listings/{listing_id}
Content-Type: application/json

{
  "price_per_unit": 0.42,
  "stock": 1500
}
```

#### 3. Bulk Upload
```http
POST /listings/bulk
Content-Type: application/json

{
  "listings": [
    {...},
    {...}
  ]
}
```

#### 4. Get Listings
```http
GET /listings?game=osrs&status=active
```

#### 5. Delete Listing
```http
DELETE /listings/{listing_id}
```

## Rate Limits

- **Standard tier**: 100 requests/minute
- **Premium tier**: 500 requests/minute
- **Bulk operations**: Up to 100 items per request

## Error Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Invalid API key |
| 403 | Forbidden - Insufficient permissions |
| 429 | Rate limit exceeded |
| 500 | Server error |

## Best Practices

1. **Rate Limiting**
   - Implement exponential backoff for 429 errors
   - Use bulk endpoints when possible
   - Cache frequently accessed data

2. **Error Handling**
   - Always validate responses
   - Log errors for debugging
   - Retry failed requests with backoff

3. **Data Validation**
   - Verify prices are within market range
   - Check stock levels before posting
   - Validate game/server combinations

## Example Integration

```python
import requests

class EldoradoAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.eldorado.gg/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def create_listing(self, listing_data):
        response = requests.post(
            f"{self.base_url}/listings",
            json=listing_data,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def bulk_upload(self, listings):
        response = requests.post(
            f"{self.base_url}/listings/bulk",
            json={"listings": listings},
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
```

## Support

- API Documentation: https://docs.eldorado.gg/api
- Support Email: support@eldorado.gg
- Discord: https://discord.gg/eldorado

## Notes

⚠️ **Important**: This is a reference implementation. Actual API endpoints may vary. Please refer to official Eldorado.gg documentation for the most up-to-date information.

The automation scripts in this repository are designed to work with the Seller API once you have proper access.
