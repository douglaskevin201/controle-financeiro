from sqlalchemy.orm import Session
from backend.app.models.category import Category

DEFAULT_CATEGORIES = [
    {"name": "Alimentação", "type": "expense", "color": "#EF4444", "icon": "utensils"},
    {"name": "Moradia / Contas", "type": "expense", "color": "#F59E0B", "icon": "home"},
    {"name": "Transporte", "type": "expense", "color": "#3B82F6", "icon": "car"},
    {"name": "Lazer e Diversão", "type": "expense", "color": "#EC4899", "icon": "film"},
    {"name": "Saúde", "type": "expense", "color": "#10B981", "icon": "activity"},
    {"name": "Educação", "type": "expense", "color": "#8B5CF6", "icon": "book-open"},
    {"name": "Assinaturas & Serviços", "type": "expense", "color": "#6366F1", "icon": "credit-card"},
    {"name": "Compras / Variados", "type": "expense", "color": "#64748B", "icon": "shopping-bag"},
    {"name": "Salário", "type": "income", "color": "#10B981", "icon": "dollar-sign"},
    {"name": "Renda Extra / Freelance", "type": "income", "color": "#06B6D4", "icon": "briefcase"},
    {"name": "Outras Receitas", "type": "income", "color": "#84CC16", "icon": "plus-circle"}
]

def seed_default_categories(db: Session, user_id: int):
    """Cria o conjunto inicial de categorias personalizadas para o novo usuário"""
    for cat_data in DEFAULT_CATEGORIES:
        category = Category(
            user_id=user_id,
            name=cat_data["name"],
            type=cat_data["type"],
            color=cat_data["color"],
            icon=cat_data["icon"]
        )
        db.add(category)
    db.commit()

