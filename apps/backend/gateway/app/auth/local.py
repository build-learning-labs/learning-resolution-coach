"""Local email/password authentication."""

from typing import Optional
from sqlalchemy.orm import Session

from shared.db import User
from app.auth.jwt import verify_password, get_password_hash


async def authenticate_user(
    db: Session,
    email: str,
    password: str,
) -> Optional[User]:
    """Authenticate user with email and password.
    
    Args:
        db: Database session
        email: User email
        password: Plain text password
        
    Returns:
        User if authenticated, None otherwise
    """
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        return None
    
    if not user.hashed_password:
        # User registered via OAuth, no password set
        return None
    
    if not verify_password(password, user.hashed_password):
        return None
    
    return user


async def create_user(
    db: Session,
    email: str,
    password: str,
    full_name: Optional[str] = None,
) -> User:
    """Create a new user with email/password.
    
    Args:
        db: Database session
        email: User email
        password: Plain text password
        full_name: Optional full name
        
    Returns:
        Created user
    """
    hashed_password = get_password_hash(password)
    
    user = User(
        email=email,
        hashed_password=hashed_password,
        full_name=full_name,
        is_active=True,
        is_verified=False,
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


async def get_or_create_oauth_user(
    db: Session,
    google_id: str,
    email: str,
    full_name: Optional[str] = None,
) -> User:
    """Get or create user from OAuth provider.
    
    Args:
        db: Database session
        google_id: Google user ID
        email: User email
        full_name: Optional full name
        
    Returns:
        Existing or newly created user
    """
    # Check if user exists by Google ID
    user = db.query(User).filter(User.google_id == google_id).first()
    
    if user:
        return user
    
    # Check if user exists by email (might have registered locally)
    user = db.query(User).filter(User.email == email).first()
    
    if user:
        # Link Google account to existing user
        user.google_id = google_id
        db.commit()
        db.refresh(user)
        return user
    
    # Create new user
    user = User(
        email=email,
        google_id=google_id,
        full_name=full_name,
        is_active=True,
        is_verified=True,  # OAuth users are verified
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user
