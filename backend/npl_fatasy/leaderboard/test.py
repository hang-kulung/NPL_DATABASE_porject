from django.test import TransactionTestCase
from django.db import connection
from .views import update_leaderboard_for_user, update_rank

class LeaderboardTestCase(TransactionTestCase):
    
    def setUp(self):
        """Insert test data into existing Supabase tables"""
        with connection.cursor() as cursor:
            # Insert fresh test data
            cursor.execute("""
                INSERT INTO fantasy_teams (fantasy_team_id, user_id, total_points)
                VALUES 
                    (1, 101, 150),
                    (2, 102, 200),
                    (3, 103, 175)
            """)
    
    def tearDown(self):
        """Clean up test data after each test"""
        with connection.cursor() as cursor:
            # Delete test data
            cursor.execute("DELETE FROM leaderboard WHERE user_id IN (101, 102, 103)")
            cursor.execute("DELETE FROM fantasy_team WHERE fantasy_team_id IN (1, 2, 3)")
    
    def test_update_leaderboard_for_user(self):
        """Test updating leaderboard for a user"""
        # Update leaderboard for team 1
        update_leaderboard_for_user(1)
        
        # Check if leaderboard was updated
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT user_id, total_points 
                FROM leaderboard 
                WHERE user_id = 101
            """)
            result = cursor.fetchone()
            
        self.assertIsNotNone(result)
        self.assertEqual(result[0], 101)  # user_id
        self.assertEqual(result[1], 150)  # total_points
        print("✓ test_update_leaderboard_for_user passed!")
    
    def test_update_rank(self):
        """Test rank calculation"""
        # Populate leaderboard
        update_leaderboard_for_user(1)
        update_leaderboard_for_user(2)
        update_leaderboard_for_user(3)
        
        # Update ranks
        update_rank()
        
        # Check ranks
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT user_id, total_points, rank 
                FROM leaderboard 
                ORDER BY rank
            """)
            results = cursor.fetchall()
        
        # User 102 has 200 points, should be rank 1
        self.assertEqual(results[0][0], 102)
        self.assertEqual(results[0][2], 1)
        
        # User 103 has 175 points, should be rank 2
        self.assertEqual(results[1][0], 103)
        self.assertEqual(results[1][2], 2)
        
        # User 101 has 150 points, should be rank 3
        self.assertEqual(results[2][0], 101)
        self.assertEqual(results[2][2], 3)
        print("✓ test_update_rank passed!")