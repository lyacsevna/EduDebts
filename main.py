# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import asyncpg
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

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:19072004@localhost:5432/EduDebts")

async def get_db_conn():
    return await asyncpg.connect(DATABASE_URL)

# Pydantic models
class FacultyCreate(BaseModel):
    name: str

class Faculty(FacultyCreate):
    id: int

class GroupCreate(BaseModel):
    name: str
    faculty_id: Optional[int]

class Group(GroupCreate):
    id: int

class SubjectCreate(BaseModel):
    name: str
    group_id: Optional[int]

class Subject(SubjectCreate):
    id: int

class StudentCreate(BaseModel):
    first_name: str
    last_name: str
    patronymic: Optional[str] = None
    record_book_number: str
    phone: Optional[str] = None
    email: Optional[str] = None
    group_id: Optional[int] = None
    date_of_birth: Optional[date] = None

class Student(StudentCreate):
    id: int

class DebtCreate(BaseModel):
    student_id: int
    subject_id: int
    reason: Optional[str] = None
    date_occurred: Optional[date] = None
    status: Optional[str] = "active"

class Debt(DebtCreate):
    id: int

# Faculties endpoints
@app.post("/faculties/", response_model=Faculty)
async def create_faculty(faculty: FacultyCreate):
    conn = await get_db_conn()
    try:
        faculty_id = await conn.fetchval(
            "INSERT INTO faculties (name) VALUES ($1) RETURNING id",
            faculty.name
        )
        return {**faculty.dict(), "id": faculty_id}
    finally:
        await conn.close()

@app.get("/faculties/", response_model=List[Faculty])
async def read_faculties():
    conn = await get_db_conn()
    try:
        return await conn.fetch("SELECT * FROM faculties ORDER BY name")
    finally:
        await conn.close()

@app.get("/faculties/{faculty_id}", response_model=Faculty)
async def read_faculty(faculty_id: int):
    conn = await get_db_conn()
    try:
        faculty = await conn.fetchrow(
            "SELECT * FROM faculties WHERE id = $1", faculty_id
        )
        if not faculty:
            raise HTTPException(status_code=404, detail="Faculty not found")
        return faculty
    finally:
        await conn.close()

@app.put("/faculties/{faculty_id}", response_model=Faculty)
async def update_faculty(faculty_id: int, faculty: FacultyCreate):
    conn = await get_db_conn()
    try:
        await conn.execute(
            "UPDATE faculties SET name = $1 WHERE id = $2",
            faculty.name, faculty_id
        )
        return {**faculty.dict(), "id": faculty_id}
    finally:
        await conn.close()

@app.delete("/faculties/{faculty_id}")
async def delete_faculty(faculty_id: int):
    conn = await get_db_conn()
    try:
        await conn.execute("DELETE FROM faculties WHERE id = $1", faculty_id)
        return {"message": "Faculty deleted"}
    finally:
        await conn.close()

# Groups endpoints
@app.post("/groups/", response_model=Group)
async def create_group(group: GroupCreate):
    conn = await get_db_conn()
    try:
        group_id = await conn.fetchval(
            "INSERT INTO groups (name, faculty_id) VALUES ($1, $2) RETURNING id",
            group.name, group.faculty_id
        )
        return {**group.dict(), "id": group_id}
    finally:
        await conn.close()

@app.get("/groups/", response_model=List[Group])
async def read_groups():
    conn = await get_db_conn()
    try:
        return await conn.fetch("SELECT * FROM groups ORDER BY name")
    finally:
        await conn.close()

@app.get("/groups/{group_id}", response_model=Group)
async def read_group(group_id: int):
    conn = await get_db_conn()
    try:
        group = await conn.fetchrow(
            "SELECT * FROM groups WHERE id = $1", group_id
        )
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        return group
    finally:
        await conn.close()

@app.put("/groups/{group_id}", response_model=Group)
async def update_group(group_id: int, group: GroupCreate):
    conn = await get_db_conn()
    try:
        await conn.execute(
            "UPDATE groups SET name = $1, faculty_id = $2 WHERE id = $3",
            group.name, group.faculty_id, group_id
        )
        return {**group.dict(), "id": group_id}
    finally:
        await conn.close()

