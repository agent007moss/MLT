import pytest


@pytest.mark.asyncio
async def test_register_verify_login_otp_session_flow(client):
    reg = await client.post(
        "/api/v1/auth/register",
        json={"email": "u@example.com", "username": "userx", "password": "securepassword1"},
    )
    assert reg.status_code == 200

    ver = await client.get("/api/v1/auth/verify-email", params={"email": "u@example.com"})
    assert ver.json()["verified"] is True

    login = await client.post(
        "/api/v1/auth/login", json={"username_or_email": "u@example.com", "password": "securepassword1"}
    )
    otp = login.json()["debug_otp"]

    token_resp = await client.post(
        "/api/v1/auth/verify-2fa", json={"username_or_email": "u@example.com", "code": otp}
    )
    access = token_resp.json()["access_token"]

    me = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {access}"})
    assert me.status_code == 200


@pytest.mark.asyncio
async def test_admin_bypass_toggle_non_prod(client):
    login = await client.post(
        "/api/v1/auth/login", json={"username_or_email": "admin@example.com", "password": "securepassword1"}
    )
    assert login.status_code == 200
    assert login.json()["mode"] == "tokens"
    assert "access_token" in login.json()
