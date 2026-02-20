from app.modules.rbac.policy import is_allowed


def test_owner_can_do_anything():
    assert is_allowed("OWNER", "any:permission")


def test_admin_permissions_are_limited():
    assert is_allowed("ADMIN", "settings:write")
    assert not is_allowed("ADMIN", "unknown:dangerous")


def test_user_least_privilege():
    assert is_allowed("USER", "dashboard:write_own")
    assert not is_allowed("USER", "settings:write")
