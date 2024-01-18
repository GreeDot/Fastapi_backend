from enum import unique, Enum as PyEnum

@unique
class RoleEnum(PyEnum):
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    MEMBER = "MEMBER"

@unique
class StatusEnum(PyEnum):
    ACTIVATE = "ACTIVATE"
    DISABLED = "DISABLED"

@unique
class GradeEnum(PyEnum):
    FREE = "FREE"
    BASIC = "BASIC"
    PREMIUM = "PREMIUM"

@unique
class LogTypeEnum(PyEnum):
    SENDTALK = "SENDTALK"
    RECEIVEDTALK = "RECEIVEDTALK"
    CLICKED = "CLICKED"