from app import app
from flask_cors import CORS

cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

## API Routes ##
from remotemed_api.blueprints.users.views import users_api_blueprint
from remotemed_api.blueprints.sessions.views import sessions_api_blueprint
from remotemed_api.blueprints.records.views import records_api_blueprint
from remotemed_api.blueprints.appointments.views import appointments_api_blueprint
from remotemed_api.blueprints.payments.views import payments_api_blueprint


app.register_blueprint(users_api_blueprint, url_prefix='/api/v1/users')
app.register_blueprint(sessions_api_blueprint, url_prefix='/api/v1/sessions')
app.register_blueprint(records_api_blueprint, url_prefix='/api/v1/records')
app.register_blueprint(appointments_api_blueprint, url_prefix='/api/v1/appointments')
app.register_blueprint(payments_api_blueprint, url_prefix='/api/v1/payments')