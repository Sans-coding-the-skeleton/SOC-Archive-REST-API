from database import db
from datetime import datetime

class Work(db.Model):
    __tablename__ = 'works'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    abstract = db.Column(db.Text, nullable=False)
    author_name = db.Column(db.String(100), nullable=False)
    author_email = db.Column(db.String(100))
    year = db.Column(db.Integer, nullable=False)
    field = db.Column(db.String(100), nullable=False)  # obor
    school = db.Column(db.String(200))
    region = db.Column(db.String(100))  # kraj
    category = db.Column(db.String(100))
    pdf_filename = db.Column(db.String(300))
    approved = db.Column(db.Boolean, default=False)
    gdpr_consent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'abstract': self.abstract,
            'author_name': self.author_name,
            'year': self.year,
            'field': self.field,
            'school': self.school,
            'region': self.region,
            'category': self.category,
            'pdf_url': f"/api/works/{self.id}/pdf" if self.pdf_filename else None,
            'approved': self.approved,
            'created_at': self.created_at.isoformat()
        }

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }