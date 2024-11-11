import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Football_Project.utils import send_picks_email
from Football_Project.models import db, Game, Pick, UserScore
# Test the email sending function
if __name__ == "__main__":
    # Sample user picks dictionary
    sample_user_picks = {
        "Game 1 (Team A vs Team B)": "Team A",
        "Game 2 (Team C vs Team D)": "Team D",
        "Game 3 (Team E vs Team F)": "Team F"
    }

    # Replace with your actual email for testing
    recipient_email = "stevenbarnes50@gmail.com"
    
    # Call the function to send email
    send_picks_email(recipient_email, sample_user_picks)
    print("Test email sent!")
