import unittest
import sqlite3
from travel_recommender import get_continent, store_places, show_recommendations_by_continent, get_city_name

class TestTravelRecommendationSystem(unittest.TestCase):
    def test_get_continents(self):
        self.assertEqual(get_continent(40.446856, -96.473234), "North America")
        self.assertEqual(get_continent(-11.752413, -55.550732), "South America")
        self.assertEqual(get_continent(47.771387, 5.691208), "Europe")
        self.assertEqual(get_continent(27.479031, 104.676204), "Asia")
        self.assertEqual(get_continent(17.620207, 18.414765), "Africa")
        self.assertEqual(get_continent(-25.405958, 145.929709), "Australia")
        self.assertEqual(get_continent(-79.267650, 43.218829), "Antarctica")

    def test_show_recommendations_empty_db(self):
        result = show_recommendations_by_continent("Europe")
        self.assertEqual(result, "No recommendations found for Europe.")

    def test_continent_name_variations(self):
        conn = sqlite3.connect('travel.db')
        c = conn.cursor()
        c.execute("INSERT INTO places (destination, name, address, continent) VALUES (?, ?, ?, ?)",
                 ("Paris, France", "Eiffel Tower", "Champ de Mars", "Europe"))
        conn.commit()
        conn.close()
        
        self.assertNotEqual(show_recommendations_by_continent("europe"), 
                          "No recommendations found for europe.")
        self.assertNotEqual(show_recommendations_by_continent("EUROPE"), 
                          "No recommendations found for EUROPE.")
        
        conn = sqlite3.connect('travel.db')
        c = conn.cursor()
        c.execute("DELETE FROM places WHERE name = ?", ("Eiffel Tower",))
        conn.commit()
        conn.close()


if __name__ == '__main__':
    unittest.main()