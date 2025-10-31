import os
from flask import Flask, request, jsonify, send_file
from flask_restx import Api, Resource, fields
from flask_cors import CORS
from database import db
from models import Work, Category
from config import Config
import werkzeug
from werkzeug.utils import secure_filename

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
CORS(app)

# Create upload directory
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize RESTx API
api = Api(app, 
          version='1.0', 
          title='SOČ Archive API',
          description='REST API for SOČ Archive System',
          doc='/api/')

# Namespaces
works_ns = api.namespace('works', description='Work operations')
categories_ns = api.namespace('categories', description='Category operations')
admin_ns = api.namespace('admin', description='Administrative operations')

# Models for Swagger documentation
work_model = api.model('Work', {
    'title': fields.String(required=True, description='Work title'),
    'abstract': fields.String(required=True, description='Abstract'),
    'author_name': fields.String(required=True, description='Author name'),
    'author_email': fields.String(description='Author email'),
    'year': fields.Integer(required=True, description='Year'),
    'field': fields.String(required=True, description='Field/obor'),
    'school': fields.String(description='School'),
    'region': fields.String(description='Region/kraj'),
    'category': fields.String(description='Category'),
    'gdpr_consent': fields.Boolean(description='GDPR consent')
})

category_model = api.model('Category', {
    'name': fields.String(required=True, description='Category name'),
    'description': fields.String(description='Category description')
})

# Utility functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['pdf']

# Routes
@works_ns.route('/')
class WorkList(Resource):
    @works_ns.doc('list_works')
    @works_ns.param('search', 'Full-text search')
    @works_ns.param('field', 'Filter by field')
    @works_ns.param('year', 'Filter by year')
    @works_ns.param('school', 'Filter by school')
    @works_ns.param('region', 'Filter by region')
    @works_ns.param('category', 'Filter by category')
    def get(self):
        """Get all works with filtering and search"""
        query = Work.query.filter_by(approved=True)
        
        # Search in title, abstract, and author name
        search = request.args.get('search')
        if search:
            query = query.filter(
                db.or_(
                    Work.title.contains(search),
                    Work.abstract.contains(search),
                    Work.author_name.contains(search),
                    Work.field.contains(search)
                )
            )
        
        # Filters
        field = request.args.get('field')
        if field:
            query = query.filter(Work.field == field)
            
        year = request.args.get('year')
        if year:
            query = query.filter(Work.year == year)
            
        school = request.args.get('school')
        if school:
            query = query.filter(Work.school.contains(school))
            
        region = request.args.get('region')
        if region:
            query = query.filter(Work.region == region)
            
        category = request.args.get('category')
        if category:
            query = query.filter(Work.category == category)
        
        works = query.all()
        return jsonify([work.to_dict() for work in works])

    @works_ns.doc('create_work')
    @works_ns.expect(work_model)
    def post(self):
        """Create a new work (import from Prihlaska)"""
        data = request.get_json()
        
        work = Work(
            title=data['title'],
            abstract=data['abstract'],
            author_name=data['author_name'],
            author_email=data.get('author_email'),
            year=data['year'],
            field=data['field'],
            school=data.get('school'),
            region=data.get('region'),
            category=data.get('category'),
            gdpr_consent=data.get('gdpr_consent', False)
        )
        
        db.session.add(work)
        db.session.commit()
        
        return work.to_dict(), 201

@works_ns.route('/<int:work_id>')
@works_ns.response(404, 'Work not found')
class WorkDetail(Resource):
    @works_ns.doc('get_work')
    def get(self, work_id):
        """Get a specific work"""
        work = Work.query.get_or_404(work_id)
        return work.to_dict()

@works_ns.route('/<int:work_id>/pdf')
@works_ns.response(404, 'Work or PDF not found')
class WorkPDF(Resource):
    def get(self, work_id):
        """Download work PDF"""
        work = Work.query.get_or_404(work_id)
        if not work.pdf_filename:
            return {'message': 'PDF not available'}, 404
            
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], work.pdf_filename)
        return send_file(pdf_path, as_attachment=True)

@works_ns.route('/<int:work_id>/gdpr')
@works_ns.response(404, 'Work not found')
class WorkGDPR(Resource):
    def delete(self, work_id):
        """Remove personal data (GDPR compliance)"""
        work = Work.query.get_or_404(work_id)
        
        # Anonymize personal data
        work.author_name = "Anonymizováno"
        work.author_email = None
        
        db.session.commit()
        
        return {'message': 'Personal data removed'}

@categories_ns.route('/')
class CategoryList(Resource):
    def get(self):
        """Get all categories"""
        categories = Category.query.all()
        return jsonify([category.to_dict() for category in categories])
    
    @categories_ns.doc('create_category')
    @categories_ns.expect(category_model)
    def post(self):
        """Create a new category"""
        data = request.get_json()
        
        category = Category(
            name=data['name'],
            description=data.get('description')
        )
        
        db.session.add(category)
        db.session.commit()
        
        return category.to_dict(), 201

@admin_ns.route('/works/<int:work_id>/approve')
class WorkApproval(Resource):
    def post(self, work_id):
        """Approve a work"""
        work = Work.query.get_or_404(work_id)
        work.approved = True
        db.session.commit()
        return {'message': 'Work approved'}

@admin_ns.route('/works/<int:work_id>/pdf')
class WorkPDFUpload(Resource):
    def post(self, work_id):
        """Upload PDF for a work"""
        work = Work.query.get_or_404(work_id)
        
        if 'pdf' not in request.files:
            return {'message': 'No PDF file provided'}, 400
            
        file = request.files['pdf']
        if file.filename == '':
            return {'message': 'No file selected'}, 400
            
        if file and allowed_file(file.filename):
            filename = secure_filename(f"work_{work_id}_{file.filename}")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            work.pdf_filename = filename
            db.session.commit()
            
            return {'message': 'PDF uploaded successfully'}
        
        return {'message': 'Invalid file type'}, 400

@admin_ns.route('/stats')
class Statistics(Resource):
    def get(self):
        """Get statistics about works"""
        total_works = Work.query.count()
        approved_works = Work.query.filter_by(approved=True).count()
        
        # Works by year
        years = db.session.query(Work.year, db.func.count(Work.id)).group_by(Work.year).all()
        
        # Works by field
        fields = db.session.query(Work.field, db.func.count(Work.id)).group_by(Work.field).all()
        
        return {
            'total_works': total_works,
            'approved_works': approved_works,
            'works_by_year': dict(years),
            'works_by_field': dict(fields)
        }

@admin_ns.route('/export')
class ExportData(Resource):
    def get(self):
        """Export works data as JSON"""
        works = Work.query.all()
        data = [work.to_dict() for work in works]
        return jsonify(data)

# Health check endpoint
@app.route('/api/health')
def health_check():
    return jsonify({'status': 'healthy', 'message': 'SOČ Archive API is running'})

# Initialize database
with app.app_context():
    db.create_all()
    
    # Add some sample categories if none exist
    if Category.query.count() == 0:
        sample_categories = [
            Category(name="Matematika", description="Matematické práce"),
            Category(name="Fyzika", description="Fyzikální práce"),
            Category(name="Informatika", description="Informatické práce"),
            Category(name="Biologie", description="Biologické práce"),
            Category(name="Chemie", description="Chemické práce")
        ]
        db.session.add_all(sample_categories)
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)