@app.delete("/groups/{group_id}")
async def delete_group(group_id: int):
    conn = await get_db_conn()
    try:
        await conn.execute("DELETE FROM groups WHERE id = $1", group_id)
        return {"message": "Group deleted"}
    finally:
        await conn.close()

# Subjects endpoints
@app.post("/subjects/", response_model=Subject)
async def create_subject(subject: SubjectCreate):
    conn = await get_db_conn()
    try:
        subject_id = await conn.fetchval(
            "INSERT INTO subjects (name, group_id) VALUES ($1, $2) RETURNING id",
            subject.name, subject.group_id
        )
        return {**subject.dict(), "id": subject_id}
    finally:
        await conn.close()

@app.get("/subjects/", response_model=List[Subject])
async def read_subjects():
    conn = await get_db_conn()
    try:
        return await conn.fetch("SELECT * FROM subjects ORDER BY name")
    finally:
        await conn.close()

@app.get("/subjects/{subject_id}", response_model=Subject)
async def read_subject(subject_id: int):
    conn = await get_db_conn()
    try:
        subject = await conn.fetchrow(
            "SELECT * FROM subjects WHERE id = $1", subject_id
        )
        if not subject:
            raise HTTPException(status_code=404, detail="Subject not found")
        return subject
    finally:
        await conn.close()

@app.put("/subjects/{subject_id}", response_model=Subject)
async def update_subject(subject_id: int, subject: SubjectCreate):
    conn = await get_db_conn()
    try:
        await conn.execute(
            "UPDATE subjects SET name = $1, group_id = $2 WHERE id = $3",
            subject.name, subject.group_id, subject_id
        )
        return {**subject.dict(), "id": subject_id}
    finally:
        await conn.close()

@app.delete("/subjects/{subject_id}")
async def delete_subject(subject_id: int):
    conn = await get_db_conn()
    try:
        await conn.execute("DELETE FROM subjects WHERE id = $1", subject_id)
        return {"message": "Subject deleted"}
    finally:
        await conn.close()

# Students endpoints
@app.post("/students/", response_model=Student)
async def create_student(student: StudentCreate):
    conn = await get_db_conn()
    try:
        student_id = await conn.fetchval(
            """INSERT INTO students 
            (first_name, last_name, patronymic, record_book_number, phone, email, group_id, date_of_birth) 
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8) RETURNING id""",
            student.first_name, student.last_name, student.patronymic,
            student.record_book_number, student.phone, student.email,
            student.group_id, student.date_of_birth
        )
        return {**student.dict(), "id": student_id}
    finally:
        await conn.close()

@app.get("/students/", response_model=List[Student])
async def read_students():
    conn = await get_db_conn()
    try:
        return await conn.fetch("SELECT * FROM students ORDER BY last_name, first_name")
    finally:
        await conn.close()

@app.get("/students/{student_id}", response_model=Student)
async def read_student(student_id: int):
    conn = await get_db_conn()
    try:
        student = await conn.fetchrow(
            "SELECT * FROM students WHERE id = $1", student_id
        )
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        return student
    finally:
        await conn.close()

@app.put("/students/{student_id}", response_model=Student)
async def update_student(student_id: int, student: StudentCreate):
    conn = await get_db_conn()
    try:
        await conn.execute(
            """UPDATE students SET 
            first_name = $1, last_name = $2, patronymic = $3, 
            record_book_number = $4, phone = $5, email = $6, 
            group_id = $7, date_of_birth = $8 
            WHERE id = $9""",
            student.first_name, student.last_name, student.patronymic,
            student.record_book_number, student.phone, student.email,
            student.group_id, student.date_of_birth, student_id
        )
        return {**student.dict(), "id": student_id}
    finally:
        await conn.close()

@app.delete("/students/{student_id}")
async def delete_student(student_id: int):
    conn = await get_db_conn()
    try:
        await conn.execute("DELETE FROM students WHERE id = $1", student_id)
        return {"message": "Student deleted"}
    finally:
        await conn.close()

# Debts endpoints
@app.post("/debts/", response_model=Debt)
async def create_debt(debt: DebtCreate):
    conn = await get_db_conn()
    try:
        debt_id = await conn.fetchval(
            """INSERT INTO debts 
            (student_id, subject_id, reason, date_occurred, status) 
            VALUES ($1, $2, $3, $4, $5) RETURNING id""",
            debt.student_id, debt.subject_id, debt.reason,
            debt.date_occurred, debt.status
        )
        return {**debt.dict(), "id": debt_id}
    finally:
        await conn.close()

