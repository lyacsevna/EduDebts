from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, Date, ForeignKey, func
from sqlalchemy.sql import select
import os
from datetime import date

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:19072004@localhost:5432/EduDebts")

engine = create_async_engine(DATABASE_URL)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()



# Models
class Faculty(Base):
    __tablename__ = "faculties"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

class Group(Base):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    faculty_id = Column(Integer, ForeignKey("faculties.id"), nullable=True)

class Subject(Base):
    __tablename__ = "subjects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    patronymic = Column(String, nullable=True)
    record_book_number = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)
    date_of_birth = Column(Date, nullable=True)

class Debt(Base):
    __tablename__ = "debts"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    reason = Column(String, nullable=True)
    date_occurred = Column(Date, nullable=True)
    status = Column(String, nullable=False, default="active")

# Базовая модель для факультета
class FacultyBase(BaseModel):
    name: str

# Базовая модель для группы
class GroupBase(BaseModel):
    name: str
    faculty_id: Optional[int]

# Базовая модель для предмета
class SubjectBase(BaseModel):
    name: str
    group_id: Optional[int]

# Базовая модель для студента
class StudentBase(BaseModel):
    first_name: str
    last_name: str
    patronymic: Optional[str] = None
    record_book_number: str
    phone: Optional[str] = None
    email: Optional[str] = None
    group_id: Optional[int] = None
    date_of_birth: Optional[date] = None

# Базовая модель для долга
class DebtBase(BaseModel):
    student_id: int
    subject_id: int
    reason: Optional[str] = None
    date_occurred: Optional[date] = None
    status: Optional[str] = "active"

# Модель для создания факультета
class FacultyCreate(FacultyBase):
    pass

# Модель для ответа по факультету
class FacultyResponse(FacultyBase):
    id: int

    class Config:
        orm_mode = True

# Модель для создания группы
class GroupCreate(GroupBase):
    pass

# Модель для ответа по группе
class GroupResponse(GroupBase):
    id: int

    class Config:
        orm_mode = True

# Модель для создания предмета
class SubjectCreate(SubjectBase):
    pass

# Модель для ответа по предмету
class SubjectResponse(SubjectBase):
    id: int

    class Config:
        orm_mode = True

# Модель для создания студента
class StudentCreate(StudentBase):
    pass

# Модель для ответа по студенту
class StudentResponse(StudentBase):
    id: int

    class Config:
        orm_mode = True

# Модель для создания долга
class DebtCreate(DebtBase):
    pass

# Модель для ответа по долгу
class DebtResponse(DebtBase):
    id: int

    class Config:
        orm_mode = True


# Groups endpoints
@app.post("/groups/", response_model=GroupResponse)
async def create_group(group: GroupCreate):
    async with async_session() as session:
        db_group = Group(**group.dict())
        session.add(db_group)
        await session.commit()
        await session.refresh(db_group)
        return db_group


@app.get("/groups/", response_model=List[GroupResponse])
async def read_groups():
    async with async_session() as session:
        result = await session.execute(select(Group))
        groups = result.scalars().all()
        return groups


@app.get("/groups/{group_id}", response_model=GroupResponse)
async def read_group(group_id: int):
    async with async_session() as session:
        group = await session.get(Group, group_id)
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        return group


@app.put("/groups/{group_id}", response_model=GroupResponse)
async def update_group(group_id: int, group: GroupCreate):
    async with async_session() as session:
        db_group = await session.get(Group, group_id)
        if not db_group:
            raise HTTPException(status_code=404, detail="Group not found")

        for key, value in group.dict().items():
            setattr(db_group, key, value)

        await session.commit()
        await session.refresh(db_group)
        return db_group


@app.delete("/groups/{group_id}")
async def delete_group(group_id: int):
    async with async_session() as session:
        group = await session.get(Group, group_id)
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")

        await session.delete(group)
        await session.commit()
        return {"message": "Group deleted"}


