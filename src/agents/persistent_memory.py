"""
Persistent Memory Management
SQLite-based persistence for agentic RAG memories
"""

import sqlite3
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import numpy as np

class PersistentMemoryManager:
    """
    SQLite-based persistent memory management for agentic RAG
    """
    
    def __init__(self, db_path: str = ".rag-demo/persistent_memory.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Episodic memories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS episodic_memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                content TEXT NOT NULL,
                context TEXT,
                embedding BLOB,
                timestamp TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Semantic memories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS semantic_memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                concept TEXT NOT NULL,
                knowledge TEXT NOT NULL,
                relationships TEXT,
                confidence REAL DEFAULT 1.0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Procedural memories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS procedural_memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                skill TEXT NOT NULL,
                steps TEXT NOT NULL,
                prerequisites TEXT,
                success_criteria TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # User profiles table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id TEXT PRIMARY KEY,
                preferences TEXT,
                learning_goals TEXT,
                learning_style TEXT,
                total_sessions INTEGER DEFAULT 0,
                last_active TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Performance metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                framework TEXT NOT NULL,
                query TEXT NOT NULL,
                response_time REAL NOT NULL,
                confidence REAL NOT NULL,
                memory_types_used TEXT,
                personalized BOOLEAN DEFAULT 0,
                success BOOLEAN DEFAULT 1,
                timestamp TEXT NOT NULL
            )
        """)
        
        # Create indexes for better performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_episodic_user_id ON episodic_memories(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_episodic_timestamp ON episodic_memories(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_semantic_concept ON semantic_memories(concept)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_procedural_skill ON procedural_memories(skill)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_performance_framework ON performance_metrics(framework)")
        
        conn.commit()
        conn.close()
    
    async def store_episodic(self, user_id: str, event_type: str, content: str, 
                           context: Dict[str, Any], embedding: List[float]) -> int:
        """Store episodic memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Convert embedding to bytes
        embedding_bytes = np.array(embedding, dtype=np.float32).tobytes()
        
        cursor.execute("""
            INSERT INTO episodic_memories (user_id, event_type, content, context, embedding, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, event_type, content, json.dumps(context), embedding_bytes, datetime.now().isoformat()))
        
        memory_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return memory_id
    
    async def retrieve_episodic(self, user_id: str, query: str = None, 
                               event_type: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve episodic memories"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Build query
        where_clauses = ["user_id = ?"]
        params = [user_id]
        
        if event_type:
            where_clauses.append("event_type = ?")
            params.append(event_type)
        
        if query:
            where_clauses.append("content LIKE ?")
            params.append(f"%{query}%")
        
        where_sql = " AND ".join(where_clauses)
        
        cursor.execute(f"""
            SELECT id, event_type, content, context, timestamp
            FROM episodic_memories
            WHERE {where_sql}
            ORDER BY timestamp DESC
            LIMIT ?
        """, params + [limit])
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "id": row[0],
                "event_type": row[1],
                "content": row[2],
                "context": json.loads(row[3]) if row[3] else {},
                "timestamp": row[4]
            })
        
        conn.close()
        return results
    
    async def store_semantic(self, concept: str, knowledge: Dict[str, Any], 
                           relationships: List[str] = None, confidence: float = 1.0) -> int:
        """Store semantic memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO semantic_memories (concept, knowledge, relationships, confidence)
            VALUES (?, ?, ?, ?)
        """, (concept, json.dumps(knowledge), json.dumps(relationships or []), confidence))
        
        memory_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return memory_id
    
    async def retrieve_semantic(self, concept: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve semantic memories"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if concept:
            cursor.execute("""
                SELECT id, concept, knowledge, relationships, confidence
                FROM semantic_memories
                WHERE concept LIKE ?
                ORDER BY confidence DESC
                LIMIT ?
            """, (f"%{concept}%", limit))
        else:
            cursor.execute("""
                SELECT id, concept, knowledge, relationships, confidence
                FROM semantic_memories
                ORDER BY confidence DESC
                LIMIT ?
            """, (limit,))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "id": row[0],
                "concept": row[1],
                "knowledge": json.loads(row[2]),
                "relationships": json.loads(row[3]) if row[3] else [],
                "confidence": row[4]
            })
        
        conn.close()
        return results
    
    async def store_procedural(self, skill: str, steps: List[Dict[str, Any]], 
                             prerequisites: List[str] = None, 
                             success_criteria: List[str] = None) -> int:
        """Store procedural memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO procedural_memories (skill, steps, prerequisites, success_criteria)
            VALUES (?, ?, ?, ?)
        """, (skill, json.dumps(steps), json.dumps(prerequisites or []), json.dumps(success_criteria or [])))
        
        memory_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return memory_id
    
    async def retrieve_procedural(self, skill: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve procedural memories"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if skill:
            cursor.execute("""
                SELECT id, skill, steps, prerequisites, success_criteria
                FROM procedural_memories
                WHERE skill LIKE ?
                ORDER BY id DESC
                LIMIT ?
            """, (f"%{skill}%", limit))
        else:
            cursor.execute("""
                SELECT id, skill, steps, prerequisites, success_criteria
                FROM procedural_memories
                ORDER BY id DESC
                LIMIT ?
            """, (limit,))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "id": row[0],
                "skill": row[1],
                "steps": json.loads(row[2]),
                "prerequisites": json.loads(row[3]) if row[3] else [],
                "success_criteria": json.loads(row[4]) if row[4] else []
            })
        
        conn.close()
        return results
    
    async def store_user_profile(self, user_id: str, preferences: Dict[str, Any], 
                               learning_goals: List[str], learning_style: str = None) -> None:
        """Store user profile"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO user_profiles 
            (user_id, preferences, learning_goals, learning_style, last_active)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, json.dumps(preferences), json.dumps(learning_goals), 
              learning_style, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT preferences, learning_goals, learning_style, total_sessions, last_active
            FROM user_profiles
            WHERE user_id = ?
        """, (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "preferences": json.loads(row[0]) if row[0] else {},
                "learning_goals": json.loads(row[1]) if row[1] else [],
                "learning_style": row[2],
                "total_sessions": row[3],
                "last_active": row[4]
            }
        
        return None
    
    async def store_performance_metrics(self, framework: str, query: str, 
                                      response_time: float, confidence: float,
                                      memory_types_used: List[str], 
                                      personalized: bool, success: bool) -> int:
        """Store performance metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO performance_metrics 
            (framework, query, response_time, confidence, memory_types_used, personalized, success, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (framework, query, response_time, confidence, json.dumps(memory_types_used), 
              personalized, success, datetime.now().isoformat()))
        
        metric_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return metric_id
    
    async def get_performance_summary(self, framework: str = None, 
                                    days: int = 30) -> Dict[str, Any]:
        """Get performance summary"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        where_clause = "timestamp >= datetime('now', '-{} days')".format(days)
        if framework:
            where_clause += f" AND framework = '{framework}'"
        
        cursor.execute(f"""
            SELECT 
                framework,
                COUNT(*) as total_queries,
                AVG(response_time) as avg_response_time,
                AVG(confidence) as avg_confidence,
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_queries,
                SUM(CASE WHEN personalized = 1 THEN 1 ELSE 0 END) as personalized_queries
            FROM performance_metrics
            WHERE {where_clause}
            GROUP BY framework
        """)
        
        results = {}
        for row in cursor.fetchall():
            results[row[0]] = {
                "total_queries": row[1],
                "avg_response_time": row[2],
                "avg_confidence": row[3],
                "successful_queries": row[4],
                "personalized_queries": row[5],
                "success_rate": row[4] / row[1] if row[1] > 0 else 0,
                "personalization_rate": row[5] / row[1] if row[1] > 0 else 0
            }
        
        conn.close()
        return results
    
    async def cleanup_old_data(self, days: int = 90):
        """Clean up old data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = datetime.now().replace(day=datetime.now().day - days).isoformat()
        
        # Clean up old episodic memories (keep last 90 days)
        cursor.execute("""
            DELETE FROM episodic_memories 
            WHERE timestamp < ?
        """, (cutoff_date,))
        
        # Clean up old performance metrics (keep last 30 days)
        cursor.execute("""
            DELETE FROM performance_metrics 
            WHERE timestamp < datetime('now', '-30 days')
        """)
        
        conn.commit()
        conn.close()
        
        print(f"🧹 Cleaned up data older than {days} days")
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Count records in each table
        tables = ['episodic_memories', 'semantic_memories', 'procedural_memories', 
                 'user_profiles', 'performance_metrics']
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            stats[f"{table}_count"] = cursor.fetchone()[0]
        
        # Database size
        stats['database_size_mb'] = self.db_path.stat().st_size / (1024 * 1024)
        
        conn.close()
        return stats
