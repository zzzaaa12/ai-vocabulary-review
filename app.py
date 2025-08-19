"""
Flask application for English Vocabulary Notebook.
Main application entry point with route definitions.
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
import os

# Import our models and services
from models import Word, VocabularyData
from services import VocabularyService


def create_app():
    """
    Application factory function to create and configure Flask app.
    
    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['DATA_DIR'] = os.path.join(os.path.dirname(__file__), 'data')
    app.config['VOCABULARY_FILE'] = os.path.join(app.config['DATA_DIR'], 'vocabulary.json')
    
    # Ensure data directory exists
    os.makedirs(app.config['DATA_DIR'], exist_ok=True)
    
    # Initialize vocabulary service
    app.vocabulary_service = VocabularyService(app.config['VOCABULARY_FILE'])
    
    # Register routes
    register_routes(app)
    
    return app


def register_routes(app):
    """
    Register all application routes.
    
    Args:
        app: Flask application instance
    """
    
    @app.route('/')
    def index():
        """
        Main page displaying vocabulary list with optional time filtering.
        """
        time_filter = request.args.get('time_filter', 'all')
        
        # TODO: Implement vocabulary service integration
        # For now, return empty template
        return render_template('index.html', 
                             words=[], 
                             time_filter=time_filter,
                             total_words=0)
    
    @app.route('/word/<word_id>')
    def word_detail(word_id):
        """
        Display detailed information for a specific word.
        
        Args:
            word_id: Unique identifier for the word
        """
        # TODO: Implement word retrieval from service
        return render_template('word_detail.html', word=None)
    
    @app.route('/add', methods=['GET', 'POST'])
    def add_word():
        """
        Handle adding new vocabulary words.
        GET: Display add word form
        POST: Process form submission
        """
        if request.method == 'POST':
            # TODO: Implement word creation logic
            flash('單字新增成功！', 'success')
            return redirect(url_for('index'))
        
        return render_template('add_word.html')
    
    @app.route('/edit/<word_id>', methods=['GET', 'POST'])
    def edit_word(word_id):
        """
        Handle editing existing vocabulary words.
        
        Args:
            word_id: Unique identifier for the word to edit
        """
        if request.method == 'POST':
            # TODO: Implement word update logic
            flash('單字更新成功！', 'success')
            return redirect(url_for('word_detail', word_id=word_id))
        
        # TODO: Retrieve word data for editing
        return render_template('edit_word.html', word=None)
    
    @app.route('/delete/<word_id>', methods=['POST'])
    def delete_word(word_id):
        """
        Handle word deletion.
        
        Args:
            word_id: Unique identifier for the word to delete
        """
        # TODO: Implement word deletion logic
        flash('單字刪除成功！', 'success')
        return redirect(url_for('index'))
    
    @app.route('/search')
    def search():
        """
        Handle vocabulary search requests.
        """
        query = request.args.get('q', '').strip()
        
        if not query:
            return jsonify({'words': [], 'message': '請輸入搜尋關鍵字'})
        
        # TODO: Implement search logic
        return jsonify({'words': [], 'message': f'搜尋 "{query}" 的結果'})
    
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 errors."""
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        return render_template('500.html'), 500


# Application instance
app = create_app()


if __name__ == '__main__':
    # Development server configuration
    app.run(debug=True, host='127.0.0.1', port=5000)