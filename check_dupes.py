from backend.utils import db_utils

def check_duplicates():
    issues = db_utils.fetch_issues()
    seen = {}
    duplicates = []
    
    for issue in issues:
        # Key by title + description to find duplicates
        key = (issue['title'], issue['description'], issue['category'])
        if key in seen:
            duplicates.append(issue)
        else:
            seen[key] = issue
            
    print(f"Total Issues: {len(issues)}")
    print(f"Duplicates Found: {len(duplicates)}")
    
    if duplicates:
        print("Duplicate IDs:", [d['id'] for d in duplicates])
        
        # Determine if we should delete them
        # For now just list them
        for d in duplicates:
             print(f"Duplicate: ID {d['id']} - {d['title']}")

if __name__ == "__main__":
    check_duplicates()
