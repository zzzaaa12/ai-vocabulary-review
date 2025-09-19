"""
Flask application for English Vocabulary Notebook.
Main application entry point with route definitions.
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from datetime import datetime
import os
import asyncio

# Import our models and services
from models import Word, VocabularyData
from services import VocabularyService
from config.auth import AuthManager, require_auth, require_auth_api


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

    # Session configuration
    app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours in seconds

    # Ensure data directory exists
    os.makedirs(app.config['DATA_DIR'], exist_ok=True)

    # Initialize vocabulary service
    app.vocabulary_service = VocabularyService(app.config['VOCABULARY_FILE'])

    # Initialize English words service
    from services.english_words_service import EnglishWordsService
    app.english_words_service = EnglishWordsService()

    # Register routes
    register_routes(app)

    return app


def register_routes(app):
    """
    Register all application routes.

    Args:
        app: Flask application instance
    """

    # HTTPS Force Redirect
    @app.before_request
    def force_https():
        """Force HTTPS redirect if enabled."""
        from config.api_config import api_config

        if (api_config.is_force_https() and
            request.endpoint and
            not request.is_secure and
            request.headers.get('X-Forwarded-Proto', 'http') != 'https'):
            return redirect(request.url.replace('http://', 'https://'))

    @app.route('/')
    @require_auth
    def index():
        """
        Main page with dashboard overview.
        """
        try:
            # Get basic statistics for dashboard
            total_words = app.vocabulary_service.get_total_word_count()
            time_stats = app.vocabulary_service.get_time_filter_stats()

            # Get recent words for quick preview (latest 3)
            recent_words = app.vocabulary_service.get_words_by_time_filter('all')[:3]

            return render_template('dashboard.html',
                                 total_words=total_words,
                                 time_stats=time_stats,
                                 recent_words=recent_words)
        except Exception as e:
            flash(f'載入儀表板時發生錯誤：{str(e)}', 'error')
            return render_template('dashboard.html',
                                 total_words=0,
                                 time_stats={},
                                 recent_words=[])

    @app.route('/vocabulary')
    @require_auth
    def vocabulary_list():
        """
        Vocabulary list page with filtering and search functionality.
        """
        time_filter = request.args.get('time_filter', 'all')

        try:
            # Get words based on time filter
            words = app.vocabulary_service.get_words_by_time_filter(time_filter)

            # Get time filter statistics
            time_stats = app.vocabulary_service.get_time_filter_stats()

            # Get all available time filters with labels
            time_filters = app.vocabulary_service.get_all_time_filters()

            # Get current filter label
            current_filter_label = app.vocabulary_service.get_time_filter_label(time_filter)

            # Get filtered count
            filtered_count = len(words)

            total_words = app.vocabulary_service.get_total_word_count()

            return render_template('index.html',
                                 words=words,
                                 time_filter=time_filter,
                                 time_filters=time_filters,
                                 time_stats=time_stats,
                                 current_filter_label=current_filter_label,
                                 filtered_count=filtered_count,
                                 total_words=total_words)
        except Exception as e:
            flash(f'載入單字時發生錯誤：{str(e)}', 'error')
            return render_template('index.html',
                                 words=[],
                                 time_filter=time_filter,
                                 time_filters={},
                                 time_stats={},
                                 current_filter_label='全部',
                                 filtered_count=0,
                                 total_words=0)

    @app.route('/word/<word_id>')
    @require_auth
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
    @require_auth
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

    @app.route('/add-batch', methods=['GET', 'POST'])
    @require_auth
    def add_words_batch():
        """
        Handle batch adding of vocabulary words.
        GET: Display batch add form
        POST: Process batch word submission (manual mode)
        """
        if request.method == 'POST':
            try:
                # Get form data
                words_text = request.form.get('words_text', '').strip()

                if not words_text:
                    flash('請輸入要新增的單字', 'error')
                    return render_template('add_batch.html')

                # Parse words from text input
                lines = [line.strip() for line in words_text.split('\n') if line.strip()]

                if not lines:
                    flash('請輸入要新增的單字', 'error')
                    return render_template('add_batch.html')

                # Create Word objects from input
                words_to_add = []
                for i, line in enumerate(lines, 1):
                    try:
                        # Parse line format: "word|chinese_meaning|english_meaning|phonetic|example_sentence|synonyms|antonyms"
                        # Minimum required: "word|chinese_meaning"
                        parts = [part.strip() for part in line.split('|')]

                        if len(parts) < 2:
                            flash(f'第 {i} 行格式錯誤：至少需要「英文單字|中文翻譯」', 'error')
                            continue

                        word = parts[0]
                        chinese_meaning = parts[1]
                        english_meaning = parts[2] if len(parts) > 2 else ''
                        phonetic = parts[3] if len(parts) > 3 else ''
                        example_sentence = parts[4] if len(parts) > 4 else ''
                        synonyms_str = parts[5] if len(parts) > 5 else ''
                        antonyms_str = parts[6] if len(parts) > 6 else ''

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

                        words_to_add.append(new_word)

                    except Exception as e:
                        flash(f'第 {i} 行處理錯誤：{str(e)}', 'error')
                        continue

                if not words_to_add:
                    flash('沒有有效的單字可以新增', 'error')
                    return render_template('add_batch.html')

                # Batch add words using vocabulary service
                result = app.vocabulary_service.add_words_batch(words_to_add)

                # Generate result messages
                if result['success_count'] > 0:
                    flash(f'成功新增 {result["success_count"]} 個單字！', 'success')

                if result['duplicate_words']:
                    flash(f'跳過重複單字：{", ".join(result["duplicate_words"])}', 'warning')

                if result['failed_words']:
                    for failed in result['failed_words']:
                        flash(f'「{failed["word"]}」新增失敗：{failed["error"]}', 'error')

                # If all successful, redirect to index
                if result['error_count'] == 0 and result['success_count'] > 0:
                    return redirect(url_for('index'))

                # Otherwise stay on the form with error messages
                return render_template('add_batch.html')

            except Exception as e:
                flash(f'批次新增時發生錯誤：{str(e)}', 'error')
                return render_template('add_batch.html')

        return render_template('add_batch.html')

    @app.route('/add-batch-ai', methods=['GET', 'POST'])
    @require_auth
    def add_words_batch_ai():
        """
        Handle AI-powered batch adding of vocabulary words.
        GET: Display AI batch add form
        POST: Process AI batch generation and save
        """
        if request.method == 'POST':
            try:
                # Get form data
                action = request.form.get('action', 'generate')

                if action == 'generate':
                    # Step 1: Generate AI content
                    words_text = request.form.get('words_text', '').strip()

                    if not words_text:
                        flash('請輸入要新增的單字', 'error')
                        return render_template('add_batch_ai.html')

                    # Parse words from text input
                    words = [word.strip() for word in words_text.split('\n') if word.strip()]

                    if not words:
                        flash('請輸入要新增的單字', 'error')
                        return render_template('add_batch_ai.html')

                    # Remove duplicates while preserving order
                    unique_words = []
                    seen = set()
                    for word in words:
                        if word.lower() not in seen:
                            unique_words.append(word)
                            seen.add(word.lower())

                    if len(unique_words) != len(words):
                        flash(f'已移除 {len(words) - len(unique_words)} 個重複單字', 'info')

                    # Store words in session for AI generation
                    session['batch_words'] = unique_words

                    return render_template('add_batch_ai.html',
                                         words=unique_words,
                                         step='generate')

                elif action == 'save':
                    # Step 2: Save AI generated results
                    ai_results = request.form.get('ai_results')
                    if not ai_results:
                        flash('沒有 AI 生成的結果可以儲存', 'error')
                        return render_template('add_batch_ai.html')

                    import json
                    try:
                        results_data = json.loads(ai_results)
                    except json.JSONDecodeError:
                        flash('AI 結果資料格式錯誤', 'error')
                        return render_template('add_batch_ai.html')

                    # Create Word objects from AI results
                    words_to_add = []
                    for result in results_data:
                        if result.get('selected', True):  # Only add selected words
                            try:
                                from models.vocabulary import Word
                                new_word = Word(
                                    word=result['word'],
                                    chinese_meaning=result['chinese_meaning'],
                                    english_meaning=result['english_meaning'],
                                    phonetic=result['phonetic'],
                                    example_sentence=result['example_sentence'],
                                    synonyms=result['synonyms'],
                                    antonyms=result['antonyms']
                                )
                                words_to_add.append(new_word)
                            except Exception as e:
                                flash(f'處理單字「{result.get("word", "未知")}」時發生錯誤：{str(e)}', 'error')

                    if not words_to_add:
                        flash('沒有有效的單字可以新增', 'error')
                        return render_template('add_batch_ai.html')

                    # Batch add words using vocabulary service
                    result = app.vocabulary_service.add_words_batch(words_to_add)

                    # Generate result messages
                    if result['success_count'] > 0:
                        flash(f'成功新增 {result["success_count"]} 個單字！', 'success')

                    if result['duplicate_words']:
                        flash(f'跳過重複單字：{", ".join(result["duplicate_words"])}', 'warning')

                    if result['failed_words']:
                        for failed in result['failed_words']:
                            flash(f'「{failed["word"]}」新增失敗：{failed["error"]}', 'error')

                    # Clear session data
                    session.pop('batch_words', None)

                    # If all successful, redirect to index
                    if result['error_count'] == 0 and result['success_count'] > 0:
                        return redirect(url_for('index'))

                    return render_template('add_batch_ai.html')

            except Exception as e:
                flash(f'處理時發生錯誤：{str(e)}', 'error')
                return render_template('add_batch_ai.html')

        return render_template('add_batch_ai.html')

    @app.route('/edit/<word_id>', methods=['GET', 'POST'])
    @require_auth
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
    @require_auth
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

    @app.route('/review')
    @require_auth
    def random_review():
        """
        Random vocabulary review page.
        """
        try:
            words = app.vocabulary_service.get_all_words()

            if not words:
                flash('沒有單字可以複習，請先新增一些單字', 'info')
                return redirect(url_for('add_word'))

            # Convert words to dictionary format for JSON serialization
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

            # Shuffle words for random review
            import random
            random.shuffle(words_data)

            return render_template('review.html', words=words_data, total_words=len(words_data))

        except Exception as e:
            flash(f'載入複習內容時發生錯誤：{str(e)}', 'error')
            return redirect(url_for('index'))

    @app.route('/search')
    @require_auth_api
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

    @app.route('/api/autocomplete')
    @require_auth_api
    def autocomplete():
        """
        提供自動完成候選單字。
        用於搜尋框的即時建議功能。
        """
        query = request.args.get('q', '').strip()
        limit = int(request.args.get('limit', 10))  # 預設最多回傳10個候選

        if not query:
            return jsonify({'suggestions': []})

        if len(query) < 2:  # 至少輸入2個字元才開始提供建議
            return jsonify({'suggestions': []})

        try:
            # 使用詞彙服務搜尋候選單字
            suggestions = app.vocabulary_service.get_autocomplete_suggestions(query, limit)

            return jsonify({
                'suggestions': suggestions,
                'query': query,
                'count': len(suggestions)
            })

        except Exception as e:
            return jsonify({
                'suggestions': [],
                'error': f'取得建議時發生錯誤: {str(e)}',
                'query': query,
                'count': 0
            })

    @app.route('/api/word-suggestions')
    @require_auth_api
    def word_suggestions():
        """
        提供英文單字建議（來自大型英文字典）。
        用於新增單字時的智能提示。
        """
        query = request.args.get('q', '').strip()
        limit = int(request.args.get('limit', 10))

        if not query:
            return jsonify({'suggestions': []})

        if len(query) < 2:
            return jsonify({'suggestions': []})

        try:
            # 使用英文單字服務取得建議
            suggestions = app.english_words_service.get_suggestions(query, limit)

            return jsonify({
                'suggestions': suggestions,
                'query': query,
                'count': len(suggestions),
                'source': 'english_dictionary'
            })

        except Exception as e:
            return jsonify({
                'suggestions': [],
                'error': f'取得英文單字建議時發生錯誤: {str(e)}',
                'query': query,
                'count': 0
            })

    @app.route('/settings')
    @require_auth
    def settings():
        """
        Display settings page with API configuration.
        """
        from config.api_config import api_config

        status = api_config.get_status_summary()
        return render_template('settings.html', status=status)

    @app.route('/settings/api', methods=['GET', 'POST'])
    @require_auth
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
    @require_auth
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
    @require_auth_api
    def test_api_connection():
        """
        Test API connection for specified provider.
        """
        from services.ai_service_tester import AIServiceTester

        provider = request.form.get('provider')
        temp_api_key = request.form.get('api_key')  # 支援臨時 API key

        if provider not in ['openai', 'gemini']:
            return jsonify({'success': False, 'message': '無效的提供商'})

        try:
            # If temp API key is provided, use it for testing
            if temp_api_key:
                # First validate format
                format_valid, format_msg = AIServiceTester.validate_and_test_key(provider, temp_api_key)
                if not format_valid:
                    return jsonify({
                        'success': False,
                        'message': format_msg
                    })

                # Test connection with temp key
                if provider == "openai":
                    success, message = asyncio.run(AIServiceTester.test_openai_connection(temp_api_key))
                else:  # gemini
                    success, message = asyncio.run(AIServiceTester.test_gemini_connection(temp_api_key))
            else:
                # Use saved API key
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
    @require_auth_api
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
    @require_auth_api
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

    @app.route('/api/batch-ai-generate', methods=['POST'])
    @require_auth_api
    def batch_ai_generate():
        """
        Generate word information for multiple words using AI.
        """
        from services.ai_word_service import ai_word_service

        try:
            data = request.get_json()
            words = data.get('words', [])
            provider = data.get('provider')

            if not words:
                return jsonify({
                    'success': False,
                    'message': '請提供要生成的單字列表'
                })

            if len(words) > 50:  # Limit batch size
                return jsonify({
                    'success': False,
                    'message': '批次處理最多支援 50 個單字'
                })

            results = []
            total_words = len(words)

            for i, word in enumerate(words):
                try:
                    word = word.strip()
                    if not word:
                        continue

                    # Validate word format
                    is_valid, error_msg = ai_word_service.validate_word(word)
                    if not is_valid:
                        results.append({
                            'word': word,
                            'success': False,
                            'error': error_msg,
                            'progress': ((i + 1) / total_words) * 100
                        })
                        continue

                    # Generate word information
                    word_info = ai_word_service.generate_word_info_sync(word, provider)

                    results.append({
                        'word': word_info.word,
                        'chinese_meaning': word_info.chinese_meaning,
                        'english_meaning': word_info.english_meaning,
                        'phonetic': word_info.phonetic,
                        'example_sentence': word_info.example_sentence,
                        'synonyms': word_info.synonyms,
                        'antonyms': word_info.antonyms,
                        'provider': word_info.provider,
                        'confidence_score': word_info.confidence_score,
                        'success': True,
                        'progress': ((i + 1) / total_words) * 100
                    })

                except Exception as e:
                    results.append({
                        'word': word,
                        'success': False,
                        'error': f'AI 生成失敗: {str(e)}',
                        'progress': ((i + 1) / total_words) * 100
                    })

            # Calculate statistics
            successful_results = [r for r in results if r.get('success', False)]
            failed_results = [r for r in results if not r.get('success', False)]

            return jsonify({
                'success': True,
                'results': results,
                'statistics': {
                    'total': len(results),
                    'successful': len(successful_results),
                    'failed': len(failed_results),
                    'success_rate': (len(successful_results) / len(results) * 100) if results else 0
                }
            })

        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'批次生成失敗: {str(e)}'
            })

    @app.route('/api/stats', methods=['GET'])
    @require_auth_api
    def get_stats():
        """
        Get vocabulary statistics.
        """
        try:
            # Get time filter statistics
            time_stats = app.vocabulary_service.get_time_filter_stats()

            # Get learning progress statistics
            progress_stats = app.vocabulary_service.get_learning_progress_stats()

            # Get all available time filters
            time_filters = app.vocabulary_service.get_all_time_filters()

            return jsonify({
                'success': True,
                'data': {
                    'time_stats': time_stats,
                    'progress_stats': progress_stats,
                    'time_filters': time_filters
                }
            })

        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'獲取統計資料失敗: {str(e)}'
            })

    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 errors."""
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        return render_template('500.html'), 500

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """
        Handle user authentication.
        GET: Display login form
        POST: Process login credentials
        """
        from config.api_config import api_config

        # If no passcode configured, redirect to settings
        if not AuthManager.is_passcode_required():
            flash('尚未設定通行碼，請先設定', 'warning')
            return redirect(url_for('api_settings'))

        # If already authenticated, redirect to intended page or home
        if AuthManager.is_authenticated():
            next_url = session.pop('next_url', None)
            return redirect(next_url or url_for('index'))

        # Check if user is blocked
        blocked_info = {}
        is_blocked, seconds_left = AuthManager.is_blocked()
        if is_blocked:
            blocked_info = {
                'is_blocked': True,
                'seconds_left': seconds_left
            }

        if request.method == 'POST':
            passcode = request.form.get('passcode', '').strip()

            if not passcode:
                flash('請輸入通行碼', 'error')
            else:
                success, message = AuthManager.authenticate(passcode)

                if success:
                    flash(message, 'success')
                    next_url = session.pop('next_url', None)
                    return redirect(next_url or url_for('index'))
                else:
                    flash(message, 'error')

        # Prepare template context
        context = {
            'blocked_info': blocked_info,
            'failed_attempts': session.get(AuthManager.SESSION_FAILED_ATTEMPTS, 0),
            'max_attempts': api_config.get_max_failed_attempts(),
            'auto_logout_hours': api_config.get_auto_logout_hours(),
            'session_info': {'auto_logout_enabled': api_config.is_auto_logout_enabled()}
        }

        return render_template('login.html', **context)

    @app.route('/logout', methods=['POST', 'GET'])
    def logout():
        """Handle user logout."""
        AuthManager.logout()
        flash('已成功登出', 'success')
        return redirect(url_for('login'))

    @app.route('/auth/status')
    def auth_status():
        """Get authentication status for AJAX requests."""
        return jsonify({
            'authenticated': AuthManager.is_authenticated(),
            'passcode_required': AuthManager.is_passcode_required(),
            'session_info': AuthManager.get_session_info()
        })

    @app.route('/settings/passcode', methods=['POST'])
    @require_auth
    def passcode_settings():
        """Handle passcode configuration."""
        from config.api_config import api_config

        try:
            # Get form data
            current_passcode = request.form.get('current_passcode', '').strip()
            new_passcode = request.form.get('new_passcode', '').strip()
            confirm_passcode = request.form.get('confirm_passcode', '').strip()
            auto_logout_enabled = request.form.get('auto_logout_enabled') == '1'
            auto_logout_hours = int(request.form.get('auto_logout_hours', 24))
            max_failed_attempts = int(request.form.get('max_failed_attempts', 5))

            # Validate new passcode
            if not new_passcode:
                flash('請輸入新通行碼', 'error')
                return redirect(url_for('settings'))

            if len(new_passcode) < 4 or len(new_passcode) > 50:
                flash('通行碼長度必須在 4-50 個字符之間', 'error')
                return redirect(url_for('settings'))

            if new_passcode != confirm_passcode:
                flash('兩次輸入的通行碼不一致', 'error')
                return redirect(url_for('settings'))

            # If updating existing passcode, verify current passcode
            if api_config.is_passcode_configured():
                if not current_passcode:
                    flash('請輸入目前的通行碼', 'error')
                    return redirect(url_for('settings'))

                if not api_config.verify_passcode(current_passcode):
                    flash('目前通行碼錯誤', 'error')
                    return redirect(url_for('settings'))

            # Update passcode
            api_config.set_passcode(new_passcode)

            # Update other settings
            api_config.set_auto_logout_enabled(auto_logout_enabled)
            api_config.set_auto_logout_hours(auto_logout_hours)
            api_config.set_max_failed_attempts(max_failed_attempts)

            flash('通行碼設定已更新', 'success')

            # If this is the first time setting a passcode, logout to force re-authentication
            if not current_passcode:
                AuthManager.logout()
                flash('通行碼已設定，請重新登入', 'info')
                return redirect(url_for('login'))

        except ValueError as e:
            flash(f'設定錯誤: {str(e)}', 'error')
        except Exception as e:
            flash(f'儲存設定時發生錯誤: {str(e)}', 'error')

        return redirect(url_for('settings'))

    @app.route('/settings/passcode/clear', methods=['POST'])
    @require_auth
    def clear_passcode():
        """Clear passcode protection."""
        from config.api_config import api_config

        try:
            # Clear passcode
            api_config.clear_passcode()

            # Logout current session
            AuthManager.logout()

            flash('通行碼保護已移除', 'success')
            return redirect(url_for('index'))  # Redirect to home since no auth required now

        except Exception as e:
            flash(f'移除通行碼時發生錯誤: {str(e)}', 'error')
            return redirect(url_for('settings'))

    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 errors (including SSL handshake attempts)."""
        return "Bad Request", 400

    @app.route('/settings/server', methods=['GET', 'POST'])
    @require_auth
    def server_settings():
        """
        Handle server configuration.
        GET: Display server settings form
        POST: Process server settings updates
        """
        from config.api_config import api_config

        if request.method == 'POST':
            try:
                # Get form data
                https_enabled = request.form.get('https_enabled') == '1'
                host = request.form.get('host', '0.0.0.0').strip()
                port = int(request.form.get('port', 8080))
                cert_file = request.form.get('cert_file', 'certs/cert.pem').strip()
                key_file = request.form.get('key_file', 'certs/key.pem').strip()
                force_https = request.form.get('force_https') == '1'

                # Validate inputs
                if port < 1 or port > 65535:
                    flash('連接埠必須在 1-65535 之間', 'error')
                    return redirect(url_for('server_settings'))

                if not cert_file or not key_file:
                    flash('請輸入憑證檔案路徑', 'error')
                    return redirect(url_for('server_settings'))

                # Update server settings
                api_config.set_https_enabled(https_enabled)
                api_config.set_server_host(host)
                api_config.set_server_port(port)
                api_config.set_cert_file(cert_file)
                api_config.set_key_file(key_file)
                api_config.set_force_https(force_https)

                flash('伺服器設定已儲存', 'success')

                # Note about restart requirement
                if https_enabled:
                    flash('HTTPS 設定已更新，請重新啟動伺服器以生效', 'info')

            except ValueError as e:
                flash(f'設定錯誤: {str(e)}', 'error')
            except Exception as e:
                flash(f'儲存設定時發生錯誤: {str(e)}', 'error')

            return redirect(url_for('server_settings'))

        # GET request - show form
        status = api_config.get_status_summary()
        return render_template('server_settings.html', status=status)


# Application instance
app = create_app()


if __name__ == '__main__':
    from config.api_config import api_config

    # Get server configuration
    host = api_config.get_server_host()
    port = api_config.get_server_port()

    # Check for SSL certificate files
    ssl_context = api_config.get_ssl_context()

    if ssl_context and api_config.is_https_enabled():
        print(f"🔐 SSL憑證已載入 - HTTPS 伺服器啟動")
        print(f"📁 憑證位置: {ssl_context[0]}")
        print(f"🔑 私鑰位置: {ssl_context[1]}")
        if api_config.is_force_https():
            print(f"🔒 已啟用強制 HTTPS 重新導向")
    else:
        ssl_context = None
        if api_config.is_https_enabled():
            print("⚠️  HTTPS 已啟用但 SSL憑證檔案不存在，使用 HTTP 模式")
            ssl_validation = api_config.validate_ssl_certificates()
            print(f"💡 請將憑證檔案放在: {ssl_validation['cert_file']}")
            print(f"💡 請將私鑰檔案放在: {ssl_validation['key_file']}")
        else:
            print("ℹ️  HTTPS 功能已停用，使用 HTTP 模式")

    # Override port with environment variable if available
    port = int(os.environ.get('PORT', port))

    if ssl_context:
        print(f"🚀 伺服器啟動於 https://{host}:{port}")
    else:
        print(f"🚀 伺服器啟動於 http://{host}:{port}")

    app.run(
        debug=True,
        host=host,
        port=port,
        ssl_context=ssl_context
    )
