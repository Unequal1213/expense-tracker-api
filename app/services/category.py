from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


def create_category(db: Session, category_data: CategoryCreate) -> Category:
    category = Category(**category_data.model_dump())

    db.add(category)
    db.commit()
    db.refresh(category)

    return category


def list_categories(db: Session) -> list[Category]:
    categories = db.scalars(select(Category).order_by(Category.id)).all()
    return list(categories)


def get_category(db: Session, category_id: int) -> Category | None:
    return db.get(Category, category_id)


def update_category(
    db: Session,
    category: Category,
    category_data: CategoryUpdate,
) -> Category:
    update_data = category_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(category, field, value)

    db.commit()
    db.refresh(category)

    return category


def delete_category(db: Session, category: Category) -> None:
    db.delete(category)
    db.commit()
