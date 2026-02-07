"""
Demo Data Seeder
"""

from app import db
from app.models import User, DeveloperProfile, ClientProfile, Article, Project
from datetime import datetime, timedelta
import json


def seed_demo_data():
    """Seed database with demo data for testing"""
    
    # Create admin account first
    admin = User.query.filter_by(email='admin@asandevnest.com').first()
    if not admin:
        admin = User(
            email='admin@asandevnest.com',
            full_name='Asan Admin',
            role='admin',
            status='verified'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin account created!")
        print("   Email: admin@asandevnest.com")
        print("   Password: admin123")
    
    # Check if data already exists
    if User.query.count() > 1:
        print("Demo data already exists. Skipping.")
        return
    
    # Create demo developers
    developers_data = [
        {
            'email': 'priya.sharma@example.com',
            'password': 'Demo@123',
            'full_name': 'Priya Sharma',
            'phone': '+91 98765 43210',
            'profile': {
                'tagline': 'Full Stack Developer | AI & ML Enthusiast',
                'bio': 'Passionate full-stack developer with 6+ years of experience building scalable web applications. Specialized in React, Node.js, and Python. Love solving complex problems with elegant solutions.',
                'experience_years': 6,
                'skills': ['React', 'Node.js', 'Python', 'TensorFlow', 'AWS', 'MongoDB', 'PostgreSQL'],
                'domains': ['FinTech', 'AI/ML', 'SaaS'],
                'hourly_rate': 75,
                'offers_classes': True,
                'offers_consulting': True
            }
        },
        {
            'email': 'rahul.kumar@example.com',
            'password': 'Demo@123',
            'full_name': 'Rahul Kumar',
            'phone': '+91 98765 43211',
            'profile': {
                'tagline': 'Mobile App Developer | Flutter & React Native',
                'bio': 'Building beautiful, performant mobile applications for over 5 years. Expert in Flutter and React Native with a passion for creating seamless user experiences.',
                'experience_years': 5,
                'skills': ['Flutter', 'React Native', 'Dart', 'JavaScript', 'Firebase', 'Swift', 'Kotlin'],
                'domains': ['Mobile Apps', 'E-commerce', 'HealthTech'],
                'hourly_rate': 65,
                'offers_classes': True,
                'offers_support': True
            }
        },
        {
            'email': 'neha.patel@example.com',
            'password': 'Demo@123',
            'full_name': 'Neha Patel',
            'phone': '+91 98765 43212',
            'profile': {
                'tagline': 'Backend Architect | Cloud & DevOps Expert',
                'bio': 'Cloud-native architect with expertise in designing highly available, scalable systems. AWS certified with strong experience in containerization and CI/CD pipelines.',
                'experience_years': 8,
                'skills': ['Python', 'Go', 'Kubernetes', 'Docker', 'AWS', 'Terraform', 'Jenkins'],
                'domains': ['Cloud Infrastructure', 'DevOps', 'Enterprise'],
                'hourly_rate': 90,
                'offers_consulting': True,
                'offers_support': True
            }
        },
        {
            'email': 'amit.singh@example.com',
            'password': 'Demo@123',
            'full_name': 'Amit Singh',
            'phone': '+91 98765 43213',
            'profile': {
                'tagline': 'Data Science Lead | NLP & Computer Vision',
                'bio': 'Leading data science initiatives with focus on natural language processing and computer vision. Published researcher with hands-on experience deploying ML models at scale.',
                'experience_years': 7,
                'skills': ['Python', 'PyTorch', 'TensorFlow', 'OpenCV', 'NLP', 'SQL', 'Spark'],
                'domains': ['AI/ML', 'Data Analytics', 'Research'],
                'hourly_rate': 85,
                'offers_classes': True,
                'offers_consulting': True
            }
        }
    ]
    
    created_developers = []
    for dev_data in developers_data:
        user = User(
            email=dev_data['email'],
            full_name=dev_data['full_name'],
            phone=dev_data['phone'],
            role='developer',
            status='verified'
        )
        user.set_password(dev_data['password'])
        db.session.add(user)
        db.session.flush()
        
        profile = DeveloperProfile(
            user_id=user.id,
            tagline=dev_data['profile']['tagline'],
            bio=dev_data['profile']['bio'],
            experience_years=dev_data['profile']['experience_years'],
            skills=json.dumps(dev_data['profile']['skills']),
            domains=json.dumps(dev_data['profile']['domains']),
            hourly_rate=dev_data['profile']['hourly_rate'],
            offers_classes=dev_data['profile'].get('offers_classes', False),
            offers_consulting=dev_data['profile'].get('offers_consulting', False),
            offers_support=dev_data['profile'].get('offers_support', False),
            availability='available',
            articles_count=len([a for a in get_demo_articles() if a['developer_index'] == len(created_developers)])
        )
        db.session.add(profile)
        created_developers.append(profile)
    
    db.session.flush()
    
    # Create demo clients
    clients_data = [
        {
            'email': 'john.miller@startup.com',
            'password': 'Demo@123',
            'full_name': 'John Miller',
            'phone': '+1 555 123 4567',
            'profile': {
                'company_name': 'TechFlow Startup',
                'company_size': 'startup',
                'industry': 'FinTech',
                'website': 'https://techflow.example.com'
            }
        },
        {
            'email': 'sarah.johnson@enterprise.com',
            'password': 'Demo@123',
            'full_name': 'Sarah Johnson',
            'phone': '+1 555 234 5678',
            'profile': {
                'company_name': 'Enterprise Solutions Inc.',
                'company_size': 'enterprise',
                'industry': 'Healthcare',
                'website': 'https://enterprise-sol.example.com'
            }
        }
    ]
    
    for client_data in clients_data:
        user = User(
            email=client_data['email'],
            full_name=client_data['full_name'],
            phone=client_data['phone'],
            role='client',
            status='verified'
        )
        user.set_password(client_data['password'])
        db.session.add(user)
        db.session.flush()
        
        profile = ClientProfile(
            user_id=user.id,
            company_name=client_data['profile']['company_name'],
            company_size=client_data['profile']['company_size'],
            industry=client_data['profile']['industry'],
            website=client_data['profile']['website']
        )
        db.session.add(profile)
    
    db.session.flush()
    
    # Create demo articles
    articles_data = get_demo_articles()
    for article_data in articles_data:
        dev_profile = created_developers[article_data['developer_index']]
        article = Article(
            developer_id=dev_profile.id,
            title=article_data['title'],
            slug=article_data['slug'],
            excerpt=article_data['excerpt'],
            content=article_data['content'],
            article_type=article_data['article_type'],
            technologies=json.dumps(article_data['technologies']),
            domain=article_data['domain'],
            status='approved',
            views_count=article_data.get('views', 0),
            published_at=datetime.utcnow() - timedelta(days=article_data.get('days_ago', 0))
        )
        article.generate_slug()
        db.session.add(article)
    
    db.session.commit()
    print("Demo data seeded successfully!")


def get_demo_articles():
    """Return demo articles data"""
    return [
        {
            'developer_index': 0,
            'title': 'Building a Real-Time Trading Dashboard with React and WebSockets',
            'slug': 'building-realtime-trading-dashboard-react-websockets',
            'excerpt': 'Learn how we built a high-performance trading dashboard that handles over 10,000 real-time price updates per second using React, Redux, and WebSockets.',
            'content': '''
                <h2>The Challenge</h2>
                <p>Our client, a leading cryptocurrency exchange, needed a trading dashboard that could handle massive amounts of real-time data without compromising performance. The existing solution was struggling with just 1,000 updates per second.</p>
                
                <h2>Our Approach</h2>
                <p>We implemented a multi-layered architecture using React for the UI, Redux for state management, and WebSockets for real-time communication. Key optimizations included:</p>
                <ul>
                    <li>Virtual scrolling for order books with 100k+ entries</li>
                    <li>Batched state updates to reduce re-renders</li>
                    <li>Web Workers for heavy calculations</li>
                    <li>Canvas-based charting for smooth animations</li>
                </ul>
                
                <h2>Results</h2>
                <p>The new dashboard handles 10,000+ updates per second with sub-16ms render times, a 10x improvement over the previous solution.</p>
            ''',
            'article_type': 'case_study',
            'technologies': ['React', 'Redux', 'WebSocket', 'Node.js', 'Canvas'],
            'domain': 'FinTech',
            'views': 1250,
            'days_ago': 5
        },
        {
            'developer_index': 0,
            'title': 'Implementing Secure Payment Processing with Stripe and React',
            'slug': 'implementing-secure-payment-processing-stripe-react',
            'excerpt': 'A comprehensive guide to building PCI-compliant payment flows using Stripe Elements and React hooks.',
            'content': '''
                <h2>Introduction</h2>
                <p>Payment security is critical for any e-commerce application. In this tutorial, I'll walk you through implementing a secure, PCI-compliant payment system using Stripe.</p>
                
                <h2>Key Concepts</h2>
                <p>We'll cover Stripe Elements, Payment Intents, and best practices for handling sensitive payment data securely in React applications.</p>
            ''',
            'article_type': 'tutorial',
            'technologies': ['React', 'Stripe', 'Node.js', 'Express'],
            'domain': 'E-commerce',
            'views': 890,
            'days_ago': 12
        },
        {
            'developer_index': 1,
            'title': 'From Zero to Store: Building a Cross-Platform E-commerce App with Flutter',
            'slug': 'zero-to-store-cross-platform-ecommerce-flutter',
            'excerpt': 'Complete case study on how we delivered a feature-rich e-commerce mobile app for iOS and Android in just 8 weeks using Flutter.',
            'content': '''
                <h2>Project Overview</h2>
                <p>A retail client needed a mobile app that could match native performance while maintaining a single codebase. Flutter was our weapon of choice.</p>
                
                <h2>Features Delivered</h2>
                <ul>
                    <li>Product catalog with advanced filtering</li>
                    <li>Real-time inventory updates</li>
                    <li>Secure checkout with multiple payment options</li>
                    <li>Push notifications for order updates</li>
                    <li>Offline mode for browsing</li>
                </ul>
                
                <h2>Technical Highlights</h2>
                <p>We used BLoC pattern for state management, Firebase for backend services, and implemented custom animations for a premium feel.</p>
            ''',
            'article_type': 'case_study',
            'technologies': ['Flutter', 'Dart', 'Firebase', 'BLoC', 'Stripe'],
            'domain': 'E-commerce',
            'views': 2100,
            'days_ago': 3
        },
        {
            'developer_index': 2,
            'title': 'Migrating a Monolith to Microservices on Kubernetes: A Practical Guide',
            'slug': 'migrating-monolith-microservices-kubernetes',
            'excerpt': 'Lessons learned from breaking down a legacy monolith into 20+ microservices running on Kubernetes, serving 10M+ daily requests.',
            'content': '''
                <h2>The Starting Point</h2>
                <p>Our client had a 10-year-old monolithic application that had become impossible to scale and maintain. Deployments were taking hours and any change risked breaking the entire system.</p>
                
                <h2>The Strategy</h2>
                <p>We adopted the Strangler Fig pattern, gradually extracting services while keeping the monolith running. Key phases included:</p>
                <ul>
                    <li>Identifying bounded contexts</li>
                    <li>Setting up Kubernetes infrastructure</li>
                    <li>Implementing service mesh with Istio</li>
                    <li>Establishing CI/CD pipelines</li>
                </ul>
                
                <h2>Outcomes</h2>
                <p>Deployment time reduced from 4 hours to 15 minutes. System availability improved to 99.99%. Development velocity doubled.</p>
            ''',
            'article_type': 'case_study',
            'technologies': ['Kubernetes', 'Docker', 'Istio', 'Go', 'Python', 'AWS'],
            'domain': 'Cloud Infrastructure',
            'views': 3500,
            'days_ago': 7
        },
        {
            'developer_index': 3,
            'title': 'Building an Intelligent Document Processing System with OCR and NLP',
            'slug': 'intelligent-document-processing-ocr-nlp',
            'excerpt': 'How we built an AI system that automatically extracts, classifies, and processes documents with 98% accuracy for a healthcare provider.',
            'content': '''
                <h2>The Problem</h2>
                <p>A healthcare organization was spending thousands of hours manually processing patient documents. They needed automation that could handle handwritten notes, scanned forms, and digital documents.</p>
                
                <h2>Our Solution</h2>
                <p>We built a comprehensive document processing pipeline using:</p>
                <ul>
                    <li>Tesseract OCR with custom training for medical terminology</li>
                    <li>BERT-based document classification</li>
                    <li>Named Entity Recognition for extracting patient information</li>
                    <li>Confidence scoring and human-in-the-loop for edge cases</li>
                </ul>
                
                <h2>Impact</h2>
                <p>Processing time reduced by 90%. Staff could focus on patient care instead of paperwork. The system processes 5,000+ documents daily.</p>
            ''',
            'article_type': 'case_study',
            'technologies': ['Python', 'PyTorch', 'BERT', 'Tesseract', 'FastAPI'],
            'domain': 'HealthTech',
            'views': 1800,
            'days_ago': 10
        },
        {
            'developer_index': 3,
            'title': 'Advanced NLP Techniques for Building Intelligent Chatbots',
            'slug': 'advanced-nlp-techniques-intelligent-chatbots',
            'excerpt': 'Deep dive into transformer architectures, intent classification, and context management for building production-grade conversational AI.',
            'content': '''
                <h2>Beyond Simple Chatbots</h2>
                <p>Modern chatbots need to understand context, handle complex queries, and provide human-like responses. This research explores advanced techniques we've developed.</p>
                
                <h2>Key Techniques</h2>
                <ul>
                    <li>Fine-tuning transformers for domain-specific language</li>
                    <li>Multi-turn context management</li>
                    <li>Entity extraction and slot filling</li>
                    <li>Retrieval-augmented generation</li>
                </ul>
            ''',
            'article_type': 'research',
            'technologies': ['Python', 'Transformers', 'PyTorch', 'Rasa', 'LangChain'],
            'domain': 'AI/ML',
            'views': 2800,
            'days_ago': 2
        }
    ]
