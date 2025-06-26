from data_base import create_reservation, find_reservation_by_phone, delete_reservation

def test_db():
    create_reservation("Test User", "1122334455", "2025-07-01", "6:00 PM", 3)
    res = find_reservation_by_phone("1122334455")
    print(res)
    deleted = delete_reservation("1122334455")
    print("Deleted:", deleted)

if __name__ == "__main__":
    test_db()
