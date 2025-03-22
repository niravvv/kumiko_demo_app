"""
Kumiko Community Demo App - Main Application File

This Flask application provides a demonstration of a community discovery platform
where users can browse, join, and interact with various communities based on their interests.

Key features:
- Community discovery with card-based interface
- User profiles and authentication (simulated)
- In-memory data storage (no database required)
- Messaging system between users
- Community membership management

The app uses Flask for the web framework and stores all data in memory using Python dictionaries.
"""

from flask import Flask, render_template, jsonify, request, redirect, url_for, session, g
import json
import os
import random
import hashlib
import csv
from datetime import datetime
import uuid

# Initialize Flask application with static folder for assets
app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = 'kumiko_demo_secret_key'

# Custom Jinja2 filters for template rendering
@app.template_filter('hash')
def hash_filter(value):
    """
    Hash a string and return an integer value.
    Used for generating consistent colors for placeholder images.
    """
    return int(hashlib.md5(str(value).encode()).hexdigest(), 16)

@app.template_filter('date')
def date_filter(value, format='%B %d, %Y'):
    """
    Format dates in templates.
    Converts string dates to datetime objects and formats them according to specified format.
    """
    if isinstance(value, str):
        try:
            value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ')
        except ValueError:
            return value
    return value.strftime(format)

@app.template_filter('time')
def time_filter(value, format='%H:%M'):
    """
    Format time in templates.
    Converts string timestamps to datetime objects and formats them according to specified format.
    """
    if isinstance(value, str):
        try:
            value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ')
        except ValueError:
            return value
    return value.strftime(format)

# In-memory data storage for the demo app
# These dictionaries simulate database tables
users = {}                # Stores user data
communities = {}          # Stores community data
swipes = {}               # Stores user actions on communities
community_members = {}    # Stores membership relationships
chat_messages = {}        # Stores messages between users

