import enum


class PlanEnum(enum.Enum):
    free = "free"
    pro = "pro"


class TypeTokensEnum(enum.Enum):
    email_verify = "email_verify"
    access = "access"
