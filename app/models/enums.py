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
    GREE_TALK = "GREE_TALK"
    USER_TALK = "USER_TALK"


@unique
class FileTypeEnum(PyEnum):
    YAML = "YAML"
    GIF = 'GIF'
    IMG = 'IMG'


@unique
class EmotionTypeEnum(PyEnum):
    HAPPY = "HAPPY"
    UNHAPPY = "UNHAPPY"