# Faculty endpoints
@app.post("/faculties/", response_model=FacultyResponse)
async def create_faculty(faculty: FacultyCreate):
    async with async_session() as session:
        db_faculty = Faculty(**faculty.dict())
        session.add(db_faculty)
        await session.commit()
        await session.refresh(db_faculty)
        return db_faculty

@app.get("/faculties/", response_model=List[FacultyResponse])
async def read_faculties():
    async with async_session() as session:
        result = await session.execute(select(Faculty))
        faculties = result.scalars().all()
        return faculties

@app.get("/faculties/{faculty_id}", response_model=FacultyResponse)
async def read_faculty(faculty_id: int):
    async with async_session() as session:
        faculty = await session.get(Faculty, faculty_id)
        if not faculty:
            raise HTTPException(status_code=404, detail="Faculty not found")
        return faculty

@app.put("/faculties/{faculty_id}", response_model=FacultyResponse)
async def update_faculty(faculty_id: int, faculty: FacultyCreate):
    async with async_session() as session:
        db_faculty = await session.get(Faculty, faculty_id)
        if not db_faculty:
            raise HTTPException(status_code=404, detail="Faculty not found")

        for key, value in faculty.dict().items():
            setattr(db_faculty, key, value)

        await session.commit()
        await session.refresh(db_faculty)
        return db_faculty


@app.delete("/faculties/{faculty_id}")
async def delete_faculty(faculty_id: int):
    async with async_session() as session:
        faculty = await session.get(Faculty, faculty_id)
        if not faculty:
            raise HTTPException(status_code=404, detail="Faculty not found")

        await session.delete(faculty)
        await session.commit()
        return {"message": "Faculty deleted"}


# Subject endpoints
@app.post("/subjects/", response_model=SubjectResponse)
async def create_subject(subject: SubjectCreate):
    async with async_session() as session:
        db_subject = Subject(**subject.dict())
        session.add(db_subject)
        await session.commit()
        await session.refresh(db_subject)
        return db_subject


@app.get("/subjects/", response_model=List[SubjectResponse])
async def read_subjects():
    async with async_session() as session:
        result = await session.execute(select(Subject))
        subjects = result.scalars().all()
        return subjects


@app.get("/subjects/{subject_id}", response_model=SubjectResponse)
async def read_subject(subject_id: int):
    async with async_session() as session:
        subject = await session.get(Subject, subject_id)
        if not subject:
            raise HTTPException(status_code=404, detail="Subject not found")
        return subject


@app.put("/subjects/{subject_id}", response_model=SubjectResponse)
async def update_subject(subject_id: int, subject: SubjectCreate):
    async with async_session() as session:
        db_subject = await session.get(Subject, subject_id)
        if not db_subject:
            raise HTTPException(status_code=404, detail="Subject not found")

        for key, value in subject.dict().items():
            setattr(db_subject, key, value)

        await session.commit()
        await session.refresh(db_subject)
        return db_subject


@app.delete("/subjects/{subject_id}")
async def delete_subject(subject_id: int):
    async with async_session() as session:
        subject = await session.get(Subject, subject_id)
        if not subject:
            raise HTTPException(status_code=404, detail="Subject not found")

        await session.delete(subject)
        await session.commit()
        return {"message": "Subject deleted"}


# Student endpoints
@app.post("/students/", response_model=StudentResponse)
async def create_student(student: StudentCreate):
    async with async_session() as session:
        db_student = Student(**student.dict())
        session.add(db_student)
        await session.commit()
        await session.refresh(db_student)
        return db_student


@app.get("/students/", response_model=List[StudentResponse])
async def read_students():
    async with async_session() as session:
        result = await session.execute(select(Student))
        students = result.scalars().all()
        return students


