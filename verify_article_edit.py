
from app import create_app, db
from app.models import User, Article, DeveloperProfile
from flask import url_for

app = create_app()

with app.app_context():
    # Ensure a test article exists
    user = User.query.filter_by(role='developer').first()
    if not user:
        print("❌ No developer found to create article.")
        exit()
        
    article = Article.query.first()
    if not article:
        print("Creating test article...")
        article = Article(
            developer_id=user.developer_profile.id,
            title="Test Article",
            slug="test-article",
            content="Original content",
            status="pending"
        )
        db.session.add(article)
        db.session.commit()
    
    print(f"Testing Article ID: {article.id}")
    print(f"Original Title: {article.title}")
    
    # Simulate Edit
    new_title = "Updated Title via Script"
    article.title = new_title
    db.session.commit()
    
    # Verify
    verify_article = Article.query.get(article.id)
    if verify_article.title == new_title:
        print("✅ Article title updated successfully!")
    else:
        print("❌ Article update failed!")
        
    # Revert
    article.title = "Test Article"
    db.session.commit()
    print("Reverted to original title.")
