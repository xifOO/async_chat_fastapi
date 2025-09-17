from pydantic import BaseModel


class UserToRoleBase(BaseModel):
    user_id: int
    role_id: int 


class UserToRoleCreate(UserToRoleBase): ...


class UserToRoleUpdate(UserToRoleBase): ...