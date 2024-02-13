# API Documentation
API Documentation for TapRx's API located at `https://taprx.xyz/`
## Table of Contents
- [User Management](#user-management)
  - [Create User](#create-user)
  - [Update User](#update-user)

# User Management
## Create User:
Creates a new user with the provided user metadata.
- ### URL
    /users/
- ### Method
    `POST`
- ### URL Params
    None
- ### Data Params
    ```json
    {
        "user_id": "string (required)",
        "first_name": "string (required)",
        "last_name": "string (required)",
        "phone": "string (optional)"
    }
    ```
- ### Headers
    - "Authorization": "Bearer {Your ID token}" (required)
- ### Success Response
    - #### Code: 201
      - #### Content:
          ```json
          {
              "message": "User created successfully",
              "user": {
                "user_id": "string",
                "first_name": "string",
                "last_name": "string",
                "phone": ["string", "null"]
              }
          }
          ```
- ### Error Response
  - #### Code: 400
    - #### Content:
      ```json
      {
          "message": ["Invalid request", "User already exists"]
      }
      ```
  - #### Code: 401
    - #### Content:
      ```json
      {
          "message": "Authorization header is missing"
      }
      ```
       
  - #### Code: 403
    - #### Content:
      ```json
      {
          "message": ["Insufficient permissions", "ID token has expired", "ID token has been revoked", "Invalid ID token"]
      } 
      ```
  - #### Code: 500
    - #### Content:
      ```json
      {
          "message": "Internal server error"
      }
      ```
- ### Sample Call
  ```
  curl -X POST \
  https://taprx.xyz/users/ \
  -H 'Authorization: Bearer {Your ID token}' \
  -H 'Content-Type: application/json' \
  -d '{
        "user_id": "your_user_id",
        "first_name": "John",
        "last_name": "Doe",
        "phone": "+1234567890"
    }'
  ```

## Update User:
Updates a user with the provided user metadata.
- ### URL
    /users/{user_id}
- ### Method
    `PUT`
- ### URL Params
    - 'user_id': The unique identifier of the user to be updated (required)
- ### Data Params
    ```json
    {
        "first_name": "string (optional)",
        "last_name": "string (optional)",
        "phone": "string (optional)"
    }
    ```
- ### Headers
    - "Authorization": "Bearer {Your ID token}" (required)
- ### Success Response
    - #### Code: 200
      - #### Content:
          ```json
          {
              "message": "User updated successfully",
              "updated user data": {
                "first_name": "string (optional)",
                "last_name": "string (optional)",
                "phone": "string (optional)"
              }
          }
          ```
- ### Error Response
  - #### Code: 401
    - #### Content:
      ```json
      {
          "message": "Authorization header is missing"
      }
      ```
  - #### Code: 403
    - #### Content:
      ```json
      {
          "message": ["Insufficient permissions", "ID token has expired", "ID token has been revoked", "Invalid ID token"]
      } 
      ```
  - #### Code: 404
    - #### Content:
      ```json
      {
          "message": ["User not found"]
      }
      ```
  - #### Code: 500
    - #### Content:
      ```json
      {
          "message": "Internal server error"
      }
      ```
- ### Sample Call
  ```
  curl -X PUT \
  https://taprx.xyz/users/{user_id} \
  -H 'Authorization: Bearer {Your ID token}' \
  -H 'Content-Type: application/json' \
  -d '{
        "first_name": "new john",
        "phone": "+1234567890"
    }'
  ```