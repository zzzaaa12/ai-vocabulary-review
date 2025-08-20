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

        try:
            # Get words based on time filter
            if time_filter == 'all':
                words = app.vocabulary_service.get_all_words()
            else:
                words = app.vocabulary_service.get_words_by_time_filter(time_filter)

            # Sort by creation date (newest first)
            words.sort(key=lambda w: w.created_date, reverse=True)

            total_words = app.vocabulary_service.get_total_word_count()

            return render_template('index.html',
                                 words=words,
                                 time_filter=time_filter,
                                 total_words=total_words)
        except Exception as e:
            flash(f'載入單字時發生錯誤：{str(e)}', 'error')
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
        try:
            word = app.vocabulary_service.get_word_by_id(word_id)

            if not word:
                flash('找不到指定的單字', 'error')
                return redirect(url_for('index'))

            return render_template('word_detail.html', word=word)

        except Exception as e:
            flash(f'載入單字時發生錯誤：{str(e)}', 'error')
            return redirect(url_for('index'))

    @app.route('/add', methods=['GET', 'POST'])
    def add_word():
        """
        Handle adding new vocabulary words.
        GET: Display add word form
        POST: Process form submission
        """
        if request.method == 'POST':
            try:
                # Get form data
                word = request.form.get('word', '').strip()
                chinese_meaning = request.form.get('chinese_meaning', '').strip()
                english_meaning = request.form.get('english_meaning', '').strip()
                phonetic = request.form.get('phonetic', '').strip()
                example_sentence = request.form.get('example_sentence', '').strip()
                synonyms_str = request.form.get('synonyms', '').strip()
                antonyms_str = request.form.get('antonyms', '').strip()

                # Validate required fields
                if not word:
                    flash('請輸入英文單字', 'error')
                    return render_template('add_word.html')

                if not chinese_meaning:
                    flash('請輸入中文翻譯', 'error')
                    return render_template('add_word.html')

                # Parse synonyms and antonyms
                synonyms = [s.strip() for s in synonyms_str.split(',') if s.strip()] if synonyms_str else []
                antonyms = [a.strip() for a in antonyms_str.split(',') if a.strip()] if antonyms_str else []

                # Create Word object
                from models.vocabulary import Word
                new_word = Word(
                    word=word,
                    chinese_meaning=chinese_meaning,
                    english_meaning=english_meaning,
                    phonetic=phonetic,
                    example_sentence=example_sentence,
                    synonyms=synonyms,
                    antonyms=antonyms
                )

                # Save word using vocabulary service
                app.vocabulary_service.add_word(new_word)

                flash(f'單字「{word}」新增成功！', 'success')
                return redirect(url_for('index'))

            except ValueError as e:
                flash(f'新增失敗：{str(e)}', 'error')
                return render_template('add_word.html')
            except Exception as e:
                flash(f'系統錯誤：{str(e)}', 'error')
                return render_template('add_word.html')

        return render_template('add_word.html')

    @app.route('/edit/<word_id>', methods=['GET', 'POST'])
    def edit_word(word_id):
        """
        Handle editing existing vocabulary words.

        Args:
            word_id: Unique identifier for the word to edit
        """
        if request.method == 'POST':
            try:
                # Get form data
                word = request.form.get('word', '').strip()
                chinese_meaning = request.form.get('chinese_meaning', '').strip()
                english_meaning = request.form.get('english_meaning', '').strip()
                phonetic = request.form.get('phonetic', '').strip()
                example_sentence = request.form.get('example_sentence', '').strip()
                synonyms_str = request.form.get('synonyms', '').strip()
                antonyms_str = request.form.get('antonyms', '').strip()

                # Validate required fields
                if not word:
                    flash('請輸入英文單字', 'error')
                    return redirect(url_for('edit_word', word_id=word_id))

                if not chinese_meaning:
                    flash('請輸入中文翻譯', 'error')
                    return redirect(url_for('edit_word', word_id=word_id))

                # Parse synonyms and antonyms
                synonyms = [s.strip() for s in synonyms_str.split(',') if s.strip()] if synonyms_str else []
                antonyms = [a.strip() for a in antonyms_str.split(',') if a.strip()] if antonyms_str else []

                # Update word using vocabulary service
                updated_word = app.vocabulary_service.update_word(
                    word_id,
                    word=word,
                    chinese_meaning=chinese_meaning,
                    english_meaning=english_meaning,
                    phonetic=phonetic,
                    example_sentence=example_sentence,
                    synonyms=synonyms,
                    antonyms=antonyms
                )

                if updated_word:
                    flash(f'單字「{word}」更新成功！', 'success')
                    return redirect(url_for('word_detail', word_id=word_id))
                else:
                    flash('找不到指定的單字', 'error')
                    return redirect(url_for('index'))

            except ValueError as e:
                flash(f'更新失敗：{str(e)}', 'error')
                return redirect(url_for('edit_word', word_id=word_id))
            except Exception as e:
                flash(f'系統錯誤：{str(e)}', 'error')
                return redirect(url_for('edit_word', word_id=word_id))

        # GET request - retrieve word data for editing
        try:
            word = app.vocabulary_service.get_word_by_id(word_id)

            if not word:
                flash('找不到指定的單字', 'error')
                return redirect(url_for('index'))

            return render_template('edit_word.html', word=word)

        except Exception as e:
            flash(f'載入單字時發生錯誤：{str(e)}', 'error')
            return redirect(url_for('index'))

    @app.route('/delete/<word_id>', methods=['POST'])
    def delete_word(word_id):
        """
        Handle word deletion.

        Args:
            word_id: Unique identifier for the word to delete
        """
        try:
            # Get word info before deletion for flash message
            word = app.vocabulary_service.get_word_by_id(word_id)

            if not word:
                flash('找不到指定的單字', 'error')
                return redirect(url_for('index'))

            # Delete word using vocabulary service
            success = app.vocabulary_service.delete_word(word_id)

            if success:
                flash(f'單字「{word.word}」刪除成功！', 'success')
            else:
                flash('刪除失敗，找不到指定的單字', 'error')

        except Exception as e:
            flash(f'刪除時發生錯誤：{str(e)}', 'error')

        return redirect(url_for('index'))

    @app.route('/search')
    def search():
        """
        Handle vocabulary search requests.
        """
        query = request.args.get('q', '').strip()

        if not query:
            return jsonify({'words': [], 'message': '請輸入搜尋關鍵字'})

        try:
            # Use vocabulary service to search
            words = app.vocabulary_service.search_words(query)

            # Convert words to dictionary format for JSON response
            words_data = []
            for word in words:
                words_data.append({
                    'id': word.id,
                    'word': word.word,
                    'chinese_meaning': word.chinese_meaning,
                    'english_meaning': word.english_meaning,
                    'phonetic': word.phonetic,
                    'example_sentence': word.example_sentence,
                    'synonyms': word.synonyms,
                    'antonyms': word.antonyms,
                    'created_date': word.created_date.strftime('%Y-%m-%d')
                })

            message = f'找到 {len(words)} 個相關單字' if words else f'沒有找到包含 "{query}" 的單字'

            return jsonify({
                'words': words_data,
                'message': message,
                'query': query,
                'count': len(words)
            })

        except Exception as e:
            return jsonify({
                'words': [],
                'message': f'搜尋時發生錯誤: {str(e)}',
                'query': query,
                'count': 0
            })

    @app.route('/settings')
    def settings():
        """
        Display settings page with API configuration.
        """
        from config.api_config import api_config

        status = api_config.get_status_summary()
        return render_template('settings.html', status=status)

    @app.route('/settings/api', methods=['GET', 'POST'])
    def api_settings():
        """
        Handle API key configuration.
        GET: Display API settings form
        POST: Process API key updates
        """
        from config.api_config import api_config

        if request.method == 'POST':
            try:
                # Get form data
                openai_key = request.form.get('openai_key', '').strip()
                gemini_key = request.form.get('gemini_key', '').strip()
                openai_model = request.form.get('openai_model', 'gpt-3.5-turbo').strip()
                gemini_model = request.form.get('gemini_model', 'gemini-pro').strip()
                default_provider = request.form.get('default_provider', 'openai')
                timeout = int(request.form.get('timeout', 30))
                max_retries = int(request.form.get('max_retries', 3))

                # Update OpenAI settings
                if openai_key:
                    api_config.set_openai_api_key(openai_key)
                    flash('OpenAI API Key 已更新', 'success')

                if openai_model:
                    api_config.set_openai_model(openai_model)

                # Update Gemini settings
                if gemini_key:
                    api_config.set_gemini_api_key(gemini_key)
                    flash('Gemini API Key 已更新', 'success')

                if gemini_model:
                    api_config.set_gemini_model(gemini_model)

                # Update general settings
                api_config.set_default_provider(default_provider)
                api_config.set_timeout(timeout)
                api_config.set_max_retries(max_retries)

                flash('設定已儲存', 'success')

            except ValueError as e:
                flash(f'設定錯誤: {str(e)}', 'error')
            except Exception as e:
                flash(f'儲存設定時發生錯誤: {str(e)}', 'error')

            return redirect(url_for('api_settings'))

        # GET request - show form
        status = api_config.get_status_summary()
        return render_template('api_settings.html', status=status)

    @app.route('/settings/api/clear', methods=['POST'])
    def clear_api_key():
        """
        Clear API key for specified provider.
        """
        from config.api_config import api_config

        provider = request.form.get('provider')

        if provider in ['openai', 'gemini']:
            api_config.clear_api_key(provider)
            flash(f'{provider.upper()} API Key 已清除', 'success')
        else:
            flash('無效的提供商', 'error')

        return redirect(url_for('api_settings'))

    @app.route('/settings/api/test', methods=['POST'])
    def test_api_connection():
        """
        Test API connection for specified provider.
        """
        from services.ai_service_tester import AIServiceTester

        provider = request.form.get('provider')

        if provider not in ['openai', 'gemini']:
            return jsonify({'success': False, 'message': '無效的提供商'})

        try:
            # Test actual API connection
            success, message = AIServiceTester.test_connection_sync(provider)

            return jsonify({
                'success': success,
                'message': message
            })

        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'測試連線時發生錯誤: {str(e)}'
            })

    @app.route('/api/ai-status', methods=['GET'])
    def ai_status():
        """
        Get AI service status.
        """
        from config.api_config import api_config

        try:
            status = api_config.get_status_summary()
            return jsonify({
                'available_providers': status['settings']['available_providers'],
                'default_provider': status['settings']['default_provider'],
                'openai_configured': status['openai']['configured'],
                'gemini_configured': status['gemini']['configured']
            })
        except Exception as e:
            return jsonify({
                'available_providers': [],
                'error': str(e)
            })

    @app.route('/api/generate-word-info', methods=['POST'])
    def generate_word_info():
        """
        Generate word information using AI.
        """
        from services.ai_word_service import ai_word_service

        try:
            data = request.get_json()
            word = data.get('word', '').strip()
            provider = data.get('provider')

            if not word:
                return jsonify({
                    'success': False,
                    'message': '請輸入英文單字'
                })

            # Validate word format
            is_valid, error_msg = ai_word_service.validate_word(word)
            if not is_valid:
                return jsonify({
                    'success': False,
                    'message': error_msg
                })

            # Generate word information
            word_info = ai_word_service.generate_word_info_sync(word, provider)

            return jsonify({
                'success': True,
                'data': {
                    'word': word_info.word,
                    'chinese_meaning': word_info.chinese_meaning,
                    'english_meaning': word_info.english_meaning,
                    'phonetic': word_info.phonetic,
                    'example_sentence': word_info.example_sentence,
                    'synonyms': ', '.join(word_info.synonyms) if word_info.synonyms else '',
                    'antonyms': ', '.join(word_info.antonyms) if word_info.antonyms else '',
                    'provider': word_info.provider,
                    'confidence_score': word_info.confidence_score
                }
            })

        except ValueError as e:
            return jsonify({
                'success': False,
                'message': str(e)
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'AI 生成失敗: {str(e)}'
            })

    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 errors."""
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        return render_template('500.html'), 500

    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 errors (including SSL handshake attempts)."""
        return "Bad Request", 400


# Application instance
app = create_app()


if __name__ == '__main__':
    # Development server configuration
    app.run(debug=True, host='127.0.0.1', port=8080)