@app.get("/debts/", response_model=List[Debt])
async def read_debts():
    conn = await get_db_conn()
    try:
        return await conn.fetch("SELECT * FROM debts ORDER BY date_occurred DESC")
    finally:
        await conn.close()

@app.get("/debts/{debt_id}", response_model=Debt)
async def read_debt(debt_id: int):
    conn = await get_db_conn()
    try:
        debt = await conn.fetchrow(
            "SELECT * FROM debts WHERE id = $1", debt_id
        )
        if not debt:
            raise HTTPException(status_code=404, detail="Debt not found")
        return debt
    finally:
        await conn.close()

@app.put("/debts/{debt_id}", response_model=Debt)
async def update_debt(debt_id: int, debt: DebtCreate):
    conn = await get_db_conn()
    try:
        await conn.execute(
            """UPDATE debts SET 
            student_id = $1, subject_id = $2, reason = $3, 
            date_occurred = $4, status = $5 
            WHERE id = $6""",
            debt.student_id, debt.subject_id, debt.reason,
            debt.date_occurred, debt.status, debt_id
        )
        return {**debt.dict(), "id": debt_id}
    finally:
        await conn.close()

@app.put("/debts/{debt_id}/settle")
async def settle_debt(debt_id: int):
    conn = await get_db_conn()
    try:
        await conn.execute(
            "UPDATE debts SET status = 'settled' WHERE id = $1",
            debt_id
        )
        return {"message": "Debt marked as settled"}
    finally:
        await conn.close()

@app.delete("/debts/{debt_id}")
async def delete_debt(debt_id: int):
    conn = await get_db_conn()
    try:
        await conn.execute("DELETE FROM debts WHERE id = $1", debt_id)
        return {"message": "Debt deleted"}
    finally:
        await conn.close()

# Reports endpoints
@app.get("/reports/debts_by_faculty")
async def debts_by_faculty():
    conn = await get_db_conn()
    try:
        return await conn.fetch("""
            SELECT f.id, f.name as faculty, COUNT(d.id) as debt_count
            FROM faculties f
            LEFT JOIN groups g ON f.id = g.faculty_id
            LEFT JOIN students s ON g.id = s.group_id
            LEFT JOIN debts d ON s.id = d.student_id AND d.status = 'active'
            GROUP BY f.id
            ORDER BY debt_count DESC
        """)
    finally:
        await conn.close()

@app.get("/reports/debts_by_group/{group_id}")
async def debts_by_group(group_id: int):
    conn = await get_db_conn()
    try:
        return await conn.fetch("""
            SELECT s.id, s.last_name || ' ' || s.first_name as student,
                   COUNT(d.id) as debt_count
            FROM students s
            LEFT JOIN debts d ON s.id = d.student_id AND d.status = 'active'
            WHERE s.group_id = $1
            GROUP BY s.id
            ORDER BY debt_count DESC
        """, group_id)
    finally:
        await conn.close()

@app.get("/reports/student_debts/{student_id}")
async def student_debts(student_id: int):
    conn = await get_db_conn()
    try:
        return await conn.fetch("""
            SELECT d.id, sub.name as subject, d.reason, 
                   d.date_occurred, d.status
            FROM debts d
            JOIN subjects sub ON d.subject_id = sub.id
            WHERE d.student_id = $1
            ORDER BY d.status, d.date_occurred DESC
        """, student_id)
    finally:
        await conn.close()

@app.get("/reports/group_debts/{group_id}")
async def group_debts(group_id: int):
    conn = await get_db_conn()
    try:
        return await conn.fetch("""
            SELECT d.id, 
                   s.last_name || ' ' || s.first_name as student,
                   sub.name as subject, d.reason, 
                   d.date_occurred, d.status
            FROM debts d
            JOIN students s ON d.student_id = s.id
            JOIN subjects sub ON d.subject_id = sub.id
            WHERE s.group_id = $1
            ORDER BY d.status, d.date_occurred DESC
        """, group_id)
    finally:
        await conn.close()