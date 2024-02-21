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

@unique
class VoiceTypeEnum(PyEnum):
    NWOOF = 'nwoof'
    NJONGHYUN = 'njonghyun'
    VDONGHYUN = 'vdonghyun'
    NMAMMON = 'nmammon'
    NGARAM = 'ngaram'
    NMEOW = 'nmeow'
    NIHYUN = 'nihyun'
    VYUNA = 'vyuna'
    VHYERI = 'vhyeri'
    NHAJUN = 'nhajun'
    NJAEWOOK = 'njaewook'
    NJOONYOUNG = 'njoonyoung'
    VDAESEONG = 'vdaeseong'
    VIAN = 'vian'
    NKYUWON = 'nkyuwon'
    VDAIN = 'vdain'
    NDAIN = 'ndain'
    NMINSEO = 'nminseo'
    NBORA = 'nbora'
    NJIWON = 'njiwon'
    VGOEUN = 'vgoeun'
    NTIFFANY = 'ntiffany'
