"""
Seed dữ liệu tối thiểu để hệ thống chạy được: 3 role STUDENT/TEACHER/ADMIN.
Chạy: python -m scripts.seed_roles
"""
from app.db.session import SessionLocal
from app.models.role import Role, RoleName


def seed_roles() -> None:
    db = SessionLocal()
    try:
        existing = {r.name for r in db.query(Role).all()}
        created = []
        for role_name in RoleName:
            if role_name not in existing:
                db.add(Role(name=role_name, description=f"{role_name.value} role"))
                created.append(role_name.value)
        db.commit()
        print(f"Seed roles done. Created: {created if created else 'none (already exist)'}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_roles()
