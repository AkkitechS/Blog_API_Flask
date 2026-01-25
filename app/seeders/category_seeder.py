from app.extensions import db
from app.models.categories import Category
from app.utils.slug import generate_unique_slug

def seed_categories():
    categories = ["Technology",
        "Business",
        "Health",
        "Education",
        "Lifestyle",
        "Sports",
        "Entertainment"]

    for category in categories:
        slug = generate_unique_slug(category)

        exists = Category.query.filter_by(slug=slug).first()
        if exists:
            continue

        catg = Category(slug=slug, name=category, description=f'{category} related articles')

        db.session.add(catg)
        db.session.commit()
        print("✅ Categories seeded successfully")