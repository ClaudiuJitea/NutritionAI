# Diet & Nutrition Tracking App

A comprehensive web application for tracking daily nutrition intake with AI-powered food analysis using image recognition.

## Features

- 🍎 **Food Tracking**: Log meals with detailed nutritional information
- 📸 **AI Image Analysis**: Analyze food photos using OpenRouter AI (Google Gemini)
- 💧 **Water Intake Tracking**: Monitor daily hydration goals
- 📊 **Statistics & Analytics**: Visualize nutrition trends and progress
- 🎯 **Goal Setting**: Set and track personalized nutrition goals
- 👤 **User Profiles**: Manage personal information and preferences
- 📱 **Responsive Design**: Works seamlessly on desktop and mobile devices

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLAlchemy with SQLite (configurable for PostgreSQL)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **AI Integration**: OpenRouter API with Google Gemini model
- **Authentication**: Flask-Login with secure password hashing
- **Forms**: Flask-WTF with CSRF protection

## Prerequisites

- Python 3.8 or higher
- OpenRouter API key (for AI food analysis)

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/nutrition-app.git
   cd nutrition-app
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env with your actual values
   # Get your OpenRouter API key from: https://openrouter.ai/
   ```

5. **Initialize the database**
   ```bash
   python -c "from app import app, db; app.app_context().push(); db.create_all()"
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

   The app will be available at `http://localhost:5000`

## Configuration

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=sqlite:///app.db

# OpenRouter AI API
OPENROUTER_API_KEY=your-openrouter-api-key

# File Uploads
UPLOAD_FOLDER=static/uploads
MAX_CONTENT_LENGTH=16777216
```

### OpenRouter API Setup

1. Visit [OpenRouter.ai](https://openrouter.ai/)
2. Create an account and get your API key
3. Add the API key to your `.env` file
4. The app uses Google Gemini 2.5 Flash model for food analysis

## Usage

### Getting Started

1. **Register an Account**: Create a new user account or use the default admin account
2. **Set Goals**: Configure your daily nutrition goals (calories, protein, carbs, fat, water)
3. **Log Food**: Add food entries manually or by uploading food photos for AI analysis
4. **Track Progress**: Monitor your daily intake and view statistics

### Default Admin Account

When you first run the application, a default admin account is automatically created:

- **Username**: `admin`
- **Email**: `admin@example.com`
- **Password**: `admin123`

**⚠️ Important Security Note**: Change the default password immediately after your first login for security purposes. You can do this through the user profile page after logging in.

### Food Logging

- **Manual Entry**: Add food items with nutritional information
- **Photo Analysis**: Upload food photos for automatic nutritional analysis
- **Meal Categories**: Organize entries by breakfast, lunch, dinner, or snacks

### Statistics

- Daily nutrition summaries
- Weekly and monthly trends
- Goal achievement tracking
- Macro-nutrient distribution charts

## API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /auth/logout` - User logout
- `GET|POST /auth/profile` - User profile management

### Nutrition
- `GET /nutrition/dashboard` - Main dashboard
- `GET|POST /nutrition/add-food` - Add food entries
- `GET /nutrition/statistics` - Nutrition statistics

### API
- `POST /api/analyze-food` - AI food analysis
- `POST /api/add-water` - Add water intake
- `GET /api/nutrition-data` - Get nutrition data

## Development

### Project Structure

```
nutrition_app/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── models.py             # Database models
├── requirements.txt      # Python dependencies
├── routes/               # Route blueprints
│   ├── auth.py          # Authentication routes
│   ├── nutrition.py     # Nutrition tracking routes
│   ├── statistics.py    # Statistics routes
│   └── api.py           # API endpoints
├── static/              # Static files (CSS, JS, images)
├── templates/           # HTML templates
└── utils/               # Utility modules
    ├── openrouter_ai.py # AI integration
    └── nutrition_db.py  # Database utilities
```

### Running in Development

```bash
# Set development environment
export FLASK_ENV=development

# Run with debug mode
python app.py
```

### Database Migrations

For database schema changes:

```bash
# Initialize migrations (first time only)
flask db init

# Create migration
flask db migrate -m "Description of changes"

# Apply migration
flask db upgrade
```

## Deployment

### Production Considerations

1. **Security**:
   - Generate a strong `SECRET_KEY`
   - Use HTTPS in production
   - Set `FLASK_ENV=production`
   - Use a production database (PostgreSQL recommended)

2. **Database**:
   ```env
   DATABASE_URL=postgresql://username:password@localhost/nutrition_app
   ```

3. **File Storage**:
   - Configure proper file upload limits
   - Consider using cloud storage for uploads

4. **Environment Variables**:
   - Never commit `.env` files to version control
   - Use environment-specific configuration

### Docker Deployment

```dockerfile
# Example Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "app.py"]
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/yourusername/nutrition-app/issues) page
2. Create a new issue with detailed information
3. Include error messages and steps to reproduce

## Acknowledgments

- OpenRouter.ai for AI-powered food analysis
- Google Gemini for advanced image recognition
- Flask community for excellent documentation
- Contributors and testers

---

**Note**: This application requires an OpenRouter API key for AI features. The free tier provides sufficient usage for personal projects.
