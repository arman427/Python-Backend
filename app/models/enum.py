from enum import Enum


class Role(str, Enum):
    TEACHER = "TEACHER"
    STUDENT = "STUDENT"
    ADMIN = "ADMIN"


class LessonStatus(str, Enum):
    PLANNED = "PLANNED"
    ACTIVE = "ACTIVE"
    FINISHED = "FINISHED"


class AttendanceStatus(str, Enum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    LATE = "LATE"


class AttendanceMethod(str, Enum):
    SWIPE_MANUAL = "SWIPE_MANUAL"
    QR_TEACHER_SCANNED = "QR_TEACHER_SCANNED"
    QR_STUDENT_SCANNED = "QR_STUDENT_SCANNED"


class QRType(str, Enum):
    TEACHER_DYNAMIC = "TEACHER_DYNAMIC"
    STUDENT_STATIC = "STUDENT_STATIC"
