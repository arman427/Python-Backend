from enum import Enum


class Role(Enum):
    TEACHER = "TEACHER"
    STUDENT = "STUDENT"
    ADMIN = "ADMIN"


class LessonStatus(Enum):
    PLANNED = "PLANNED"
    ACTIVE = "ACTIVE"
    FINISHED = "FINISHED"


class AttendanceStatus(Enum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    LATE = "LATE"


class AttendanceMethod(Enum):
    SWIPE_MANUAL = "SWIPE_MANUAL"
    QR_TEACHER_SCANNED = "QR_TEACHER_SCANNED"
    QR_STUDENT_SCANNED = "QR_STUDENT_SCANNED"


class QRType(Enum):
    TEACHER_DYNAMIC = "TEACHER_DYNAMIC"
    STUDENT_STATIC = "STUDENT_STATIC"