@app.get("/students/{student_id}", response_model=StudentResponse)
async def read_student(student_id: int):
    async with async_session() as session:
        student = await session.get(Student, student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        return student


@app.put("/students/{student_id}", response_model=StudentResponse)
async def update_student(student_id: int, student: StudentCreate):
    async with async_session() as session:
        db_student = await session.get(Student, student_id)
        if not db_student:
            raise HTTPException(status_code=404, detail="Student not found")

        for key, value in student.dict().items():
            setattr(db_student, key, value)

        await session.commit()
        await session.refresh(db_student)
        return db_student


@app.delete("/students/{student_id}")
async def delete_student(student_id: int):
    async with async_session() as session:
        student = await session.get(Student, student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        await session.delete(student)
        await session.commit()
        return {"message": "Student deleted"}


# Debt endpoints
@app.post("/debts/", response_model=DebtResponse)
async def create_debt(debt: DebtCreate):
    async with async_session() as session:
        db_debt = Debt(**debt.dict())
        session.add(db_debt)
        await session.commit()
        await session.refresh(db_debt)
        return db_debt


@app.get("/debts/", response_model=List[DebtResponse])
async def read_debts():
    async with async_session() as session:
        result = await session.execute(select(Debt))
        debts = result.scalars().all()
        return debts


@app.get("/debts/{debt_id}", response_model=DebtResponse)
async def read_debt(debt_id: int):
    async with async_session() as session:
        debt = await session.get(Debt, debt_id)
        if not debt:
            raise HTTPException(status_code=404, detail="Debt not found")
        return debt


@app.put("/debts/{debt_id}", response_model=DebtResponse)
async def update_debt(debt_id: int, debt: DebtCreate):
    async with async_session() as session:
        db_debt = await session.get(Debt, debt_id)
        if not db_debt:
            raise HTTPException(status_code=404, detail="Debt not found")

        for key, value in debt.dict().items():
            setattr(db_debt, key, value)

        await session.commit()
        await session.refresh(db_debt)
        return db_debt


@app.put("/debts/{debt_id}/settle")
async def settle_debt(debt_id: int):
    async with async_session() as session:
        db_debt = await session.get(Debt, debt_id)
        if not db_debt:
            raise HTTPException(status_code=404, detail="Debt not found")

        db_debt.status = "settled"
        await session.commit()
        await session.refresh(db_debt)
        return {"message": "Debt marked as settled"}


@app.delete("/debts/{debt_id}")
async def delete_debt(debt_id: int):
    async with async_session() as session:
        debt = await session.get(Debt, debt_id)
        if not debt:
            raise HTTPException(status_code=404, detail="Debt not found")

        await session.delete(debt)
        await session.commit()
        return {"message": "Debt deleted"}

# Reports endpoints
@app.get("/reports/debts_by_faculty")
async def debts_by_faculty():
    async with async_session() as session:
        # Здесь можно использовать более сложные запросы с joins
        result = await session.execute(
            select(Faculty.name, func.count(Debt.id))
            .join(Group, Faculty.id == Group.faculty_id, isouter=True)
            .join(Student, Group.id == Student.group_id, isouter=True)
            .join(Debt, Student.id == Debt.student_id, isouter=True)
            .group_by(Faculty.name)
        )
        return [{"faculty": row[0], "debt_count": row[1]} for row in result.all()]

@app.get("/reports/debts_by_group/{group_id}")
async def debts_by_group(group_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(Student.last_name, Student.first_name, func.count(Debt.id))
            .join(Debt, Student.id == Debt.student_id, isouter=True)
            .where(Student.group_id == group_id)
            .group_by(Student.last_name, Student.first_name)
        )
        return [{"student": f"{row[0]} {row[1]}", "debt_count": row[2]} for row in result.all()]

@app.get("/reports/student_debts/{student_id}")
async def student_debts(student_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(Subject.name, Debt.reason, Debt.date_occurred, Debt.status)
            .join(Debt, Debt.subject_id == Subject.id)
            .where(Debt.student_id == student_id)
        )
        return [{
            "subject": row[0],
            "reason": row[1],
            "date_occurred": row[2],
            "status": row[3]
        } for row in result.all()]

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)