# Load mock data from CSV files and initialize in-memory data structures
def load_mock_data():
    """
    Loads mock data from CSV files into memory.
    This function simulates database initialization by populating the 
    in-memory dictionaries with test data for users, communities, and memberships.
    """
    global users, communities, community_members

    # Mock users data
    users = {
        "user1": {
            "id": "user1",
            "username": "alex_gamer",
            "email": "alex@example.com",
            "password_hash": "hashed_password",
            "bio": "Hardcore gamer and anime fan",
            "profile_picture_url": "/static/images/user1.jpg",
            "interests": ["gaming", "anime", "tech"],
            "created_at": "2024-01-15T12:00:00Z"
        },
        "user2": {
            "id": "user2",
            "username": "samantha_cosplay",
            "email": "sam@example.com",
            "password_hash": "hashed_password",
            "bio": "Cosplayer and fantasy book lover",
            "profile_picture_url": "/static/images/user2.jpg",
            "interests": ["cosplay", "fantasy", "art"],
            "created_at": "2024-02-01T10:30:00Z"
        },
        "user3": {
            "id": "user3",
            "username": "tech_mike",
            "email": "mike@example.com",
            "password_hash": "hashed_password",
            "bio": "Software developer and technology enthusiast",
            "profile_picture_url": "/static/images/user3.jpg",
            "interests": ["tech", "gaming", "sci-fi"],
            "created_at": "2024-01-20T15:45:00Z"
        },
        "user4": {
            "id": "user4",
            "username": "bookworm_lisa",
            "email": "lisa@example.com",
            "password_hash": "hashed_password",
            "bio": "Book lover and aspiring writer",
            "profile_picture_url": "/static/images/user4.jpg",
            "interests": ["books", "writing", "fantasy"],
            "created_at": "2024-02-10T09:15:00Z"
        },
        "user5": {
            "id": "user5",
            "username": "art_jay",
            "email": "jay@example.com",
            "password_hash": "hashed_password",
            "bio": "Digital artist and game designer",
            "profile_picture_url": "/static/images/user5.jpg",
            "interests": ["art", "design", "gaming"],
            "created_at": "2024-01-25T11:20:00Z"
        }
    }
    
    # Load communities from CSV file
    communities = {}
    try:
        with open('communities.csv', 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Convert is_moderated string to boolean
                is_moderated = row['is_moderated'].lower() == 'true'
                # Convert member_count to integer
                try:
                    member_count = int(row['member_count'])
                except ValueError:
                    print(f"Invalid member_count for community {row['id']}: {row['member_count']}")
                    member_count = 0
                
                # Generate a hash-based color for the community
                color_hash = int(hashlib.md5(row['name'].encode()).hexdigest(), 16) % 16777215
                placeholder_url = f"https://placehold.co/600x300/{color_hash:06x}/fff?text={row['category']}"
                
                community = {
                    'id': row['id'],
                    'name': row['name'],
                    'description': row['description'],
                    'category': row['category'],
                    'is_moderated': is_moderated,
                    'member_count': member_count,
                    'image_url': placeholder_url,  # Use placeholder instead of the Imgur URL
                    'created_at': row['created_at']
                }
                communities[row['id']] = community
    except Exception as e:
        print(f"Error loading communities: {e}")
        # Fallback to empty communities if file loading fails
        communities = {}
    
    # Load community memberships from CSV file
    community_members = {}
    try:
        with open('memberships.csv', 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                membership_id = row.get('id', f"{row['user_id']}_{row['community_id']}")
                joined_at = row.get('joined_at', datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'))
                
                membership = {
                    'id': membership_id,
                    'user_id': row['user_id'],
                    'community_id': row['community_id'],
                    'status': row.get('status', 'joined'),
                    'joined_at': joined_at
                }
                community_members[membership_id] = membership
    except Exception as e:
        print(f"Error loading memberships: {e}")
        # Fallback to empty memberships if file loading fails
        community_members = {}
    
    # Initialize empty chat messages for each community
    for community_id in communities:
        chat_messages[community_id] = []

# Load mock data at startup
load_mock_data()

# Flask request processing hooks
@app.before_request
def before_request():
    """
    Executes before each request.
    Sets up global user data and current user for the request context.
    For demo purposes, always logs in as user1.
    """
    # Make the global users object accessible
    g.users = users
    g.current_user = users.get('user1')  # Always set user1 as current_user for demo

@app.context_processor
def inject_current_user():
    """
    Makes the current_user variable available to all templates.
    This eliminates the need to pass current_user to each render_template call.
    """
    # For demo purposes, always set user1 as current_user
    return {'current_user': g.current_user}

# Route definitions
@app.route('/')
def index():
    """
    Home page route.
    Displays the landing page with featured communities.
    """
    # Get featured communities
    featured_communities = []
    for comm_id, community in communities.items():
        if len(featured_communities) < 3:
            featured_communities.append(community)
    
    return render_template('index.html', 
                          featured_communities=featured_communities,
                          current_user=g.current_user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login route.
    In this demo, automatically logs in as user1 without authentication.
    """
    session['user_id'] = 'user1'
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    """
    User logout route.
    Removes the user_id from session and redirects to the home page.
    """
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    """
    User dashboard route.
    Shows communities the user has joined and recommended communities.
    """
    user_id = 'user1'  # Always use user1 for demo
    
    # Get communities the user has joined
    user_communities = []
    for member_id, member in community_members.items():
        if member['user_id'] == user_id and member['status'] == 'joined':
            user_communities.append(communities[member['community_id']])
    
    # Get recommended communities
    recommended_communities = []
    user_community_ids = [c['id'] for c in user_communities]
    
    # Simple recommendation: communities the user hasn't joined yet
    for comm_id, community in communities.items():
        if comm_id not in user_community_ids and len(recommended_communities) < 3:
            recommended_communities.append(community)
    
    return render_template('dashboard.html', 
                          user_communities=user_communities, 
                          recommended_communities=recommended_communities,
                          current_user=g.current_user)

@app.route('/discover')
def discover():
    """
    Discover page route.
    Shows a card-based interface for discovering new communities.
    """
    user_id = 'user1'  # Always use user1 for demo
    
    # Get communities the user hasn't interacted with yet
    # First, get all communities the user has swiped on
    user_swipes = [community_id for community_id, direction in swipes.get(user_id, {}).items()]
    
    # Then get all communities the user is a member of
    user_community_ids = [member['community_id'] for member_id, member in community_members.items() 
                          if member['user_id'] == user_id]
    
    # Combine the IDs the user has interacted with
    interacted_community_ids = set(user_swipes + user_community_ids)
    
    # Filter by category if provided
    category = request.args.get('category')
    
    # Get communities the user hasn't interacted with
    discover_communities = []
    for comm_id, community in communities.items():
        if comm_id not in interacted_community_ids:
            if not category or community['category'] == category:
                discover_communities.append(community)
    
    return render_template('discover.html', 
                          discover_communities=discover_communities,
                          current_user=g.current_user)

@app.route('/profile')
@app.route('/profile/<user_id>')
def profile(user_id=None):
    """
    User profile route.
    Displays user information, their joined communities, and for other users,
    shows communities in common with the current user.
    
    Args:
        user_id (str, optional): ID of the user to display. If None, shows current user's profile.
    """
    current_user_id = 'user1'  # Always use user1 for demo
    
    # If no user_id provided, show current user's profile
    if not user_id:
        user_id = current_user_id
    
    # Get the user
    user = users.get(user_id)
    if not user:
        return render_template('error.html', 
                              message="User not found",
                              current_user=g.current_user)
    
    # Get communities the user has joined
    user_communities = []
    for member_id, member in community_members.items():
        if member['user_id'] == user_id and member['status'] == 'joined':
            user_communities.append(communities[member['community_id']])
    
    # For other users, find common communities
    common_communities = []
    if user_id != current_user_id:
        current_user_community_ids = [member['community_id'] for member_id, member in community_members.items() 
                                      if member['user_id'] == current_user_id and member['status'] == 'joined']
        
        for community in user_communities:
            if community['id'] in current_user_community_ids:
                common_communities.append(community)
    
    return render_template('profile.html', 
                          user=user, 
                          user_communities=user_communities,
                          common_communities=common_communities,
                          user_community_count=len(user_communities),
                          current_user=g.current_user)

@app.route('/swipe', methods=['POST'])
def swipe():
    """
    Community interaction API endpoint.
    Handles user actions on community cards (like, super_like, reject).
    
    Expected JSON payload:
    {
        "community_id": "string", // ID of the community being interacted with
        "action": "string"        // One of: "like", "super_like", "reject"
    }
    
    Returns:
        JSON response with status and message
    """
    data = request.json
    user_id = 'user1'  # Demo user
    community_id = data.get('community_id')
    action = data.get('action')
    
    if not community_id or not action:
        return jsonify({"error": "Missing required parameters", "status": "error"}), 400
    
    # Record the swipe
    swipe_id = f"{user_id}_{community_id}"
    swipes[swipe_id] = {
        "id": swipe_id,
        "user_id": user_id,
        "community_id": community_id,
        "action": action,
        "timestamp": datetime.now().isoformat()
    }
    
    # Get community
    community = communities.get(community_id)
    if not community:
        return jsonify({"error": "Community not found", "status": "error"}), 404
    
    # Process based on action
    if action == 'like':
        # Check if the community is moderated
        if community['is_moderated']:
            status = 'pending'
            message = f"Join request for {community['name']} is pending approval."
        else:
            status = 'joined'
            community['member_count'] += 1
            message = f"You've joined {community['name']}!"
        
        # Add to community members
        member_id = f"{user_id}_{community_id}"
        community_members[member_id] = {
            "id": member_id,
            "user_id": user_id,
            "community_id": community_id,
            "status": status,
            "joined_at": datetime.now().isoformat() if status == 'joined' else None
        }
    elif action == 'super_like':
        # Super like - user becomes a featured member
        status = 'featured'
        community['member_count'] += 1
        message = f"You're now a featured member of {community['name']}!"
        
        # Add to community members as featured
        member_id = f"{user_id}_{community_id}"
        community_members[member_id] = {
            "id": member_id,
            "user_id": user_id,
            "community_id": community_id,
            "status": "featured",
            "joined_at": datetime.now().isoformat(),
            "featured": True
        }
    else:  # reject action
        status = 'rejected'
        message = f"You've skipped {community['name']}."
    
    return jsonify({
        "status": "success", 
        "message": message,
        "community": {
            "id": community_id,
            "name": community['name'],
            "member_count": community['member_count'],
            "category": community['category']
        }
    })

@app.route('/community/<community_id>')
def community_detail(community_id):
    user_id = session.get('user_id', 'user1')
    
    community = communities.get(community_id)
    
    if not community:
        return render_template('error.html', 
                              message="Community not found",
                              current_user=g.current_user)
    
    # Check if user is a member
    member_id = f"{user_id}_{community_id}"
    is_member = member_id in community_members and community_members[member_id]['status'] == 'joined'
    
    # Get community members
    community_member_details = []
    for m_id, member in community_members.items():
        if member['community_id'] == community_id and member['status'] == 'joined':
            member_user = users.get(member['user_id'])
            if member_user:
                community_member_details.append(member_user)
    
    # Get community messages
    messages = chat_messages.get(community_id, [])
    
    return render_template('community.html', 
                           community=community, 
                           is_member=is_member, 
                           messages=messages,
                           users=users,
                           community_members=community_member_details,
                           current_user=g.current_user)

@app.route('/api/communities')
def api_communities():
    return jsonify(list(communities.values()))

@app.route('/api/users')
def api_users():
    return jsonify(list(users.values()))

@app.route('/post_message', methods=['POST'])
def post_message():
    user_id = 'user1'  # Demo user
    community_id = request.form.get('community_id')
    message_text = request.form.get('message')
    
    if not community_id or not message_text:
        return jsonify({"error": "Missing required parameters"}), 400
    
    # Check if user is a member of the community
    member_id = f"{user_id}_{community_id}"
    if member_id not in community_members or community_members[member_id]['status'] != 'joined':
        return jsonify({"error": "You are not a member of this community"}), 403
    
    # Create and store message
    message = {
        "id": str(uuid.uuid4()),
        "sender_id": user_id,
        "message": message_text,
        "timestamp": datetime.now().isoformat()
    }
    
    if community_id not in chat_messages:
        chat_messages[community_id] = []
    
    chat_messages[community_id].append(message)
    
    return redirect(url_for('community_detail', community_id=community_id))

@app.route('/messages')
@app.route('/messages/<conversation_id>')
def messages(conversation_id=None):
    try:
        # For the demo, we'll just create some mock data
        mock_conversations = [
            {
                'id': '1',
                'user': users['user2'],
                'last_message': 'Hey, have you checked out the new gaming community?',
                'unread': 2
            },
            {
                'id': '2',
                'user': users['user3'],
                'last_message': 'Thanks for the welcome message!',
                'unread': 0
            }
        ]
        
        # Mock messages for the first conversation
        mock_messages = [
            {
                'id': '1',
                'user_id': 'user2',
                'user': users['user2'],
                'content': 'Hey, how are you doing today?',
                'timestamp': '2024-03-21T14:30:00Z'
            },
            {
                'id': '2',
                'user_id': 'user1',
                'user': users['user1'],
                'content': 'I\'m doing great! Just browsing some communities.',
                'timestamp': '2024-03-21T14:32:00Z'
            },
            {
                'id': '3',
                'user_id': 'user2',
                'user': users['user2'],
                'content': 'Have you checked out the new gaming community?',
                'timestamp': '2024-03-21T14:35:00Z'
            }
        ]
        
        # Users available for conversations
        available_users = [users[user_id] for user_id in users if user_id != 'user1']
        
        active_user = None
        if conversation_id:
            # In a real app, we would fetch the actual user
            active_user = users['user2']
        
        return render_template('messages.html',
                              conversations=mock_conversations,
                              active_conversation=conversation_id,
                              active_user=active_user,
                              messages=mock_messages if conversation_id == '1' else [],
                              available_users=available_users,
                              current_user=g.current_user)
    except Exception as e:
        app.logger.error(f"Error in messages route: {str(e)}")
        return redirect(url_for('error', message="There was an error loading the messages page."))

@app.route('/messages_simple')
def messages_simple():
    try:
        # Users available for conversations
        available_users = [users[user_id] for user_id in users if user_id != 'user1']
        
        return render_template('messages_simple.html',
                              available_users=available_users,
                              current_user=g.current_user)
    except Exception as e:
        app.logger.error(f"Error in messages_simple route: {str(e)}")
        return redirect(url_for('error', message="There was an error loading the messages page."))

@app.route('/start_conversation', methods=['POST'])
def start_conversation():
    # This would actually create a new conversation in a real app
    # For demo, just redirect to the messages page
    return redirect(url_for('messages'))

@app.route('/send_message', methods=['POST'])
def send_message():
    # This would actually save the message in a real app
    # For demo, just redirect back to the conversation
    conversation_id = request.form.get('conversation_id', '1')
    return redirect(url_for('messages', conversation_id=conversation_id))

@app.route('/error')
def error():
    message = request.args.get('message', 'An error occurred')
    return render_template('error.html', 
                          message=message,
                          current_user=g.current_user)

if __name__ == '__main__':
    # Ensure the static folders exist
    os.makedirs('static/images', exist_ok=True)
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=3000)