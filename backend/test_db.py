from utils import db_utils

# Add a test issue
db_utils.add_issue(
    "Pothole in Main St",
    "Big pothole near bus stop",
    "road",
    24.817,
    93.936,
    severity=2
)

# Fetch and print all issues
print("All Issues:", db_utils.get_all_issues())

# Fetch Red Zones
print("Red Zones:", db_utils.get_red_zones())
