import DataStructures

class Memory:
    def __init__(self):
        self.cuisine_preference = None  # Will hold a DataStructures.CuisinePreference instance
        self.suggested_dish = None  # Will hold a DataStructures.SuggestedDish instance

    def addPreference(self, message):
        # Assume message is a dict with keys for cuisine, is_vegetarian, and dish
        self.cuisine_preference = DataStructures.CuisinePreference(
            cuisine=message.get('cuisine'),
            is_vegetarian=message.get('is_vegetarian')
        )        

    def getPreference(self):
       return self.cuisine_preference
