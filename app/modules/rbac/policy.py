ROLE_PERMISSIONS: dict[str, set[str]] = {
    "OWNER": {"*"},
    "ADMIN": {
        "settings:read",
        "settings:write",
        "audit:read",
        "personnel:read",
        "personnel:write",
        "org:read",
        "org:write",
    },
    "USER": {
        "settings:read_own",
        "dashboard:write_own",
        "personnel:read",
        "org:read",
    },
}


def is_allowed(role: str, permission: str) -> bool:
    perms = ROLE_PERMISSIONS.get(role.upper(), set())
    return "*" in perms or permission in perms
