"""
Asan DevNest - Application Entry Point
A trusted execution platform connecting verified developers with clients
"""

from app import create_app, db
from app.models import User, DeveloperProfile, ClientProfile, Article, Project, Team, Appointment
import click

app = create_app()


@app.shell_context_processor
def make_shell_context():
    """Make database models available in flask shell"""
    return {
        'db': db,
        'User': User,
        'DeveloperProfile': DeveloperProfile,
        'ClientProfile': ClientProfile,
        'Article': Article,
        'Project': Project,
        'Team': Team,
        'Appointment': Appointment
    }


@app.cli.command('create-admin')
@click.option('--email', default='admin@asandevnest.com', help='Admin email')
@click.option('--password', default='admin123', help='Admin password')
@click.option('--name', default='Asan Admin', help='Admin name')
def create_admin(email, password, name):
    """Create an admin user"""
    from app.models import User
    
    existing = User.query.filter_by(email=email).first()
    if existing:
        click.echo(f'Admin with email {email} already exists!')
        return
    
    admin = User(
        email=email,
        full_name=name,
        role='admin',
        status='verified'
    )
    admin.set_password(password)
    
    db.session.add(admin)
    db.session.commit()
    
    click.echo(f'Admin user created successfully!')
    click.echo(f'Email: {email}')
    click.echo(f'Password: {password}')


@app.cli.command('init-db')
def init_db():
    """Initialize the database with tables"""
    db.create_all()
    click.echo('Database tables created successfully!')


@app.cli.command('seed-demo')
def seed_demo():
    """Seed database with demo data"""
    from app.utils.seed_data import seed_demo_data
    seed_demo_data()
    click.echo('Demo data seeded successfully!')


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    # In production, we must listen on all interfaces (0.0.0.0)
    # Debug is False if FLASK_ENV is production
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
