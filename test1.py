import unittest
from travel_recommender import get_lat_lon


# This unit test checks that the logic for pulling the latitude and longitude from the Google API output works correctly. It is crucial that the logic works corectly because the latitude and longitude are needed in (LATITUDE,LONGITUDE) format to be correctly fed into the Geoapify API
class TestTravelRecommendationSystem(unittest.TestCase):
  def test_get_lon_lat(self):
       # sample output from the Google API
      test_response = "Charleston, NC\n27.9281, -79.9311\nCharleston is an exceptional choice for your trip."


      lat, lon = get_lat_lon(test_response)
      self.assertEqual(lat, 27.9281)
      self.assertEqual(lon, -79.9311)