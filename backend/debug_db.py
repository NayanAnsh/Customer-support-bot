"""
Database debugging helper script
View conversations and their history directly from the database
"""
from database import get_db_context
from db_operations import list_conversations, get_conversation
import json
from datetime import datetime

def print_separator():
    print("=" * 80)

def format_timestamp(ts_str):
    """Format ISO timestamp to readable format"""
    try:
        dt = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return ts_str

def view_all_conversations():
    """Display all conversations in the database"""
    print_separator()
    print("ALL CONVERSATIONS IN DATABASE")
    print_separator()
    
    with get_db_context() as db:
        conversations = list_conversations(db, limit=100)
        
        if not conversations:
            print("No conversations found in database.")
            return
        
        print(f"\nTotal conversations: {len(conversations)}\n")
        
        for i, conv in enumerate(conversations, 1):
            print(f"\n{i}. Session ID: {conv.session_id}")
            print(f"   Created: {conv.created_at}")
            print(f"   Updated: {conv.updated_at}")
            print(f"   Status: {conv.status}")
            print(f"   Messages: {len(conv.history) if conv.history else 0}")
            
            if conv.history:
                print("   Last message preview:")
                last_msg = conv.history[-1]
                content = last_msg.get('content', '')[:60]
                print(f"   {last_msg.get('role', 'unknown')}: {content}...")

def view_conversation_details(session_id):
    """Display detailed information about a specific conversation"""
    print_separator()
    print(f"CONVERSATION DETAILS: {session_id}")
    print_separator()
    
    with get_db_context() as db:
        conv = get_conversation(db, session_id)
        
        if not conv:
            print(f"Conversation {session_id} not found.")
            return
        
        print(f"\nSession ID: {conv.session_id}")
        print(f"Created: {conv.created_at}")
        print(f"Updated: {conv.updated_at}")
        print(f"Status: {conv.status}")
        print(f"Total Messages: {len(conv.history) if conv.history else 0}")
        
        if conv.history:
            print("\nMessage History:")
            print("-" * 80)
            
            for i, msg in enumerate(conv.history, 1):
                role = msg.get('role', 'unknown').upper()
                content = msg.get('content', '')
                timestamp = format_timestamp(msg.get('timestamp', ''))
                
                print(f"\n[{i}] {role} ({timestamp})")
                print(f"{content}")
        else:
            print("\nNo messages in this conversation.")

def view_conversations_by_status(status):
    """Display conversations filtered by status"""
    print_separator()
    print(f"CONVERSATIONS WITH STATUS: {status.upper()}")
    print_separator()
    
    with get_db_context() as db:
        conversations = list_conversations(db, limit=100, status=status)
        
        if not conversations:
            print(f"No {status} conversations found.")
            return
        
        print(f"\nFound {len(conversations)} conversations\n")
        
        for i, conv in enumerate(conversations, 1):
            print(f"\n{i}. Session ID: {conv.session_id}")
            print(f"   Created: {conv.created_at}")
            print(f"   Messages: {len(conv.history) if conv.history else 0}")

def view_latest_conversation():
    """Display the most recent conversation"""
    print_separator()
    print("LATEST CONVERSATION")
    print_separator()
    
    with get_db_context() as db:
        conversations = list_conversations(db, limit=1)
        
        if not conversations:
            print("No conversations found.")
            return
        
        conv = conversations[0]
        view_conversation_details(conv.session_id)

def export_conversation_json(session_id, filename=None):
    """Export conversation to JSON file"""
    with get_db_context() as db:
        conv = get_conversation(db, session_id)
        
        if not conv:
            print(f"Conversation {session_id} not found.")
            return
        
        data = {
            "session_id": str(conv.session_id),
            "created_at": str(conv.created_at),
            "updated_at": str(conv.updated_at),
            "status": conv.status,
            "message_count": len(conv.history) if conv.history else 0,
            "history": conv.history or []
        }
        
        if filename is None:
            filename = f"conversation_{session_id}.json"
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Conversation exported to {filename}")

def stats():
    """Show database statistics"""
    print_separator()
    print("DATABASE STATISTICS")
    print_separator()
    
    with get_db_context() as db:
        all_convs = list_conversations(db, limit=1000)
        active = list_conversations(db, limit=1000, status="active")
        escalated = list_conversations(db, limit=1000, status="escalated")
        resolved = list_conversations(db, limit=1000, status="resolved")
        
        total_messages = sum(len(c.history) if c.history else 0 for c in all_convs)
        avg_messages = total_messages / len(all_convs) if all_convs else 0
        
        print(f"\nTotal Conversations: {len(all_convs)}")
        print(f"Active: {len(active)}")
        print(f"Escalated: {len(escalated)}")
        print(f"Resolved: {len(resolved)}")
        print(f"\nTotal Messages: {total_messages}")
        print(f"Average Messages per Conversation: {avg_messages:.2f}")
        
        if all_convs:
            print(f"\nOldest Conversation: {all_convs[-1].created_at}")
            print(f"Newest Conversation: {all_convs[0].created_at}")

def interactive_menu():
    """Interactive menu for database exploration"""
    while True:
        print("\n" + "=" * 80)
        print("DATABASE DEBUG MENU")
        print("=" * 80)
        print("\n1. View all conversations")
        print("2. View latest conversation")
        print("3. View conversation details (by ID)")
        print("4. View conversations by status")
        print("5. Database statistics")
        print("6. Export conversation to JSON")
        print("0. Exit")
        
        choice = input("\nEnter choice: ").strip()
        
        if choice == "1":
            view_all_conversations()
        elif choice == "2":
            view_latest_conversation()
        elif choice == "3":
            session_id = input("Enter session ID: ").strip()
            view_conversation_details(session_id)
        elif choice == "4":
            status = input("Enter status (active/escalated/resolved): ").strip()
            view_conversations_by_status(status)
        elif choice == "5":
            stats()
        elif choice == "6":
            session_id = input("Enter session ID: ").strip()
            export_conversation_json(session_id)
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "list":
            view_all_conversations()
        elif command == "latest":
            view_latest_conversation()
        elif command == "stats":
            stats()
        elif command == "view" and len(sys.argv) > 2:
            view_conversation_details(sys.argv[2])
        elif command == "status" and len(sys.argv) > 2:
            view_conversations_by_status(sys.argv[2])
        else:
            print("Usage:")
            print("  python debug_db.py list              # List all conversations")
            print("  python debug_db.py latest            # View latest conversation")
            print("  python debug_db.py stats             # Show statistics")
            print("  python debug_db.py view <session_id> # View specific conversation")
            print("  python debug_db.py status <status>   # View by status")
            print("  python debug_db.py                   # Interactive menu")
    else:
        interactive_menu()