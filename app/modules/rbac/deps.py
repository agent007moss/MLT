from fastapi import Depends, HTTPException, status
from app.modules.auth.deps import get_current_user
from app.modules.rbac.policy import is_allowed


def require_permission(permission: str):
    async def dependency(user=Depends(get_current_user)):
        if not is_allowed(user.role, permission):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return user

    return dependency
