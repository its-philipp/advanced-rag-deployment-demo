"""
User context management for personalized coaching.
Stores user preferences, chat history, and learning goals.
"""
import time
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
import os

@dataclass
class ChatMessage:
    """Represents a single chat message in the conversation."""
    timestamp: float
    role: str  # 'user' or 'assistant'
    content: str
    sources: List[Dict[str, Any]] = None
    confidence: float = 0.0

@dataclass
class UserProfile:
    """User profile with preferences and learning goals."""
    user_id: str
    preferences: Dict[str, Any]
    learning_goals: List[str]
    created_at: float
    last_active: float
    learning_style: Optional[str] = None
    total_sessions: int = 0

class UserContext:
    """Manages user-specific context and personalization."""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.profile = self._load_or_create_profile()
        self.chat_history: List[ChatMessage] = []
        self._load_chat_history()
    
    def _load_or_create_profile(self) -> UserProfile:
        """Load existing profile or create a new one."""
        profile_file = f".rag-demo/users/{self.user_id}/profile.json"
        
        if os.path.exists(profile_file):
            try:
                with open(profile_file, 'r') as f:
                    data = json.load(f)
                    return UserProfile(**data)
            except Exception as e:
                print(f"Error loading profile for {self.user_id}: {e}")
        
        # Create new profile
        profile = UserProfile(
            user_id=self.user_id,
            preferences={},
            learning_goals=[],
            created_at=time.time(),
            last_active=time.time()
        )
        self._save_profile(profile)
        return profile
    
    def _save_profile(self, profile: UserProfile):
        """Save user profile to disk."""
        os.makedirs(f".rag-demo/users/{self.user_id}", exist_ok=True)
        profile_file = f".rag-demo/users/{self.user_id}/profile.json"
        
        with open(profile_file, 'w') as f:
            json.dump(asdict(profile), f, indent=2)
    
    def _load_chat_history(self):
        """Load chat history from disk."""
        history_file = f".rag-demo/users/{self.user_id}/chat_history.json"
        
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r') as f:
                    data = json.load(f)
                    self.chat_history = [ChatMessage(**msg) for msg in data]
            except Exception as e:
                print(f"Error loading chat history for {self.user_id}: {e}")
                self.chat_history = []
    
    def _save_chat_history(self):
        """Save chat history to disk."""
        os.makedirs(f".rag-demo/users/{self.user_id}", exist_ok=True)
        history_file = f".rag-demo/users/{self.user_id}/chat_history.json"
        
        with open(history_file, 'w') as f:
            json.dump([asdict(msg) for msg in self.chat_history], f, indent=2)
    
    def add_chat_interaction(self, query: str, response: str, sources: List[Dict[str, Any]], confidence: float = 0.0):
        """Add a new chat interaction to the history."""
        # Add user message
        user_message = ChatMessage(
            timestamp=time.time(),
            role="user",
            content=query
        )
        self.chat_history.append(user_message)
        
        # Add assistant response
        assistant_message = ChatMessage(
            timestamp=time.time(),
            role="assistant",
            content=response,
            sources=sources,
            confidence=confidence
        )
        self.chat_history.append(assistant_message)
        
        # Update profile
        self.profile.last_active = time.time()
        self.profile.total_sessions += 1
        
        # Save to disk
        self._save_chat_history()
        self._save_profile(self.profile)
    
    def update_preferences(self, preferences: Dict[str, Any]):
        """Update user preferences."""
        self.profile.preferences.update(preferences)
        self.profile.last_active = time.time()
        self._save_profile(self.profile)
    
    def update_learning_goals(self, goals: List[str]):
        """Update user learning goals."""
        self.profile.learning_goals = goals
        self.profile.last_active = time.time()
        self._save_profile(self.profile)
    
    def update_learning_style(self, style: str):
        """Update user learning style."""
        self.profile.learning_style = style
        self.profile.last_active = time.time()
        self._save_profile(self.profile)
    
    def get_recent_context(self, limit: int = 5) -> List[ChatMessage]:
        """Get recent chat context."""
        return self.chat_history[-limit:] if self.chat_history else []
    
    def get_personality_prompt(self) -> str:
        """Build personalized system prompt based on user profile."""
        base_prompt = "Du bist ein persönlicher Lern-Coach."
        
        # Add learning style personalization
        if self.profile.learning_style:
            style_descriptions = {
                "visual": "Du erklärst Konzepte mit visuellen Beispielen und Diagrammen.",
                "auditory": "Du verwendest mündliche Erklärungen und Diskussionen.",
                "kinesthetic": "Du zeigst praktische Anwendungen und Übungen.",
                "reading": "Du stellst detaillierte schriftliche Erklärungen bereit."
            }
            if self.profile.learning_style in style_descriptions:
                base_prompt += f" {style_descriptions[self.profile.learning_style]}"
        
        # Add learning goals context
        if self.profile.learning_goals:
            goals_text = ", ".join(self.profile.learning_goals)
            base_prompt += f" Die aktuellen Lernziele des Nutzers sind: {goals_text}."
        
        # Add preferences context
        if self.profile.preferences.get("subject_focus"):
            subject = self.profile.preferences["subject_focus"]
            base_prompt += f" Der Fokus liegt auf dem Fachgebiet: {subject}."
        
        if self.profile.preferences.get("difficulty_level"):
            level = self.profile.preferences["difficulty_level"]
            base_prompt += f" Das bevorzugte Schwierigkeitsniveau ist: {level}."
        
        # Add recent context awareness
        recent_context = self.get_recent_context(3)
        if recent_context:
            base_prompt += " Berücksichtige den vorherigen Gesprächsverlauf für bessere Kontinuität."
        
        return base_prompt
    
    def get_user_summary(self) -> Dict[str, Any]:
        """Get a summary of the user's profile and recent activity."""
        return {
            "user_id": self.user_id,
            "preferences": self.profile.preferences,
            "learning_goals": self.profile.learning_goals,
            "learning_style": self.profile.learning_style,
            "total_sessions": self.profile.total_sessions,
            "recent_messages": len(self.chat_history),
            "last_active": datetime.fromtimestamp(self.profile.last_active).isoformat()
        }
